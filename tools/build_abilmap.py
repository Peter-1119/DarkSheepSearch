# -*- coding: utf-8 -*-
"""產生 data/abilmap.json：每個英雄技能的「機制依賴矩陣」。

目的有兩個：
  1. 反向查詢 —— 「哪些技能會施加冰凍」「哪些技能走 key 13 中繼」「哪些技能讀 key 18」。
  2. 改版影響分析 —— 新地圖進來時 diff_map.py 會逐函式比對，
     再拿這份矩陣反查：FrostUnit 改了 → 這 N 個技能受影響。

每個技能的標籤都從程式碼抽（跟卷宗同一套範圍計算：自己的分支 + 跟著回呼追三層），
不是從說明文字猜。純原生技能（JASS 裡沒有實作）標 native=True，
它們的改動只會出現在物件資料的 diff。

輸出結構：
  abilities: [ {id, hero, hero_n, n, kind, native, base, fns, status, hits, attack,
                scale, keys, own_fns, lines} ... ]
  by_fn / by_status / by_key / by_flag: 反向索引（值是技能 id 清單）
  fn_owner: {函式名: [技能 id]} —— 這支函式「屬於」哪些技能（own spans 落在裡面）
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
from mpq import MPQ
import w3obj
import build_dossier as bd

OUT = os.path.join(ROOT, 'data', 'abilmap.json')

# 共用函式 -> 狀態標籤。施加函式與結算函式分開列，結算函式是「所有同類狀態」的依賴。
STATUS_FN = {
    'BurnUnit': 'burn', 'Burn_Dmg': 'burn', 'FlammabilityUnit': 'flam', 'RemoveFlammability': 'flam',
    'FrostUnit': 'freeze', 'RemoveFrost': 'freeze', 'ShockUnit': 'shock', 'RemoveShock': 'shock',
    'BleedUnit': 'bleed', 'Bleed_Dmg': 'bleed', 'DiseaseUnit': 'disease', 'Disease_Dmg': 'disease',
    'CurseUnit': 'curse', 'WeakUnit': 'weak', 'VulnerabilityUnit': 'vuln', 'CharmUnit': 'charm',
    'SliceUnit': 'slice', 'AnathemaUnit': 'anathema', 'StunUnit': 'stun',
    'KnockBackUnit': 'knockback', 'KnockBackUnit2': 'knockback',
}
STATUS_N = {
    'burn': ['點燃', 'Burn', 'Поджог'], 'flam': ['易燃', 'Flammable', 'Горючесть'],
    'freeze': ['冰凍', 'Freeze', 'Заморозка'], 'shock': ['電擊', 'Shock', 'Шок'],
    'bleed': ['流血', 'Bleed', 'Кровотечение'], 'disease': ['疾病', 'Disease', 'Болезнь'],
    'curse': ['詛咒', 'Curse', 'Проклятие'], 'weak': ['虛弱', 'Weakness', 'Слабость'],
    'vuln': ['易傷', 'Vulnerability', 'Уязвимость'], 'charm': ['魅惑', 'Charm', 'Очарование'],
    'slice': ['切口', 'Slice', 'Надрез'], 'anathema': ['詛咒審判', 'Anathema', 'Анафема'],
    'stun': ['暈眩', 'Stun', 'Оглушение'], 'knockback': ['擊退', 'Knockback', 'Отбрасывание'],
}
# 旗標（布林）的說明
FLAG_N = {
    'native':  ['純原生', 'Native only', 'Только объектные данные'],
    'aoe':     ['範圍', 'AoE', 'По области'],
    'tick':    ['多跳', 'Multi-tick', 'Многотактовый'],
    'proj':    ['投射物', 'Projectile', 'Снаряд'],
    'relay':   ['key 13 中繼', 'Key-13 relay', 'Реле key 13'],
    'summon':  ['召喚', 'Summon', 'Призыв'],
    'heal':    ['治療', 'Heal', 'Лечение'],
    'onhit':   ['攻擊觸發', 'On-attack', 'При атаке'],
    'onkill':  ['擊殺觸發', 'On-kill', 'При убийстве'],
    'permanent': ['永久累加', 'Permanent stacking', 'Постоянное накопление'],
    'itemcd':  ['吃裝備技能冷卻', 'Uses item cooldown', 'Использует перезарядку предметов'],
    'chaos':   ['CHAOS 傷害', 'CHAOS damage', 'Урон CHAOS'],
}
SCALE_N = {
    'sp': ['技能強度', 'Spell power', 'Сила умений'], 'mod': ['裝備技能威力', 'Modifier power', 'Сила модификаторов'],
    'str': ['力量', 'STR', 'Сила'], 'agi': ['敏捷', 'AGI', 'Ловкость'], 'int': ['智力', 'INT', 'Разум'],
    'maxhp': ['最大生命', 'Max HP', 'Макс. здоровье'], 'lvl': ['技能等級', 'Ability level', 'Уровень умения'],
    'herolvl': ['英雄等級', 'Hero level', 'Уровень героя'],
}

CALLED = re.compile(r'\b(?:function|call) ([A-Za-z0-9_]+)')
DMG = re.compile(r'UnitDamageTarget\(')
ATK = re.compile(r'ATTACK_TYPE_([A-Z]+),DAMAGE_TYPE_([A-Z]+)')
KEY_R = re.compile(r'Load(?:Real|Integer|Boolean|Str|\w+Handle)\(hash,[A-Za-z_0-9()]+,(\d+)\)')
KEY_W = re.compile(r'Save(?:Real|Integer|Boolean|Str|\w+Handle)\(hash,[A-Za-z_0-9()]+,(\d+),')
SKEY = re.compile(r"(?:Save|Load|Remove)\w*\(hash,[A-Za-z_0-9()]+,'([A-Za-z0-9]{4})'")
SP_READ = re.compile(r'udg_ItemBonusDMG\[\w+\](?!\s*=\s*udg_ItemBonusDMG)')
SP_SET = re.compile(r'udg_ItemBonusDMG\[\w+\]=udg_ItemBonusDMG\[\w+\]\s*[+-][^*]*$')
KEY18_READ = re.compile(r'LoadReal\(hash,[A-Za-z_0-9()]+,18\)')
KEY18_SET = re.compile(r'SaveReal\(hash,[A-Za-z_0-9()]+,18,\s*LoadReal\(hash,[A-Za-z_0-9()]+,18\)')


def tag_ability(idx, spans, aid, A):
    lines, strip, fn, fspan, path = idx
    own = bd.merge(spans.get(aid) or [])
    all_r = bd.merge(bd.follow_callbacks(idx, own))
    rec = {'fns': set(), 'status': set(), 'flags': set(), 'attack': set(),
           'scale': set(), 'kr': set(), 'kw': set(), 'skeys': set(), 'own_fns': set(), 'lines': 0}
    if not own:
        rec['flags'].add('native')
    for lo, hi in own:
        rec['own_fns'].update(fn[i] for i in range(lo, hi))
    dmg_calls = 0
    for lo, hi in all_r:
        rec['lines'] += hi - lo
        for i in range(lo, hi):
            t = strip[i]
            if t.startswith('function '):
                continue
            for nm in CALLED.findall(t):
                if nm in fspan and nm not in bd.NOISE_FN:
                    rec['fns'].add(nm)
                if nm in STATUS_FN:
                    rec['status'].add(STATUS_FN[nm])
                if nm == 'StartModCooldown' and ("'%s'" % aid) in t:
                    rec['flags'].add('itemcd')
            if DMG.search(t):
                dmg_calls += 1
            for a, d in ATK.findall(t):
                rec['attack'].add(a + '/' + d)
                if a == 'CHAOS':
                    rec['flags'].add('chaos')
            if 'GroupEnumUnitsInRange' in t or 'GroupEnumUnitsInRect' in t:
                rec['flags'].add('aoe')
            if 'TimerStart(' in t and 'true' in t:
                rec['flags'].add('tick')
            if 'CreateProjectile(' in t or 'ProjectileMove' in t:
                rec['flags'].add('proj')
            if re.search(r'SaveReal\(hash,GetHandleId\(\w+\),13,', t):
                rec['flags'].add('relay')
            if bd.CREATE.search(t):
                rec['flags'].add('summon')
            if 'SetWidgetLife(' in t or 'UNIT_STATE_LIFE,' in t and 'SetUnitState' in t:
                rec['flags'].add('heal')
            if 'GetAttacker()' in t or 'EVENT_PLAYER_UNIT_ATTACKED' in t:
                rec['flags'].add('onhit')
            if 'GetKillingUnit()' in t or 'GetDyingUnit()' in t:
                rec['flags'].add('onkill')
            if re.search(r'SetHero(Str|Agi|Int)\([^,]+,[^,]+,true\)', t) or 'SetUnitBaseDamage(' in t:
                rec['flags'].add('permanent')
            if SP_READ.search(t) and not SP_SET.search(t):
                rec['scale'].add('sp')
            if KEY18_READ.search(t) and not KEY18_SET.search(t):
                rec['scale'].add('mod')
            for k in ('Str', 'Agi', 'Int'):
                if ('GetHero%s(' % k) in t:
                    rec['scale'].add(k.lower())
            if 'UNIT_STATE_MAX_LIFE' in t:
                rec['scale'].add('maxhp')
            if ('GetUnitAbilityLevel(u,\'%s\')' % aid) in t or 'GetUnitAbilityLevel(u,Skill)' in t:
                rec['scale'].add('lvl')
            if 'GetHeroLevel(' in t:
                rec['scale'].add('herolvl')
            rec['kr'].update(int(k) for k in KEY_R.findall(t))
            rec['kw'].update(int(k) for k in KEY_W.findall(t))
            rec['skeys'].update(k for k in SKEY.findall(t) if k != aid)
    rec['dmg_calls'] = dmg_calls
    # 物件資料
    a = A.get(aid, {})
    rec['base'] = a.get('_base')
    cd = a.get('acdn'); rec['acdn'] = cd if isinstance(cd, list) else ([cd] if cd is not None else None)
    lv = a.get('alev'); rec['alev'] = lv[0] if isinstance(lv, list) else lv
    return rec


def main():
    mp = json.load(io.open(os.path.join(HERE, 'version.json'), encoding='utf-8'))['map_file']
    if len(sys.argv) > 1 and sys.argv[1].lower().endswith('.w3x'):
        mp = sys.argv[1]
    m = MPQ(mp)
    jass = m.read('war3map.j').decode('utf-8', 'replace')
    A = w3obj.parse(m.read('war3map.w3a'), True)
    heroes = json.load(io.open(os.path.join(ROOT, 'data', 'heroes.json'), encoding='utf-8'))['heroes']
    idx = bd.index_jass(jass)
    spans = bd.ability_spans(idx)

    out, seen = [], set()
    def add(h, a, kind):
        if a['id'] in seen:
            return
        seen.add(a['id'])
        r = tag_ability(idx, spans, a['id'], A)
        out.append({
            'id': a['id'], 'hero': h['id'], 'hero_n': h['n'], 'n': a['n'], 'kind': kind,
            'icon': a.get('icon'),
            'native': 'native' in r['flags'], 'base': r['base'], 'alev': r['alev'], 'acdn': r['acdn'],
            'fns': sorted(r['fns']), 'own_fns': sorted(r['own_fns']),
            'status': sorted(r['status']), 'flags': sorted(r['flags'] - {'native'}),
            'attack': sorted(r['attack']), 'scale': sorted(r['scale']),
            'kr': sorted(r['kr']), 'kw': sorted(r['kw']), 'skeys': sorted(r['skeys']),
            'dmg_calls': r['dmg_calls'], 'lines': r['lines'],
        })
    for h in heroes:
        for a in h['ab']:
            if a['n'][0] in (u'轉移／移除據點',):
                continue
            add(h, a, a.get('kind') or 'hero')
            for o in a.get('opts') or []:
                add(h, o, 'talent')
        for s in h.get('skins') or []:
            for a in s.get('add') or []:
                add(h, a, 'skin')

    # 反向索引
    by_fn, by_status, by_key, by_flag, by_scale, fn_owner = {}, {}, {}, {}, {}, {}
    for r in out:
        for f in r['fns']: by_fn.setdefault(f, []).append(r['id'])
        for f in r['own_fns']: fn_owner.setdefault(f, []).append(r['id'])
        for s in r['status']: by_status.setdefault(s, []).append(r['id'])
        for k in r['kr'] + r['kw']: by_key.setdefault(str(k), []).append(r['id'])
        for k in r['skeys']: by_key.setdefault(k, []).append(r['id'])
        for f in r['flags']: by_flag.setdefault(f, []).append(r['id'])
        for f in r['scale']: by_scale.setdefault(f, []).append(r['id'])
    for d in (by_fn, by_status, by_key, by_flag, by_scale, fn_owner):
        for k in d: d[k] = sorted(set(d[k]))

    data = {'map': os.path.basename(mp), 'abilities': out,
            'by_fn': by_fn, 'by_status': by_status, 'by_key': by_key, 'by_flag': by_flag,
            'by_scale': by_scale, 'fn_owner': fn_owner,
            'names': {'status': STATUS_N, 'flag': FLAG_N, 'scale': SCALE_N,
                      'key': {str(k): v for k, v in bd.KEYS.items()}},
            'engine_fns': sorted(bd.ENGINE_FN)}
    io.open(OUT, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1))
    nat = sum(1 for r in out if r['native'])
    print('abilmap.json：%d 個技能（純原生 %d）、%d 支函式被引用、狀態 %s'
          % (len(out), nat, len(by_fn), {k: len(v) for k, v in by_status.items()}))


if __name__ == '__main__':
    main()
