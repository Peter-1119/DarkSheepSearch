# -*- coding: utf-8 -*-
"""Build the trilingual dataset the website consumes."""
import json, os, re, sys
sys.path.insert(0, '.')
from tr_stats import tr_bonus
import stat_values
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep'
DB = json.load(open('db_items.json', encoding='utf-8'))
NZH = json.load(open('names2.json', encoding='utf-8'))
NEN = json.load(open('names_en.json', encoding='utf-8'))
AB = json.load(open('ab_db.json', encoding='utf-8'))
ABEN = json.load(open('ab_en.json', encoding='utf-8'))
WIKI = {w['url'][:-5]: w for w in json.load(open('wiki_items.json', encoding='utf-8'))}
MAP = json.load(open('name_map.json', encoding='utf-8'))
RAW = {x['id']: x for x in json.load(
    open(os.path.join(ROOT, 'data', 'items_database.json'), encoding='utf-8'))}
SITE = json.load(open(os.path.join(ROOT, 'data', 'items.json'), encoding='utf-8'))

# attach the English ability strings
it = iter(ABEN)
for uid, e in AB.items():
    e['en'] = [next(it) for _ in e['parts']]

zh_old = {}
for v in MAP.values():
    zh_old.setdefault(v['url'][:-5], re.sub(r'【.*?】', '', v['zh']))
SHOPS = {'地精商店': ('地精商店', 'Goblin Shop', 'Магазин гоблинов'),
         '巫毒商店': ('巫毒商店', 'Voodoo Shop', 'Магазин вуду'),
         '神秘藏宝室': ('神祕藏寶室', 'Secret Vault', 'Тайная сокровищница')}

# ---------------------------------------------------------------- taxonomy
# (russian class -> zh, en) ; rank = display order, lower is stronger
GROUPS = [
    ('神器（lv.5）', 'Артефакт (5 ур.)', 'Artifact lv.5'),
    ('神器（lv.4）', 'Артефакт (4 ур.)', 'Artifact lv.4'),
    ('神器（lv.3）', 'Артефакт (3 ур.)', 'Artifact lv.3'),
    ('神器（lv.2）', 'Артефакт (2 ур.)', 'Artifact lv.2'),
    ('神器（lv.1）', 'Артефакт (1 ур.)', 'Artifact lv.1'),
    ('特殊（lv.5++）', 'Особый (5++ ур.)', 'Special lv.5++'),
    ('特殊（lv.5+）', 'Особый (5+ ур.)', 'Special lv.5+'),
    ('特殊（lv.5）', 'Особый (5 ур.)', 'Special lv.5'),
    ('特殊（lv.4）', 'Особый (4 ур.)', 'Special lv.4'),
    ('特殊（lv.3）', 'Особый (3 ур.)', 'Special lv.3'),
    ('特殊（lv.2）', 'Особый (2 ур.)', 'Special lv.2'),
    ('特殊（lv.1）', 'Особый (1 ур.)', 'Special lv.1'),
    ('傳說', 'Легендарный', 'Legendary'),
    ('獨特', 'Уникальный', 'Unique'),
    ('稀有', 'Редкий', 'Rare'),
    ('普通', 'Обычный', 'Common'),
    ('完美', 'Совершенный', 'Perfected'),
    ('折射', 'Преломленный', 'Refracted'),
    ('聖物', 'Реликвия', 'Relic'),
    ('任務物品（2/2）', 'Квестовый [2/2]', 'Quest item [2/2]'),
    ('任務物品（1/2）', 'Квестовый [1/2]', 'Quest item [1/2]'),
    ('扭曲', 'Искаженный', 'Distorted'),
    ('淬鍊', 'Закаленный', 'Tempered'),
    ('附加', 'Дополнительный', 'Extra'),
    ('儀式', 'Ритуальный', 'Ritual'),
    ('耳環', 'Серьги', 'Earrings'),
    ('寶石', 'Самоцвет', 'Gem'),
    ('新年', 'Новогодний', 'New Year'),
    ('復活節', 'Пасхальный', 'Easter'),
    ('萬聖節', 'Хэллоуин', 'Halloween'),
    ('強化', 'Усилитель', 'Enhancer'),
    ('符文', 'Руна', 'Rune'),
    ('信使', 'Курьер', 'Courier'),
    ('消耗品／掉落物', 'Расходники', 'Consumables'),
]
GRANK = {g[0]: n for n, g in enumerate(GROUPS)}
SET = {'c1': ('英勇', 'Valor', 'Доблесть'), 'c2': ('深淵', 'Abyss', 'Бездна'),
       'c3': ('風暴', 'Storm', 'Шторм'), 'c4': ('地獄', 'Infernal', 'Адский')}
LABEL = {'能力': ('能力', 'Ability', 'Способности'),
         'MOD': ('MOD', 'Mod', 'Модификатор'),
         '倍增': ('倍增', 'Multiplier', 'Множитель'),
         '任務': ('任務', 'Quest', 'Задание'),
         '特性': ('特性', 'Trait', 'Особенность'),
         '獨特能力': ('獨特能力', 'Unique ability', 'Уник. способность'),
         '獨特特性': ('獨特特性', 'Unique trait', 'Уник. особенность'),
         '負面': ('負面', 'Drawback', 'Негативные эффекты'),
         '機率': ('機率', 'Odds', 'Шанс получения'),
         '光環': ('光環', 'Aura', 'Аура'),
         '說明': ('說明', 'Description', 'Описание')}

CLSRU = {g[0]: g[1] for g in GROUPS}
CLSEN = {g[0]: g[2] for g in GROUPS}

items = {}
for r in DB:
    i = r['id']
    prev = SITE['items'][i]
    grp = prev['group']
    m = re.match(r'\|c[fF]{2}([0-9a-fA-F]{6})', RAW[i].get('name') or '')
    colour = '#' + m.group(1).upper() if m else None
    eff = []
    e = AB.get(i)
    if e:
        for k, (lab, ru) in enumerate(e['parts']):
            zh, en = e['zh'][k], e['en'][k]
            if not zh or zh.strip() in ('-', ''):
                continue
            eff.append({'l': list(LABEL.get(lab, (lab, lab, lab))),
                        't': [zh, en, ru]})
    sets = r['fields'].get('Комплект')
    items[i] = {
        'id': i,
        'n': [NZH[i], NEN[i], r['name_ru']],
        'a': zh_old.get(i) if zh_old.get(i) != NZH[i] else None,
        'g': GRANK[grp],
        'c': [prev['cls'], prev['cls'].replace(grp, CLSEN[grp]),
              prev['cls'].replace(grp, CLSRU[grp])],
        'k': colour,
        's': tr_bonus(r['fields'].get('Бонусы', ''), 'zh')[0] and [
            tr_bonus(r['fields'].get('Бонусы', ''), 'zh')[0],
            tr_bonus(r['fields'].get('Бонусы', ''), 'en')[0],
            r['fields'].get('Бонусы', '')] or None,
        'e': eff,
        'img': prev['image'],
        'set': list(SET[sets]) if sets else None,
        'shop': list(SHOPS[[k for k in SHOPS if MAP and
                            ('【%s】' % k) in (next((v['zh'] for v in MAP.values()
                                                    if v['url'][:-5] == i), ''))][0]])
                if any(('【%s】' % k) in (next((v['zh'] for v in MAP.values()
                                               if v['url'][:-5] == i), ''))
                       for k in SHOPS) else None,
        'r': prev['recipe'],
        'u': prev['used_in'],
        'v': stat_values.parse(r['fields'].get('Бонусы', '')) or None,
    }

# ---------------------------------------------------------------- 版本資訊
# 地圖物件資料裡沒有版本號（WC3 的版本寫在 war3map.w3i 或檔名，沒有被匯出），
# 所以顯示「資料擷取日期」而不是編一個版本出來。查到地圖版本就填進 version.json。
import datetime
VER = json.load(open('version.json', encoding='utf-8'))
dbfile = os.path.join(ROOT, 'data', 'items_database.json')
data_date = VER.get('data_date') or datetime.datetime.fromtimestamp(
    os.path.getmtime(dbfile)).strftime('%Y-%m-%d')
meta = {
    'mapVersion': (VER.get('map_version') or '').strip(),
    'dataDate': data_date,
    'items': len(items),
    'icons': sum(1 for v in items.values() if v['img']),
}

# 只保留有足夠樣本的屬性，免得下拉選單塞滿只有 1-2 件的項目
import collections as _c
_have = _c.Counter(k for v in items.values() for k in (v['v'] or {}))
statmeta = [m for m in stat_values.META if _have[m['k']] >= 8]
for m in statmeta:
    m['n'] = _have[m['k']]

# ---------------------------------------------------------------- 順序資訊
# 扭曲：舊合成表畫成封閉迴圈，箭頭有明確方向，只有「第一次轉出」是隨機
#       → 之後每次用扭曲卷軸都是固定的下一件
# 折射：同一張表在折射區寫了 9 次「隨機」，Wiki 也只說「換成另一件折射裝備」
#       → 視為 4 件一組的池子，順序不保證
CYC = {i: n for n, i in enumerate(SITE['cycle'])}
RIT = {i: n for n, i in enumerate(SITE.get('ritual', []))}
REF = {}
for gi, (q1, q2, relic, group, perfect) in enumerate(SITE['refract']):
    for n, i in enumerate(group):
        REF[i] = {'g': gi, 'n': n, 'relic': relic, 'group': group, 'perfect': perfect}
for i, v in items.items():
    if i in CYC:
        v['cyc'] = CYC[i]
    if i in RIT:
        v['rit'] = RIT[i]
    if i in REF:
        v['ref'] = REF[i]

out = {
    'meta': meta,
    'stats': statmeta,
    'cycle': SITE['cycle'],
    'ritual': SITE.get('ritual', []),
    'items': items,
    'groups': [{'zh': g[0], 'ru': g[1], 'en': g[2]} for g in GROUPS],
    'ladder': SITE['ladder'], 'refract': SITE['refract'],
    'cycle': SITE['cycle'],
    'ritual': SITE.get('ritual', []), 'gem': SITE['gem'],
    'recipes': SITE['recipes'],
}
json.dump(out, open(os.path.join(ROOT, 'data', 'site.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
print('meta:', meta)
print('rankable stats:', ', '.join('%s(%d)' % (m['zh'], m['n']) for m in statmeta))
print('items:', len(items))
print('with colour:', sum(1 for v in items.values() if v['k']))
print('with image:', sum(1 for v in items.values() if v['img']))
print('size: %.0f KB' % (os.path.getsize(os.path.join(ROOT, 'data', 'site.json')) / 1024))
