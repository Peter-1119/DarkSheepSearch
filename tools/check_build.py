# -*- coding: utf-8 -*-
"""配裝檢查器：驗規則、算總計、列出每件裝備的效果。

用法：
    python tools/check_build.py I00E sor5 kpin I067 I0AM I09G --s1 oli2 --s2 I0AV
    python tools/check_build.py --file my_builds.json      # 檢查整個配裝檔

規則（跟網站 site_template.html 裡的一致）：
  6 個正常欄位，另外兩個不佔格的額外欄位：
    s1 = 吸收器（特殊 lv.1）—— 自己挑
    s2 = 祕密寶盒（特殊 lv.2）—— 隨機生成
  同一件神器最多 1 個（鐵匠可以複製其中一件，所以最多允許 1 件出現 2 次）
  耳環類最多 1 件（war3map.j 的 TryTakeEarringsSlot，違反時裝備會被退回地上）
  乘算器最多 1 件（TryTakeMultiplierSlot；封閉心智頭盔 iwbr 走同一個處理器但不佔格）
  取得難度篩選：排除 新年／復活節／萬聖節／儀式／完美／特殊 lv.5++
  每套最多 1 件 特殊 lv.5+

不可疊加的屬性（魔法傷害減免、狀態防護）取最高值，不相加。
"""
import argparse, collections, io, json, os, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(io.open(os.path.join(ROOT, 'data', 'items.json'), encoding='utf-8'))['items']
S = json.load(io.open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))
IT = S['items']
NOSTACK = set(S.get('nostack') or [])
META = {m['k']: m for m in S['stats']}

BAN = {'新年', '復活節', '萬聖節', '儀式', '完美', '特殊（lv.5++）'}
# 乘算器欄位：war3map.j:24663 走 OnEquip_Multiplier 的那一串道具。
# iwbr 也走同一個處理器，但 22197 那行把它排除在佔格判斷外，所以不算。
# I078 洞察之戒走的是另一段程式（24678-24680），但佔的是同一個 player hash key 13，
# 所以它也算乘算器。只看 OnEquip_Multiplier 的道具清單會漏掉它。
MULTIPLIER = {'ckng', 'tfar', 'oven', 'kysn', 'jpnt', 'moon',
              'I0A8', 'I01P', 'I00B', 'I078'}
EARRING = {'I00E', 'I00F', 'I00O', 'I00P', 'I00Q'}
BY_NAME = {}
for _i, _v in D.items():
    BY_NAME.setdefault(_v['name'], _i)


def resolve(x):
    """接受道具 ID 或中文名稱。"""
    if x in D:
        return x
    if x in BY_NAME:
        return BY_NAME[x]
    raise SystemExit('找不到道具：%s' % x)


def totals(ids):
    tot, mx = collections.defaultdict(float), collections.defaultdict(float)
    for i in ids:
        for k, v in (IT[i].get('v') or {}).items():
            if k in NOSTACK:
                mx[k] = max(mx[k], v)
            else:
                tot[k] += v
    tot.update(mx)
    return tot


def check(items, s1=None, s2=None):
    """回傳問題清單，空的代表合法。"""
    bad = []
    extra = [x for x in (s1, s2) if x]
    all_ = list(items) + extra
    if len(items) != 6:
        bad.append('正常欄位有 %d 件，應該是 6 件' % len(items))
    for i in all_:
        if D[i]['group'] in BAN:
            bad.append('%s 是「%s」，不在取得範圍內' % (D[i]['name'], D[i]['group']))
    g = [D[i]['group'] for i in all_]
    if g.count('特殊（lv.5+）') > 1:
        bad.append('特殊 lv.5+ 有 %d 件，最多 1 件' % g.count('特殊（lv.5+）'))
    ear = [i for i in all_ if i in EARRING or D[i]['group'] == '耳環']
    if len(ear) > 1:
        bad.append('耳環有 %d 件，最多 1 件：%s' % (len(ear), [D[i]['name'] for i in ear]))
    mul = [i for i in all_ if i in MULTIPLIER]
    if len(mul) > 1:
        bad.append('乘算器有 %d 件，最多 1 件：%s' % (len(mul), [D[i]['name'] for i in mul]))
    arts = collections.Counter(i for i in all_ if D[i]['group'].startswith('神器'))
    twice = [k for k, v in arts.items() if v > 1]
    if len(twice) > 1 or any(arts[k] > 2 for k in twice):
        bad.append('神器重複超過規則：%s（只允許其中 1 件靠鐵匠複製成 2 個）'
                   % [D[k]['name'] for k in twice])
    if s1 and D[s1]['group'] != '特殊（lv.1）':
        bad.append('s1「%s」是 %s，必須是 特殊（lv.1）' % (D[s1]['name'], D[s1]['group']))
    if s2 and D[s2]['group'] != '特殊（lv.2）':
        bad.append('s2「%s」是 %s，必須是 特殊（lv.2）' % (D[s2]['name'], D[s2]['group']))
    dup = [k for k, v in collections.Counter(all_).items()
           if v > 1 and not D[k]['group'].startswith('神器')]
    if dup:
        bad.append('重複道具：%s' % [D[k]['name'] for k in dup])
    return bad


def report(tag, items, s1=None, s2=None, verbose=True):
    items = [resolve(x) for x in items]
    s1 = resolve(s1) if s1 else None
    s2 = resolve(s2) if s2 else None
    bad = check(items, s1, s2)
    print('%s %s' % ('✔' if not bad else '✘', tag))
    for b in bad:
        print('    ! ' + b)
    all_ = items + [x for x in (s1, s2) if x]
    t = totals(all_)
    order = [k for k in (m['k'] for m in S['stats']) if t.get(k)]
    print('    總計：' + '　'.join(
        '%s%+g%s' % (META[k]['zh'], round(t[k], 2), '%' if META[k].get('pct') else '')
        for k in order))
    print('    金幣：%d' % sum(D[i].get('gold') or 0 for i in all_))
    if verbose:
        for i in all_:
            v = D[i]
            slot = 's1' if i == s1 else 's2' if i == s2 else '  '
            print('    %-2s %-5s %-12s %-14s %s' % (
                slot, i, v['name'], v['group'], (v.get('stats') or '-')[:44]))
            for e in v.get('effects') or []:
                print('           [%s] %s' % (e['label'], e['zh'][:96]))
    print()
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('items', nargs='*')
    ap.add_argument('--s1')
    ap.add_argument('--s2')
    ap.add_argument('--file', help='配裝 JSON（{"list":[…]} 或 {"builds":{英雄:[…]}}）')
    ap.add_argument('-q', '--quiet', action='store_true', help='只印總計，不列每件裝備')
    a = ap.parse_args()

    if a.file:
        j = json.load(io.open(a.file, encoding='utf-8'))
        rows = []
        if isinstance(j.get('list'), list):
            rows = [(b['id'] + ' ' + b['n'][0], b) for b in j['list']]
        for hero, bs in (j.get('builds') or {}).items():
            rows += [('%s / %s %s' % (hero, b['id'], b['n'][0]), b) for b in bs]
        # 也接受直接以英雄 ID 當頂層鍵的形式：{"H01E": [ … ]}
        for hero, bs in j.items():
            if hero in ('list', 'builds') or hero.startswith('_'):
                continue
            if isinstance(bs, list) and bs and isinstance(bs[0], dict) and 'items' in bs[0]:
                rows += [('%s / %s %s' % (hero, b['id'], b['n'][0]), b) for b in bs]
        ok = 0
        for tag, b in rows:
            bo = b.get('bonus') or {}
            ok += report(tag, b['items'], bo.get('s1'), bo.get('s2'), not a.quiet)
        print('=== %d / %d 套通過 ===' % (ok, len(rows)))
        sys.exit(0 if ok == len(rows) else 1)

    if not a.items:
        ap.error('請給 6 件道具，或用 --file')
    report('（指定的配裝）', a.items, a.s1, a.s2, not a.quiet)


if __name__ == '__main__':
    main()
