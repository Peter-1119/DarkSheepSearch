# -*- coding: utf-8 -*-
"""檢查成品地圖裡有沒有簡體字：逐字判斷「轉繁體會變、轉簡體不變」的字。"""
import sys, re, collections
sys.path.insert(0, r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/tools')
sys.stdout.reconfigure(encoding='utf-8')
import mpq, zhconv

MAP = sys.argv[1] if len(sys.argv) > 1 else r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/0UD_合併底圖_E2.w3x'
m = mpq.MPQ(MAP)
_cache = {}


def simp(c):
    if c not in _cache:
        _cache[c] = zhconv.convert(c, 'zh-tw') != c and zhconv.convert(c, 'zh-hans') == c
    return _cache[c]


hits = collections.Counter()
ctx = {}
for f in ['war3map.j', 'war3map.w3t', 'war3map.w3u', 'war3map.w3a', 'war3map.w3q', 'war3map.w3h',
          'war3map.wts', 'war3map.w3i', 'war3mapSkin.txt']:
    try:
        t = m.read(f).decode('utf-8', 'replace')
    except Exception:
        continue
    for i, c in enumerate(t):
        if '\u4e00' <= c <= '\u9fff' and simp(c):
            hits[(f, c)] += 1
            ctx.setdefault((f, c), t[max(0, i - 12):i + 12].replace('\n', ' '))
print('簡體字：%d 種、%d 處' % (len({c for _, c in hits}), sum(hits.values())))
for (f, c), n in hits.most_common(60):
    print(' ', f, c, '→', zhconv.convert(c, 'zh-tw'), n, '｜', ctx[(f, c)])
