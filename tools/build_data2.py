# -*- coding: utf-8 -*-
"""Merge the map object data (authoritative) with icons, translations,
the xlsx synthesis chart and the wiki recipe graph."""
import json, os, re, shutil, sys
sys.path.insert(0, '.')
from tr_bonus2 import tr_bonus
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep'
DB = json.load(open('db_items.json', encoding='utf-8'))
# cooldown_group 只有原始匯出檔才有，db_items.json 沒帶過來
_RAWDB = {x['id']: x for x in json.load(
    open(os.path.join(ROOT, 'data', 'items_database.json'), encoding='utf-8'))}
NAMES = json.load(open('names2.json', encoding='utf-8'))
AB = json.load(open('ab_db.json', encoding='utf-8'))
WIKI = {w['url'][:-5]: w for w in json.load(open('wiki_items.json', encoding='utf-8'))}
MAP = json.load(open('name_map.json', encoding='utf-8'))
RECIPES = json.load(open('recipes.json', encoding='utf-8'))

# ------------------------------------------------------------------ old names
zh_old, xlsx_img = {}, {}
for v in MAP.values():
    i = v['url'][:-5]
    zh_old.setdefault(i, v['zh'])
    xlsx_img.setdefault(i, v['img'])
SHOP = {'地精商店': '地精商店', '巫毒商店': '巫毒商店', '神秘藏宝室': '神祕藏寶室'}

# ------------------------------------------------------------------ icons
SRC_ICON = os.path.join(ROOT, 'data', 'icons')
OUT_IMG = os.path.join(ROOT, 'images')
os.makedirs(OUT_IMG, exist_ok=True)
have = set(os.listdir(SRC_ICON))
import zipfile
xz = zipfile.ZipFile(os.path.join(ROOT, 'synthesis.xlsx'))


# The BLP extractor decoded palettised icons correctly but left JPEG-compressed
# ones in BGR order, so red and blue are swapped on those. The two paths are
# distinguishable by colour count: a palettised BLP can only carry 256 colours.
from PIL import Image
RB_THRESHOLD = 256


def needs_rb_swap(path):
    with Image.open(path) as im:
        return len(im.convert('RGB').getcolors(1 << 20) or []) > RB_THRESHOLD


def load_icon(path):
    """Return the icon with colour channels corrected if necessary."""
    im = Image.open(path).convert('RGBA')
    if len(im.convert('RGB').getcolors(1 << 20) or []) > RB_THRESHOLD:
        r, g, b, a = im.split()
        im = Image.merge('RGBA', (b, g, r, a))
    return im


def icon_for(r):
    for f in (r.get('icon_png'), r.get('icon_file'), r.get('icon')):
        if f:
            b = os.path.basename(str(f).replace('\\', '/'))
            b = re.sub(r'\.(blp|png)$', '.png', b, flags=re.I)
            if b in have:
                return os.path.join(SRC_ICON, b)
    return None


# ------------------------------------------------------------------ taxonomy
CLS = {}
for lv in range(1, 6):
    CLS['Артефакт (%d ур.)' % lv] = '神器（lv.%d）' % lv
    CLS['Особый (%d ур.)' % lv] = '特殊（lv.%d）' % lv
CLS.update({'Особый (5+ ур.)': '特殊（lv.5+）', 'Особый (5++ ур.)': '特殊（lv.5++）',
            'Усилитель': '強化', 'Искаженный': '扭曲', 'Преломленный': '折射',
            'Реликвия': '聖物', 'Обычный': '普通', 'Редкий': '稀有',
            'Уникальный': '獨特', 'Легендарный': '傳說', 'Дополнительный': '附加',
            'Закаленный': '淬鍊', 'Самоцвет': '寶石', 'Серьги': '耳環',
            'Ритуальный': '儀式', 'Совершенный': '完美', 'Новогодний': '新年',
            'Пасхальный': '復活節', 'Хэллоуин': '萬聖節', 'Руна': '符文',
            'Курьер': '信使',
            'Квестовый [1/2]': '任務物品（1/2）', 'Квестовый [2/2]': '任務物品（2/2）'})
SET = {'Адский': '地獄', 'Доблесть': '英勇', 'Бездна': '深淵', 'Шторм': '風暴'}
# display order of the item-list sections
ORDER = ['普通', '稀有', '獨特', '傳說',
         '特殊（lv.1）', '特殊（lv.2）', '特殊（lv.3）', '特殊（lv.4）', '特殊（lv.5）',
         '特殊（lv.5+）', '特殊（lv.5++）',
         '神器（lv.1）', '神器（lv.2）', '神器（lv.3）', '神器（lv.4）', '神器（lv.5）',
         '扭曲', '任務物品（1/2）', '任務物品（2/2）', '聖物', '折射', '完美',
         '附加', '淬鍊', '儀式', '寶石', '耳環', '強化', '符文', '信使',
         '新年', '復活節', '萬聖節', '消耗品／掉落物']


def tr_class(c):
    if not c:
        return '消耗品／掉落物'
    parts = [p.strip() for p in re.split(r'\s+\+\s+', c)]
    base = CLS.get(parts[0])
    if base is None:
        return '消耗品／掉落物'
    return '＋'.join([base] + [SET.get(p, p) for p in parts[1:]])


# 套裝歸屬有兩個來源，要取聯集：
#   1. 說明裡的「Бонусы комплекта "-c2"」 -> parse_db 解析成 fields['Комплект']
#   2. Класс 那行後面接的套裝名，例如「Особый (5 ур.) + Бездна」
# 絕大多數兩者一致，但「三位一體 Триада」只有第 2 種來源，
# 而且一次屬於三個套裝（英勇＋深淵＋風暴，地獄除外），只看 Комплект 會漏掉。
SET_RU = {'Доблесть': 'c1', 'Бездна': 'c2', 'Шторм': 'c3', 'Адский': 'c4'}

def set_keys(r):
    """回傳該道具所屬的套裝代號清單（依 c1..c4 排序），沒有就 None。"""
    ks = set()
    f = r['fields'].get('Комплект')
    if f:
        ks.add(f)
    cls = r['fields'].get('Класс', '') or ''
    for ru, k in SET_RU.items():
        if ru in cls:
            ks.add(k)
    return sorted(ks) or None


# 主動技能 vs 被動技能。
# 判斷依據有兩個，取聯集：
#   1. cooldown_group 有值 —— 有冷卻群組就代表要「使用」才會觸發（69 件）
#   2. 說明裡的「При использовании…」（使用這件道具時…）
# 特別注意要排除「Использование умений / способностей」——
# 那是「英雄施放技能時」觸發的被動，不是主動道具（女巫帽、法力催化劑那類）。
ACT_TXT = re.compile(r'при использовании(?!\s+(?:умени|способност))', re.I)

def is_active(i, r):
    if (_RAWDB.get(i, {}).get('cooldown_group') or '').strip():
        return True
    blob = ' '.join(str(v) for v in r['fields'].values())
    return bool(ACT_TXT.search(blob))


items, copied, noimg, fixed = {}, 0, [], 0
for r in DB:
    i = r['id']
    cls_ru = r['fields'].get('Класс', '')
    cls = tr_class(cls_ru)
    eff = []
    e = AB.get(i)
    if e:
        for (lab, ru), zh in zip(e['parts'], e['zh']):
            if zh and zh.strip() not in ('-', ''):
                eff.append({'label': lab, 'zh': zh, 'ru': ru})
    src = icon_for(r)
    img = None
    if src:
        load_icon(src).save(os.path.join(OUT_IMG, i + '.png'), 'PNG', optimize=True)
        img, copied = 'images/%s.png' % i, copied + 1
        if needs_rb_swap(src):
            fixed += 1
    elif i in xlsx_img:
        open(os.path.join(OUT_IMG, i + '.png'), 'wb').write(
            xz.read('xl/drawings/media/' + xlsx_img[i]))
        img = 'images/%s.png' % i
    else:
        noimg.append(i)
    old = zh_old.get(i)
    shop = next((v for k, v in SHOP.items() if old and '【%s】' % k in old), None)
    if old:
        old = re.sub(r'【.*?】', '', old)
    w = WIKI.get(i)
    items[i] = {
        'id': i, 'name': NAMES[i], 'name_ru': r['name_ru'],
        'name_old': old, 'shop': shop,
        'cls': cls, 'cls_ru': cls_ru or None, 'group': cls.split('＋')[0],
        'set': set_keys(r),
        'active': is_active(i, r),
        'stats': tr_bonus(r['fields'].get('Бонусы', ''))[0],
        'stats_ru': r['fields'].get('Бонусы', ''),
        'effects': eff,
        'image': img, 'icon_src': 'map' if src else ('xlsx' if img else None),
        'level': r.get('level'), 'gold': r.get('gold'),
        'recipe': [x['url'][:-5] for x in w['recipe']] if w else [],
        'used_in': [],
        'in_wiki': bool(w),
    }

# Recipe corrections confirmed in-game (the wiki is wrong here).
RECIPE_FIX = {'sbok': ['schl', 'pclr']}     # 黃道十二宮 = 潛能覺醒 + 覺醒卷軸
for k, v in RECIPE_FIX.items():
    items[k]['recipe'] = v
# derive "used in" from the recipe graph so the two stay consistent
for i, v in items.items():
    for c in v['recipe']:
        if c in items and i not in items[c]['used_in']:
            items[c]['used_in'].append(i)

# recipes / charts (from the xlsx, verified against play experience)
LADDER = [('I00C', 'ratc', 'belv', 'stel'), ('I001', 'rat6', 'rde1', 'lhst'),
          ('I005', 'rat9', 'rde2', 'bgst'), ('I018', 'ward', 'rwiz', 'rst1'),
          ('I01N', 'penr', 'rlif', 'clsd'), ('I00K', 'spsh', 'rde3', 'bspd'),
          ('I00U', 'cnob', 'ciri', 'evtl'), ('I01I', 'pmna', 'rin1', 'gcel'),
          ('I02J', 'dsum', 'sbch', 'brac'), ('I013', 'rhth', 'mcou', 'ssil'),
          ('I01T', 'hcun', 'clfm', 'odef')]
REFRACT = [('I00I', 'I00J', 'I00T', ['woms', 'mnst', 'whwd', 'fgsk'], 'pams'),
           ('I026', 'I027', 'I029', ['wshs', 'wcyc', 'will', 'wlsd'], 'nflg'),
           ('I039', 'I03C', 'I03D', ['pomn', 'hlst', 'ankh', 'infs'], 'stpg'),
           ('I00Z', 'I010', 'I028', ['rej3', 'wild', 'fgrg', 'pnvu'], 'pspd')]
# 扭曲循環（29 件）。從 synthesis.xlsx 的箭頭圖抽出，
# 之後由玩家提供的遊戲內順序獨立驗證過 —— 集合與順序完全一致，只差起點。
# 這裡採用玩家的起點（扭曲權杖），方便跟遊戲內對照。
CYCLE = ['shea', 'pinv', 'spro', 'ssan', 'skul', 'pman', 'rnec', 'wneg', 'silk',
         'shas', 'moon', 'sneg', 'tsct', 'sman', 'vamp', 'phea', 'sreg', 'wneu',
         'hslv', 'tcas', 'mcri', 'tret', 'stwp', 'pnvl', 'tgrh', 'sor1', 'pgin',
         'fwss', 'shdt']

# 儀式循環（11 件，玩家提供）。深淵之矛 ram1 是最後一個，之後繞回深淵蘑菇。
RITUAL = ['sand', 'srrc', 'sres', 'sror', 'fgdg', 'totw', 'pghe', 'pres',
          'pgma', 'pdiv', 'ram1']
GEM = [('lmbr', 'rma2', 'I00P'), ('gfor', 'sor3', 'I00Q'), ('gomn', 'sor2', 'I00F'),
       ('tpow', 'sor5', 'I00E'), ('guvi', 'sor4', 'I00O')]

# -c5「軍團遺產」（軍團軍械庫）。跟 c1~c4 不同：成員不是寫在道具的 Класс 欄位，
# 而是一份跨類別的指定清單，所以只能手動維護。除了這 9 件，還要背包裡有
# 任一件「聖物」類道具。玩家自遊戲內取得，物件資料查不到。
LEGION = {
    'key': 'c5',
    'zh': '軍團遺產', 'en': 'Legion Legacy', 'ru': 'Наследие легиона',
    'colour': '#D9455C',
    'items': ['spro', 'pman', 'phea', 'ssan',    # 扭曲
              'rej3', 'wlsd',                     # 折射
              'tbak', 'spre', 'modt'],            # 神器
    'anyOf': {'zh': '任一件「聖物」類道具', 'en': 'any Relic-class item',
              'ru': 'любой предмет класса «Реликвия»'},
    'anyGroup': '聖物',
}

recipes = [{'row': r['row'],
            'seq': [{'kind': 'item', 'id': s['url'][:-5]} if s['kind'] == 'item'
                    else {'kind': 'op', 'op': s['op']} for s in r['seq']]}
           for r in RECIPES]

for n, i in enumerate(LEGION['items']):
    if i in items:
        items[i]['legion'] = n

data = {'items': items, 'order': ORDER, 'ladder': LADDER, 'refract': REFRACT,
        'cycle': CYCLE, 'ritual': RITUAL, 'gem': GEM, 'recipes': recipes,
        'legion': LEGION}
json.dump(data, open(os.path.join(ROOT, 'data', 'items.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print('items:', len(items))
print('icons from map:', copied, '(R/B corrected:', str(fixed) + ')',
      '| from xlsx:', sum(1 for v in items.values() if v['icon_src'] == 'xlsx'),
      '| none:', len(noimg))
print('no image:', [(i, items[i]['name']) for i in noimg])
unk = sorted({v['group'] for v in items.values()} - set(ORDER))
print('groups not in ORDER:', unk)
import collections
print(collections.Counter(v['group'] for v in items.values()).most_common())
