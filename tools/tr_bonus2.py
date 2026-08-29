# -*- coding: utf-8 -*-
"""Russian -> Traditional Chinese translator for the map's `Бонусы` strings.

The current map build splits damage into "attack & ability" damage and
"status" damage (burn / bleed / disease / freeze), so the stat vocabulary is
compositional.  Simple stats stay table-driven; the damage/defence family is
parsed grammatically.
"""
import re, sys, collections

NUM = r'[-+]?\d+(?:\.\d+)?%?'

# ---------------------------------------------------------------- simple stats
_SIMPLE = [
    ('HP regen', '生命回復'), ('MP regen', '法力回復'),
    ('HP', '生命值'), ('MP', '法力值'),
    ('атаки', '攻擊力'), ('атк', '攻擊力'), ('atk', '攻擊力'),
    ('защиты', '護甲'), ('защита', '護甲'), ('armor', '護甲'),
    ('сила умений', '技能強度'), ('spell power', '技能強度'),
    ('скорость атаки', '攻擊速度'), ('atk speed', '攻擊速度'),
    ('скорость передвижения и атаки', '移動與攻擊速度'),
    ('скорость передвижения', '移動速度'), ('скорость бега', '移動速度'),
    ('move speed', '移動速度'),
    ('пробитие', '穿透'),
    ('силы', '力量'), ('сила', '力量'), ('str', '力量'),
    ('ловкости', '敏捷'), ('ловкость', '敏捷'), ('agi', '敏捷'),
    ('разума', '智力'), ('разум', '智力'), ('int', '智力'),
    ('ко всем характеристикам', '全屬性'), ('к характеристикам', '全屬性'),
    ('all stats', '全屬性'), ('main stat', '主屬性'),
    ('ответный урон', '反傷'), ('усиление ответного урона', '反傷加成'),
    ('сила модификаторов', '裝備技能威力'),
    ('перезарядка модификаторов', '裝備技能冷卻'),
    ('увеличение перезарядки предметов (дебаф)', '物品冷卻時間（負面）'),
    ('время воскрешения', '復活時間'),
    ('вампиризм', '吸血'), ('эффект вампиризма', '吸血'),
    ('золото за убийства', '擊殺金幣'),
    ('награда за убийство врагов', '擊殺敵人獎勵'),
    ('ед. ежеминутный доход золота', '每分鐘金幣收入'),
    ('ежеминутный доход золота', '每分鐘金幣收入'),
    ('доход золота', '金幣收入'),
    ('ед./сек. прирост опыта героя', '英雄經驗成長（每秒）'),
    ('прирост опыта героя', '英雄經驗成長'),
    ('mag resist', '魔法傷害減免'),
    ('защиты от магического урона', '魔法傷害減免'),
    ('защита от магического урона', '魔法傷害減免'),
    ('защита от магии', '魔法傷害減免'),
    ('magic defence', '魔法傷害減免'),
    ('dmg to melee units', '對近戰單位傷害'),
]
_SIMPLE.sort(key=lambda x: -len(x[0]))

# ---------------------------------------------------------------- flat phrases
FLAT = {
    'сопротивление проклятиям': '抵抗詛咒',
    'сопротивление поджогу': '抵抗點燃',
    'сопротивление поджогу и горючести': '抵抗點燃與燃燒',
    'сопротивление кровотечению': '抵抗流血',
    'сопротивление заморозке': '抵抗冰凍',
    'сопротивление болезни': '抵抗疾病',
    'сопротивление кровотечению и заморозке': '抵抗流血與冰凍',
    'кровотечению': '抵抗流血', 'заморозке': '抵抗冰凍', 'проклятиям': '抵抗詛咒',
    'болезни': '抵抗疾病', 'поджогу': '抵抗點燃',
    'иммунитет к ответному урону': '免疫反傷',
    'дарует состояние "чумной"': '賦予「瘟疫」狀態',
    '-': '',
    # one-off phrases that are not part of the compositional grammar
    '+10% получаемый урон и наносимый урон от атак и умений против героев':
        '+10%對英雄的攻擊與技能受到及造成傷害',
    '14% вампиризм и 17% сплеш-эффект от атак': '14%吸血、攻擊17%濺射',
    'блокирует 10 ед. физического урона от атак': '格擋攻擊 10 點物理傷害',
    '+15% защита от атак, умений и статусов': '+15%攻擊、技能與狀態防禦',
    'умений и статусов': '',
    '+8% защита от урона не от статусов': '+8%非狀態傷害減免',
    '+20% увеличение перезарядки модификаторов': '+20%裝備技能冷卻時間（負面）',
    '+25% защита от кровотечения и поджога': '+25%流血與點燃抗性',
    '+2 ед./сек. прирост опыта героя': '+2/秒英雄經驗成長',
}
CHUMA = 'дарует состояние "чумной"'

# ------------------------------------------------------- damage/defence family
KIND = [('снижение получаемого урона', '傷害減免'), ('снижение урона', '傷害減免'),
        ('получаемый урон', '受到傷害'), ('получаемого урона', '受到傷害'),
        ('наносимый урон', '造成傷害'),
        ('урон', '傷害'), ('защиты', '防禦'), ('защита', '防禦')]
MOD = [('от атак и умений', '攻擊與技能'), ('(не от статусов)', '非狀態'),
       ('не от статусов', '非狀態'), ('от статусов', '狀態'),
       ('от поджога', '點燃'), ('от кровотечения', '流血'),
       ('от болезни', '疾病'), ('от заморозки', '冰凍'),
       ('от повторной заморозки', '二次冰凍'),
       ('от кровотечения и болезни', '流血與疾病'),
       ('от атаки и умений', '攻擊與技能'), ('от урона', '')]
TGT = [('вражеских героев', '敵方英雄'), ('вражеским героям', '敵方英雄'),
       ('героям', '英雄'), ('героев', '英雄'), ('героями', '英雄'), ('героям', '英雄'),
       ('не-героям', '非英雄單位'), ('не-героев', '非英雄單位'),
       ('врагам не-героям', '非英雄單位'), ('врагов не-героев', '非英雄單位'),
       ('врагам не-героев', '非英雄單位'), ('врагов не-героям', '非英雄單位'),
       ('нежити', '亡靈'),
       ('юнитам ближнего боя', '近戰單位'), ('юнитов ближнего боя', '近戰單位'),
       ('врагам ближнего боя', '近戰單位'), ('врагов ближнего боя', '近戰單位'),
       ('юнитам дальнего боя', '遠程單位'), ('юнитов дальнего боя', '遠程單位'),
       ('врагам дальнего боя', '遠程單位'), ('врагов дальнего боя', '遠程單位'),
       ('магии', '魔法'), ('магического урона', '魔法'), ('атак', '攻擊')]
LVL = re.compile(r'(?:врагам|врагов|юнитам|юнитов)\s+([\d\-\+]+)\s*уровня')


def _strip(text, table):
    """Longest-first removal of one phrase from `table`; returns (zh, rest)."""
    for ru, zh in sorted(table, key=lambda x: -len(x[0])):
        for pat in (' ' + ru, ru):
            idx = text.find(pat)
            if idx != -1:
                return zh, (text[:idx] + ' ' + text[idx + len(pat):]).strip()
    return None, text


def dmg_family(num, rest):
    kind, rest = _strip(rest, KIND)
    if kind is None:
        return None
    mod, rest = _strip(rest, MOD)
    rest = re.sub(r'^(?:по|против|от|к)\b', '', rest).strip()
    tgt = None
    m = LVL.search(rest)
    if m:
        tgt = m.group(1) + '級敵人'
        rest = LVL.sub('', rest).strip()
    else:
        tgt, rest = _strip(rest, TGT)
        rest = re.sub(r'^(?:по|против|от|к)\b', '', rest).strip()
    if rest:                       # leftover words -> not confidently parsed
        return None
    zh = num
    # "защита от поджога/кровотечения/статусов" reads better as a resistance
    if kind == '防禦' and not tgt and mod in ('點燃', '流血', '疾病', '冰凍',
                                              '狀態', '二次冰凍', '流血與疾病'):
        return zh + mod + '抗性'
    if tgt:
        zh += ('對' if kind in ('傷害', '防禦', '造成傷害', '傷害減免') else '受到') + tgt
    if mod:
        zh += mod
    zh += kind
    return zh


NOSTAT = re.compile(r'\s*\((?:не влияет на статусы|не защищает от статусов|'
                    r'не влияет на урон от статусов)\)\s*$', re.I)


def tr_one(part):
    p = part.strip().rstrip('.')
    low = p.lower()
    if low.startswith(CHUMA):
        return '賦予「瘟疫」狀態：免疫疾病，並可對敵人施加疾病（詳見 F2 圖鑑）', True
    m = NOSTAT.search(p)
    if m:
        zh, ok = tr_one(p[:m.start()])
        return (zh + '（不影響狀態）' if ok else p), ok
    if low in FLAT:
        return FLAT[low], True
    m = re.match(r'^(%s)\s+(.*)$' % NUM, p)
    if not m:
        return p, False
    num, rest = m.group(1), m.group(2).strip()
    rest = re.sub(r'^ед\.(?!/)\s*', '', rest)
    for ru, zh in _SIMPLE:
        if rest.lower() == ru.lower():
            return num + zh, True
    if rest.lower().startswith('крит. удар'):
        mm = re.search(r'[хx]([\d.]+)', rest)
        if mm:
            return '%s機率造成%s倍暴擊' % (num, mm.group(1)), True
    hit = dmg_family(num, rest.lower())
    if hit:
        return hit, True
    return p, False


def tr_bonus(s):
    s = (s or '').replace('НР', 'HP').replace('МР', 'MP').replace('МP', 'MP')
    # phrases that contain a comma and must not be split
    for ru, zh in FLAT.items():
        if s.strip().lower().endswith(ru) and ',' in ru:
            head, _, _ = s.strip().lower().rpartition(ru)
            pre, _ = tr_bonus(s.strip()[:len(head)].rstrip(', '))
            return ('，'.join(x for x in (pre, zh) if x)), []
    parts = [x.strip() for x in re.split(r',(?![^()]*\))', s) if x.strip()]
    out, bad = [], []
    for p in parts:
        zh, ok = tr_one(p)
        if not ok:
            bad.append(p)
        if zh:
            out.append(zh)
    return '，'.join(out), bad


if __name__ == '__main__':
    import json
    sys.stdout.reconfigure(encoding='utf-8')
    D = json.load(open('db_items.json', encoding='utf-8'))
    bad = collections.Counter()
    for r in D:
        _, b = tr_bonus(r['fields'].get('Бонусы', ''))
        for x in b:
            bad[x] += 1
    print('UNTRANSLATED:', len(bad), 'occurrences:', sum(bad.values()))
    for k, v in bad.most_common(80):
        print(' %2d %s' % (v, k))
