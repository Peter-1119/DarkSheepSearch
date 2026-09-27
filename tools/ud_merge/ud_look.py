# -*- coding: utf-8 -*-
"""查既有譯法：python ud_look.py 詞1 詞2 …（完全符合，找不到再列出包含它的對照）"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
from ud_seg import norm
BASE = os.path.dirname(os.path.abspath(__file__))
TMS = []
for f in sorted(os.listdir(BASE)):
    if f.startswith('ud_tm_') and f.endswith('.json'):
        d = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
        TMS.append((f[6:-5], {norm(k): v for k, v in d.items()}))
for w in sys.argv[1:]:
    w = norm(w)
    hit = [(n, d[w]) for n, d in TMS if w in d]
    if hit:
        print('%s → %s' % (w, '；'.join('%s〔%s〕' % (v, n) for n, v in hit)))
        continue
    part = [(n, k, v) for n, d in TMS for k, v in d.items() if w in k and len(k) < len(w) + 30][:4]
    print('%s → （無完全符合）%s' % (w, '；'.join('%s=%s〔%s〕' % (k, v, n) for n, k, v in part)))
