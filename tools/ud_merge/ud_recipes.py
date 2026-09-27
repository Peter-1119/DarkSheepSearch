# -*- coding: utf-8 -*-
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
def recipes(J):
    out = {}
    for m in re.finditer(r'\nfunction (\w+) takes[^\n]*\n(.*?)\nendfunction', J, re.S):
        name, body = m.group(1), m.group(2)
        rs = re.findall(r"local integer R\d+='(\w{4})'", body)
        res = re.findall(r"UnitAddItemById\(u,'(\w{4})'\)", body)
        if len(rs) >= 2 and len(res) == 1:
            out[name] = (sorted(rs), res[0])
    return out
if __name__ == '__main__':
    O = recipes(open('ud_382.j', encoding='utf-8', errors='replace').read())
    N = recipes(open('ud_new.j', encoding='utf-8', errors='replace').read())
    site = json.load(open(r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/data/items.json', encoding='utf-8'))['items']
    print(len(O), len(N))
    byres = lambda D: {v[1]: (k, v[0]) for k, v in D.items()}
    bo, bn = byres(O), byres(N)
    for r in sorted(set(bo) | set(bn)):
        o = bo.get(r, (None, None))[1]; n = bn.get(r, (None, None))[1]
        s = sorted(site.get(r, {}).get('recipe') or [])
        nm = site.get(r, {}).get('name')
        flag = '' if (o == n and n == s) else '  <<<'
        if flag or '-v' in sys.argv:
            print(r, nm, bn.get(r, bo.get(r))[0], '\n   3.82', o, '\n   new ', n, '\n   site', s, flag)
