# -*- coding: utf-8 -*-
import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

E = json.load(open('xlsx_entries.json', encoding='utf-8'))
W = json.load(open('wiki_items.json', encoding='utf-8'))

SYM = set('+=←→↑↓↖↗↘↙')
def is_sym(n): return all(ch in SYM or ch.isspace() for ch in n)

# unique xlsx items
uniq = {}
for e in E:
    if is_sym(e['name']): continue
    key = (e['name'], e['text'])
    uniq.setdefault(key, e)
items = list(uniq.values())
print('xlsx unique items:', len(items))

def zh_class(t):
    m = re.search(r'品质[:：]\s*(.+)', t)
    return m.group(1).strip() if m else ''

CLS = {}
for lv in range(1, 6):
    CLS['神器（lv.%d）' % lv] = 'Артефакт (%d ур.)' % lv
    CLS['特殊（lv.%d）' % lv] = 'Особый (%d ур.)' % lv
CLS.update({'强化': 'Усилитель', '扭曲': 'Искаженный', '折射': 'Преломленный',
            '圣物': 'Реликвия', '普通': 'Обычный', '传说': 'Легендарный',
            '附加': 'Дополнительный', '淬炼': 'Закаленный',
            '特殊（lv.3）+风暴': 'Особый (3 ур.) + Шторм'})

def nums(s):
    return collections.Counter(re.findall(r'\d+(?:\.\d+)?', s.replace('，', ',')))

def bonus_line(t):
    m = re.search(r'(?:属性)[:：]\s*(.+)', t)
    return m.group(1) if m else ''

def sim(a, b):
    if not a and not b: return 0.0
    inter = sum((a & b).values()); union = sum((a | b).values())
    return inter / union if union else 0.0

wiki_by_class = collections.defaultdict(list)
for w in W:
    wiki_by_class[w['fields']['Класс']].append(w)

results = []
for it in items:
    zc = zh_class(it['text'])
    rc = CLS.get(zc)
    cands = wiki_by_class.get(rc, []) if rc else []
    if zc.startswith('任务物品'):
        cands = wiki_by_class['Квестовый [1/2]'] + wiki_by_class['Квестовый [2/2]']
    if not cands and rc and rc.startswith('Особый'):
        cands = [w for w in W if w['fields']['Класс'].startswith(rc)]
    if not cands:
        cands = W
    zb = nums(bonus_line(it['text'])); zall = nums(it['text'])
    scored = []
    for w in cands:
        f = w['fields']
        wb = nums(f.get('Бонусы', ''))
        wall = nums(' '.join(v if isinstance(v, str) else ' '.join(v) for v in f.values()))
        s = sim(zb, wb) * 2 + sim(zall, wall)
        scored.append((s, w))
    scored.sort(key=lambda x: -x[0])
    results.append({'zh': it, 'cands': [(round(s, 3), w['name_ru'], w['url'],
                                        w['fields'].get('Бонусы', '')) for s, w in scored[:3]]})

json.dump(results, open('match_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for r in results:
    it = r['zh']
    print('### %s [%s]  img=%s' % (it['name'], zh_class(it['text']), it['img']))
    print('    ZH:', bonus_line(it['text']) or it['text'].split('\n', 2)[-1].replace('\n', ' / ')[:90])
    for s, n, u, b in r['cands']:
        print('    %.2f %-32s %s | %s' % (s, n, u, b[:70]))
