# -*- coding: utf-8 -*-
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

DB = json.load(open('db_items.json', encoding='utf-8'))
OLD = {u: parts for u, n, parts in json.load(open('abilities.json', encoding='utf-8'))}
OLDTR = json.load(open('ab.json', encoding='utf-8'))

LAB = [('Способности', '能力'), ('Модификатор', 'MOD'), ('Множитель', '倍增'),
       ('Задание', '任務'), ('Особенность', '特性'), ('Аура', '光環'),
       ('Уникальная способность', '獨特能力'),
       ('Уникальный модификатор', '獨特MOD'),
       ('Уникальная особенность', '獨特特性'),
       ('Негативные эффекты', '負面'), ('Шанс получения', '機率')]


def norm(s):
    s = re.sub(r'\s+', ' ', s or '').strip().rstrip('.')
    return s.replace('НР', 'HP').replace('МР', 'MP').lower()


# reuse map: normalised russian -> chinese, from the previous wiki pass
reuse = {}
for u, parts in OLD.items():
    tr = OLDTR.get(u, [])
    for (lab, ru), zh in zip(parts, tr):
        if zh.strip() not in ('-', ''):
            reuse[norm(ru)] = zh

need, done, out = [], 0, {}
for r in DB:
    parts = []
    for key, lab in LAB:
        v = r['fields'].get(key)
        if isinstance(v, str) and v.strip() and v.strip() != '-':
            parts.append((lab, v.strip()))
    for e in r['extra']:
        parts.append(('說明', e))
    if not parts:
        continue
    zh = []
    for lab, ru in parts:
        hit = reuse.get(norm(ru))
        zh.append(hit)
        if hit:
            done += 1
        else:
            need.append((r['id'], r['name_ru'], lab, ru))
    out[r['id']] = {'parts': parts, 'zh': zh}

json.dump(out, open('ab_db.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('items with effects:', len(out))
print('reused translations:', done, '| need translation:', len(need))
json.dump(need, open('ab_need.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
tot = sum(len(x[3]) for x in need)
print('chars to translate:', tot)
