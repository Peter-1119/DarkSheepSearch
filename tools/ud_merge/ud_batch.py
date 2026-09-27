# -*- coding: utf-8 -*-
"""輸出第 N 批待翻片段（附上下文）。用法：python ud_batch.py 起 迄"""
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
from ud_seg import split, template, needs, COLOR
BASE = os.path.dirname(os.path.abspath(__file__))
a, b = int(sys.argv[1]), int(sys.argv[2])
miss = json.load(open(os.path.join(BASE, 'ud_tr_missing.json'), encoding='utf-8'))
inv = json.load(open(os.path.join(BASE, 'ud_tr_inventory.json'), encoding='utf-8'))
J = open(os.path.join(BASE, 'ud_new', 'war3map.j'), encoding='utf-8', errors='replace').read()
pool = [x for *_, x in inv['all']] + [s for s in re.findall(r'"((?:[^"\\]|\\.)*)"', J) if needs(s)]
ctx = {}
want = set(t for t, c in miss[a:b])
for s in pool:
    for k, v in split(s):
        if k == 'txt' and needs(v):
            t = template(v)[1]
            if t in want and t not in ctx:
                ctx[t] = COLOR.sub('', s).replace('\r\n', ' / ').replace('|n', ' / ')
for i, (t, c) in enumerate(miss[a:b], a):
    extra = ''
    if len(t) < 40 and t in ctx and ctx[t].strip() != t:
        extra = '    ⟨%s⟩' % ctx[t][:140]
    print('%d|%d|%s%s' % (i, c, t, extra))
