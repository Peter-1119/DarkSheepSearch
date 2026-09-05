# -*- coding: utf-8 -*-
"""從 .w3x 地圖檔讀出可選英雄。

名單來源分兩層：
  1. Trig_HeroPick_Actions —— 選英雄時真正比對的清單，共 57 個，這是權威。
  2. RandomStr / RandomAgi / RandomInt —— 隨機英雄池，只有 53 個，
     但額外提供「主屬性」與「經驗值解鎖門檻」。
兩者相差的 4 個（占星師／超重型坦克／女武神／遠古九頭蛇）全是 T3+，
只能手動挑、不會被隨機抽到，所以不在隨機池裡 —— 只讀隨機池會漏掉它們。

技能也分兩種：
  uhab = 英雄技能（QWER，可升級）
  uabi = 固有技能（被動、專屬機制、「選擇天賦」的入口）

說明文字的欄位也有兩個：可學習技能寫在 arut，被動／固有技能寫在 aub1，
兩個都要試，否則會有 73 個技能抓不到文字。
"""
import re, sys, os, io, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpq import MPQ
import w3obj
from map_items import clean

ATTR = {'RandomStr': 'str', 'RandomAgi': 'agi', 'RandomInt': 'int'}

# 這些不是真的技能，不列出來：
#   AInv = 背包欄位
#   A03U = LHGlow，掛在英雄身上的光暈特效（base 是減速光環但數值 0，只有模型）
SKIP_ABIL = {'AInv', 'A03U'}

# 遊戲本體的原版技能名稱檔。地圖沒覆寫的技能，名稱在這裡面。
GAME_DIRS = [r'D:\Warcraft III', r'C:\Program Files (x86)\Warcraft III',
             r'C:\Program Files\Warcraft III']
GAME_MPQS = ['War3Patch.mpq', 'War3x.mpq', 'war3.mpq']
STOCK_FILES = ['Human', 'Orc', 'NightElf', 'Undead',
               'Neutral', 'Common', 'Item', 'Campaign']


def stock_names():
    """讀遊戲本體的原版技能名稱。沒裝遊戲就回空的，不影響其他流程。"""
    import os
    bs = chr(92)
    arcs = []
    for d in GAME_DIRS:
        if not os.path.isdir(d):
            continue
        for n in GAME_MPQS:
            p = os.path.join(d, n)
            if os.path.isfile(p):
                try:
                    arcs.append(MPQ(p))
                except Exception:
                    pass
        break
    out = {}
    for f in STOCK_FILES:
        d = None
        for a in arcs:
            try:
                d = a.read('Units' + bs + f + 'AbilityStrings.txt')
            except Exception:
                d = None
            if d:
                break
        if not d:
            continue
        try:
            txt = d.decode('utf-8-sig')
        except UnicodeDecodeError:
            txt = d.decode('cp950', 'replace')
        cur = None
        for line in txt.replace(chr(13), chr(10)).split(chr(10)):
            line = line.strip()
            m = re.match(r'^\[([A-Za-z0-9]{4})\]$', line)
            if m:
                cur = m.group(1)
                continue
            if cur and line.startswith('Name='):
                out.setdefault(cur, line[5:].strip().strip('"'))
    return out

# 英雄說明是半結構化的，有兩種格式：
#   A) Ранг силы / Потенциал поздней игры / Роль / Описание
#   B) Роль / Атака / Тип защиты / Особенности
PROFILE_LINE = {
    'tier': r'Ранг\s+силы\s*:\s*(.+)',
    'late': r'Потенциал\s+поздней\s+игры\s*:\s*(.+)',
    'role': r'Роль\s*:\s*(.+)',
    'atk':  r'Атака\s*:\s*(.+)',
    'def':  r'Тип\s+защиты\s*:\s*(.+)',
}
PROFILE_BLOCK = {
    'desc':  r'Описание\s*:\s*(.+?)(?=\n[А-ЯЁ][а-яёА-ЯЁ ]{2,30}\s*:|\Z)',
    'trait': r'Особенности\s*:\s*(.+?)(?=\n[А-ЯЁ][а-яёА-ЯЁ ]{2,30}\s*:|\Z)',
}


def _fn_body(lines, name):
    st = en = None
    for i, l in enumerate(lines):
        if l.startswith('function %s ' % name):
            st = i
        elif st is not None and l.startswith('endfunction'):
            en = i
            break
    return lines[st:en] if st is not None else []


def pick_list(jass):
    """Trig_HeroPick_Actions 比對過的英雄 = 可選名單（權威）。"""
    out = []
    for l in _fn_body(jass.split('\n'), 'Trig_HeroPick_Actions'):
        for u in re.findall(r"GetUnitTypeId\(u\)=='(.{4})'", l):
            if u not in out:
                out.append(u)
    return out


def roster(jass):
    """隨機英雄池，回傳 {英雄ID: (主屬性, 解鎖經驗)}。"""
    lines = jass.split('\n')
    out = {}
    for fn, attr in list(ATTR.items()) + [('RandomAll', None)]:
        thr = 0
        for l in _fn_body(lines, fn):
            m = re.match(r'if ExpGo\[n\]>=(\d+) then', l.strip())
            if m:
                thr = int(m.group(1))
                continue
            m = re.match(r"set RH\[\d+\]='(.{4})'", l.strip())
            if m:
                uid = m.group(1)
                if uid not in out or (attr and out[uid][0] is None):
                    out[uid] = (attr, thr if uid not in out else out[uid][1])
    return out


# 玩家投稿的英雄會在說明結尾署名，抽出來單獨顯示，不要混在敘述裡
MADEBY = re.compile(r'\s*Made\s+by\s+(\S+)\s*$', re.I)


def parse_profile(txt):
    out = {}
    m = MADEBY.search(txt)
    if m:
        out['author'] = m.group(1)
        txt = MADEBY.sub('', txt)
    for k, pat in PROFILE_LINE.items():
        m = re.search(pat, txt)
        if m and m.group(1).strip():
            out[k] = m.group(1).strip()
    for k, pat in PROFILE_BLOCK.items():
        m = re.search(pat, txt, re.S)
        if m and m.group(1).strip():
            out[k] = m.group(1).strip()
    return out


def _first(v):
    """有多個等級的技能，欄位會是 list（每級一段文字），取第一段。"""
    return v[0] if isinstance(v, list) else v


def account_locks(jass):
    """帳號鎖定的英雄。

    單位的 ureq 欄位寫著要哪個科技，而那些科技只在 Trig_NewInit_Actions 裡
    對特定的玩家名稱 SetPlayerTechResearched。絕大多數英雄用的是共通的 R00I
    （＝一般解鎖），只有兩個科技綁了帳號名單。

    回傳 {科技ID: [帳號名, …]}。
    """
    out = {}
    for names, tech in re.findall(
            r'if ((?:name=="[^"]+"(?: or )?)+)\s*then\s+'
            r'call SetPlayerTechResearched\(pl,\'(.{4})\',1\)', jass):
        out.setdefault(tech, []).extend(re.findall(r'"([^"]+)"', names))
    return out


def _base_modified(U, base):
    """基礎物件本身有沒有被地圖改過。

    魔獸的自訂單位（w3u 第二張表）是從**原版**物件繼承的，不是從地圖對同一個
    原始物件做的改動繼承。所以 base 若出現在第一張表（＝地圖改過原始物件），
    它的欄位就不能拿來當自訂單位的預設值。

    這裡有兩隻會踩到：N01K 的 base 是 Ntin，而地圖把 Ntin 改成了儀式師的皮膚
    「Воитель глубин」；H00Z 的 base 是 Hpb2，被改成蠻族戰士的皮膚「Злой Санта」。
    照舊的寫法，N01K 會被標成別人皮膚的名字，敏捷與三個成長值也是那個皮膚的。
    """
    return base in U and not U[base].get('_base')


def _stat(U, uid, base, field):
    v = U.get(uid, {}).get(field)
    if v is None and not _base_modified(U, base):
        v = U.get(base, {}).get(field)
    return v


def _primary(st, fallback):
    """隨機池沒收錄的英雄，用「每級成長最高」判主屬性。

    地圖的 upra 欄位不可靠（軍團特使標 INT，實際卻在力量池），所以不採用。
    """
    if fallback:
        return fallback
    g = {k: (st.get(k + '_lv') or 0) for k in ('str', 'agi', 'int')}
    return max(g, key=lambda k: g[k]) if any(g.values()) else 'int'


# 技能 ID 也被混入了西里爾同形字（例如釀酒師的天賦寫成 'А0НК'，
# А 和 Н 是西里爾字母），不還原就查不到那個技能。
ID_HOMO = str.maketrans({
    'А': 'A', 'В': 'B', 'С': 'C', 'Е': 'E', 'Н': 'H', 'К': 'K', 'М': 'M',
    'О': 'O', 'Р': 'P', 'Т': 'T', 'Х': 'X',
    'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x',
})


# 「[Уровень %d]」等級標記與結尾的快捷鍵「(Q)」，從提示文字取名時要去掉
_LVLTAG = re.compile(r'\s*\[[^\]]*\]\s*')
_HOTKEY = re.compile(r'\s*\([^)]{1,4}\)\s*$')


def _abil_name(a):
    """技能名稱。

    大多數技能寫在 anam，但有 18 個技能（含拜火者的 Q「火柱」）沒有 anam，
    名稱改寫在 aret / atp1 這兩個提示欄位裡。只看 anam 會把它們整個漏掉，
    英雄就會少一招。
    """
    nm = clean(_first(a.get('anam')) or '')
    if nm:
        return nm
    for k in ('aret', 'atp1'):
        t = clean(_first(a.get(k)) or '')
        if t:
            t = _HOTKEY.sub('', _LVLTAG.sub(' ', t)).strip()
            # 提示文字有時是「名稱, 說明…」的形式，只取名稱那一段
            return t.split(',')[0].strip(' ,.-')
    return ''


# 說明裡「標籤：數值」的行
_LABLINE = re.compile(r'^([^:：\n]{1,40})\s*[:：]\s*(.+)$')


def _levels(a):
    """抽出隨等級變動的數值。

    aub1 本身就是每級一段完整說明，所以不必自己算成長公式 ——
    直接比對各級同一行的數值，只留會變的那幾行。
    回傳 [{'i': 行號, 'v': [各級數值]}]，行號對應說明文字的第幾行，
    網站再用該行的標籤（已翻譯）當表頭。
    """
    v = a.get('aub1')
    if not isinstance(v, list):
        return None
    # aub1 的段數不一定等於技能等級數 —— 有些技能（例如惡魔獵手的「著魔」，
    # alev = 1）後面還留著改造前那個技能的舊說明。多出來的不是等級，要切掉。
    lv = _first(a.get('alev'))
    if isinstance(lv, int) and lv >= 1:
        v = v[:lv]
    if len(v) < 2:
        return None
    texts = [clean(x) for x in v]
    if len([t for t in texts if t]) < 2 or len(set(texts)) <= 1:
        return None
    base = texts[0].split('\n')
    rows = []
    for li, line in enumerate(base):
        m = _LABLINE.match(line.strip())
        if not m:
            continue
        vals = []
        for t in texts:
            ls = t.split('\n')
            mm = _LABLINE.match(ls[li].strip()) if li < len(ls) else None
            vals.append(mm.group(2).strip() if mm else None)
        if None in vals or len(set(vals)) <= 1:   # 缺行或各級相同 -> 不列
            continue
        # 各級數值多半只有開頭的數字在變，公式的其餘部分（含俄文單位）
        # 完全相同。把共同的前後綴切掉，表格裡就只剩會變的那一段。
        rows.append({'i': li, 'v': _trim_common(vals)})
    return rows or None


def _trim_common(vals):
    """去掉各級數值的共同前綴與後綴，只留下真正變動的部分。

    切點不能落在數字中間 —— 40 / 60 / 80 / 100 / 120 的結尾都是 0，
    直接比對會把那個 0 當成共同後綴切掉，變成 4 / 6 / 8 / 10 / 12。
    """
    n = min(len(v) for v in vals)
    pre = 0
    while pre < n and len({v[pre] for v in vals}) == 1:
        pre += 1
    # 前綴結尾若卡在數字中間（前一個字和下一個字都是數字），往回退
    while pre > 0 and vals[0][pre - 1].isdigit() and any(
            len(v) > pre and v[pre].isdigit() for v in vals):
        pre -= 1

    suf = 0
    while suf < n - pre and len({v[len(v) - 1 - suf] for v in vals}) == 1:
        suf += 1
    while suf > 0 and all(v[len(v) - suf].isdigit() for v in vals) and any(
            v[len(v) - suf - 1].isdigit() for v in vals):
        suf -= 1

    out = [v[pre:len(v) - suf] if suf else v[pre:] for v in vals]
    # 切完變空或全都一樣就放棄，寧可顯示完整字串
    if not all(o.strip() for o in out) or len(set(out)) <= 1:
        return vals
    return out


def _abil(A, aid, kind, depth=0, stock=None):
    a = A.get(aid, {})
    nm = _abil_name(a)
    if not nm and stock:                    # 最後才問遊戲本體的原版名稱
        nm = stock.get(a.get('_base') or aid, '') or stock.get(aid, '')
    rec = {
        'id': aid,
        'kind': kind,                       # 'hero' = QWER；'innate' = 固有
        'name_ru': nm,
        # aub1（一般提示）優先，arut（學習提示）只當備援。
        # 原因：很多技能沒有自訂 arut，那裡殘留著預設的擊退說明 —— 70 個技能
        # 因此拿到同一段不相干的文字。aub1 則是遊戲裡實際會顯示的那一段。
        'text_ru': clean(_first(a.get('aub1')) or '') or clean(_first(a.get('arut')) or ''),
        'icon': (_first(a.get('aart')) or _first(a.get('arar')) or '').strip(),
        'hotkey': (_first(a.get('ahky')) or '').strip(),
        'levels': _first(a.get('alev')),
        'perlv': _levels(a),          # 隨等級變動的數值
    }
    # 技能書（Aspb）—— 「選擇天賦」「選擇技能」「額外技能」都是這種。
    # 真正的選項清單在 spb1，每個英雄可選的天賦都不一樣。
    if a.get('_base') == 'Aspb' and depth == 0:
        ids = [x.strip().translate(ID_HOMO)
               for x in str(_first(a.get('spb1')) or '').split(',') if x.strip()]
        opts = [_abil(A, i, 'opt', depth + 1, stock) for i in ids if i in A]
        if opts:
            rec['opts'] = opts
    return rec


def skins(jass, U):
    """英雄皮膚。

    RegisterSkin(玩家, 啟用技能, 皮膚單位, 預設開關) 註冊了 41 種皮膚，
    但那裡沒說皮膚屬於哪個英雄。真正的對應在 Trig_HeroPick_Actions：
    選到某個英雄時，若該皮膚已啟用就 ReplaceUnitBJ 換掉單位。
    """
    default = {}
    for sk, hid, st in re.findall(
            r"""RegisterSkin\([^,]+,'(.{4})','(.{4})',"(\w+)"\)""", jass):
        default[hid] = st
    lines = jass.split('\n')
    body = _fn_body(lines, 'Trig_HeroPick_Actions')
    out, cur = {}, None
    for l in body:
        t = l.strip()
        m = re.search(r"GetUnitTypeId\(u\)=='(.{4})'", t)
        if m:
            cur = m.group(1)
        m = re.search(r"ReplaceUnitBJ\(u,'(.{4})'", t)
        if m and cur:
            sid = m.group(1)
            out.setdefault(cur, []).append({
                'id': sid,
                'name_ru': clean(U.get(sid, {}).get('unam') or '') or sid,
                # 預設關閉的多半是稀有／限定，介面上要標出來
                'on': default.get(sid, 'on') != 'off',
                # 皮膚不是只換外觀 —— 41 個裡有 25 個的英雄技能跟本體不一樣，
                # 換皮膚等於換掉一部分技能。這裡先原樣記下，load() 再跟本體比對。
                'hab': [a.strip() for a in
                        str(U.get(sid, {}).get('uhab') or '').split(',')
                        if a.strip()],
            })
    return out


def load(map_path, jass_text=None):
    m = MPQ(map_path)
    if jass_text is None:
        jass_text = m.read('war3map.j').decode('utf-8', 'replace')
    U = w3obj.parse(m.read('war3map.w3u'))
    A = w3obj.parse(m.read('war3map.w3a'), True)

    stock = stock_names()                    # 原版技能名稱（沒裝遊戲就是空的）
    skn = skins(jass_text, U)                # 英雄皮膚
    locks = account_locks(jass_text)         # 綁帳號名的解鎖科技
    pool = roster(jass_text)                 # 主屬性與解鎖門檻
    picks = pick_list(jass_text)             # 權威名單
    for uid in pool:                         # 理論上是子集，保險起見補齊
        if uid not in picks:
            picks.append(uid)

    bs = chr(92)
    icons = dict(re.findall("SaveStr" + re.escape("(hash,1,'") + '(.{4})' +
                            re.escape("',") + '"((?:[^"' + bs + bs + ']|' +
                            bs + bs + '.)*)"' + re.escape(")"), jass_text))

    out = {}
    for uid in picks:
        u = U.get(uid, {})
        base = u.get('_base', '')
        name = clean(u.get('unam') or (
            '' if _base_modified(U, base) else U.get(base, {}).get('unam')) or '')
        txt = clean(u.get('utub') or '')
        attr, unlock = pool.get(uid, (None, None))

        abils = []
        for aid in str(u.get('uhab') or '').split(','):
            if aid.strip() and aid.strip() not in SKIP_ABIL:
                abils.append(_abil(A, aid.strip(), 'hero', stock=stock))
        for aid in str(u.get('uabi') or '').split(','):
            aid = aid.strip()
            if aid and aid not in SKIP_ABIL:
                abils.append(_abil(A, aid, 'innate', stock=stock))

        st = {k: _stat(U, uid, base, f) for k, f in (
            ('str', 'ustr'), ('str_lv', 'ustp'),
            ('agi', 'uagi'), ('agi_lv', 'uagp'),
            ('int', 'uint'), ('int_lv', 'uinp'),
            ('speed', 'umvs'))}

        # 皮膚的技能差異。base_hab 是本體的英雄技能，順序有意義（QWER）。
        base_hab = [a.strip() for a in str(u.get('uhab') or '').split(',')
                    if a.strip() and a.strip() not in SKIP_ABIL]
        sk_out = []
        for k in skn.get(uid, []):
            hab = [a for a in k.get('hab', []) if a not in SKIP_ABIL]
            add = [a for a in hab if a not in base_hab]
            rm = [a for a in base_hab if a not in hab]
            sk_out.append({
                'id': k['id'],
                'name_ru': k['name_ru'],
                'on': k['on'],
                # add 與 rm 成對出現時就是「替換」，介面上並排顯示比較好懂
                'add': [_abil(A, a, 'hero', stock=stock) for a in add],
                'rm': [_abil(A, a, 'hero', stock=stock) for a in rm],
            })

        out[uid] = {
            'id': uid,
            'name_ru': name,
            'proper_ru': clean(u.get('upro') or '').split(',')[0],
            'attr': _primary(st, attr),
            'unlock': unlock or 0,
            # 隨機池裡沒有 = 只能手動挑，介面上要標出來
            'random': uid in pool,
            # 綁帳號名的英雄（占星師、遠古九頭蛇）一般玩家根本拿不到，要標出來
            'lock': locks.get(str(_first(u.get('ureq')) or '').strip()),
            'icon': (icons.get(uid) or u.get('uico') or '').replace(bs + bs, bs),
            'stats': st,
            'skins': sk_out,
            'profile_ru': parse_profile(txt),
            'text_ru': txt,
            'abilities': abils,
        }
    return out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    import collections
    h = load(sys.argv[1])
    print('可選英雄 %d 個（其中 %d 個不在隨機池，只能手動挑）' %
          (len(h), sum(1 for v in h.values() if not v['random'])))
    print('主屬性:', dict(collections.Counter(v['attr'] for v in h.values())))
    print('有強度等級:', sum(1 for v in h.values() if 'tier' in v['profile_ru']))
    ab = [a for v in h.values() for a in v['abilities']]
    print('技能 %d 個（英雄技能 %d ／ 固有 %d），不重複 %d 個' % (
        len(ab), sum(1 for a in ab if a['kind'] == 'hero'),
        sum(1 for a in ab if a['kind'] == 'innate'),
        len({a['id'] for a in ab})))
    print('有說明文字的不重複技能:',
          len({a['id'] for a in ab if a['text_ru']}))
    print()
    for uid in ['Nbrn', 'Ekee', 'Nsjs', 'H03I']:
        v = h[uid]
        print('  %-6s %-22s %s %s' % (uid, v['name_ru'][:22], v['attr'],
                                      v['profile_ru'].get('tier', '')))
