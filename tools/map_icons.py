# -*- coding: utf-8 -*-
"""把地圖／遊戲本體裡的 BLP 圖示抽出來轉成 PNG。

圖示有兩個來源：
  1. 地圖自帶的（war3mapImported\\… 或直接放根目錄）
  2. 原版遊戲內建的（ReplaceableTextures\\CommandButtons\\…），
     這些不在地圖裡，要去 war3.mpq / War3x.mpq / War3Patch.mpq 找。
補丁包優先，其次資料片，最後本體 —— 跟遊戲自己的載入順序一致。
"""
import os, io, sys, re

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

    def png(s, path, size=64):
        d, where = s.raw(path)
        if not d:
            return None, None
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
