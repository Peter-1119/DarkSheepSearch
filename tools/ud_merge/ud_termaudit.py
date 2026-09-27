# -*- coding: utf-8 -*-
"""朋友的統一名詞表（data/translation.txt）vs 目前地圖譯文與網站譯名。

輸出 ud_termaudit.json：
  terms   : 解析出來的 (俄文, 中文, 註記)
  dup     : 同一俄文在表裡給了不同中文
  site    : 與網站譯名（技能／英雄／道具／狀態／套裝）不同
  usage   : 每個詞在地圖片段中出現幾次、其中幾次譯文用了表上的中文、各來源的分布、反例
"""
import sys, os, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
from ud_seg import split, template, needs, norm
import ud_translate
from ud_gloss import glossary

SRC = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/data/translation.txt'
CJK = re.compile(r'[\u4e00-\u9fff]')


def parse():
    out = []
    for ln in open(SRC, encoding='utf-8'):
        ln = ln.strip()
        if not ln or not re.search(r'[\u0400-\u04ff]', ln[:3] + ln):
            continue
        m = CJK.search(ln)
        if not m or not re.match(r'[\u0400-\u04ffA-Za-z]', ln):
            continue
        ru = ln[:m.start()].strip()
        zh = ln[m.start():].strip()
        ru = re.sub(r'\s+[A-Za-z]+$', '', ru).strip()          # 「Волшебник Wizard」→ 去掉英文
        note = ''
        mm = re.match(r'^(.*?)[（(](.*)[)）]\s*$', zh)
        if mm:
            zh, note = mm.group(1).strip(), mm.group(2)
        if '翻譯成' in zh:
            zh = zh.replace('翻譯成', '').strip()
        alts = zh.split()
        out.append({'ru': ru, 'zh': alts[0], 'alts': alts[1:], 'note': note})
    return out


def pool():
    inv = json.load(open(os.path.join(BASE, 'ud_tr_inventory.json'), encoding='utf-8'))
    J = open(os.path.join(BASE, 'ud_new', 'war3map.j'), encoding='utf-8', errors='replace').read()
    src = [x for *_, x in inv['all']] + [s for s in re.findall(r'"((?:[^"\\]|\\.)*)"', J) if needs(s)]
    segs = collections.Counter()
    for s in src:
        for k, v in split(s):
            if k == 'txt' and needs(v):
                segs[v] += 1
    return segs


def main():
    terms = parse()
    by = collections.defaultdict(set)
    for t in terms:
        by[norm(t['ru']).lower()].add(t['zh'])
    dup = {k: sorted(v) for k, v in by.items() if len(v) > 1}
    G = glossary()
    Gl = {k.lower(): v for k, v in G.items()}
    site = []
    for t in terms:
        g = Gl.get(norm(t['ru']).lower())
        if g and g[0] != t['zh'] and t['zh'] not in g[0]:
            site.append({'ru': t['ru'], 'friend': t['zh'], 'site': g[0], 'kind': g[1]})
    TR = ud_translate.Translator()
    segs = pool()
    rows = []                                       # (原文, 譯文, 來源)
    for v, c in segs.items():
        lead, tpl, nums, trail = template(v)
        z, srcname = None, None
        for name, d in TR.tm:
            if tpl in d:
                z, srcname = d[tpl], name
                break
        rows.append((norm(v), z or '', srcname or '未翻', c))
    usage = []
    seen = set()
    for t in terms:
        key = norm(t['ru']).lower()
        if key in seen or len(key) < 3:
            continue
        seen.add(key)
        rx = re.compile(r'(?<![\u0400-\u04ff])' + re.escape(key), re.I)
        hit = [r for r in rows if rx.search(r[0])]
        if not hit:
            continue
        zs = [t['zh']] + t['alts']
        ok = [r for r in hit if any(z in r[1] for z in zs)]
        bad = [r for r in hit if not any(z in r[1] for z in zs)]
        usage.append({'ru': t['ru'], 'zh': t['zh'], 'n': len(hit), 'ok': len(ok),
                      'src_bad': dict(collections.Counter(r[2] for r in bad)),
                      'eg': [[r[0][:80], r[1][:80]] for r in bad[:4]]})
    json.dump({'terms': terms, 'dup': dup, 'site': site, 'usage': usage},
              open(os.path.join(BASE, 'ud_termaudit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('名詞 %d 條；表內一詞多譯 %d；與網站譯名不同 %d；地圖中有出現 %d' % (len(terms), len(dup), len(site), len(usage)))
    n = sum(u['n'] for u in usage); ok = sum(u['ok'] for u in usage)
    print('出現片段合計 %d，譯文已符合 %d（%.0f%%）' % (n, ok, 100.0 * ok / max(n, 1)))
    src = collections.Counter()
    for u in usage:
        src.update(u['src_bad'])
    print('不符合的來源：', dict(src))


if __name__ == '__main__':
    main()
