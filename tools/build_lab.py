# -*- coding: utf-8 -*-
"""產生 lab.html：英雄定位圖（實驗頁，先不進正式網站）。

想回答的問題是「這隻英雄靠什麼、站在哪」。每個維度都要說得出來源，
所以分四組、各自標明從哪裡算：

  A. 配裝傾向  —— 從 tools/hero_builds.json 的推薦配裝推導。
     每套配裝把 6 格＋不佔格的道具數值加總，同一隻英雄取各套的最大值
     （＝這隻「能走多深」），再跨英雄換成 0～100 的名次分位。
     用名次而不是原始值，是因為技能強度 2275 跟穿透 165 沒有共同尺度，
     而且極端值會把其他人壓成一坨。
  B. 基礎底子  —— 地圖檔 war3map.w3u 的 25 級屬性（初始＋成長×24）。
     沒覆寫的欄位是 null，圖上會標成「無法確認」而不是 0。
  C. 作者評級  —— 地圖檔英雄說明裡作者自己寫的「強度等級」「後期潛力」「解鎖門檻」。
  D. 程式碼旗標 —— 從 war3map.j 驗證過的：吃技能強度的技能數、吃／給裝備技能威力。

複合軸（輸出傾向、坦度傾向…）是 A 組幾個分位的平均，公式寫在 COMPOSITE 裡，
頁面上滑到軸名就看得到。
"""
import io, json, os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.stdout.reconfigure(encoding='utf-8')

SITE = json.load(io.open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))
HEROES, ITEMS = SITE['heroes'], SITE['items']

# ---- A. 配裝傾向：要看哪些道具數值 -------------------------------------------
# (代碼, 三語標籤, 道具數值欄位清單, 說明)
BUILD_DIMS = [
    ('sp',    ['技能強度', 'Spell power', 'Сила умений'],          ['sp'],
     '推薦配裝裡技能強度加總的最大值'),
    ('pen',   ['穿透', 'Penetration', 'Пробитие'],                 ['pen'],
     '推薦配裝裡穿透加總的最大值。穿透是每個傷害事件另外結算的一段，多段技能的英雄特別吃'),
    ('atk',   ['攻擊力', 'Attack', 'Атака'],                        ['atk'],
     '推薦配裝裡攻擊力加總的最大值'),
    ('as',    ['攻擊速度', 'Attack speed', 'Скорость атаки'],      ['as'],
     '推薦配裝裡攻擊速度加總的最大值（負值算 0）'),
    ('hp',    ['生命', 'Health', 'Здоровье'],                       ['hp'],
     '推薦配裝裡生命值加總的最大值'),
    ('armor', ['護甲', 'Armour', 'Броня'],                          ['armor'],
     '推薦配裝裡護甲加總的最大值'),
    ('thorn', ['反傷', 'Thorns', 'Ответный урон'],                  ['thorn'],
     '推薦配裝裡反傷加總的最大值。反傷走獨立管線，出手就結算、不吃護甲'),
    ('stat',  ['狀態傷害', 'Status damage', 'Урон статусов'],       ['dstat', 'dburn', 'dbleed', 'ddise'],
     '點燃／流血／疾病／通用狀態傷害 +% 的加總最大值'),
    ('mod',   ['裝備技能威力', 'Modifier power', 'Сила модификаторов'], ['mod'],
     '推薦配裝裡裝備技能威力加總的最大值。只有 3 隻英雄的技能直接吃這個'),
    ('cd',    ['裝備技能冷卻', 'Item cooldown', 'Перезарядка предметов'], ['cdmod'],
     '推薦配裝裡裝備技能冷卻縮減的最大值（取絕對值）。7 個技能的內冷會被它縮短'),
    ('mres',  ['魔法減免', 'Magic resist', 'Защита от магии'],      ['mres'],
     '推薦配裝裡魔法傷害減免加總的最大值'),
]

# ---- 複合軸 ---------------------------------------------------------------
COMPOSITE = [
    ('out',  ['輸出傾向', 'Damage lean', 'Уклон в урон'],
     ['sp', 'pen', 'atk', 'stat'], '技能強度、穿透、攻擊力、狀態傷害四個分位裡最高兩個的平均，再重排名次'),
    ('tank', ['坦度傾向', 'Tank lean', 'Уклон в живучесть'],
     ['hp', 'armor', 'thorn', 'mres'], '生命、護甲、反傷、魔法減免四個分位裡最高兩個的平均，再重排名次'),
    ('skill', ['技能依賴', 'Skill reliance', 'Опора на умения'],
     ['sp', 'mod', 'cd'], '技能強度、裝備技能威力、裝備技能冷卻三個分位裡最高兩個的平均，再重排名次'),
    ('auto', ['普攻依賴', 'Auto-attack reliance', 'Опора на автоатаку'],
     ['atk', 'as', 'pen'], '攻擊力、攻擊速度、穿透三個分位裡最高兩個的平均，再重排名次'),
]

TIER = {'T1': 1, 'T2': 2, 'T3': 3, 'T3+': 4}
LATE = {u'低': 1, u'中': 2, u'高': 3, u'極高': 4}


def build_vec(b):
    acc = {}
    ids = list(b.get('items') or []) + [v for v in (b.get('bonus') or {}).values()]
    for i in ids:
        it = ITEMS.get(i)
        if not it or not it.get('v'):
            continue
        for k, v in it['v'].items():
            acc[k] = acc.get(k, 0.0) + float(v)
    return acc


def rank_pct(vals):
    """0～100 名次分位＝「有多少比例的英雄比你低」。None 保持 None。

    刻意不用平均名次：裝備技能冷卻 57 隻裡有 46 隻是 0，平均名次會把
    「完全沒有」算成 40 分。改成嚴格小於的比例之後，0 就是 0，
    唯一的最高者是 100，平手的人拿一樣的分數。"""
    have = [v for v in vals if v is not None]
    if len(have) < 2:
        return [None if v is None else 50.0 for v in vals]
    n = len(have) - 1
    return [None if v is None else round(100.0 * sum(1 for w in have if w < v) / n, 1) for v in vals]


def main():
    rows = []
    for h in HEROES:
        raw = {}
        src = {}
        for code, _, fields, _ in BUILD_DIMS:
            best, bname = None, None
            for b in h.get('builds') or []:
                v = build_vec(b)
                s = sum(v.get(f, 0.0) for f in fields)
                if code == 'cd':
                    s = abs(s)
                if code == 'as':
                    s = max(0.0, s)
                if best is None or s > best:
                    best, bname = s, b['n']
            raw[code] = best            # None = 沒有配裝
            src[code] = bname
        st = h.get('st') or {}
        def lv25(k):
            b, g = st.get(k), st.get(k + '_lv')
            return None if b is None or g is None else round(b + g * 24)
        rows.append({
            'id': h['id'], 'n': h['n'], 'attr': h['attr'], 'icon': h['icon'],
            'roles': h['roles'], 'unlock': h['unlock'], 'random': h.get('random', True),
            'lock': h.get('lock'), 'nb': len(h.get('builds') or []),
            'raw': raw, 'src': src,
            'base': {'str': lv25('str'), 'agi': lv25('agi'), 'int': lv25('int')},
            'tier': TIER.get((h.get('tier') or [''])[0]),
            'late': LATE.get((h.get('late') or [''])[0]),
            'tierL': h.get('tier'), 'lateL': h.get('late'),
            'nsp': len(h.get('sp') or []), 'nab': sum(1 for a in h['ab'] if (a.get('kind') or 'hero') == 'hero'),
            'mod': bool(h.get('mod')), 'give': bool(h.get('give')),
        })

    # 名次分位
    pct = {}
    for code, *_ in BUILD_DIMS:
        pct[code] = rank_pct([r['raw'][code] for r in rows])
    for k in ('str', 'agi', 'int'):
        pct['b_' + k] = rank_pct([r['base'][k] for r in rows])
    pct['b_sum'] = rank_pct([None if None in r['base'].values() else sum(r['base'].values()) for r in rows])
    pct['nsp'] = rank_pct([r['nsp'] for r in rows])
    pct['unlock'] = rank_pct([math.log10(r['unlock'] + 1) for r in rows])
    for i, r in enumerate(rows):
        r['p'] = {k: v[i] for k, v in pct.items()}
        r['p']['tier'] = r['tier']
        r['p']['late'] = r['late']
    # 複合軸：先取幾個分位的平均，再把平均值本身重新排名次。
    # 不重排的話平均會往中間縮（只用到 15～75），象限的右半邊永遠是空的；
    # 重排之後每個軸的 50 都是真正的中位數，四個象限各有人。
    for code, _, parts, _ in COMPOSITE:
        mean = []
        for r in rows:
            xs = sorted((r['p'][q] for q in parts if r['p'].get(q) is not None), reverse=True)[:2]
            # 取前兩高的平均，不是全部平均：拜火者的穿透與攻擊力是 0，
            # 全部平均會把它的技能強度稀釋成「中等輸出」，但它是全圖最強的點燃法師。
            # 「輸出傾向」要反映的是這隻最強的那條路線，不是它沒走的路線。
            mean.append(round(sum(xs) / len(xs), 3) if xs else None)
        for r, v in zip(rows, rank_pct(mean)):
            r['p'][code] = v

    # 軸的說明書（頁面上用）
    axes = []
    for code, lab, fields, note in BUILD_DIMS:
        axes.append({'k': code, 'n': lab, 'g': 'A', 'note': note, 'unit': 'pct'})
    for code, lab, parts, note in COMPOSITE:
        axes.append({'k': code, 'n': lab, 'g': 'X', 'note': note, 'unit': 'pct'})
    for k, lab in (('b_str', ['25 級力量', 'STR @25', 'Сила @25']),
                   ('b_agi', ['25 級敏捷', 'AGI @25', 'Ловкость @25']),
                   ('b_int', ['25 級智力', 'INT @25', 'Разум @25']),
                   ('b_sum', ['25 級三圍總和', 'Stat total @25', 'Сумма @25'])):
        axes.append({'k': k, 'n': lab, 'g': 'B', 'unit': 'pct',
                     'note': '地圖檔的初始值＋成長×24；沒覆寫的欄位標成無法確認'})
    axes.append({'k': 'tier', 'n': ['強度等級', 'Power tier', 'Ранг силы'], 'g': 'C', 'unit': 'ord',
                 'ticks': ['T1', 'T2', 'T3', 'T3+'], 'note': '地圖作者在英雄說明裡自己寫的評級'})
    axes.append({'k': 'late', 'n': ['後期潛力', 'Late-game potential', 'Потенциал поздней игры'], 'g': 'C', 'unit': 'ord',
                 'ticks': [u'低', u'中', u'高', u'極高'], 'note': '地圖作者在英雄說明裡自己寫的評級'})
    axes.append({'k': 'unlock', 'n': ['解鎖門檻', 'Unlock cost', 'Порог открытия'], 'g': 'C', 'unit': 'pct',
                 'note': '帳號經驗門檻（0 / 5 萬 / 50 萬 / 400 萬）的對數名次'})
    axes.append({'k': 'nsp', 'n': ['吃技能強度的技能數', 'SP-scaling abilities', 'Умений со скейлом'], 'g': 'D', 'unit': 'pct',
                 'note': '程式碼裡真的讀 udg_ItemBonusDMG 的技能數（不含只寫入的）'})

    out = {'heroes': rows, 'axes': axes,
           'roles': sorted({r[0] for h in HEROES for r in h['roles']}),
           'meta': SITE.get('meta', {})}
    tpl = io.open(os.path.join(HERE, 'lab_template.html'), encoding='utf-8').read()
    html = tpl.replace('/*__LAB_DATA__*/', 'const LAB = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';')
    dst = os.path.join(ROOT, 'lab.html')
    io.open(dst, 'w', encoding='utf-8').write(html)
    print('lab.html：%d 隻英雄、%d 個軸，%.0f KB' % (len(rows), len(axes), len(html.encode('utf-8')) / 1024))

    # 分布快照，確認沒有一坨在同一個值
    if '--check' in sys.argv:
        for code, lab, *_ in BUILD_DIMS + COMPOSITE:
            vals = [r['p'][code] for r in rows if r['p'].get(code) is not None]
            zeros = sum(1 for r in rows if r['raw'].get(code) == 0)
            print('  %-6s %-10s n=%d 零值=%d' % (code, lab[0], len(vals), zeros))


if __name__ == '__main__':
    main()
