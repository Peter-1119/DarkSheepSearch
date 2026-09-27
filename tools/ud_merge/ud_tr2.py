# -*- coding: utf-8 -*-
"""片段化之後的工作量，以及 2.3.0 能對齊出多少片段對照。"""
import sys, os, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')
TOOLS = r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\tools'
sys.path.insert(0, TOOLS)
import mpq, w3obj
from ud_seg import split, template, needs, align
import zhconv

BASE = os.path.dirname(os.path.abspath(__file__))
D = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/'
inv = json.load(open(os.path.join(BASE, 'ud_tr_inventory.json'), encoding='utf-8'))
S = {(a, b, c, d): x for a, b, c, d, x in inv['all']}

segs = collections.Counter()
for x in S.values():
    for k, v in split(x):
        if k == 'txt' and needs(v):
            segs[template(v)[1]] += 1
print('物件檔片段：出現 %d 次，唯一模板 %d 種' % (sum(segs.values()), len(segs)))
top = segs.most_common()
acc = 0
for n_ in (50, 200, 500, 1000, 2000):
    print('  前 %4d 種模板涵蓋 %.1f%% 的片段' % (n_, 100.0 * sum(c for t, c in top[:n_]) / sum(segs.values())))

# 2.3.0 對齊
FILES = (('war3map.w3t', False), ('war3map.w3u', False), ('war3map.w3a', True), ('war3map.w3q', True))
m23 = mpq.MPQ(D + '000肥羊的聖誕禮物_2.3.0_ty.w3x')
Z = {f: w3obj.parse(m23.read(f), lv) for f, lv in FILES}


def get(objs, f, k, mid, l):
    v = objs[f].get(k, {}).get(mid)
    if isinstance(v, list):
        return v[l - 1] if 0 < l <= len(v) else None
    return v


tm = collections.defaultdict(collections.Counter)
ok = bad = 0
for (f, k, mid, l), x in S.items():
    z = get(Z, f, k, mid, l)
    if not isinstance(z, str) or not re.search(r'[\u4e00-\u9fff]', z):
        continue
    pr = align(x, zhconv.convert(z, 'zh-tw'))
    if pr is None:
        bad += 1; continue
    ok += 1
    for a, b in pr:
        tm[a][b] += 1
print('\n2.3.0 同物件同欄位：結構對得上 %d 筆，對不上 %d 筆' % (ok, bad))
print('  對齊出片段對照 %d 種；其中譯法不唯一的 %d 種' % (len(tm), sum(1 for v in tm.values() if len(v) > 1)))
cov = sum(c for t, c in segs.items() if t in tm)
print('  以片段計，可直接套 2.3.0 譯法的：%d 種模板（出現 %d 次，%.1f%%）'
      % (sum(1 for t in segs if t in tm), cov, 100.0 * cov / sum(segs.values())))
rest = {t: c for t, c in segs.items() if t not in tm}
print('  剩下的模板 %d 種，俄文字元 %s' % (len(rest), '{:,}'.format(sum(len(re.findall(r'[\u0400-\u04FF]', t)) for t in rest))))
json.dump({a: b.most_common(1)[0][0] for a, b in tm.items()},
          open(os.path.join(BASE, 'ud_tm_230.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(sorted(rest.items(), key=lambda r: -r[1]),
          open(os.path.join(BASE, 'ud_rest_segs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('\n最常見、還沒有譯法的 25 個片段：')
for t, c in sorted(rest.items(), key=lambda r: -r[1])[:25]:
    print('  %5d  %s' % (c, t[:80]))
