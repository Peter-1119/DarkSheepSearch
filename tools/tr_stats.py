# -*- coding: utf-8 -*-
"""Russian item bonuses -> Traditional Chinese / English.

Simple stats are table driven; the damage/defence family is parsed
grammatically (kind x modifier x target) because the current map build
splits damage into "attack & ability" vs "status" damage.
"""
import re, sys, collections

NUM = r'[-+]?\d+(?:\.\d+)?%?'

# ---------------------------------------------------------------- simple stats
_SIMPLE = [
    ('HP regen', '生命回復', 'HP regen'), ('MP regen', '法力回復', 'MP regen'),
    ('HP', '生命值', 'HP'), ('MP', '法力值', 'MP'),
    ('атаки', '攻擊力', 'attack'), ('атк', '攻擊力', 'attack'), ('atk', '攻擊力', 'attack'),
    ('защиты', '護甲', 'armor'), ('защита', '護甲', 'armor'), ('armor', '護甲', 'armor'),
    ('сила умений', '技能強度', 'spell power'), ('spell power', '技能強度', 'spell power'),
    ('скорость атаки', '攻擊速度', 'attack speed'), ('atk speed', '攻擊速度', 'attack speed'),
    ('скорость передвижения и атаки', '移動與攻擊速度', 'move & attack speed'),
    ('скорость передвижения', '移動速度', 'move speed'),
    ('скорость бега', '移動速度', 'move speed'),
    ('move speed', '移動速度', 'move speed'),
    ('пробитие', '穿透', 'penetration'),
    ('силы', '力量', 'STR'), ('сила', '力量', 'STR'), ('str', '力量', 'STR'),
    ('ловкости', '敏捷', 'AGI'), ('ловкость', '敏捷', 'AGI'), ('agi', '敏捷', 'AGI'),
    ('разума', '智力', 'INT'), ('разум', '智力', 'INT'), ('int', '智力', 'INT'),
    ('ко всем характеристикам', '全屬性', 'all stats'),
    ('к характеристикам', '全屬性', 'all stats'),
    ('all stats', '全屬性', 'all stats'), ('main stat', '主屬性', 'main stat'),
    ('ответный урон', '反傷', 'thorns'),
    ('усиление ответного урона', '反傷加成', 'thorns bonus'),
    ('сила модификаторов', '裝備技能威力', 'mod power'),
    ('перезарядка модификаторов', '裝備技能冷卻', 'mod cooldown'),
    ('увеличение перезарядки предметов (дебаф)', '物品冷卻時間（負面）',
     'item cooldown (debuff)'),
    ('время воскрешения', '復活時間', 'respawn time'),
    ('вампиризм', '吸血', 'lifesteal'), ('эффект вампиризма', '吸血', 'lifesteal'),
    ('золото за убийства', '擊殺金幣', 'gold per kill'),
    ('награда за убийство врагов', '擊殺敵人獎勵', 'kill reward'),
    ('ед. ежеминутный доход золота', '每分鐘金幣收入', 'gold per minute'),
    ('ежеминутный доход золота', '每分鐘金幣收入', 'gold per minute'),
    ('доход золота', '金幣收入', 'gold income'),
    ('ед./сек. прирост опыта героя', '英雄經驗成長（每秒）', 'hero XP per sec'),
    ('прирост опыта героя', '英雄經驗成長', 'hero XP gain'),
    ('mag resist', '魔法傷害減免', 'magic resist'),
    ('защиты от магического урона', '魔法傷害減免', 'magic resist'),
    ('защита от магического урона', '魔法傷害減免', 'magic resist'),
    ('защита от магии', '魔法傷害減免', 'magic resist'),
    ('magic defence', '魔法傷害減免', 'magic resist'),
    ('dmg to melee units', '對近戰單位傷害', 'dmg to melee units'),
]
_SIMPLE.sort(key=lambda x: -len(x[0]))

FLAT = {
    'сопротивление проклятиям': ('抵抗詛咒', 'curse resistance'),
    'сопротивление поджогу': ('抵抗點燃', 'burn resistance'),
    'сопротивление поджогу и горючести': ('抵抗點燃與易燃', 'burn & flammable resistance'),
    'сопротивление кровотечению': ('抵抗流血', 'bleed resistance'),
    'сопротивление заморозке': ('抵抗冰凍', 'freeze resistance'),
    'сопротивление болезни': ('抵抗疾病', 'disease resistance'),
    'сопротивление кровотечению и заморозке': ('抵抗流血與冰凍', 'bleed & freeze resistance'),
    'кровотечению': ('抵抗流血', 'bleed resistance'),
    'заморозке': ('抵抗冰凍', 'freeze resistance'),
    'проклятиям': ('抵抗詛咒', 'curse resistance'),
    'болезни': ('抵抗疾病', 'disease resistance'),
    'поджогу': ('抵抗點燃', 'burn resistance'),
    'иммунитет к ответному урону': ('免疫反傷', 'thorns immunity'),
    '-': ('', ''),
    '+10% получаемый урон и наносимый урон от атак и умений против героев':
        ('+10%對英雄的攻擊與技能受到及造成傷害',
         '+10% attack & ability damage dealt to and taken from heroes'),
    '14% вампиризм и 17% сплеш-эффект от атак':
        ('14%吸血、攻擊17%濺射', '14% lifesteal and 17% attack splash'),
    'блокирует 10 ед. физического урона от атак':
        ('格擋攻擊 10 點物理傷害', 'blocks 10 physical damage from attacks'),
    '+15% защита от атак, умений и статусов':
        ('+15%攻擊、技能與狀態防禦', '+15% defence vs attacks, abilities and statuses'),
    'умений и статусов': ('', ''),
    '+8% защита от урона не от статусов': ('+8%非狀態傷害減免', '+8% non-status damage reduction'),
    '+20% увеличение перезарядки модификаторов':
        ('+20%裝備技能冷卻時間（負面）', '+20% mod cooldown (debuff)'),
    '+25% защита от кровотечения и поджога':
        ('+25%流血與點燃抗性', '+25% bleed and burn resistance'),
    '+2 ед./сек. прирост опыта героя': ('+2/秒英雄經驗成長', '+2/sec hero XP gain'),
}
CHUMA = 'дарует состояние "чумной"'
CHUMA_TR = ('賦予「瘟疫」狀態：免疫疾病，並可對敵人施加疾病（詳見 F2 圖鑑）',
            'Grants the "Plagued" state: immune to disease and able to apply disease '
            'to enemies (see the F2 codex)')

# ------------------------------------------------------- damage/defence family
KIND = [('снижение получаемого урона', '傷害減免', 'damage reduction'),
        ('снижение урона', '傷害減免', 'damage reduction'),
        ('получаемый урон', '受到傷害', 'damage taken'),
        ('получаемого урона', '受到傷害', 'damage taken'),
        ('наносимый урон', '造成傷害', 'damage dealt'),
        ('урон', '傷害', 'damage'), ('защиты', '防禦', 'defence'),
        ('защита', '防禦', 'defence')]
MOD = [('от атак и умений', '攻擊與技能', 'attack & ability'),
       ('(не от статусов)', '非狀態', 'non-status'),
       ('не от статусов', '非狀態', 'non-status'),
       ('от статусов', '狀態', 'status'),
       ('от поджога', '點燃', 'burn'), ('от кровотечения', '流血', 'bleed'),
       ('от болезни', '疾病', 'disease'), ('от заморозки', '冰凍', 'freeze'),
       ('от повторной заморозки', '二次冰凍', 'shatter'),
       ('от кровотечения и болезни', '流血與疾病', 'bleed & disease'),
       ('от атаки и умений', '攻擊與技能', 'attack & ability'),
       ('от урона', '', '')]
TGT = [('вражеских героев', '敵方英雄', 'enemy heroes'),
       ('вражеским героям', '敵方英雄', 'enemy heroes'),
       ('героям', '英雄', 'heroes'), ('героев', '英雄', 'heroes'),
       ('героями', '英雄', 'heroes'),
       ('не-героям', '非英雄單位', 'non-heroes'), ('не-героев', '非英雄單位', 'non-heroes'),
       ('врагам не-героям', '非英雄單位', 'non-hero enemies'),
       ('врагов не-героев', '非英雄單位', 'non-hero enemies'),
       ('врагам не-героев', '非英雄單位', 'non-hero enemies'),
       ('врагов не-героям', '非英雄單位', 'non-hero enemies'),
       ('нежити', '亡靈', 'undead'),
       ('юнитам ближнего боя', '近戰單位', 'melee units'),
       ('юнитов ближнего боя', '近戰單位', 'melee units'),
       ('врагам ближнего боя', '近戰單位', 'melee enemies'),
       ('врагов ближнего боя', '近戰單位', 'melee enemies'),
       ('юнитам дальнего боя', '遠程單位', 'ranged units'),
       ('юнитов дальнего боя', '遠程單位', 'ranged units'),
       ('врагам дальнего боя', '遠程單位', 'ranged enemies'),
       ('врагов дальнего боя', '遠程單位', 'ranged enemies'),
       ('магии', '魔法', 'magic'), ('магического урона', '魔法', 'magic'),
       ('атак', '攻擊', 'attacks')]
LVL = re.compile(r'(?:врагам|врагов|юнитам|юнитов)\s+([\d\-\+]+)\s*уровня')
STATUS_MODS = ('點燃', '流血', '疾病', '冰凍', '狀態', '二次冰凍', '流血與疾病')


def _strip(text, table, idx):
    for row in sorted(table, key=lambda x: -len(x[0])):
        ru = row[0]
        for pat in (' ' + ru, ru):
            k = text.find(pat)
            if k != -1:
                return row[idx], (text[:k] + ' ' + text[k + len(pat):]).strip()
    return None, text


def dmg_family(num, rest, lang):
    idx = 1 if lang == 'zh' else 2
    kind, rest = _strip(rest, KIND, idx)
    if kind is None:
        return None
    mod, rest = _strip(rest, MOD, idx)
    rest = re.sub(r'^(?:по|против|от|к)\b', '', rest).strip()
    m = LVL.search(rest)
    if m:
        tgt = (m.group(1) + '級敵人') if lang == 'zh' else ('lvl %s enemies' % m.group(1))
        rest = LVL.sub('', rest).strip()
    else:
        tgt, rest = _strip(rest, TGT, idx)
        rest = re.sub(r'^(?:по|против|от|к)\b', '', rest).strip()
    if rest:
        return None
    if lang == 'zh':
        zh = num
        if kind == '防禦' and not tgt and mod in STATUS_MODS:
            return zh + mod + '傷害減免'
        if tgt:
            zh += ('對' if kind in ('傷害', '防禦', '造成傷害', '傷害減免') else '受到') + tgt
            # 目標與限定詞同時存在時補「的」，否則會黏成一長串難斷句
            if mod:
                zh += '的'
        if mod:
            zh += mod
        return zh + kind
    out = num + ' '
    if kind == 'defence' and not tgt and mod:
        return out + mod + ' damage reduction'
    if mod:
        out += mod + ' '
    out += kind
    if tgt:
        out += (' vs ' if kind in ('damage', 'defence', 'damage dealt',
                                   'damage reduction') else ' from ') + tgt
    return out


NOSTAT = re.compile(r'\s*\((?:не влияет на статусы|не защищает от статусов|'
                    r'не влияет на урон от статусов)\)\s*$', re.I)


def tr_one(part, lang):
    idx = 0 if lang == 'zh' else 1
    p = part.strip().rstrip('.')
    low = p.lower()
    if low.startswith(CHUMA):
        return CHUMA_TR[idx], True
    m = NOSTAT.search(p)
    if m:
        t, ok = tr_one(p[:m.start()], lang)
        suffix = '（不影響狀態）' if lang == 'zh' else ' (does not affect statuses)'
        return (t + suffix if ok else p), ok
    if low in FLAT:
        return FLAT[low][idx], True
    m = re.match(r'^(%s)\s+(.*)$' % NUM, p)
    if not m:
        return p, False
    num, rest = m.group(1), m.group(2).strip()
    rest = re.sub(r'^ед\.(?!/)\s*', '', rest)
    for ru, zh, en in _SIMPLE:
        if rest.lower() == ru.lower():
            return (num + zh) if lang == 'zh' else (num + ' ' + en), True
    if rest.lower().startswith('крит. удар'):
        mm = re.search(r'[хx]([\d.]+)', rest)
        if mm:
            return (('%s機率造成%s倍暴擊' % (num, mm.group(1))) if lang == 'zh'
                    else ('%s chance of x%s crit' % (num, mm.group(1)))), True
    hit = dmg_family(num, rest.lower(), lang)
    if hit:
        return hit, True
    return p, False


def tr_bonus(s, lang='zh'):
    s = (s or '').replace('НР', 'HP').replace('МР', 'MP').replace('МP', 'MP')
    sep = '，' if lang == 'zh' else ', '
    for ru, pair in FLAT.items():
        if ',' in ru and s.strip().lower().endswith(ru):
            head = s.strip()[:len(s.strip()) - len(ru)].rstrip(', ')
            pre, _ = tr_bonus(head, lang)
            return sep.join(x for x in (pre, pair[0 if lang == 'zh' else 1]) if x), []
    out, bad = [], []
    for p in [x.strip() for x in re.split(r',(?![^()]*\))', s) if x.strip()]:
        zh, ok = tr_one(p, lang)
        if not ok:
            bad.append(p)
        if zh:
            out.append(zh)
    return sep.join(out), bad


if __name__ == '__main__':
    import json
    sys.stdout.reconfigure(encoding='utf-8')
    D = json.load(open('db_items.json', encoding='utf-8'))
    for lang in ('zh', 'en'):
        bad = collections.Counter()
        for r in D:
            _, b = tr_bonus(r['fields'].get('Бонусы', ''), lang)
            for x in b:
                bad[x] += 1
        print(lang, 'UNTRANSLATED:', len(bad))
        for k, v in bad.most_common(10):
            print('  ', v, k)
    for i in ('clsd', 'I09B', 'bgst', 'I01A', 'ram1', 'I0A8'):
        r = next(x for x in D if x['id'] == i)
        b = r['fields'].get('Бонусы', '')
        print('%-6s ZH %s' % (i, tr_bonus(b, 'zh')[0]))
        print('       EN %s' % tr_bonus(b, 'en')[0])
