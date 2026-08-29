# -*- coding: utf-8 -*-
"""Detect BGR/RGB channel swap in the extracted icons.

The xlsx screenshots were captured from the running game, so their colours are
ground truth. For every item that has both an xlsx screenshot and a map icon we
compare mean R and B; if swapping R/B fits better, that icon is channel-swapped.
"""
import os, sys, json, zipfile, io, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

ROOT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep'
MAP = json.load(open(os.path.join(ROOT, 'tools/name_map.json'), encoding='utf-8'))
xz = zipfile.ZipFile(os.path.join(ROOT, 'synthesis.xlsx'))
xlsx = {}
for v in MAP.values():
    xlsx.setdefault(v['url'][:-5], v['img'])

db = {x['id']: x for x in json.load(
    open(os.path.join(ROOT, 'data/items_database.json'), encoding='utf-8'))}
ICON = os.path.join(ROOT, 'data/icons')
have = set(os.listdir(ICON))


def icon_file(i):
    for f in (db[i].get('icon_png'), db[i].get('icon_file'), db[i].get('icon')):
        if f:
            b = os.path.basename(str(f).replace('\\', '/'))
            b = re.sub(r'\.(blp|png)$', '.png', b, flags=re.I)
            if b in have:
                return b
    return None


def mean_rgb(im, keep=0.6):
    im = im.convert('RGB')
    w, h = im.size
    m = int(min(w, h) * (1 - keep) / 2)
    im = im.crop((m, m, w - m, h - m)).resize((8, 8))
    px = list(im.getdata())
    n = len(px)
    return tuple(sum(p[c] for p in px) / n for c in range(3))


rows = []
for i, img in xlsx.items():
    fn = icon_file(i)
    if not fn:
        continue
    a = mean_rgb(Image.open(io.BytesIO(xz.read('xl/drawings/media/' + img))))
    b = mean_rgb(Image.open(os.path.join(ICON, fn)))
    normal = abs(a[0] - b[0]) + abs(a[2] - b[2])
    swapped = abs(a[0] - b[2]) + abs(a[2] - b[0])
    rows.append((i, fn, normal, swapped, a, b))

TH = 12
sw = [r for r in rows if r[3] < r[2] - TH]
ok = [r for r in rows if r[2] <= r[3] - TH]
amb = [r for r in rows if abs(r[2] - r[3]) <= TH]
print('可比對的圖示: %d' % len(rows))
print('  顏色正常     : %d' % len(ok))
print('  疑似 R/B 顛倒: %d' % len(sw))
print('  難以判定     : %d' % len(amb))
print()
for i, fn, n, s, a, b in sorted(sw, key=lambda r: r[2] - r[3])[:15]:
    print('  %-6s %-28s xlsx(%3.0f,%3.0f,%3.0f) icon(%3.0f,%3.0f,%3.0f)  正常%3.0f / 交換%3.0f'
          % (i, fn[:28], a[0], a[1], a[2], b[0], b[1], b[2], n, s))
json.dump([r[0] for r in sw], open('swapped_ids.json', 'w'), indent=0)
