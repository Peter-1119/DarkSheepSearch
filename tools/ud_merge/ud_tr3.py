# -*- coding: utf-8 -*-
"""網站人工翻譯 → 片段對照；與 2.3.0 對照合併後，算剩下要翻的量並輸出待翻清單。"""
import sys, os, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')
TOOLS = r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\tools'
DATA = r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\data'
sys.path.insert(0, TOOLS)
from ud_seg import split, template, needs, norm, CYR
from map_items import clean

BASE = os.path.dirname(os.path.abspath(__file__))
inv = json.load(open(os.path.join(BASE, 'ud_tr_inventory.json'), encoding='utf-8'))
S = {(a, b, c, d): x for a, b, c, d, x in inv['all']}
jl = lambda n, d=TOOLS: json.load(open(os.path.join(d, n), encoding='utf-8'))
AT, AN = jl('abilities_text_zh.json')['text'], jl('abilities_zh.json')['names']
TZ, HZ = jl('talents_zh.json')['talents'], jl('heroes_zh.json')
ITEMS = jl('items.json', DATA)['items']
ABDB = jl('ab_db.json')

SITE = {}
stat = collections.Counter()


def add(ru, zh, tag):
    """一組 ru/zh 片段 → 模板對照；數字要能一一對上。"""
    if not ru or not zh or not needs(ru):
        return False
    _, ta, na, _ = template(ru)
    _, tb, nb, _ = template(zh)
    if sorted(na) != sorted(nb):
        stat[tag + '·數字對不上'] += 1
        return False
    used, mp = set(), {}
    for i, n in enumerate(nb):
        j = next(k for k, x in enumerate(na) if x == n and k not in used)
        used.add(j); mp[i] = j
    tb = re.sub(r'\{(\d+)\}', lambda m: '{%d}' % mp[int(m.group(1))], tb)
    SITE.setdefault(ta, tb)
    stat[tag] += 1
    return True


def lines_raw(raw):
    """原文依換行拆成行，每行是要翻的文字 token 清單。"""
    out, cur = [], []
    for k, v in split(raw.replace('\r\n', '\n')):
        if k == 'sep' and v in ('\n', '|n', '|N', '\r\n'):
            out.append(cur); cur = []
        elif k == 'txt':
            cur.append(v)
    out.append(cur)
    return [[t for t in L if t.strip()] for L in out]


def align_lines(raw, zh, tag):
    rl = lines_raw(raw)
    zl = zh.split('\n')
    rl_nonempty = [L for L in rl]
    if len(rl_nonempty) != len(zl):
        stat[tag + '·行數不同'] += 1
        return
    for toks, z in zip(rl_nonempty, zl):
        toks = [t for t in toks if needs(t)] or toks
        if not toks or not z.strip():
            continue
        if len(toks) == 1:
            add(toks[0], z.strip(), tag)
        elif len(toks) == 2 and norm(toks[0]).rstrip().endswith(':'):
            m = re.match(r'(.*?[：:])\s*(.*)$', z)
            if m:
                add(toks[0], m.group(1), tag); add(toks[1], m.group(2), tag)


def first(v):
    return v[0] if isinstance(v, list) else v


A = collections.defaultdict(dict)
for (f, k, mid, l), x in S.items():
    if f == 'war3map.w3a' and l in (0, 1):
        A[k].setdefault(mid, x)

# 1. 英雄技能說明、天賦說明（逐行）
for aid, (zh, en) in ((k, v) for k, v in AT.items() if not k.startswith('_')):
    raw = A.get(aid, {}).get('aub1') or A.get(aid, {}).get('arut')
    if raw:
        align_lines(raw, zh, '技能說明')
for tid, v in TZ.items():
    if tid.startswith('_'):
        continue
    raw = A.get(tid, {}).get('aub1') or A.get(tid, {}).get('arut')
    if raw:
        align_lines(raw, v['t'][0], '天賦說明')
    if A.get(tid, {}).get('anam'):
        add(A[tid]['anam'], v['n'][0], '天賦名')
# 2. 名稱
for aid, v in AN.items():
    if not aid.startswith('_') and A.get(aid, {}).get('anam'):
        add(A[aid]['anam'], v[0], '技能名')
for iid, it in ITEMS.items():
    add(it.get('name_ru'), it.get('name'), '道具名')
    add(it.get('cls_ru'), it.get('cls'), '道具品質')
    add(it.get('stats_ru'), it.get('stats'), '道具屬性')
    for e in it.get('effects') or []:
        add(e.get('ru'), e.get('zh'), '道具能力')
for aid, v in ABDB.items():
    for (lab, ru), zh in zip(v.get('parts', []), v.get('zh', [])):
        add(ru, zh, '道具技能')
for uid, v in HZ['names'].items():
    raw = S.get(('war3map.w3u', uid, 'unam', 0))
    if raw:
        add(raw, v[0], '英雄名')
for grp in HZ['vocab'].values():
    for ru, (zh, en) in grp.items():
        add(ru, zh, '英雄詞彙')

# 3. 網站術語表（abilmap 技能名、英雄名、道具名、狀態、套裝）
from ud_gloss import glossary
for ru, (zh, kind) in glossary().items():
    add(ru, zh, '術語·' + kind)

print('網站片段對照：%d 種' % len(SITE))
for k, v in sorted(stat.items()):
    print('  %-16s %d' % (k, v))

T230 = json.load(open(os.path.join(BASE, 'ud_tm_230.json'), encoding='utf-8'))
# 2.3.0 的模板是舊版 norm 前產生的，重新正規化鍵
T230 = {template(k)[1] if False else norm(k): v for k, v in T230.items()}
segs = collections.Counter()
for x in S.values():
    for k, v in split(x):
        if k == 'txt' and needs(v):
            segs[template(v)[1]] += 1
tot = sum(segs.values())
c_site = sum(c for t, c in segs.items() if t in SITE)
c_230 = sum(c for t, c in segs.items() if t not in SITE and t in T230)
rest = {t: c for t, c in segs.items() if t not in SITE and t not in T230}
print('\n同形字母還原後：唯一模板 %d 種（出現 %d 次）' % (len(segs), tot))
print('  網站對照可用：%d 種 / %.1f%%' % (sum(1 for t in segs if t in SITE), 100.0 * c_site / tot))
print('  2.3.0 對照可用：%d 種 / %.1f%%' % (sum(1 for t in segs if t not in SITE and t in T230), 100.0 * c_230 / tot))
print('  剩下要翻：%d 種 / %.1f%%，俄文字元 %s'
      % (len(rest), 100.0 * sum(rest.values()) / tot, '{:,}'.format(sum(len(CYR.findall(t)) for t in rest))))
json.dump(SITE, open(os.path.join(BASE, 'ud_tm_site.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
json.dump(sorted(rest.items(), key=lambda r: -r[1]), open(os.path.join(BASE, 'ud_rest_segs.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)
