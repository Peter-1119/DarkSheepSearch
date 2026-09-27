# -*- coding: utf-8 -*-
"""重翻批次：輸出待翻模板＋上下文＋必須使用的譯名提示。
python ud_rbatch.py 起 迄 > 檔案"""
import sys, os, re, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
from ud_seg import norm
import ud_terms
from ud_gloss import glossary

a, b = int(sys.argv[1]), int(sys.argv[2])
miss = json.load(open(os.path.join(BASE, 'ud_tr_missing.json'), encoding='utf-8'))[a:b]
G = {k.lower(): v for k, v in glossary().items() if len(k) >= 5}
# 朋友的表優先：網站譯名若與名詞表衝突，以名詞表為準
Gk = sorted(G, key=len, reverse=True)

out = subprocess.run([sys.executable, os.path.join(BASE, 'ud_batch.py'), str(a), str(b)],
                     capture_output=True, text=True, encoding='utf-8').stdout.splitlines()
for line in out:
    idx, cnt, rest = line.split('|', 2)
    tpl = rest.split('    ⟨')[0]
    low = norm(tpl).lower()
    hints = []
    for zh, var, note in ud_terms.rules_for(tpl):
        hints.append(zh.split('|')[0])
    used = low
    for k in Gk:
        if k in used:
            zh = G[k][0]
            fixed = ud_terms.rules_for(k)
            if fixed:
                zh = fixed[0][0].split('|')[0] if len(fixed) == 1 else zh
            hints.append('%s=%s' % (k, zh))
            used = used.replace(k, ' ')
    print(line + ('    【%s】' % '、'.join(dict.fromkeys(hints)) if hints else ''))
