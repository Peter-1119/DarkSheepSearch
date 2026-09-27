# -*- coding: utf-8 -*-
"""新版道具：說明「Бонусы」那一行 vs InitItemDB 實際數值。"""
import sys, re, json, collections
sys.path.insert(0, r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/tools')
sys.stdout.reconfigure(encoding='utf-8')
import mpq, w3obj, stat_values
from map_items import HOMO
MAP = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/UD_test_24_09_26_opt.w3x'
J = open('ud_new.j', encoding='utf-8', errors='replace').read()
T = w3obj.parse(mpq.MPQ(MAP).read('war3map.w3t'), False)
body = J[J.index('function InitItemDB'):]
body = body[:body.index('endfunction')]
F = ['str', 'agi', 'int', 'hp', 'mp', 'armor', 'atk', 'as', 'main', 'hpreg', 'mpreg', 'sp']
DBv = collections.OrderedDict()
for m in re.finditer(r"call (DB|DB_HR|DB_HI|DB_Inc|DB_Ab)\('(\w{4})',([^)]*)\)", body):
    f, i, a = m.group(1), m.group(2), [x.strip() for x in m.group(3).split(',')]
    d = DBv.setdefault(i, {'hr': {}, 'hi': {}, 'ab': [], 'base': {}})
    if f == 'DB':
        for k, v in zip(F, a):
            v = float(v)
            if v: d['base'][k] = v
    elif f == 'DB_HR': d['hr'][a[0]] = d['hr'].get(a[0], 0) + float(a[1])
    elif f == 'DB_HI': d['hi'][a[0]] = d['hi'].get(a[0], 0) + int(a[1])
    elif f == 'DB_Inc': d['inc'] = [int(x) for x in a]
    else: d['ab'].append(a[0])
LAT = ['agi', 'str', 'int', 'atk', 'speed', 'regen', 'armor', 'HP', 'MP', 'all stats', 'main stat', 'spell power']
def clean(s):
    s = re.sub(r'\|c[0-9A-Fa-f]{8}|\|r', '', s or '').replace('\r', '').translate(HOMO)
    for w in LAT: s = s.replace(w.translate(HOMO), w)
    return s
def bonus(i):
    t = clean(T.get(i, {}).get('ides'))
    m = re.search(r'Бонусы:\s*(.*)', t)
    return (m.group(1).strip() if m else ''), t
out = {'DB': {k: v for k, v in DBv.items()}}
TIP = {}
for i in DBv:
    b, t = bonus(i)
    TIP[i] = (stat_values.parse(b), b, clean(T.get(i, {}).get('unam')))
# 推斷 hash 實數槽的意義：同槽的道具說明裡哪個屬性值最常相符
slotmap = {}
for kind in ('hr', 'hi'):
    for slot in sorted({s for d in DBv.values() for s in d[kind]}):
        c = collections.Counter(); n = 0
        for i, d in DBv.items():
            if slot in d[kind]:
                n += 1
                v = d[kind][slot]
                for k, tv in TIP[i][0].items():
                    for mul in (1, 100, 0.01):
                        if abs(tv - v * mul) < 1e-6: c[(k, mul)] += 1
        slotmap[(kind, slot)] = (c.most_common(3), n)
for k, v in slotmap.items(): print(k, v)
json.dump({'db': DBv, 'tip': {k: [v[0], v[1], v[2]] for k, v in TIP.items()}}, open('ud_itemcheck.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(DBv), 'items in DB;', sum(1 for i in T if i not in DBv), 'w3t objects not in DB')
