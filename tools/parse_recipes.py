# -*- coding: utf-8 -*-
import json, re, sys, hashlib
import openpyxl
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/synthesis.xlsx'
wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb['合成表']
M = json.load(open('name_map.json', encoding='utf-8'))
def sig(name, text): return name + '|' + hashlib.sha1(text.encode('utf-8')).hexdigest()[:8]
KEY = {k: v['url'] for k, v in M.items()}

def cell(r, c):
    v = ws.cell(row=r, column=c).value
    return v.strip() if isinstance(v, str) and v.strip() else None

ITEM_COLS = [2, 5, 8, 11, 14, 17, 20]
OP_COLS = [3, 6, 9, 12, 15, 18]

def resolve(txt):
    name = [l.strip() for l in txt.split('\n') if l.strip()][0]
    return {'name': name, 'url': KEY.get(sig(name, txt)), 'text': txt}

recipes = []
for r in range(3, 43):
    seq = []
    for i, c in enumerate(ITEM_COLS):
        t = cell(r, c)
        if t:
            seq.append({'kind': 'item', **resolve(t)})
        if i < len(OP_COLS):
            op = cell(r, OP_COLS[i])
            if op:
                seq.append({'kind': 'op', 'op': op})
    if seq:
        recipes.append({'row': r, 'seq': seq})

print('recipes:', len(recipes))
missing = [(x['row'], s['name']) for x in recipes for s in x['seq']
           if s['kind'] == 'item' and not s['url']]
print('unresolved item refs:', missing)
json.dump(recipes, open('recipes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for x in recipes:
    print(x['row'], ' '.join(s['name'] if s['kind'] == 'item' else s['op'] for s in x['seq']))
