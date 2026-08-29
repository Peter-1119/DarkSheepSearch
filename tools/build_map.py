# -*- coding: utf-8 -*-
import json, re, sys, hashlib, collections
sys.stdout.reconfigure(encoding='utf-8')

E = json.load(open('xlsx_entries.json', encoding='utf-8'))
R = json.load(open('match_raw.json', encoding='utf-8'))
W = {w['url']: w for w in json.load(open('wiki_items.json', encoding='utf-8'))}

SYM = set('+=←→↑↓↖↗↘↙')
def is_sym(n): return all(ch in SYM or ch.isspace() for ch in n)
def sig(name, text): return name + '|' + hashlib.sha1(text.encode('utf-8')).hexdigest()[:8]

# manual overrides:  (xlsx name, distinguishing substring of text) -> wiki url
OVER = [
    ('升级卷轴',   None, 'I01F.html'),   # Cвитoк yлyчшeния
    ('强化卷轴',   None, 'I01G.html'),   # Cвитoк ycилeния
    ('觉醒卷轴',   None, 'I01H.html'),   # Cвитoк пpoбyждeния
    ('转化卷轴',   None, 'sksh.html'),   # Свиток преобразования
    ('扭曲卷轴',   None, None),          # Свиток искажения
    ('折射卷轴',   None, None),          # Свиток преломления
    ('淬火卷轴',   None, None),          # Свиток закаливания
    ('不稳定卷轴', None, 'esaz.html'),   # Нестабильный свиток
    ('仪式匕首',   None, None),          # Ритуальный кинжал
    ('念珠',       None, None),          # Чётки
    ('十字军的护符', None, None),        # Талисман крестоносца
    ('生锈头盔',   None, None),          # Ржавый шлем
    ('力量吊坠',   None, None),          # Подвеска силы
    ('智力吊坠',   None, None),          # Подвеска разума
    ('力量戒指【神秘藏宝室】', None, None),
    ('智力戒指【神秘藏宝室】', None, None),
    ('普通手套【巫毒商店】',   None, None),
    ('仪式圣杯',   '1.3倍',  None),      # Кинжал ястреба
    ('迷雾之矛',   '17%',    None),      # Наручи крови
    ('刺客之刺',   '溅射',   None),      # Обсидиан
]
# resolved by russian name instead of url (filled below)
BYNAME = {
    '扭曲卷轴': 'Свиток искажения', '折射卷轴': 'Свиток преломления',
    '淬火卷轴': 'Свиток закаливания', '升级卷轴': 'Cвитoк yлyчшeния',
    '强化卷轴': 'Cвитoк ycилeния',  '觉醒卷轴': 'Cвитoк пpoбyждeния',
    '转化卷轴': 'Свиток преобразования', '不稳定卷轴': 'Нестабильный свиток',
    '仪式匕首': 'Ритуальный кинжал', '念珠': 'Чётки',
    '十字军的护符': 'Талисман крестоносца', '生锈头盔': 'Ржавый шлем',
    '力量吊坠': 'Подвеска силы', '智力吊坠': 'Подвеска разума',
    '力量戒指【神秘藏宝室】': 'Кольцо силы', '智力戒指【神秘藏宝室】': 'Кольцо разума',
    '普通手套【巫毒商店】': 'Простые перчатки',
    '十字军之刃': 'Клинок крестоносца', '金色王冠': 'Золотая диадема',
}
RU2URL = {w['name_ru']: u for u, w in W.items()}
SPECIAL = {  # (name, text-substring) -> russian name
    ('仪式圣杯', '1.3倍'): 'Кинжал ястреба',
    ('迷雾之矛', '17%'): 'Наручи крови',
    ('刺客之刺', '溅射'): 'Обсидиан',
}

uniq = {}
for e in E:
    if is_sym(e['name']) or e['name'] == '随机扭曲装备':
        continue
    uniq.setdefault(sig(e['name'], e['text']), e)

auto = {}
for r in R:
    it = r['zh']
    if is_sym(it['name']) or it['name'] == '随机扭曲装备':
        continue
    auto[sig(it['name'], it['text'])] = r['cands'][0]

mapping = {}
unmatched = []
for k, e in uniq.items():
    ru = None
    for (nm, sub), rn in SPECIAL.items():
        if e['name'] == nm and sub in e['text']:
            ru = rn
    if ru is None and e['name'] in BYNAME:
        ru = BYNAME[e['name']]
    if ru is not None:
        url = RU2URL.get(ru)
        if not url:
            unmatched.append((e['name'], ru)); continue
        mapping[k] = {'url': url, 'src': 'manual'}
    else:
        s, n, url, b = auto[k]
        mapping[k] = {'url': url, 'src': 'auto', 'score': s}
    mapping[k].update({'zh': e['name'], 'img': e['img'], 'text': e['text']})

print('mapped', len(mapping), 'unmatched', unmatched)
json.dump(mapping, open('name_map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# duplicates: two xlsx items -> same wiki url?
c = collections.Counter(v['url'] for v in mapping.values())
for u, n in c.items():
    if n > 1:
        print('DUP', u, W[u]['name_ru'], [v['zh'] for v in mapping.values() if v['url'] == u])
