# -*- coding: utf-8 -*-
"""Parse data/items_database.json (extracted from the .w3x map) into the same
shape as the wiki parse, so both can be diffed / merged."""
import json, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep'
db = json.load(open(os.path.join(ROOT, 'data', 'items_database.json'), encoding='utf-8'))

# The map text mixes Latin homoglyphs into Cyrillic words ("Kлacc", "Ocoбый").
# Normalise the other way round: Latin lookalike -> Cyrillic, but only inside
# words that already contain real Cyrillic.
L2C = str.maketrans({'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с', 'y': 'у',
                     'x': 'х', 'A': 'А', 'E': 'Е', 'O': 'О', 'P': 'Р', 'C': 'С',
                     'Y': 'У', 'X': 'Х', 'T': 'Т', 'H': 'Н', 'K': 'К', 'B': 'В',
                     'M': 'М', 't': 'т'})
CYR = re.compile(r'[А-Яа-яЁё]')
# Latin words that legitimately appear in the map text and must stay Latin
C2L = str.maketrans({'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y',
                     'х': 'x', 'т': 't', 'А': 'A', 'Е': 'E', 'О': 'O', 'Р': 'P',
                     'С': 'C', 'У': 'Y', 'Х': 'X', 'Т': 'T', 'Н': 'H', 'К': 'K',
                     'В': 'B', 'М': 'M'})
LATIN = {'hp', 'mp', 'agi', 'str', 'int', 'atk', 'armor', 'regen', 'speed',
         'dmg', 'magic', 'mag', 'spell', 'power', 'defence', 'defense', 'melee',
         'units', 'to', 'all', 'stats', 'main', 'stat', 'resist', 'move', 'crit',
         'sec', 'mod', 'hero', 'heroes', 'x'}


def decyr(s):
    def fix(m):
        w = m.group(0)
        if w.translate(C2L).lower() in LATIN:
            return w.translate(C2L)
        return w.translate(L2C)
    return re.sub(r'[A-Za-zА-Яа-яЁё]+', fix, s)


FIELD = {'Класс': 'Класс', 'Бонусы': 'Бонусы', 'Способности': 'Способности',
         'Способность': 'Способности', 'Споссобности': 'Способности',
         'Модификатор': 'Модификатор', 'Множитель': 'Множитель',
         'Задание': 'Задание', 'Особенность': 'Особенность', 'Аура': 'Аура',
         'Уникальная способность': 'Уникальная способность',
         'Уникальный модификатор': 'Уникальный модификатор',
         'Уникальная особенность': 'Уникальная особенность',
         'Негативные эффекты': 'Негативные эффекты',
         'Шанс получения': 'Шанс получения', 'Рецепт': 'Рецепт'}
KEYS = sorted(FIELD, key=len, reverse=True)
HEAD = re.compile(r'(?:^|\n)\s*(' + '|'.join(re.escape(k) for k in KEYS) + r')\s*:\s*')

# internal dummies that are not real items
SKIP = re.compile(r'^(id\d\d|gold)$')

out = []
for x in db:
    if SKIP.match(x['id']):
        continue
    name = decyr((x.get('name_clean') or '').strip())
    raw = (x.get('desc_clean') or '').replace('\r', '')
    txt = decyr(raw)
    fields, extra = {}, []
    pos, last_key, last_start = [], None, None
    marks = list(HEAD.finditer(txt))
    if marks:
        if txt[:marks[0].start()].strip():
            extra.append(txt[:marks[0].start()].strip())
        for n, m in enumerate(marks):
            end = marks[n + 1].start() if n + 1 < len(marks) else len(txt)
            key = FIELD[m.group(1)]
            val = txt[m.end():end].strip()
            fields[key] = (fields[key] + ' ' + val).strip() if key in fields else val
    elif txt.strip():
        extra.append(txt.strip())
    # "Бонусы комплекта "-c1"." is appended to whichever field came last
    for k in list(fields):
        m = re.search(r'\s*Бонусы комплекта\s*"?-?[cс](\d)"?\.?\s*$', fields[k])
        if m:
            fields[k] = fields[k][:m.start()].strip()
            fields['Комплект'] = 'c' + m.group(1)
    for e in list(extra):
        m = re.search(r'Бонусы комплекта\s*"?-?[cс](\d)"?\.?', e)
        if m:
            fields['Комплект'] = 'c' + m.group(1)
            extra.remove(e)
    fields = {k: v for k, v in fields.items() if v.strip() and v.strip() != '-'}
    rec = {'id': x['id'], 'name_ru': name, 'fields': fields,
           'extra': [e for e in extra if e],
           'icon': x.get('icon'), 'icon_file': x.get('icon_file'),
           'icon_png': x.get('icon_png'), 'level': x.get('level'),
           'gold': x.get('gold_cost')}
    out.append(rec)

json.dump(out, open('db_items.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('parsed', len(out))
import collections
print(collections.Counter(k for r in out for k in r['fields']))
print('no Класс:', sum(1 for r in out if 'Класс' not in r['fields']))
print(collections.Counter(r['fields'].get('Класс', '(none)') for r in out).most_common())
