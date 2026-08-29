# -*- coding: utf-8 -*-
"""Validate: "icon has >256 unique colours" predicts "R/B channels are swapped".

Rationale: BLP1 stores either a 256-colour palette or JPEG-compressed BGR data.
The extractor got the palette path right and the JPEG path wrong, so the colour
count is a direct proxy for which decoder ran.
"""
import os, sys, json, zipfile, io, re
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

ROOT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep'
SEP = chr(92)
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
            b = re.sub(r'\.(blp|png)$', '.png',
                       os.path.basename(str(f).replace(SEP, '/')), flags=re.I)
            if b in have:
                return b
    return None


def mean_rgb(im, keep=0.6):
    im = im.convert('RGB')
    w, h = im.size
    m = int(min(w, h) * (1 - keep) / 2)
    px = list(im.crop((m, m, w - m, h - m)).resize((8, 8)).getdata())
    return tuple(sum(p[c] for p in px) / len(px) for c in range(3))


def swap_rb(im):
    r, g, b, a = im.convert('RGBA').split()
    return Image.merge('RGBA', (b, g, r, a))


def ncolours(im):
    return len(im.convert('RGB').getcolors(1 << 20) or [])


tp = tn = fp = fn = 0
undecided = 0
bad = []
for i, img in xlsx.items():
    f = icon_file(i)
    if not f:
        continue
    ref = Image.open(io.BytesIO(xz.read('xl/drawings/media/' + img)))
    ic = Image.open(os.path.join(ICON, f))
    a, b0, b1 = mean_rgb(ref), mean_rgb(ic), mean_rgb(swap_rb(ic))
    e0 = sum(abs(a[c] - b0[c]) for c in range(3))
    e1 = sum(abs(a[c] - b1[c]) for c in range(3))
    if abs(e0 - e1) < 10:            # near-grey: measurement can't tell
        undecided += 1
        continue
    truth_swapped = e1 < e0
    pred_swapped = ncolours(ic) > 256
    if truth_swapped and pred_swapped: tp += 1
    elif not truth_swapped and not pred_swapped: tn += 1
    elif pred_swapped and not truth_swapped: fp += 1; bad.append(('假陽性', i, f, ncolours(ic)))
    else: fn += 1; bad.append(('假陰性', i, f, ncolours(ic)))

print('可判定樣本: %d（另有 %d 張接近灰階無法判定）' % (tp + tn + fp + fn, undecided))
print('  規則命中「顛倒」  : %d' % tp)
print('  規則命中「正常」  : %d' % tn)
print('  誤判              : %d' % (fp + fn))
for x in bad:
    print('   ', x)
print()
allf = sorted(os.listdir(ICON))
nsw = sum(1 for f in allf if ncolours(Image.open(os.path.join(ICON, f))) > 256)
print('套用到全部 %d 張 data/icons：需要修正 %d 張，維持原樣 %d 張'
      % (len(allf), nsw, len(allf) - nsw))
