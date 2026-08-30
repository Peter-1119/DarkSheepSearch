# -*- coding: utf-8 -*-
"""把俄文屬性字串拆成可比較的數值，供排行功能使用。

tr_stats.py 產生的是給人看的字串；這裡產生的是給程式排序用的
{ 屬性代碼: 數值 }。兩者共用同一份俄文原文，不會有不一致的問題。
"""
import re, sys, collections

# 屬性代碼 -> (俄文樣式, 中文, English, Русский, 是否百分比)
STATS = [
    ('str',   r'(?:силы|сила|str)',                 '力量',       'Strength',    'Сила',        0),
    ('agi',   r'(?:ловкости|ловкость|agi)',         '敏捷',       'Agility',     'Ловкость',    0),
    ('int',   r'(?:разума|разум|int)',              '智力',       'Intellect',   'Разум',       0),
    ('all',   r'(?:ко всем характеристикам|к характеристикам|all stats)',
                                                    '全屬性',     'All stats',   'Все хар-ки',  0),
    ('main',  r'main stat',                         '主屬性',     'Main stat',   'Осн. хар-ка', 0),
    ('hp',    r'HP(?!\s*regen)',                    '生命值',     'HP',          'HP',          0),
    ('mp',    r'MP(?!\s*regen)',                    '法力值',     'MP',          'MP',          0),
    ('hpreg', r'HP\s*regen',                        '生命回復',   'HP regen',    'HP rеgеn',    0),
    ('mpreg', r'MP\s*regen',                        '法力回復',   'MP regen',    'MP rеgеn',    0),
    ('atk',   r'(?:атаки|атк|atk)(?!\s*speed)',     '攻擊力',     'Attack',      'Атака',       0),
    ('armor', r'(?:защиты|защита|armor)',           '護甲',       'Armor',       'Защита',      0),
    ('sp',    r'(?:сила умений|spell power)',       '技能強度',   'Spell power', 'Сила умений', 0),
    ('as',    r'(?:скорость атаки|atk\s*speed)',    '攻擊速度',   'Attack speed', 'Скор. атаки', 1),
    ('pen',   r'пробитие',                          '穿透',       'Penetration', 'Пробитие',    0),
    ('thorn', r'ответный урон',                     '反傷',       'Thorns',      'Отв. урон',   0),
    ('thornp', r'усиление ответного урона',         '反傷加成',   'Thorns bonus', 'Усил. отв. урона', 1),
    ('ms',    r'(?:скорость передвижения|скорость бега|move\s*speed)',
                                                    '移動速度',   'Move speed',  'Скор. бега',  0),
    ('mod',   r'сила модификаторов',                '裝備技能威力', 'Mod power',  'Сила мод.',   1),
    # 減傷類。跟上面的加成不同，這些多半不疊加（同類只取最高），
    # 配裝計算時要另外處理，見 build_site_data.py 的 NOSTACK。
    ('mres',  r'(?:защиты? от магического урона|защита от магии|mag\s*resist)',
                                                    '魔法傷害減免', 'Magic resist', 'Защита от магии', 1),
    ('sres',  r'защита от статусов',                '狀態防護',   'Status protection', 'Защита от статусов', 1),
]
NUM = r'([-+]?\d+(?:\.\d+)?)\s*(%?)'


def parse(bonus):
    """回傳 {代碼: 數值}。

    用白名單：只有整段剛好等於「數字 + 已知屬性名」才採計。
    條件加成（例如「+15% 對 0-1 級敵人的非狀態傷害」）不會 fullmatch 到
    任何屬性樣式，自然被略過 —— 那種數值本來就不能拿來跟裸屬性比大小。"""
    out = {}
    if not bonus:
        return out
    s = bonus.replace('НР', 'HP').replace('МР', 'MP').replace('МP', 'MP')
    for part in re.split(r',(?![^()]*\))', s):
        p = part.strip().rstrip('.')
        if not p:
            continue
        m = re.match(r'^' + NUM + r'\s+(.+)$', p)
        if not m:
            continue
        val, pct, rest = float(m.group(1)), m.group(2), m.group(3).strip()
        rest = re.sub(r'^ед\.(?!/)\s*', '', rest)
        for code, pat, *_ in STATS:
            if re.fullmatch(pat, rest, re.I):
                out[code] = out.get(code, 0) + val
                break
    return out


META = [{'k': c, 'zh': zh, 'en': en, 'ru': ru, 'pct': bool(p)}
        for c, _, zh, en, ru, p in STATS]

if __name__ == '__main__':
    import json, os
    sys.stdout.reconfigure(encoding='utf-8')
    HERE = os.path.dirname(os.path.abspath(__file__))
    DB = json.load(open(os.path.join(HERE, 'db_items.json'), encoding='utf-8'))
    D = json.load(open(os.path.join(os.path.dirname(HERE), 'data/items.json'),
                       encoding='utf-8'))['items']
    cnt = collections.Counter()
    best = collections.defaultdict(list)
    for r in DB:
        for k, v in parse(r['fields'].get('Бонусы', '')).items():
            cnt[k] += 1
            best[k].append((v, D[r['id']]['name']))
    print('%-7s %-10s %5s   %s' % ('代碼', '屬性', '件數', '前 3 名'))
    print('-' * 76)
    for m in META:
        k = m['k']
        top = sorted(best[k], reverse=True)[:3]
        print('%-7s %-10s %5d   %s' % (k, m['zh'], cnt[k],
              '  '.join('%g %s' % (v, n) for v, n in top)))
