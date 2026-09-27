# -*- coding: utf-8 -*-
"""把兩張圖需要的檔案解出來快取到磁碟（PKWARE 解壓很慢，只做一次）。"""
import sys, os, time
sys.path.insert(0, r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\tools')
sys.stdout.reconfigure(encoding='utf-8')
import mpq

BASE = os.path.dirname(os.path.abspath(__file__))
JOBS = {
    'new': r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/UD_test_24_09_26_opt.w3x',
    'old': r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/肥羊的聖誕禮物_1.41_ty.w3x',
}
WANT = ['war3map.j', 'war3map.w3e', 'war3map.doo', 'war3map.w3i', 'war3map.wts',
        'war3map.w3u', 'war3map.w3t', 'war3map.w3a', 'war3map.w3q', 'war3map.wpm']

for tag, P in JOBS.items():
    out = os.path.join(BASE, 'ud_' + tag)
    os.makedirs(out, exist_ok=True)
    m = mpq.MPQ(P)
    for f in WANT:
        dst = os.path.join(out, f.replace('\\', '_'))
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            print('%s/%s 已存在，跳過' % (tag, f), flush=True)
            continue
        t = time.time()
        try:
            d = m.read(f)
        except Exception as e:
            print('%s/%s 失敗: %s' % (tag, f, e), flush=True)
            continue
        if not d:
            print('%s/%s 不存在' % (tag, f), flush=True)
            continue
        open(dst, 'wb').write(d)
        print('%s/%-18s %9d bytes  %.1f 秒' % (tag, f, len(d), time.time() - t), flush=True)
print('全部完成')
