# -*- coding: utf-8 -*-
"""比較 3.82fix 與新版每件道具的「實際效果程式」＋說明文字。"""
import sys, re, json, collections
sys.path.insert(0, r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/tools')
sys.stdout.reconfigure(encoding='utf-8')
import mpq, w3obj
from map_items import HOMO
D = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/'

def func(J, name):
    i = J.index('function %s takes' % name)
    return J[i:J.index('\nendfunction', i)]

SET = [(r'SetHeroStr\(u,\w+([+-])sign\*([\d.]+)', 'str'), (r'SetHeroAgi\(u,\w+([+-])sign\*([\d.]+)', 'agi'),
       (r'SetHeroInt\(u,\w+([+-])sign\*([\d.]+)', 'int'), (r'SetUnitLife\(u,\w+([+-])sign\*([\d.]+)', 'hp'),
       (r'SetUnitMana\(u,\w+([+-])sign\*([\d.]+)', 'mp'), (r'SetUnitExtraArmor\(u,\w+([+-])sign\*([\d.]+)', 'armor'),
       (r'SetUnitExtraDamage\(u,\w+([+-])sign\*([\d.]+)', 'atk'), (r'SetUnitAttackSpeed\(u,\w+([+-])sign\*([\d.]+)', 'as'),
       (r'SetUnitLifeRegeneration\(u,\w+([+-])sign\*([\d.]+)', 'hpreg'), (r'SetUnitManaRegeneration\(u,\w+([+-])sign\*([\d.]+)', 'mpreg'),
       (r'udg_ItemBonusDMG\[n\]\+?([+-])sign\*([\d.]+)', 'sp'), (r'udg_Income\[n\]([+-])sign\*([\d.]+)', 'income'),
       (r'udg_SIncome\[n\]([+-])sign\*([\d.]+)', 'sincome'), (r'udg_ExpIncome\[n\]([+-])sign\*([\d.]+)', 'expincome')]

def scan(body, acc):
    stack = []
    for ln in body.split('\n'):
        ln = ln.strip()
        ids = re.findall(r"ItemID==('\w{4}')", ln)
        if ln.startswith('if ') or ln.startswith('if('):
            stack.append([x.strip("'") for x in ids])
            continue
        if ln.startswith('elseif'):
            if stack: stack[-1] = [x.strip("'") for x in ids]
            continue
        if ln == 'else':
            if stack: stack[-1] = []
            continue
        if ln == 'endif':
            if stack: stack.pop()
            continue
        cur = next((s for s in reversed(stack) if s), None)
        if not cur: continue
        for it in cur:
            d = acc.setdefault(it, collections.Counter())
            for rx, k in SET:
                m = re.search(rx, ln)
                if m: d[k] += (1 if m.group(1) == '+' else -1) * float(m.group(2))
            m = re.search(r'Save(Real|Integer)\(hash,u_Id,(\S+?),Load\w+\(hash,u_Id,\S+?\)([+-])sign\*([\d.]+)\)', ln)
            if m: d[('hr' if m.group(1) == 'Real' else 'hi') + ':' + m.group(2)] += (1 if m.group(3) == '+' else -1) * float(m.group(4))
            m = re.search(r'ApplyMainStatBonus\(u,\w+,(\d+),sign\)', ln)
            if m: d['main'] += float(m.group(1))
            m = re.search(r"UnitAddAbility\(u,'(\w{4})'\)", ln)
            if m: d['ab:' + m.group(1)] += 1
            if 'DB_Apply(' in ln: d['<DB>'] += 0
            if not re.search(r'DB_Apply|ApplyStaticItemStats|UnitRemoveAbility|^set \w+=null|^call RemoveItem|^return', ln) and not any(re.search(rx, ln) for rx, _ in SET) and 'LoadReal(hash,u_Id' not in ln and 'LoadInteger(hash,u_Id' not in ln and 'ApplyMainStatBonus' not in ln and 'UnitAddAbility' not in ln:
                d['~' + ln[:70]] += 1

def db(J):
    body = func(J, 'InitItemDB'); acc = {}
    F = ['str', 'agi', 'int', 'hp', 'mp', 'armor', 'atk', 'as', 'main', 'hpreg', 'mpreg', 'sp']
    for m in re.finditer(r"call (DB|DB_HR|DB_HI|DB_Inc|DB_Ab)\('(\w{4})',([^)]*)\)", body):
        f, i, a = m.group(1), m.group(2), [x.strip() for x in m.group(3).split(',')]
        d = acc.setdefault(i, collections.Counter())
        if f == 'DB':
            for k, v in zip(F, a):
                if float(v): d[k] += float(v)
        elif f == 'DB_HR': d['hr:' + a[0]] += float(a[1])
        elif f == 'DB_HI': d['hi:' + a[0]] += float(a[1])
        elif f == 'DB_Inc':
            for k, v in zip(('income', 'sincome', 'expincome'), a):
                if int(v): d[k] += int(v)
        else: d['ab:' + a[0].strip("'")] += 1
    return acc

Jo = open('ud_382.j', encoding='utf-8', errors='replace').read()
Jn = open('ud_new.j', encoding='utf-8', errors='replace').read()
OLD, NEW = {}, db(Jn)
SETF = ('ApplySetAbyssal', 'ApplySetStorm', 'ApplySetValor', 'ApplySetHellish', 'ApplyLegendaryItems')
for fn in ('ApplyStaticItemStats', 'Trig_AddStat_Actions') + SETF:
    scan(func(Jo, fn), OLD)
for fn in ('Trig_AddStat_Actions',) + SETF:
    scan(func(Jn, fn), NEW)
for d in list(OLD.values()) + list(NEW.values()):
    for k in [k for k in d if d[k] == 0 and not k.startswith('<')]: del d[k]
    d.pop('<DB>', None)

def tips(f):
    return w3obj.parse(mpq.MPQ(D + f).read('war3map.w3t'), False)
TO, TN = tips('UD_v3_82fix_opt.w3x'), tips('UD_test_24_09_26_opt.w3x')
cl = lambda s: re.sub(r'\|c[0-9A-Fa-f]{8}|\|r', '', s or '').replace('\r', '').translate(HOMO).strip()
rows = []
for i in sorted(set(OLD) | set(NEW) | set(TN)):
    o, n = dict(OLD.get(i, {})), dict(NEW.get(i, {}))
    to, tn = cl(TO.get(i, {}).get('ides')), cl(TN.get(i, {}).get('ides'))
    ic, tc = o != n, to != tn
    if ic or tc:
        rows.append(dict(id=i, name=cl(TN.get(i, TO.get(i, {})).get('unam')), impl_changed=ic, tip_changed=tc,
                         old=o, new=n, tip_old=to, tip_new=tn))
json.dump(rows, open('ud_itemimpl.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
c = collections.Counter((r['impl_changed'], r['tip_changed']) for r in rows)
print(c)
for r in rows:
    if r['impl_changed']:
        ks = sorted(set(r['old']) | set(r['new']), key=str)
        diff = ['%s:%s→%s' % (k, r['old'].get(k, 0), r['new'].get(k, 0)) for k in ks if r['old'].get(k) != r['new'].get(k)]
        print('%s %s 說明%s｜%s' % (r['id'], r['name'], '有改' if r['tip_changed'] else '沒改', '；'.join(diff)[:300]))
