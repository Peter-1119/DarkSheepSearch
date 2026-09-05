# -*- coding: utf-8 -*-
"""用地圖檔重建 db_items.json，並補上缺少的道具圖示。

以前 db_items.json 要靠人工從地圖編輯器匯出再跑 parse_db.py，
現在直接讀 .w3x，改版只要換一個檔案。
輸出格式跟 parse_db.py 完全一樣，所以 build_data2.py 不用改。
"""
import os, sys, io, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import map_items
from map_icons import IconSource

ICON_DIR = os.path.join(ROOT, 'data', 'icons')
# 從地圖／遊戲本體直接解碼出來的圖示放這裡。
# 跟 data/icons 分開的原因：那批是舊的外部抽取器產生的，JPEG 壓縮的 BLP
# 有 R/B 顛倒的問題，build_data2 會再修一次；這裡的已經是對的，不能再修。
MAP_ICON_DIR = os.path.join(ROOT, 'data', 'icons_map')


def main(map_path):
    items = map_items.load(map_path)
    old_path = os.path.join(HERE, 'db_items.json')
    old = {}
    if os.path.isfile(old_path):
        old = {x['id']: x for x in json.load(io.open(old_path, encoding='utf-8'))}

    os.makedirs(ICON_DIR, exist_ok=True)
    os.makedirs(MAP_ICON_DIR, exist_ok=True)
    have = {f.lower() for f in os.listdir(ICON_DIR)}
    src, added, failed = IconSource(map_path), [], []

    out = []
    for iid in sorted(items):
        r = items[iid]
        blp = r['icon']
        png = os.path.basename(blp.replace(chr(92), '/'))
        png = (png[:-4] if png.lower().endswith('.blp') else png) + '.png'
        # 每張都直接從地圖抽一份顏色正確的
        if blp:
            im, _ = src.png(blp)
            if im:
                im.save(os.path.join(MAP_ICON_DIR, png), 'PNG', optimize=True)
                added.append(png)
            elif png.lower() not in have:
                failed.append((iid, blp))
        o = old.get(iid, {})
        out.append({
            'id': iid,
            'name_ru': r['name_ru'],
            'fields': r['fields'],
            'extra': [],
            'icon': blp,
            'icon_file': blp,
            # 舊資料裡人工對過的 icon_png 優先，沒有就照檔名推
            'icon_png': o.get('icon_png') or ('icons_png/' + png),
            'level': r['level'],
            'gold': r['gold'],
        })

    json.dump(out, io.open(old_path, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('db_items.json：%d 件（原本 %d 件）' % (len(out), len(old)))
    if added:
        print('  從地圖抽出圖示 %d 張 -> data/icons_map/' % len(added))
    if failed:
        print('  仍無圖示 %d 件：%s' % (len(failed),
              ', '.join('%s(%s)' % (i, b or '無路徑') for i, b in failed[:8])))
    # 換源之後最容易掉的就是套裝歸屬，明確報一次
    sets = sum(1 for r in items.values() if 'Комплект' in r['fields'])
    print('  有套裝歸屬 %d 件' % sets)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main(sys.argv[1])
