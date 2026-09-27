# -*- coding: utf-8 -*-
"""網站術語表（俄文名 → 網站中文名）：技能、英雄、道具、狀態、套裝。
   python ud_gloss.py 名稱1 名稱2 … 可直接查詢。"""
import sys, os, json
from ud_seg import norm
ROOT = r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep'


def glossary():
    g = {}
    jl = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
    for x in jl('data/abilmap.json')['abilities']:
        n = x.get('n') or []
        if len(n) > 2 and n[2] and n[0]:
            g.setdefault(norm(n[2].strip()), (n[0], '技能'))
    for h in jl('data/heroes.json')['heroes']:
        n = h.get('n') or []
        if len(n) > 2:
            g.setdefault(norm(n[2].strip()), (n[0], '英雄'))
    for it in jl('data/items.json')['items'].values():
        if it.get('name_ru') and it.get('name'):
            g.setdefault(norm(it['name_ru'].strip()), (it['name'], '道具'))
    for k, v in jl('data/site.json')['status'].items():
        g.setdefault(norm(v['n'][2]), (v['n'][0], '狀態'))
    for ru, zh in (('Доблесть', '英勇'), ('Бездна', '深淵'), ('Шторм', '風暴'), ('Адский', '地獄'),
                   ('Наследие легиона', '軍團遺產')):
        g.setdefault(norm(ru), (zh, '套裝'))
    return g


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    G = glossary()
    for w in sys.argv[1:]:
        hit = G.get(norm(w))
        if hit:
            print('%s → %s〔%s〕' % (w, hit[0], hit[1]))
        else:
            part = [(k, v) for k, v in G.items() if norm(w).lower() in k.lower()][:3]
            print('%s → （無）%s' % (w, '；'.join('%s=%s' % (k, v[0]) for k, v in part)))
