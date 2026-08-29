# -*- coding: utf-8 -*-
import re, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

items = json.load(open('itemlist.json', encoding='utf-8'))
out = []
FIELDS = ['Бонусы', 'Способности', 'Модификатор', 'Mножитель', 'Множитель',
          'Уникальная способность', 'Уникальный модификатор', 'Аура']

def clean(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&quot;', '"')
    return s.strip()

for it in items:
    h = open(os.path.join('pages', it['url']), encoding='utf-8').read()
    body = h.split('<div class="content">', 1)[1].split('</body>')[0]
    rec = {'name_ru': it['name'], 'url': it['url'], 'group': it['cat']}
    m = re.search(r'<h2>(.*?)</h2>', body)
    rec['title'] = clean(m.group(1)) if m else it['name']
    # split at Рецепт / Компонент
    head = body
    recipe, comps = [], []
    if 'Рецепт:' in body:
        head, rest = body.split('Рецепт:', 1)
        tail = rest
        if 'Компонент:' in rest:
            tail, comp_part = rest.split('Компонент:', 1)
            comps = [(u, clean(t)) for u, t in re.findall(r'<a href="([^"]+)">([^<]*)</a>', comp_part)]
        recipe = [(u, clean(t)) for u, t in re.findall(r'<a href="([^"]+)">([^<]*)</a>', tail)]
    elif 'Компонент:' in body:
        head, comp_part = body.split('Компонент:', 1)
        comps = [(u, clean(t)) for u, t in re.findall(r'<a href="([^"]+)">([^<]*)</a>', comp_part)]
    rec['recipe'] = [{'url': u, 'label': t.lstrip('- ').strip()} for u, t in recipe]
    rec['used_in'] = [{'url': u, 'label': t.strip()} for u, t in comps]
    # parse head fields
    texts = [clean(x) for x in re.findall(r'<p1>(.*?)</p1>', head, re.S)]
    rec['fields'] = {}
    for t in texts:
        if ':' in t or '：' in t:
            k, _, v = t.partition(':')
            rec['fields'][k.strip()] = v.strip()
        elif t:
            rec['fields'].setdefault('_extra', []).append(t)
    out.append(rec)

json.dump(out, open('wiki_items.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('parsed', len(out))
from collections import Counter
c = Counter(k for r in out for k in r['fields'])
print(c)
