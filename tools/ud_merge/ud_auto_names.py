# -*- coding: utf-8 -*-
"""待翻清單裡「名稱 + (」「名稱 [」「[名稱]」「(名稱)」這類，用網站術語表自動產生譯文。"""
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
from ud_seg import norm
from ud_gloss import glossary
BASE = os.path.dirname(os.path.abspath(__file__))
G = glossary()
miss = json.load(open(os.path.join(BASE, 'ud_tr_missing.json'), encoding='utf-8'))
out = {}
for t, c in miss:
    for pat, fmt in ((r'^(.+?) \($', '{} ('), (r'^(.+?) \[$', '{} ['), (r'^\[(.+)\]$', '[{}]'),
                     (r'^\((.+)\)$', '（{}）'), (r'^(.+)$', '{}')):
        m = re.match(pat, t)
        if m:
            hit = G.get(norm(m.group(1).strip()))
            if hit:
                out[t] = fmt.format(hit[0])
                break
json.dump(out, open(os.path.join(BASE, 'ud_tm_manual_007_auto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('自動產生 %d 條：' % len(out))
for k, v in out.items():
    print('  %s → %s' % (k, v))
