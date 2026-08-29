# -*- coding: utf-8 -*-
"""Contact sheet: xlsx reference | icon as-is | icon with R/B swapped."""
import os, sys, json, zipfile, io, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw

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
            b = re.sub(r'\.(blp|png)$', '.png', os.path.basename(str(f).replace('\\', '/')),
                       flags=re.I)
            if b in have:
                return b
    return None


def swap_rb(im):
    im = im.convert('RGBA')
    r, g, b, a = im.split()
    return Image.merge('RGBA', (b, g, r, a))


IDS = sys.argv[1].split(',')
S = 64
sheet = Image.new('RGB', (S * 3 + 40, S * len(IDS) + 4), (18, 20, 27))
d = ImageDraw.Draw(sheet)
for n, i in enumerate(IDS):
    y = n * S + 2
    fn = icon_file(i)
    ref = Image.open(io.BytesIO(xz.read('xl/drawings/media/' + xlsx[i]))).convert('RGB')
    ic = Image.open(os.path.join(ICON, fn)).convert('RGB')
    sheet.paste(ref.resize((S, S)), (36, y))
    sheet.paste(ic.resize((S, S)), (36 + S, y))
    sheet.paste(swap_rb(ic).convert('RGB').resize((S, S)), (36 + S * 2, y))
    d.text((3, y + S // 2 - 4), i, fill=(200, 205, 215))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[2])
sheet.save(out)
print('欄位: 遊戲截圖(正解) | 目前圖示 | 交換R/B後')
print(out)
