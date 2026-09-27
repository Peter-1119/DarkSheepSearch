# -*- coding: utf-8 -*-
"""檢查重翻批次檔：鍵是否剛好涵蓋該批、佔位符一致、無俄文、名詞規則。 python ud_rcheck.py 檔名 起 迄"""
import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
from ud_seg import norm
import ud_terms, ud_termfix
f, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
m = [norm(t) for t, c in json.load(open('ud_tr_missing.json', encoding='utf-8'))[a:b]]
d = json.load(open(f, encoding='utf-8'))
ks = {norm(k) for k in d}
print(len(d), '未涵蓋', [t for t in m if t not in ks][:8], '多出', [k for k in d if norm(k) not in set(m)][:8])
for k, v in d.items():
    errs = []
    if sorted(re.findall(r'\{\d+\}', k)) != sorted(re.findall(r'\{\d+\}', v)):
        errs.append('佔位符')
    if re.search('[\u0400-\u04ff]', v):
        errs.append('俄文')
    z = ud_termfix.fix(k, v)
    miss = [r[0] for r in ud_terms.rules_for(k) if not ud_terms.ok(r[0], z)]
    if miss:
        errs.append('名詞:' + ','.join(miss))
    if errs:
        print(' ', k[:60], '→', v[:50], errs)
