# -*- coding: utf-8 -*-
import zipfile, json, os, sys, struct
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/synthesis.xlsx'
OUT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/images'
os.makedirs(OUT, exist_ok=True)

M = json.load(open('name_map.json', encoding='utf-8'))
W = {w['url']: w for w in json.load(open('wiki_items.json', encoding='utf-8'))}
z = zipfile.ZipFile(SRC)

def png_size(b):
    if b[:8] == b'\x89PNG\r\n\x1a\n':
        w, h = struct.unpack('>II', b[16:24]); return w, h
    return None

manifest, seen = [], {}
for k, v in sorted(M.items(), key=lambda x: x[1]['url']):
    url = v['url']
    if url in seen:
        continue
    seen[url] = True
    iid = url[:-5]                     # strip .html -> WC3 item id
    data = z.read('xl/drawings/media/' + v['img'])
    fn = iid + '.png'
    open(os.path.join(OUT, fn), 'wb').write(data)
    w = W[url]
    manifest.append({'id': iid, 'file': 'images/' + fn,
                     'name_zh_old': v['zh'], 'name_ru': w['name_ru'],
                     'class_ru': w['fields']['Класс'], 'size': png_size(data),
                     'src_img': v['img']})

json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('extracted', len(manifest), 'images ->', OUT)
from collections import Counter
print('sizes:', Counter(str(m['size']) for m in manifest))
print('wiki items without image:', len(W) - len(manifest))
