# -*- coding: utf-8 -*-
"""產生 data/dossier/_engine.md：共用引擎函式與全域常數。

英雄卷宗只放「這隻英雄的技能」，但很多關鍵行為其實在共用函式裡：
點燃／冰凍／電擊的機率修正鏈、投射物命中時附帶什麼狀態、傷害管線怎麼組
DefCof、穿透怎麼結算。這些對每隻英雄都一樣，複製 57 份是浪費，
所以抽成一份附錄，agent 讀一次就好。

另外附上 war3mapMisc.txt 的全域常數（英雄等級上限、屬性換算、
護甲類型倍率表）—— 沒有這些就算不出裸屬性與實際傷害。
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
from mpq import MPQ

OUT = os.path.join(ROOT, 'data', 'dossier', '_engine.md')

# 要整支附上原始碼的共用函式，依主題分組
GROUPS = [
    ('狀態的「施加」—— 機率修正鏈都在這裡', [
        'BurnUnit', 'FlammabilityUnit', 'FrostUnit', 'ShockUnit',
        'BleedUnit', 'DiseaseUnit', 'CurseUnit', 'WeakUnit',
        'VulnerabilityUnit', 'CharmUnit', 'SliceUnit', 'AnathemaUnit',
    ]),
    ('狀態的「結算」—— 每跳傷害怎麼算', [
        'Burn_Dmg', 'Bleed_Dmg', 'Disease_Dmg', 'RemoveShock',
        'RemoveFlammability', 'ClearUnit',
    ]),
    ('投射物 —— 命中時會附帶狀態，技能只呼叫 CreateProjectile 是看不出來的', [
        'CreateProjectile', 'ProjectileMove',
    ]),
    ('傷害管線 —— DefCof、穿透、反傷、苦難面具都在這一支', [
        'Trig_HeroTakeDamage_Actions',
    ]),
    ('道具觸發的入口 —— 注意它們各自的過濾條件', [
        'Trig_ItemAttacksFromHero_Conditions', 'Trig_ItemKills_Conditions',
        'Trig_UseSkillsEndcast_Conditions', 'StartModCooldown',
    ]),
]

# war3mapMisc.txt 裡值得抄出來的常數
MISC_KEYS = [
    ('MaxHeroLevel', '英雄等級上限'),
    ('MaxLevel', '單位等級上限'),
    ('StrRegenBonus', '每點力量的生命回復'),
    ('StrHitPointBonus', '每點力量的生命值'),
    ('IntRegenBonus', '每點智力的法力回復'),
    ('IntManaBonus', '每點智力的法力值'),
    ('AgiDefenseBonus', '每點敏捷的護甲'),
    ('AgiAttackSpeedBonus', '每點敏捷的攻擊速度'),
    ('DamageBonusNormal', '普通攻擊 vs 各護甲類型'),
    ('DamageBonusPierce', '穿刺攻擊 vs 各護甲類型'),
    ('DamageBonusSiege', '攻城攻擊 vs 各護甲類型'),
    ('DamageBonusMagic', '魔法攻擊 vs 各護甲類型'),
    ('DamageBonusChaos', '混亂攻擊 vs 各護甲類型'),
    ('DamageBonusHero', '英雄攻擊 vs 各護甲類型'),
]
ARMOR_ORDER = '順序：無甲 / 輕甲 / 中甲 / 重甲 / 城牆 / 英雄 / 神聖 / 其他'


def fspans(jass):
    lines = jass.split('\n')
    out, cur, start = {}, None, 0
    for i, l in enumerate(lines):
        m = re.match(r'function ([A-Za-z0-9_]+) ', l)
        if m:
            if cur:
                out[cur] = (start, i)
            cur, start = m.group(1), i
    if cur:
        out[cur] = (start, len(lines))
    return lines, out


def main():
    mp = json.load(io.open(os.path.join(HERE, 'version.json'),
                           encoding='utf-8'))['map_file']
    m = MPQ(mp)
    jass = m.read('war3map.j').decode('utf-8', 'replace')
    lines, spans = fspans(jass)

    L = ['# 引擎附錄：共用函式與全域常數', '',
         '英雄卷宗只放各自的技能。這一份放**所有英雄共用**的東西：',
         '狀態怎麼被施加與結算、投射物命中時附帶什麼、傷害管線怎麼組成、',
         '以及算裸屬性必備的全域常數。', '',
         '搭配 `data/dossier/<英雄ID>.md` 與 `tools/BUILD_BRIEF.md` 一起看。', '',
         '---', '', '## 全域常數（war3mapMisc.txt）', '']

    try:
        misc = m.read('war3mapMisc.txt').decode('utf-8-sig', 'replace')
    except Exception:
        misc = ''
    got = {}
    for line in misc.replace('\r\n', '\n').split('\n'):
        if '=' in line and not line.strip().startswith('//'):
            k, v = line.split('=', 1)
            got[k.strip()] = v.strip()
    if got:
        L.append('| 常數 | 值 | 意義 |')
        L.append('|---|---|---|')
        for k, lab in MISC_KEYS:
            if k in got:
                L.append('| `%s` | `%s` | %s |' % (k, got[k], lab))
        L.append('')
        L.append('護甲類型倍率的%s。' % ARMOR_ORDER)
        L.append('')
        L.append('> 這些是**地圖有覆寫**的值。沒列出來的走魔獸預設，')
        L.append('> 例如 `IntManaBonus` 若不在表上就是預設的 15 法力／點智力。')
    else:
        L.append('*（讀不到 war3mapMisc.txt，走魔獸預設值）*')
    L.append('')

    # hash key 對照表 —— 兩位 agent 都說得從 Trig_HeroTakeDamage_Actions
    # 與 Disease_Dmg 裡反推，直接列出來省一輪
    import build_dossier
    L += ['---', '', '## hash key 對照表', '',
          '同一個數字在「施加者」與「受害者」身上是完全不同的東西，',
          '而且實數槽與整數槽是**兩張不同的表**。', '',
          '| key | 意義 |', '|---|---|']
    for k in sorted(build_dossier.KEYS):
        L.append('| **%d** | %s |' % (k, build_dossier.KEYS[k]))
    L.append('')

    for title, fns in GROUPS:
        L.append('---')
        L.append('')
        L.append('## %s' % title)
        L.append('')
        for f in fns:
            if f not in spans:
                continue
            lo, hi = spans[f]
            body = [x for x in lines[lo:hi] if x.strip()]
            L.append('### `%s`　war3map.j:%d（%d 行）' % (f, lo + 1, hi - lo))
            L.append('')
            L.append('```jass')
            L.extend(body)
            L.append('```')
            L.append('')

    L += ['---', '',
          '*由 `tools/build_engineref.py` 從 UD_v3.81 地圖檔產生。*', '']
    doc = '\n'.join(L)
    d = os.path.dirname(OUT)
    if not os.path.isdir(d):
        os.makedirs(d)
    io.open(OUT, 'w', encoding='utf-8').write(doc)
    print('引擎附錄 -> %s（%d 支函式，%.0f KB）'
          % (os.path.relpath(OUT, ROOT),
             sum(1 for _, fs in GROUPS for f in fs if f in spans),
             len(doc.encode('utf-8')) / 1024))


if __name__ == '__main__':
    main()
