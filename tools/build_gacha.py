# -*- coding: utf-8 -*-
"""tools/gacha.json（人工整理的機率）+ 地圖（道具清單與價格）-> data/gacha.json。

從地圖直接讀出來的部分：
  - 每一階（T1~T7）的道具清單與件數 —— `set T1_Item[n]='xxxx'`
  - 盒子的金價與製作時間 —— war3map.w3u 的 ugol／ubld（沒覆寫就沿用原型值）
機率表、保底門檻、加成與陷阱說明放在 gacha.json，因為那些是條件分支，
硬要從程式碼推回「玩家看得懂的表」反而容易錯。
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from mpq import MPQ
import w3obj

# 盒子沒覆寫金價時沿用的原型值（war3.mpq 的 Units\UnitBalance.slk）
BASE_GOLD = {'hpea': 75, 'hars': 150}


def main():
    V = json.load(io.open(os.path.join(HERE, 'version.json'), encoding='utf-8'))
    G = json.load(io.open(os.path.join(HERE, 'gacha.json'), encoding='utf-8'))
    m = MPQ(V['map_file'])
    jass = m.read('war3map.j').decode('utf-8', 'replace')
    U = w3obj.parse(m.read('war3map.w3u'))
    SITE = json.load(io.open(os.path.join(ROOT, 'data', 'site.json'),
                             encoding='utf-8'))['items'] \
        if os.path.isfile(os.path.join(ROOT, 'data', 'site.json')) else {}

    # ---- 每一階的道具清單
    pools = {}
    for line in jass.split('\n'):
        mm = re.match(r"set T([1-7])_Item\[(\d+)\]='(\w+)'", line.strip())
        if mm:
            pools.setdefault('t' + mm.group(1), {})[int(mm.group(2))] = mm.group(3)
    for t in G['tiers']:
        ids = [v for _, v in sorted(pools.get(t['k'], {}).items())]
        t['pool'] = ids
        t['n_pool'] = len(ids)
        if not ids:
            print('  ! %s 抽不到道具清單' % t['k'])

    # ---- 盒子的價格／時間
    def cost(uid):
        r = U.get(uid) or {}
        g = r.get('ugol')
        if g is None:
            g = BASE_GOLD.get(r.get('_base'))
        return g, r.get('ubld')

    for b in G['boxes'] + G['scrolls']:
        if b['id'] in U:                       # 書記官訓練出來的盒子是「單位」
            g, s = cost(b['id'])
            if g is not None:
                b['gold'] = g
            if s is not None:
                b['sec'] = s
        elif b['id'] in SITE:                  # 包裹／大包裹是道具，價格在 site.json
            p = SITE[b['id']].get('p')
            if p:
                b['gold'] = p

    # ---- 書記官／學院本身
    G['where'] = {
        'arch': {'id': 'h00T', 'gold': cost('h00T')[0], 'sec': cost('h00T')[1],
                 'n': ['書記官', 'Archivist', 'Архивариус'],
                 't': ['收益點升級而成，全部的盒子都在這裡「製作」。',
                       'An upgrade of a profit point; every box is trained here.',
                       'Улучшение точки прибыли; все коробки создаются здесь.']},
        'vault': {'id': 'h00R', 'gold': None, 'sec': None,
                  'n': ['倉庫', 'Vault', 'Хранилище'],
                  't': ['直接買包裹，撿起來就開，但開不出 lv.5 以上。',
                        'Sells parcels that open on pickup, but never above lv.4.',
                        'Продаёт посылки, которые открываются при подборе, но не выше 4 ур.']},
        'academy': {'id': 'o02D', 'gold': (U.get('o02D') or {}).get('ugol'),
                    'sec': (U.get('o02D') or {}).get('ubld'),
                    'n': ['學院', 'Academy', 'Академия'],
                    't': ['研究「先知」天賦的地方，需要遊戲第 2 階段。',
                          'Where the Seer talent is researched; needs game phase 2.',
                          'Здесь изучается талант «Провидец»; нужна 2-я фаза игры.']},
    }
    G.pop('_說明', None)
    out = os.path.join(ROOT, 'data', 'gacha.json')
    json.dump(G, io.open(out, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('抽裝資料 -> %s（%d 種盒子、%d 種卷軸盒，牌堆 %s）'
          % (out, len(G['boxes']), len(G['scrolls']),
             '／'.join('%s %d' % (t['n'][0], t['n_pool']) for t in G['tiers'])))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
