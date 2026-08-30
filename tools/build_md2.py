# -*- coding: utf-8 -*-
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
SETB = json.load(open(os.path.join(os.path.dirname(__file__),
                                   'set_bonus.json'), encoding='utf-8'))

ROOT = r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep'
D = json.load(open(os.path.join(ROOT, 'data', 'items.json'), encoding='utf-8'))
I = D['items']

L = []
def w(s=''):
    L.append(s)

def icon(i, size=40):
    it = I[i]
    return ('<img src="%s" width="%d" alt="%s">' % (it['image'], size, it['name'])
            if it['image'] else '')

def link(i):
    return '[%s](#%s)' % (I[i]['name'], I[i]['id'].lower())

def inline(i, size=28):
    ic = icon(i, size)
    return (ic + ' ' if ic else '') + link(i)

def effs(i, sep='<br>'):
    e = I[i]['effects']
    return sep.join('**%s：**%s' % (x['label'], x['zh'].replace('\n', ' '))
                    for x in e) if e else ''

def cell(i):
    return '<br>'.join(x for x in (I[i]['stats'], effs(i)) if x) or '—'

NIMG = sum(1 for v in I.values() if v['image'])
NEQ = sum(1 for v in I.values() if v['group'] != '消耗品／掉落物')

# ---------------------------------------------------------------- header
import json as _json, datetime as _dt
_ver = _json.load(open('version.json', encoding='utf-8'))
_mv = (_ver.get('map_version') or '').strip()
_dd = _ver.get('data_date') or _dt.datetime.fromtimestamp(
    os.path.getmtime(os.path.join(ROOT, 'data', 'items_database.json'))).strftime('%Y-%m-%d')

w('# 肥羊的聖誕禮物 — 裝備合成攻略 & 裝備一覽')
w()
w('> 魔獸爭霸 III 地圖《肥羊的聖誕禮物》（原版：**Underground Defence**）裝備資料整理。')
w('> 地圖版本 **%s**　·　資料擷取日 %s' % (_mv or '未知', _dd))
w('> 共 **%d** 件裝備 ＋ **%d** 件消耗品／掉落物，其中 **%d** 件附有遊戲內圖示。'
  % (NEQ, len(I) - NEQ, NIMG))
w()
w('## 資料來源')
w()
w('| 來源 | 內容 | 用途 |')
w('|---|---|---|')
w('| **`data/items_database.json` + `data/icons/`**<br>（自地圖檔匯出） | 474 件道具的名稱、品質、屬性、能力，以及 407 張 64×64 遊戲原始圖示 | **本文的資料主體**，數值與圖示全部以此為準 |')
w('| `synthesis.xlsx`（女神十一製作合成表） | 40 條合成配方、扭曲／折射流程圖、中文既有譯名 | **合成路線的唯一來源**（地圖物件資料不含配方，配方寫在觸發裡） |')
w('| [felinhart.github.io/udwiki](https://felinhart.github.io/udwiki/items.html) | 俄文 Wiki，431 件裝備 | 僅用來補充「配方／用於」的關聯，**數值已過時、不採用** |')
w()
w('**版本落差說明：**')
w()
w('- 地圖檔的資料比 Wiki 新。兩邊對照後，**93 件裝備的數值不同**、13 件的俄文名不同，')
w('  另有 **6 件裝備 Wiki 完全沒有收錄**（見 [Wiki 未收錄的裝備](#wikimiss)）。')
w('- 最明顯的改版是**傷害拆成「攻擊與技能傷害」與「狀態傷害」兩套**，')
w('  很多裝備因此改寫了加成敘述（見 [狀態系統](#status)）。')
w('- 因此凡是 Wiki 與地圖檔衝突之處，本文一律採用地圖檔。')
w()

# ---------------------------------------------------------------- status
w('<a id="status"></a>')
w()
w('## 一、狀態（status）系統')
w()
w('目前版本把傷害拆成兩類，很多裝備的加成只對其中一類生效，看屬性時要特別注意：')
w()
w('| 分類 | 內容 | 屬性寫法 |')
w('|---|---|---|')
w('| **攻擊與技能傷害** | 普攻、英雄技能、裝備 MOD 的直接傷害 | 「攻擊與技能傷害」「非狀態傷害」 |')
w('| **狀態傷害** | 由下列負面狀態造成的持續／延遲傷害 | 「狀態傷害」「點燃傷害」「流血傷害」… |')
w()
w('主要狀態：')
w()
w('| 中文 | 俄文 | 說明 |')
w('|---|---|---|')
for a, b, c in [('點燃', 'поджог', '持續火焰傷害，多數火系裝備的主力；先有易燃更容易命中'),
                ('易燃', 'горючесть', '標記狀態，先施加後讓點燃更容易命中／加重'),
                ('流血', 'кровотечение', '持續傷害，常見於匕首與爪類'),
                ('疾病', 'болезнь', '持續傷害；「瘟疫」狀態可免疫並反過來施加'),
                ('冰凍', 'заморозка', '定身；解除後結算「二次冰凍」傷害'),
                ('電擊', 'шок', '雷系裝備附加的負面狀態'),
                ('詛咒', 'проклятие', '普攻有機率落空'),
                ('虛弱', 'слабость', '降低目標輸出'),
                ('易傷', 'уязвимость', '提高目標受到的傷害')]:
    w('| %s | %s | %s |' % (a, b, c))
w()
w('所以像「+18%對非英雄單位非狀態傷害」這種寫法，指的是**只加成普攻與技能**，')
w('點燃／流血那類持續傷害不吃這條加成。反過來「+15%點燃傷害」只加成點燃。')
w()

# ---------------------------------------------------------------- classes
w('## 二、品質（類別）體系')
w()
w('| 中文 | 俄文原名 | 件數 | 說明 |')
w('|---|---|---:|---|')
import collections
cnt = collections.Counter(v['group'] for v in I.values())
ROWS = [
    ('普通 / 稀有 / 獨特 / 傳說', 'Обычный / Редкий / Уникальный / Легендарный',
     cnt['普通'] + cnt['稀有'] + cnt['獨特'] + cnt['傳說'],
     '基礎裝備四階，靠升級／強化／覺醒卷軸往上推'),
    ('特殊 lv.1 ~ lv.5', 'Особый (1–5 ур.)',
     sum(cnt['特殊（lv.%d）' % n] for n in range(1, 6)),
     '主要掉落與商店裝備，也是神器配方的素材'),
    ('特殊 lv.5+ / lv.5++', 'Особый (5+ / 5++ ур.)',
     cnt['特殊（lv.5+）'] + cnt['特殊（lv.5++）'], '高階特殊裝備，多為套裝件'),
    ('神器 lv.1 ~ lv.5', 'Артефакт (1–5 ур.)',
     sum(cnt['神器（lv.%d）' % n] for n in range(1, 6)), '合成表的主要產物'),
    ('強化', 'Усилитель', cnt['強化'], '各種卷軸與工具，用來升級／轉換其他裝備'),
    ('扭曲', 'Искаженный', cnt['扭曲'], '用扭曲卷軸從獨特裝備轉出，可反覆重骰（固定循環）'),
    ('任務物品 → 聖物 → 折射 → 完美',
     'Квестовый → Реликвия → Преломленный → Совершенный',
     cnt['任務物品（1/2）'] + cnt['任務物品（2/2）'] + cnt['聖物'] + cnt['折射'] + cnt['完美'],
     '地精商店任務裝備的專屬升級鏈'),
    ('附加 → 淬鍊', 'Дополнительный → Закаленный', cnt['附加'] + cnt['淬鍊'],
     '用淬火卷軸升級的輔助道具線'),
    ('寶石 / 耳環', 'Самоцвет / Серьги', cnt['寶石'] + cnt['耳環'],
     '寶石三合一 → 純淨寶石，兩顆純淨寶石 → 耳環（只能帶 1 件）'),
    ('儀式', 'Ритуальный', cnt['儀式'], ''),
    ('新年 / 復活節 / 萬聖節', 'Новогодний / Пасхальный / Хэллоуин',
     cnt['新年'] + cnt['復活節'] + cnt['萬聖節'], '節慶活動限定裝備'),
    ('符文 / 信使', 'Руна / Курьер', cnt['符文'] + cnt['信使'], ''),
    ('消耗品／掉落物', '—', cnt['消耗品／掉落物'], '藥水、金幣、屬性碎片、禮物盒、地基等'),
]
for a, b, c, d in ROWS:
    w('| %s | %s | %d | %s |' % (a, b, c, d))
w()
w('### 套裝（комплект）')
w()
w('部分「特殊」裝備屬於套裝，遊戲中輸入指令可查看套裝加成：')
w()
SETROW = [('c1', '英勇', 'Доблесть'), ('c2', '深淵', 'Бездна'),
          ('c3', '風暴', 'Шторм'), ('c4', '地獄', 'Адский'),
          ('c5', '軍團遺產', 'Наследие легиона')]
LEGION_IDS = set((D.get('legion') or {}).get('items') or [])
w('| 指令 | 套裝 | 俄文 | 件數 |')
w('|---|---|---|---:|')
for k, zh, ru in SETROW:
    n = (len(LEGION_IDS) if k == 'c5'
         else sum(1 for v in I.values() if k in (v['set'] or [])))
    w('| `-%s` | %s | %s | %d |' % (k, zh, ru, n))
w()
w('※ 三位一體（Триада）同時屬於英勇／深淵／風暴三個套裝。')
w('※ 英勇之錘、風暴之錘、吞噬萬物 各自算作「2 件」該套裝道具。')
w('※ `-c5` 軍團遺產另需「任一件『聖物』類道具」，且僅限「軍團特使」使用。')
w()
w('#### 套裝加成')
w()
w('地圖的物件資料裡查不到這些數值 —— 套裝效果寫在觸發腳本，匯出時抓不到。')
w('以下是玩家在遊戲內輸入 `-c1` ~ `-c5` 抄回來的，原始出處為俄文版。')
w()
for k, zh, ru in SETROW:
    b = SETB.get(k) or {}
    if not b.get('tiers'):
        continue
    only = (b.get('only') or {}).get('zh')
    w('**`-%s` %s**%s' % (k, zh, ('　（%s）' % only) if only else ''))
    w()
    w('| 件數 | 加成 |')
    w('|---:|---|')
    for r in b['tiers']:
        w('| %d | %s%s |' % (r['n'], r['zh'],
                             '　⚠ 原文辨識不確定' if r.get('q') else ''))
    w()

# ---------------------------------------------------------------- scrolls
w('## 三、強化道具與品質階梯')
w()
w('| 圖示 | 名稱 | 效果 |')
w('|:---:|---|---|')
for i in [v['id'] for v in I.values() if v['group'] == '強化']:
    w('| %s | **%s**<br><sub>%s</sub> | %s |' % (icon(i), link(i), I[i]['name_ru'], effs(i)))
w()
w('### 品質階梯（升級卷軸 → 強化卷軸 → 覺醒卷軸）')
w()
w('11 條掉落裝備線，各自從「普通」一路升到「傳說」。傳說裝備是多條神器配方的必要素材。')
w()
w('| 普通 | → 升級卷軸 → 稀有 | → 強化卷軸 → 獨特 | → 覺醒卷軸 → 傳說 |')
w('|---|---|---|---|')
for a, b, c, d in D['ladder']:
    w('| %s | %s | %s | %s |' % (inline(a), inline(b), inline(c), inline(d)))
w()

# ---------------------------------------------------------------- recipes
w('## 四、合成表（40 條）')
w()
w('資料來自 `synthesis.xlsx`；產物的屬性與能力已換成地圖檔的最新數值。')
w()
w('> **神器的持有限制**：每件神器只能合成一次。鐵匠雖然可以複製一件神器，')
w('> 但該能力全場只能用一次，而且同一件神器仍然無法重複配戴 ——')
w('> 所以一套配裝裡不會出現兩件相同的神器。（此規則由玩家提供，地圖資料未記錄。）')
w()
w('符號：`+` 材料相加、`=` 合成結果、`→` 完成任務後變成、`←` 對左邊的裝備使用右邊的卷軸。')
w()
w('| # | 合成路線 | 產物 | 產物屬性 |')
w('|---:|---|---|---|')
for n, r in enumerate(D['recipes'], 1):
    ids = [s['id'] for s in r['seq'] if s['kind'] == 'item']
    res = ids[-1]
    line = ' '.join(('`%s`' % s['op']) if s['kind'] == 'op' else inline(s['id'])
                    for s in r['seq'][:-1])
    w('| %d | %s | %s **%s**<br><sub>%s</sub> | %s |' %
      (n, line, icon(res), I[res]['name'], I[res]['cls'], cell(res)))
w()
w('> 第 17、20、29、30、33、34、38、39 條是把「卷軸階梯」整條展開，')
w('> 等同於「傳說裝備 ＋ 最後一張卷軸」。')
w()

# ---------------------------------------------------------------- cycle
w('## 五、扭曲裝備循環（29 件）')
w()
w('對「獨特」品質裝備使用 **扭曲卷軸** 會轉成一件扭曲裝備；')
w('對扭曲裝備再次使用扭曲卷軸則**按固定順序**換成下一件，走完一圈回到起點。')
w()
w('| 順序 | 圖示 | 裝備 | 屬性 | 能力 |')
w('|---:|:---:|---|---|---|')
for n, i in enumerate(D['cycle'], 1):
    w('| %d | %s | **%s**<br><sub>%s</sub> | %s | %s |' %
      (n, icon(i), link(i), I[i]['name_ru'], I[i]['stats'] or '—', effs(i) or '—'))
w()
w('> 第 29 件（爆裂十字弩）之後回到第 1 件（紅寶石權杖）。')
w()

# ---------------------------------------------------------------- refract
w('## 六、任務物品 → 聖物 → 折射 → 完美')
w()
w('地精商店的 4 件任務物品各自有一條專屬升級鏈：')
w()
w('```')
w('任務物品(1階) --完成任務--> 任務物品(2階) --完成任務--> 聖物')
w('                                                    │')
w('                          折射卷軸 ─────────────────┤')
w('                          （4 件循環，可重複重骰）    │')
w('                                                    │')
w('                          鐵匠技能 ─────────────────┘')
w('                          （產出完美裝備）')
w('```')
w()
w('**分岔點在聖物**：折射與完美是聖物的兩條分支，完美不是折射的下一階。')
w()
w('※「不穩定卷軸」有 50% 機率直接完成任務，失敗則摧毀該物品。')
w()
for q, q2, relic, group, perfect in D['refract']:
    w('### %s線' % I[q]['name'])
    w()
    w('| 階段 | 圖示 | 裝備 | 屬性 / 能力 |')
    w('|---|:---:|---|---|')
    for lab, i in [('任務物品 1 階', q), ('任務物品 2 階', q2), ('聖物', relic)]:
        w('| %s | %s | **%s**<br><sub>%s</sub> | %s |'
          % (lab, icon(i), link(i), I[i]['name_ru'], cell(i)))
    for n, i in enumerate(group, 1):
        w('| 折射 %d/4 | %s | **%s**<br><sub>%s</sub> | %s |'
          % (n, icon(i), link(i), I[i]['name_ru'], cell(i)))
    w('| **完美**<br><sub>聖物＋鐵匠技能</sub> | %s | **%s**<br><sub>%s</sub> | %s |'
      % (icon(perfect), link(perfect), I[perfect]['name_ru'], cell(perfect)))
    w()
w('> 「折射 → 完美」的對應由舊合成表流程圖 ＋ 品質分類推得，Wiki 與地圖物件資料都沒有記錄')
w('> 這段配方，建議以遊戲內實測為準。')
w()

# ---------------------------------------------------------------- gems
w('## 七、寶石與耳環')
w()
w('| 寶石 | ×3 → 純淨寶石 | ×2 → 耳環 | 耳環屬性 |')
w('|---|---|---|---|')
for a, b, c in D['gem']:
    w('| %s（%s） | %s（%s） | %s | **%s** |'
      % (inline(a), I[a]['stats'], inline(b), I[b]['stats'], inline(c), I[c]['stats']))
w()
w('- 3 顆相同寶石 ＋ **寶石轉化器** → 1 顆純淨寶石')
w('- 2 顆相同純淨寶石 ＋ **珠寶匠工具組** → 1 件耳環')
w('- **耳環類道具全身只能攜帶 1 件。**')
w()

# ---------------------------------------------------------------- wiki gaps
w('<a id="wikimiss"></a>')
w()
w('## 八、Wiki 未收錄的裝備')
w()
w('以下 6 件在地圖檔裡存在，但俄文 Wiki 沒有頁面：')
w()
w('| 圖示 | 名稱 | 品質 | 屬性 / 能力 |')
w('|:---:|---|---|---|')
for i in [v['id'] for v in I.values()
          if not v['in_wiki'] and v['group'] not in ('消耗品／掉落物', '符文', '信使')]:
    w('| %s | **%s**<br><sub>%s</sub> | %s | %s |'
      % (icon(i), link(i), I[i]['name_ru'], I[i]['cls'], cell(i)))
w()

# ---------------------------------------------------------------- full list
w('## 九、裝備一覽（%d 件）' % len(I))
w()
w('「別名」為舊合成表使用的中文名，與本文譯名並列方便對照。🛒 為商店販售。')
w()
groups = [g for g in D['order'] if any(v['group'] == g for v in I.values())]
w('**快速跳轉：** ' + ' · '.join('[%s](#g%d)' % (g, n) for n, g in enumerate(groups)))
w()
for n, g in enumerate(groups):
    ids = [v['id'] for v in I.values() if v['group'] == g]
    w('<a id="g%d"></a>' % n)
    w()
    w('### %s（%d 件）' % (g, len(ids)))
    w()
    w('| 圖示 | 名稱 | 品質 | 屬性 | 能力 | 配方 / 去向 |')
    w('|:---:|---|---|---|---|---|')
    for i in ids:
        it = I[i]
        name = '<a id="%s"></a>**%s**<br><sub>%s</sub>' % (i.lower(), it['name'], it['name_ru'])
        if it['name_old'] and it['name_old'] != it['name']:
            name += '<br><sub>別名：%s</sub>' % it['name_old']
        if it['shop']:
            name += '<br><sub>🛒 %s</sub>' % it['shop']
        rec = []
        if it['recipe']:
            rec.append('**配方：**' + ' + '.join(link(x) for x in it['recipe']))
        if it['used_in']:
            rec.append('**用於：**' + '、'.join(link(x) for x in it['used_in']))
        cls = it['cls'] + (('<br><sub>套裝 %s</sub>'
                           % '、'.join('`-%s`' % k for k in it['set']))
                          if it['set'] else '')
        w('| %s | %s | %s | %s | %s | %s |'
          % (icon(i), name, cls, it['stats'] or '—', effs(i) or '—',
             '<br>'.join(rec) or '—'))
    w()

# ---------------------------------------------------------------- files
w('## 十、檔案與圖片')
w()
w('```')
w('DarkSheep/')
w('├─ synthesis.xlsx            舊版中文合成表（合成路線來源）')
w('├─ images/                   %d 張裝備圖示，檔名 = 道具 ID' % NIMG)
w('├─ data/')
w('│   ├─ items_database.json   自地圖檔匯出的原始物件資料')
w('│   ├─ items_database.csv    同上，CSV 版')
w('│   ├─ icons/                自地圖檔匯出的 407 張 64×64 圖示')
w('│   └─ items.json            本文的合併資料（建站直接用這份）')
w('├─ tools/                    重建腳本')
w('└─ 裝備合成攻略.md            本文件')
w('```')
w()
w('**圖片：**')
w()
nomap = [v for v in I.values() if v['icon_src'] != 'map']
w('- `images/<道具ID>.png`，%d 張來自地圖檔（統一 64×64），%d 張來自舊 xlsx（尺寸不一）。'
  % (sum(1 for v in I.values() if v['icon_src'] == 'map'),
     sum(1 for v in I.values() if v['icon_src'] == 'xlsx')))
w('- 仍缺 **%d** 張，都是地圖直接沿用暴雪內建圖示（`ReplaceableTextures\\CommandButtons\\…`）'
  % sum(1 for v in I.values() if not v['image']))
w('  而沒有被匯出，可從 War3 本體的 `War3.mpq` / `war3.w3mod` 取得：')
w()
w('| 道具 | 內建圖示檔名 |')
w('|---|---|')
NEED = {'cnob': 'BTNThoriumArmor', 'ciri': 'BTNArcaniteArmor', 'stwa': 'BTNRunedBracers',
        'brag': 'BTNBlink', 'gobm': 'BTNOrcBattleStandard', 'rots': 'BTNMaskOfDeath',
        'uflg': 'BTNStaffOfNegation', 'btst': 'BTNHornOfCenarius', 'tlum': 'BTNHornOfDoom',
        'crdt': 'BTNTomeBrown', 'klmm': 'BTNGlove', 'lure': 'BTNRingSkull',
        'oli2': 'BTNTalisman', 'olig': 'BTNGatherGold', 'I00G': 'BTNPotionGreenSmall',
        'I00H': 'BTNPotionBlueSmall', 'I00J': 'BTNVialFull', 'I027': 'BTNAdvancedUnholyArmor',
        'I04D': 'BTNNecromancerAdept', 'I09G': 'BTNPodkova', 'I0AC': 'BTN3M3',
        'I00W': 'BTNImprovedBows', 'I014': 'BTNManaStone'}
for i, f in NEED.items():
    if i in I and not I[i]['image']:
        w('| %s<br><sub>%s</sub> | `%s.blp` |' % (I[i]['name'], I[i]['name_ru'], f))
w()
w('- 建站時建議統一用 `width:64px; height:64px; object-fit:cover;`，')
w('  舊 xlsx 的圖不是正方形。')
w()

path = os.path.join(ROOT, '裝備合成攻略.md')
open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('wrote', path, len(L), 'lines')
