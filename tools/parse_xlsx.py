# -*- coding: utf-8 -*-
import zipfile, json, re, os, sys, hashlib
from xml.etree import ElementTree as ET
import openpyxl
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/synthesis.xlsx'
z = zipfile.ZipFile(SRC)
rels = ET.fromstring(z.read('xl/drawings/_rels/drawing1.xml.rels'))
rmap = {r.get('Id'): r.get('Target').split('/')[-1] for r in rels}
NS = {'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
d = ET.fromstring(z.read('xl/drawings/drawing1.xml'))
anchors = {}   # (row, col) -> image file
for anc in d:
    frm = anc.find('xdr:from', NS)
    col = int(frm.find('xdr:col', NS).text) + 1
    row = int(frm.find('xdr:row', NS).text) + 1
    blip = anc.find('.//a:blip', NS)
    anchors[(row, col)] = rmap.get(blip.get(R))

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb['合成表']
cells = {}
for row in ws.iter_rows():
    for c in row:
        if c.value is not None and isinstance(c.value, str) and c.value.strip():
            cells[(c.row, c.column)] = c.value.strip()

# md5 of each image, to dedupe identical images stored twice
md5 = {}
for n in z.namelist():
    if n.startswith('xl/drawings/media/'):
        md5[n.split('/')[-1]] = hashlib.md5(z.read(n)).hexdigest()

entries = []
for (row, col), img in anchors.items():
    txt = cells.get((row, col + 1))
    if not txt:
        continue
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    name = lines[0]
    entries.append({'row': row, 'col': col, 'img': img, 'md5': md5.get(img),
                    'name': name, 'text': txt})

json.dump(entries, open('xlsx_entries.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('anchored entries:', len(entries), 'anchors total:', len(anchors))

# unique names
from collections import defaultdict
byname = defaultdict(set)
for e in entries:
    byname[e['name']].add(e['md5'])
print('unique names:', len(byname))
conf = {k: v for k, v in byname.items() if len(v) > 1}
print('names with >1 distinct image:', len(conf))
for k, v in conf.items():
    print('  ', k, len(v))
