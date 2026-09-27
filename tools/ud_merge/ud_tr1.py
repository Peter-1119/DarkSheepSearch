# -*- coding: utf-8 -*-
"""翻譯盤點：底圖裡所有俄文字串，以及三層來源各能涵蓋多少。"""
import sys, os, re, io, json, collections
sys.stdout.reconfigure(encoding='utf-8')
TOOLS = r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\tools'
sys.path.insert(0, TOOLS)
import mpq, w3obj

BASE = os.path.dirname(os.path.abspath(__file__))
D = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/'
CYR = re.compile(r'[\u0400-\u04FF]')
COL = re.compile(r'\|c[0-9A-Fa-f]{8}|\|r|\|n|\|R|\|N')
FILES = (('war3map.w3t', False), ('war3map.w3u', False), ('war3map.w3a', True), ('war3map.w3q', True))


def load(path):
    m = mpq.MPQ(path)
    return {f: w3obj.parse(m.read(f), lv) for f, lv in FILES}, m.read('war3map.j').decode('utf-8', 'replace'), m


def strings(objs):
    """[(檔, 物件, 欄位, 等級, 文字)]，只留含俄文的。"""
    out = []
    for f, recs in objs.items():
        for k, rec in recs.items():
            for mid, v in rec.items():
                if mid.startswith('_'):
                    continue
                vals = v if isinstance(v, list) else [v]
                for i, x in enumerate(vals):
                    if isinstance(x, str) and CYR.search(x):
                        out.append((f, k, mid, i + 1 if isinstance(v, list) else 0, x))
    return out


NEW, JN, MN = load(D + 'UD_test_24_09_26_opt.w3x')
F82, J82, _ = load(D + '0UD_v3_82fix_opt.w3x')
Z23, J23, _ = load(D + '000肥羊的聖誕禮物_2.3.0_ty.w3x')
S = strings(NEW)
print('=== 1. 底圖物件檔裡的俄文字串 ===')
by = collections.Counter((f, mid) for f, k, mid, l, x in S)
chars = collections.Counter()
for f, k, mid, l, x in S:
    chars[f] += len(CYR.findall(x))
for f, lv in FILES:
    rows = sorted(((mid, n) for (ff, mid), n in by.items() if ff == f), key=lambda r: -r[1])
    print('  %s：%d 筆、%s 個俄文字元　欄位 %s' % (f, sum(n for m, n in rows), '{:,}'.format(chars[f]),
                                        ' '.join('%s×%d' % r for r in rows[:10])))
print('  合計 %d 筆' % len(S))
# 去掉數字後的唯一句型
tmpl = lambda s: re.sub(r'\d+(?:[.,]\d+)?', '#', COL.sub('', s)).strip()
print('  去掉數字、顏色碼後的唯一句型：%d 種' % len(set(tmpl(x) for f, k, m, l, x in S)))

js = [s for s in re.findall(r'"((?:[^"\\]|\\.)*)"', JN) if CYR.search(s)]
print('\n=== 2. 腳本 war3map.j：含俄文的字串 %d 條（唯一 %d）===' % (len(js), len(set(js))))
wts = MN.read('war3map.wts')
print('=== 3. war3map.wts：%s ===' % ('%d bytes，含俄文 %s' % (len(wts), bool(CYR.search(wts.decode('utf-8', 'replace')))) if wts else '無'))

# ---------------- 來源 1：專案裡的人工翻譯（v3.82fix）----------------
def jl(n):
    return json.load(open(os.path.join(TOOLS, n), encoding='utf-8'))
AT = jl('abilities_text_zh.json')['text']
AN = jl('abilities_zh.json')['names']
HZ = jl('heroes_zh.json')
TZ = jl('talents_zh.json')['talents']
N2 = jl('names2.json')
print('\n=== 4. 專案人工翻譯：技能說明 %d、技能名 %d、天賦 %d、道具名 %d；英雄資料鍵 %s ==='
      % (len(AT), len(AN), len(TZ), len(N2), list(HZ)[:6]))

same82 = diff82 = 0
cover1 = set()
def get(objs, f, k, mid, l):
    v = objs[f].get(k, {}).get(mid)
    if isinstance(v, list):
        return v[l - 1] if 0 < l <= len(v) else (v[0] if l == 0 else None)
    return v
for f, k, mid, l, x in S:
    hit = None
    if f == 'war3map.w3a' and mid in ('aub1', 'atp1') and k in AT:
        hit = 'AT'
    elif f == 'war3map.w3a' and mid == 'anam' and (k in AN or k in TZ):
        hit = 'AN'
    elif f == 'war3map.w3a' and k in TZ:
        hit = 'TZ'
    elif f == 'war3map.w3t' and mid == 'unam' and k in N2:
        hit = 'N2'
    if hit:
        if get(F82, f, k, mid, l) == x:
            same82 += 1; cover1.add((f, k, mid, l))
        else:
            diff82 += 1
print('  有人工翻譯的欄位：與 v3.82fix 原文一致 %d、不一致 %d（不一致的要重翻）' % (same82, diff82))

# ---------------- 來源 2：2.3.0 中文（數字一致才用）----------------
nums = lambda s: sorted(re.findall(r'\d+(?:[.,]\d+)?', COL.sub(' ', s)))
cover2 = set(); stale = 0
for f, k, mid, l, x in S:
    if (f, k, mid, l) in cover1:
        continue
    z = get(Z23, f, k, mid, l)
    if isinstance(z, str) and re.search(r'[\u4e00-\u9fff]', z):
        if nums(z) == nums(x):
            cover2.add((f, k, mid, l))
        else:
            stale += 1
print('\n=== 5. 2.3.0 中文：數字一致可直接用 %d、數字不同 %d ===' % (len(cover2), stale))
rest = [s for s in S if (s[0], s[1], s[2], s[3]) not in cover1 | cover2]
print('\n=== 6. 剩下要翻的：%d 筆、唯一句型 %d 種、俄文字元 %s ==='
      % (len(rest), len(set(tmpl(x) for f, k, m, l, x in rest)),
         '{:,}'.format(sum(len(CYR.findall(x)) for f, k, m, l, x in rest))))
c = collections.Counter((f, m) for f, k, m, l, x in rest)
print('   ' + '  '.join('%s/%s×%d' % (f[-3:], m, n) for (f, m), n in c.most_common(14)))
json.dump(dict(all=S, cover1=sorted(cover1), cover2=sorted(cover2)),
          open(os.path.join(BASE, 'ud_tr_inventory.json'), 'w', encoding='utf-8'), ensure_ascii=False)
