# -*- coding: utf-8 -*-
"""把地圖／遊戲本體裡的 BLP 圖示抽出來轉成 PNG。

圖示有兩個來源：
  1. 地圖自帶的（war3mapImported\\… 或直接放根目錄）
  2. 原版遊戲內建的（ReplaceableTextures\\CommandButtons\\…），
     這些不在地圖裡，要去 war3.mpq / War3x.mpq / War3Patch.mpq 找。
補丁包優先，其次資料片，最後本體 —— 跟遊戲自己的載入順序一致。
"""
import os, io, sys, re, struct

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpq import MPQ
from PIL import Image

BS = chr(92)
GAME_DIRS = [r'D:\Warcraft III', r'C:\Program Files (x86)\Warcraft III',
             r'C:\Program Files\Warcraft III']
GAME_MPQS = ['War3Patch.mpq', 'War3x.mpq', 'war3.mpq']


class IconSource(object):
    def __init__(s, map_path):
        s.arcs = [('map', MPQ(map_path))]
        for d in GAME_DIRS:
            if not os.path.isdir(d):
                continue
            for name in GAME_MPQS:
                p = os.path.join(d, name)
                if os.path.isfile(p):
                    try:
                        s.arcs.append((name, MPQ(p)))
                    except Exception:
                        pass
            break
        s.cache = {}

    def raw(s, path):
        """依序試：原路徑 -> 只有檔名 -> war3mapImported\\檔名。"""
        path = (path or '').replace(BS + BS, BS).strip()
        if not path:
            return None, None
        if path in s.cache:
            return s.cache[path]
        base = path.split(BS)[-1]
        for cand in (path, base, 'war3mapImported' + BS + base):
            for where, a in s.arcs:
                try:
                    d = a.read(cand)
                except Exception:
                    continue
                if d:
                    s.cache[path] = (d, where)
                    return d, where
        s.cache[path] = (None, None)
        return None, None

    @staticmethod
    def _blp1_shifted(d):
        """BLP1 調色盤圖，且 mip0 的宣告偏移不是標準的 1180 時，自己解。

        標準的調色盤 BLP1 是「156 位元組標頭 + 1024 位元組調色盤」，
        所以第 0 層的資料從 1180 開始。但 Pillow（至少到 10.1）**不看
        mipOffsets[0]**，一律從 1180 讀 —— 檔案若把資料放得比較前面，
        整張圖就會被當成從錯的位元組開始，看起來像被水平捲動過
        （右邊的內容跑到左邊）。

        這張地圖的 2277 個 BLP 裡有 4 個是這樣，剛好是四把短刀
        （BTNKnifes1~4，偏移 1100/1112/1136/1172），位移 16/4/44/8 欄。
        照宣告的偏移讀就正常了 —— 邊框接縫會回到跟其他圖示一樣的位置。

        回傳 PIL 影像；不是這種情況就回 None，交給 Pillow 走原本的路。
        """
        if len(d) < 156 or d[:4] != b'BLP1':
            return None
        content, alpha_bits = struct.unpack_from('<ii', d, 4)
        if content != 1:                      # 0 = JPEG，Pillow 處理得好
            return None
        w, h = struct.unpack_from('<ii', d, 12)
        off0, size0 = struct.unpack_from('<i', d, 28)[0], struct.unpack_from('<i', d, 92)[0]
        if off0 == 156 + 1024:                # 標準位置，Pillow 沒問題
            return None
        if not (0 < w <= 4096 and 0 < h <= 4096) or off0 + w * h > len(d):
            return None
        pal = d[156:156 + 1024]
        idx = d[off0:off0 + w * h]
        im = Image.new('RGBA', (w, h))
        px = im.load()
        ap = None
        if alpha_bits == 8 and off0 + 2 * w * h <= len(d):
            ap = d[off0 + w * h:off0 + 2 * w * h]
        for y in range(h):
            row = y * w
            for x in range(w):
                c = idx[row + x] * 4
                px[x, y] = (pal[c + 2], pal[c + 1], pal[c],
                            ap[row + x] if ap else 255)
        return im

    def png(s, path, size=64):
        d, where = s.raw(path)
        if not d:
            return None, None
        im = s._blp1_shifted(d)
        if im is None:
            try:
                im = Image.open(io.BytesIO(d))
                im.load()
            except Exception:
                return None, None
        im = im.convert('RGBA')
        if im.size != (size, size):
            im = im.resize((size, size), Image.LANCZOS)
        return im, where


def save_all(src, jobs, outdir, size=64):
    """jobs = [(輸出檔名不含副檔名, BLP 路徑)]，回傳 (成功, 失敗清單)。"""
    os.makedirs(outdir, exist_ok=True)
    ok, bad, seen = 0, [], {}
    for name, path in jobs:
        key = (path or '').lower()
        if key in seen:                       # 同一張圖多個英雄共用
            if seen[key] != name:
                im, _ = src.png(path, size)
                if im:
                    im.save(os.path.join(outdir, name + '.png'), 'PNG', optimize=True)
                    ok += 1
                    continue
            continue
        im, where = src.png(path, size)
        if im is None:
            bad.append((name, path))
            continue
        im.save(os.path.join(outdir, name + '.png'), 'PNG', optimize=True)
        seen[key] = name
        ok += 1
    return ok, bad


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    import map_heroes
    mp = sys.argv[1]
    src = IconSource(mp)
    print('圖示來源：%s' % ', '.join(n for n, _ in src.arcs))
    H = map_heroes.load(mp)
    jobs = [('h_' + h['id'], h['icon']) for h in H.values()]
    seen = set()
    for h in H.values():
        # 技能書的天賦選項也要抽圖示，不然天賦清單會是空框
        for a in h['abilities']:
            for x in [a] + a.get('opts', []):
                if x['id'] not in seen:
                    seen.add(x['id'])
                    jobs.append(('a_' + x['id'], x['icon']))
        # 皮膚換掉的技能同理 —— 41 個皮膚裡有 25 個的技能跟本體不一樣
        for k in h['skins']:
            for x in k['add'] + k['rm']:
                if x['id'] not in seen:
                    seen.add(x['id'])
                    jobs.append(('a_' + x['id'], x['icon']))
    ok, bad = save_all(src, jobs, os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images', 'heroes'))
    print('輸出 %d 張，失敗 %d 張' % (ok, len(bad)))
    for n, p in bad[:15]:
        print('   %-8s %s' % (n, p or '(沒有圖示路徑)'))
