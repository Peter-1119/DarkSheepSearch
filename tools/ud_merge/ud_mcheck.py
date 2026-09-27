# -*- coding: utf-8 -*-
"""檢查手動翻譯檔：鍵是否對得上待翻清單、佔位符是否一致、譯文是否殘留俄文。"""
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
from ud_seg import norm, CYR
BASE = os.path.dirname(os.path.abspath(__file__))
from ud_seg import split, template, needs
inv = json.load(open(os.path.join(BASE, 'ud_tr_inventory.json'), encoding='utf-8'))
J = open(os.path.join(BASE, 'ud_new', 'war3map.j'), encoding='utf-8', errors='replace').read()
pool = [x for *_, x in inv['all']] + [s for s in re.findall(r'"((?:[^"\\]|\\.)*)"', J) if needs(s)]
univ = set()
for s in pool:
    for k, v in split(s):
        if k == 'txt' and needs(v):
            univ.add(template(v)[1])
still = {norm(t) for t, c in json.load(open(os.path.join(BASE, 'ud_tr_missing.json'), encoding='utf-8'))}
miss = univ
tot = bad = 0
done = set()
for f in sorted(os.listdir(BASE)):
    if not (f.startswith('ud_tm_manual') and f.endswith('.json')):
        continue
    d = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
    for k, v in d.items():
        tot += 1
        nk = norm(k)
        done.add(nk)
        errs = []
        if nk not in miss:
            errs.append('不在待翻清單')
        if sorted(re.findall(r'\{\d+\}', k)) != sorted(re.findall(r'\{\d+\}', v)):
            errs.append('佔位符不一致')
        if CYR.search(v):
            errs.append('譯文殘留俄文')
        if errs:
            bad += 1
            print('%s｜%s｜%s' % (f, k[:60], '、'.join(errs)))
print('手動翻譯 %d 條，有問題 %d 條；待翻清單還剩 %d 種' % (tot, bad, len(still - done)))
