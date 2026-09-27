# -*- coding: utf-8 -*-
import sys, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')
sys.argv = ['x']
exec(open('ud_itemimpl.py', encoding='utf-8').read().split("def tips(f):")[0])
import stat_values
sys.path.insert(0, r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/tools')
from map_items import HOMO
TN = w3obj.parse(mpq.MPQ(D + 'UD_test_24_09_26_opt.w3x').read('war3map.w3t'), False)
LAT = ['agi', 'str', 'int', 'atk', 'speed', 'regen', 'armor', 'HP', 'MP', 'all stats', 'main stat', 'spell power']
def clean(s):
    s = re.sub(r'\|c[0-9A-Fa-f]{8}|\|r', '', s or '').replace('\r', '').translate(HOMO)
    for w in LAT: s = s.replace(w.translate(HOMO), w)
    return s
MAPK = {'str': 'str', 'agi': 'agi', 'int': 'int', 'hp': 'hp', 'mp': 'mp', 'armor': 'armor', 'atk': 'atk', 'as': 'as',
        'sp': 'sp', 'hpreg': 'hpreg', 'mpreg': 'mpreg', 'main': 'main', 'pen': 'hr:16', 'thorn': 'hr:17',
        'mod': ('hr:18', 100), 'thornp': ('hr:19', 100), 'cdmod': ('hr:1', 100)}
bad = []
for i, impl in sorted(NEW.items()):
    t = clean(TN.get(i, {}).get('ides'))
    m = re.search(r'Бонусы:\s*(.*)', t)
    if not m: continue
    tip = stat_values.parse(m.group(1))
    if 'all' in tip:
        for k in ('str', 'agi', 'int'): tip[k] = tip.get(k, 0) + tip['all']
    diffs = []
    for tk, ik in MAPK.items():
        mul = 1
        if isinstance(ik, tuple): ik, mul = ik
        tv = tip.get(tk, 0); iv = impl.get(ik, 0) * mul
        if tk == 'cdmod': iv = -iv if iv else 0
        if abs(tv - iv) > 1e-6 and not (tk == 'cdmod' and abs(tv + iv) < 1e-6):
            diffs.append('%s 說明%g／實際%g' % (tk, tv, iv))
    if diffs:
        bad.append((i, clean(TN.get(i, {}).get('unam')), m.group(1)[:120], diffs))
for b in bad: print(b[0], b[1], '｜', b[2], '\n    ', '；'.join(b[3]))
print(len(bad))
