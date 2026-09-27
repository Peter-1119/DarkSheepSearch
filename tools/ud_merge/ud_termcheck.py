# -*- coding: utf-8 -*-
"""用 ud_terms 的規則檢查每個模板的譯文（手動＋網站；2.3.0 來源會重翻，不檢查）。

python ud_termcheck.py            統計
python ud_termcheck.py -v 規定中文  列出該詞的違規
輸出 ud_termcheck.json：[{tpl, zh, src, miss:[規定中文...]}]
"""
import sys, os, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
from ud_seg import template
import ud_translate, ud_terms, ud_termfix
from ud_termaudit import pool


def collect(skip_230=True):
    TR = ud_translate.Translator()
    out = {}
    for v in pool():
        tpl = template(v)[1]
        if tpl in out:
            continue
        for name, d in TR.tm:
            if tpl in d:
                if not (skip_230 and name.startswith('2.3.0')):
                    out[tpl] = (ud_termfix.fix(tpl, ud_translate.latin_stats(d[tpl]) or d[tpl]), name)
                break
    return out


def check(pairs):
    bad = []
    for tpl, (zh, src) in pairs.items():
        miss = [r[0] for r in ud_terms.rules_for(tpl) if not ud_terms.ok(r[0], zh)]
        if miss:
            bad.append({'tpl': tpl, 'zh': zh, 'src': src, 'miss': miss})
    return bad


if __name__ == '__main__':
    pairs = collect()
    bad = check(pairs)
    json.dump(bad, open(os.path.join(BASE, 'ud_termcheck.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    if '-v' in sys.argv:
        w = sys.argv[sys.argv.index('-v') + 1]
        for b in bad:
            if w in b['miss']:
                print('%s\n   %s' % (b['tpl'][:110], b['zh'][:110]))
        sys.exit()
    c = collections.Counter(m for b in bad for m in b['miss'])
    print('檢查模板 %d，違規模板 %d（網站 %d、手動 %d）' % (len(pairs), len(bad),
          sum(b['src'] == '網站' for b in bad), sum(b['src'] == '手動' for b in bad)))
    for k, n in c.most_common(70):
        print('  %-10s %d' % (k, n))
