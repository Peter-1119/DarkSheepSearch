# -*- coding: utf-8 -*-
"""配裝試算：白銀執法官（E00S）與拜火者（Hamg）。

所有公式直接取自 war3map.j：
  白銀之刃 A0OE   20+20*lv + SP*0.20，命中 3 名（SP>=500 為 5 名），內冷 6 秒
  迴旋投擲 A0OA   40+40*lv + SP*0.40，範圍 400；175 內再吃一次 0.50 倍
  均衡者之眼 A0OF 50 + SP*0.20，每 0.5 秒 22 跳，且只打「當前生命高於自己」的敵人
  追擊 AEbl       ACac 光環，+30~70% 攻擊力；SetUnitExtraArmor +3+lv
  律法之字 A0OD   ACct 原生暴擊，20% 機率，倍率 1.7 起、每殺一個敵方英雄 +0.3（上限 31 級）

  火山爆破 A03F   30+30*lv + SP*0.25，點燃底值 x1.50，機率 0.75
  烈焰旋風 A03O   每 0.30 秒放一顆、共 40 顆；60 + SP*0.30，點燃底值 x2.50，機率 0.60
  烈焰洪流 A02J   15+5*lv 顆（火焰浪潮 x2）；6+6*lv + SP*0.03，點燃底值 x1.00，機率 0.50
  火柱 AHfs       (20+25*lv + SP*0.20)*0.33，每秒一次共 16 秒，不施加點燃
  熔面者 A031     智力 x2.0，並以 120% 機率施加易燃

  點燃係數 DoT    1.00 + 點燃加成 + 零時迷子0.50；易燃時跳數 16 -> 32（傷害翻倍）
  點燃係數 瞬燃    1.50 + 點燃加成 + 零時迷子0.50；易燃只加機率不加傷害
  機率倍率        易燃 x1.5、幸運馬蹄鐵 x1.5（相乘）
"""
import json, io, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep'
D = json.load(io.open(os.path.join(ROOT, 'data', 'items.json'), encoding='utf-8'))['items']
S = json.load(io.open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))
IT, NS = S['items'], set(S.get('nostack') or [])
META = {m['k']: m for m in S['stats']}

BAN = {'新年', '復活節', '萬聖節', '儀式', '完美', '特殊（lv.5++）'}
BURN_IMMUNE = {'I01A', 'I06A', 'gmfr', 'ram4', 'rnsp', 'shhn', 'sorf', 'wolg'}


def totals(items, s1=None, s2=None):
    """把一套配裝的屬性加總；不可疊加的取最高。"""
    tot, mx = collections.defaultdict(float), collections.defaultdict(float)
    for i in items + [x for x in (s1, s2) if x]:
        for k, v in (IT[i].get('v') or {}).items():
            if k in NS:
                mx[k] = max(mx[k], v)
            else:
                tot[k] += v
    tot.update(mx)
    return tot


def check(items, s1, s2):
    """規則檢查：稀有度、5+ 只能 1 件、神器不重複、耳環 1 件、格數。"""
    msg = []
    all_ = items + [x for x in (s1, s2) if x]
    bad = [(D[i]['name'], D[i]['group']) for i in all_ if D[i]['group'] in BAN]
    if bad:
        msg.append('稀有度不合：' + '；'.join('%s(%s)' % x for x in bad))
    if len(items) != 6:
        msg.append('正常格 %d 件（應為 6）' % len(items))
    g = [D[i]['group'] for i in all_]
    if g.count('特殊（lv.5+）') > 1:
        msg.append('特殊 lv.5+ 超過 1 件')
    arts = [i for i in all_ if D[i]['group'].startswith('神器')]
    dup = [k for k, v in collections.Counter(arts).items() if v > 1]
    if dup:
        msg.append('神器重複：%s' % [D[k]['name'] for k in dup])
    if g.count('耳環') > 1:
        msg.append('耳環超過 1 件')
    if s1 and D[s1]['group'] != '特殊（lv.1）':
        msg.append('s1 不是特殊 lv.1')
    if s2 and D[s2]['group'] != '特殊（lv.2）':
        msg.append('s2 不是特殊 lv.2')
    return msg


def show(tag, items, s1, s2, keys):
    t = totals(items, s1, s2)
    msg = check(items, s1, s2)
    print('%s %s' % ('✔' if not msg else '✘', tag))
    if msg:
        print('    ' + '；'.join(msg))
    print('    ' + '  '.join('%s%+g%s' % (META[k]['zh'], t.get(k, 0),
                                          '%' if META[k].get('pct') else '')
                             for k in keys if t.get(k)))
    print('    金幣 %d ｜ %s' % (
        sum(D[i].get('gold') or 0 for i in items + [x for x in (s1, s2) if x]),
        '、'.join(D[i]['name'] for i in items)))
    if s1 or s2:
        print('    額外格：%s ／ %s' % (D[s1]['name'] if s1 else '-',
                                       D[s2]['name'] if s2 else '-'))
    return t


# ---------------------------------------------------------------- 白銀執法官
print('=' * 78)
print('白銀執法官 E00S　（敏捷，基礎攻擊力 10，攻擊間隔 1.5 秒，基礎敏 24 +3.5/級）')
print('=' * 78)

LIC = [
    ('A 均衡者・技能強度流',
     ['I00E', 'sor5', 'kpin', 'ofro', 'I007', 'mnsf'], 'fgun', 'I01Q'),
    ('B 律法之刃・攻速暴擊',
     ['I0A7', 'I076', 'gcel', 'prvt', 'grsl', 'I047'], 'klmm', 'I08F'),
    ('C 五刃門檻・雙修',
     ['I00E', 'I0A7', 'I076', 'gcel', 'prvt', 'grsl'], 'klmm', 'I08F'),
    ('D 逆境之眼・吸血',
     ['I00E', 'kpin', 'ofro', 'I0A8', 'grsl', 'I076'], 'lure', 'I01Q'),
    ('E 平價過渡（中期就能湊齊）',
     ['sor5', 'I044', 'I003', 'rin1', 'I006', 'odef'], 'klmm', 'I01Q'),
]
KEYS_L = ['sp', 'atk', 'as', 'agi', 'armor', 'hp', 'vamp', 'pen', 'mp', 'ms']
LV = 25
for tag, its, s1, s2 in LIC:
    t = show(tag, its, s1, s2, KEYS_L)
    sp = t.get('sp', 0)
    agi = 24 + 3.5 * (LV - 1) + t.get('agi', 0) + t.get('all', 0) + t.get('main', 0)
    atk = 10 + agi + t.get('atk', 0)
    asp = 1.0 + t.get('as', 0) / 100 + (0.03 * LV if s1 == 'klmm' else 0)
    blades = 5 if sp >= 500 else 3
    print('    -> 白銀之刃 %.0f x%d = %.0f／6秒　迴旋投擲 %.0f（近身 %.0f）'
          % (120 + sp * .2, blades, (120 + sp * .2) * blades,
             240 + sp * .4, (240 + sp * .4) * 1.5))
    print('    -> 均衡者之眼 每跳 %.0f x22 = %.0f／敵人　（範圍 400，只打生命高於你的）'
          % (50 + sp * .2, (50 + sp * .2) * 22))
    print('    -> 平砍 %.0f，攻速 x%.2f -> %.2f 秒/下；追擊開啟時攻擊力 %.0f'
          % (atk, asp, 1.5 / asp, atk * 1.7))
    print('    -> 期望平砍 DPS（暴擊 20%% x1.7）%.0f ／ 追擊期間 %.0f'
          % (atk * asp / 1.5 * 1.14, atk * 1.7 * asp / 1.5 * 1.14))
    print()

# ------------------------------------------------------------------ 拜火者
print('=' * 78)
print('拜火者 Hamg　（單體、技能全滿、一輪完整輸出）')
print('=' * 78)


def hamg(tag, items, s1, s2, talent, flam_uptime=1.0):
    t = show(tag, items, s1, s2, ['sp', 'int', 'hp', 'mp', 'armor', 'dburn', 'dstat', 'as'])
    sp = t.get('sp', 0)
    B = (t.get('dburn', 0) + t.get('dstat', 0)) / 100
    Z = 0.50 if (set(items) | {s1, s2}) & BURN_IMMUNE and 'I086' in items else 0.0
    horse = 1.5 if 'I09G' in set(items) | {s1, s2} else 1.0
    inst = talent == 'A03J'
    fl = flam_uptime
    cof = (1.5 if inst else 1.0) + B + Z
    # 易燃：瞬燃只加機率；DoT 讓跳數 16->32，等於傷害翻倍
    dur = 1.0 if inst else (1.0 + fl)
    cmul = (1.0 + 0.5 * fl) * horse

    def burn(base, chance):
        return base * cof * dur * min(1.0, chance * cmul)

    rows = []
    d = 180 + sp * .25
    rows.append(('火山爆破', d, burn(d * 1.5, .75)))
    d = 60 + sp * .30
    rows.append(('烈焰旋風 x40', d * 40, burn(d * 2.5, .60) * 40))
    n = 80 if talent == 'A03G' else 40
    d = 36 + sp * .03
    rows.append(('烈焰洪流 x%d' % n, d * n, burn(d, .50) * n))
    d = (145 + sp * .20) * 0.33
    rows.append(('火柱 16 秒', d * 16, 0.0))
    print('    點燃係數 %.2f（%s）｜跳數倍率 x%.2f｜機率倍率 x%.2f%s'
          % (cof, '瞬燃' if inst else 'DoT', dur, cmul,
             '　零時迷子生效' if Z else ''))
    td = tb = 0
    for nm, dd, bb in rows:
        print('      %-14s 直傷 %8.0f ｜ 點燃 %8.0f' % (nm, dd, bb))
        td += dd
        tb += bb
    print('    == 一輪總傷害 %.0f（直傷 %.0f ＋ 點燃 %.0f）' % (td + tb, td, tb))
    print()
    return td + tb


HAM = [
    ('現有：瞬燃機率流（人間煉獄）',
     ['I00E', 'sor5', 'kpin', 'I067', 'I0AM', 'I09G'], 'oli2', 'I0AV', 'A03J'),
    ('新 F：易燃雙倍燃（火焰浪潮）',
     ['I00E', 'sor5', 'kpin', 'I067', 'I086', 'I06A'], 'oli2', 'I0AV', 'A03G'),
    ('新 G：易燃＋馬蹄鐵（火焰浪潮）',
     ['I00E', 'kpin', 'I067', 'I086', 'I06A', 'I09G'], 'oli2', 'I0AV', 'A03G'),
    ('對照：瞬燃＋零時迷子（人間煉獄）',
     ['I00E', 'kpin', 'I067', 'I086', 'I06A', 'I09G'], 'oli2', 'I0AV', 'A03J'),
]
for tag, its, s1, s2, tal in HAM:
    hamg(tag, its, s1, s2, tal)
print('※ 易燃斷檔（uptime 50%）時：')
for tag, its, s1, s2, tal in HAM[1:3]:
    hamg('  ' + tag, its, s1, s2, tal, flam_uptime=0.5)
