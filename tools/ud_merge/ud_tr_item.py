# -*- coding: utf-8 -*-
"""道具嚴格模式的影響：道具與道具技能改成不用 2.3.0，要多翻多少；新增道具有哪些。"""
import sys, os, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')
TOOLS = r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\tools'
sys.path.insert(0, TOOLS)
import mpq, w3obj
from ud_seg import split, template, needs, norm

BASE = os.path.dirname(os.path.abspath(__file__))
D = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/'
MN = mpq.MPQ(D + 'UD_test_24_09_26_opt.w3x')
T = w3obj.parse(MN.read('war3map.w3t'), False)
T23 = w3obj.parse(mpq.MPQ(D + '000肥羊的聖誕禮物_2.3.0_ty.w3x').read('war3map.w3t'), False)
ITEMS = json.load(open(r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\data\items.json', encoding='utf-8'))['items']

# 道具用到的技能
item_abil = set()
for k, r in T.items():
    v = r.get('iabi')
    for x in (v if isinstance(v, list) else [v]):
        if isinstance(x, str):
            item_abil |= {a.strip() for a in x.split(',') if a.strip()}
print('道具 %d 件，用到的道具技能 %d 個' % (len(T), len(item_abil)))

new_vs_230 = sorted(k for k in T if k not in T23)
new_vs_site = sorted(k for k in T if k not in ITEMS)
print('2.3.0 沒有的道具（新增）：%d 件' % len(new_vs_230))
print('網站沒有的道具：%d 件：%s' % (len(new_vs_site), ', '.join('%s %s' % (k, T[k].get('unam', '')) for k in new_vs_site)))

json.dump(sorted(item_abil), open(os.path.join(BASE, 'ud_item_abils.json'), 'w'), indent=0)

# 嚴格模式下，道具字串的片段有多少只能靠 2.3.0
inv = json.load(open(os.path.join(BASE, 'ud_tr_inventory.json'), encoding='utf-8'))
site = json.load(open(os.path.join(BASE, 'ud_tm_site.json'), encoding='utf-8'))
man = {}
for f in os.listdir(BASE):
    if f.startswith('ud_tm_manual') and f.endswith('.json'):
        man.update({norm(k): v for k, v in json.load(open(os.path.join(BASE, f), encoding='utf-8')).items()})
need = collections.Counter()
tot = 0
for f, k, m, l, x in inv['all']:
    if f == 'war3map.w3t' or (f == 'war3map.w3a' and k in item_abil):
        for kk, v in split(x):
            if kk == 'txt' and needs(v):
                tot += 1
                t = template(v)[1]
                if t not in site and t not in man:
                    need[t] += 1
print('道具相關片段 %d 個；不用 2.3.0 時缺譯文的 %d 個（%d 種）' % (tot, sum(need.values()), len(need)))
json.dump(need.most_common(), open(os.path.join(BASE, 'ud_item_need.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
