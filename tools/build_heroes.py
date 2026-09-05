# -*- coding: utf-8 -*-
"""產生 data/heroes.json：英雄資料 + 與裝備的連結。

資料全部來自 UD_v3.81 地圖本體：
  單位/技能定義 -> war3map.w3u / war3map.w3a
  可選名單、主屬性、解鎖門檻 -> war3map.j 的 Random* 函式
  「這個英雄的技能吃不吃裝備技能威力」-> 直接看該技能的 JASS 有沒有讀 real key 18

連結的作法：從技能文字掃出機制關鍵字，對應到網站既有的屬性代碼，
讓英雄頁可以直接跳到「這個英雄該找的裝備」。
"""
import os, re, sys, json, io

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import map_heroes
from mpq import MPQ

MAP = sys.argv[1] if len(sys.argv) > 1 else json.load(
    io.open(os.path.join(HERE, 'version.json'), encoding='utf-8')).get('map_file')

# 技能文字裡的機制關鍵字 -> (網站屬性代碼, 狀態代碼)
# 屬性代碼取自 stat_values.META，狀態代碼取自 status.json。
MECH = [
    ('sp',     None,     r'сил[аыу] умений'),
    ('mod',    None,     r'сил[аыу] модификатор'),
    ('as',     None,     r'скорост[ьи] атаки'),
    ('armor',  None,     r'\bброн|защит[аыу]\b'),
    ('hp',     None,     r'запас[а]? здоровья|ед\. здоровья'),
    ('mp',     None,     r'\bман[аыу]\b|ед\. маны'),
    ('pen',    None,     r'пробити'),
    ('thorn',  None,     r'ответн\w+ урон'),
    ('vamp',   None,     r'вампириз'),
    ('dburn',  'burn',   r'поджог|подожж'),
    ('dbleed', 'bleed',  r'кровотеч'),
    ('ddise',  'disease', r'болезн|заболе'),
    (None,     'flam',   r'горюч'),
    (None,     'freeze', r'заморозк|заморож'),
    (None,     'shock',  r'\bшок\b|шоком|шока'),
    (None,     'curse',  r'проклят'),
    (None,     'weak',   r'слабост'),
    (None,     'vuln',   r'уязвим'),
]


def mechanics(hero):
    """回傳 (屬性代碼集合, 狀態代碼集合)。"""
    txt = ' '.join(a['name_ru'] + ' ' + a['text_ru']
                   for a in hero['abilities']).lower()
    stats, sts = [], []
    for code, st, pat in MECH:
        if re.search(pat, txt):
            if code and code not in stats:
                stats.append(code)
            if st and st not in sts:
                sts.append(st)
    return stats, sts


def scaling(heroes, jass):
    """哪些英雄的技能真的吃裝備技能威力 / 技能強度（讀原始碼判斷）。

    早期版本是「函式級」判定 —— 技能 ID 只要出現在任何有讀
    udg_ItemBonusDMG／hash key 18 的函式裡就算數。那太寬鬆：
    Trig_HeroPick_Actions 幾乎提到每一個技能，Trig_i_Actions（-i 指令）
    更是把所有屬性印一遍，害 32 個標記裡有一半是誤判。

    現在改成三件事：
      1. 分支級 —— 技能若出現在 if/elseif 的條件式裡（技能分派的標準寫法），
         範圍就只算那個分支，不是整個函式。
      2. 跟著呼叫走 —— 分支裡寫 TimerStart(...,function Hero49R) 的話，
         Hero49R 用到的東西也算，因為技能常把傷害丟給計時器回呼。
      3. 忽略純顯示 —— DisplayTimedTextToPlayer 那行提到的技能不算使用。
      4. 忽略排除條件 —— GetSpellAbilityId()!='A03V' 是「這個技能不走這裡」，
         不是使用。轉移據點被 14 個處理器排除，不修的話每隻英雄都會中。
      5. 條件接動作 —— 魔獸的觸發器拆成 Foo_Conditions / Foo_Actions 兩半，
         技能 ID 只出現在前者，傷害寫在後者（例如烈焰旋風 A03O）。

    最後再跟技能說明文字取聯集：說明明講「сила умений」的就算，
    程式碼那邊還是有 8 個抓不到（傷害寫在追不到的輔助函式裡）。
    技能書本身不標記 —— 該標的是書裡的個別天賦。
    """
    lines = jass.split('\n')
    n = len(lines)
    strip = [l.strip() for l in lines]

    # --- 切函式（JASS 的函式在檔案裡是連續的，記起訖行號就好） --------
    fn, fspan, cur, start = [], {}, '?', 0
    for i, l in enumerate(lines):
        m = re.match(r'function ([A-Za-z0-9_]+) ', l)
        if m:
            fspan[cur] = (start, i)
            cur, start = m.group(1), i
        fn.append(cur)
    fspan[cur] = (start, n)

    # --- 每行的分支路徑（同一函式內 if/elseif/else 的巢狀編號） --------
    IFLINE = re.compile(r'(else)?if\b.*\bthen$')
    path, stack, seq, prev = [], [], 0, None
    for i, t in enumerate(strip):
        if fn[i] != prev:
            stack, prev = [], fn[i]
        if IFLINE.match(t):
            if t.startswith('elseif') and stack:
                stack.pop()
            seq += 1
            stack.append(seq)
        elif t == 'else':
            if stack:
                stack.pop()
            seq += 1
            stack.append(seq)
        path.append(tuple(stack))          # if 那行本身就屬於自己的分支
        if t == 'endif' and stack:
            stack.pop()

    # --- 直接用到的行 --------------------------------------------------
    KEY18 = re.compile(r'LoadReal\(hash,[A-Za-z_0-9()]+,18\)')
    # 「SaveReal(…,18, LoadReal(…,18)+x)」是把裝備技能威力**加給**單位，
    # 不是拿它來放大傷害。67 處讀取裡有 30 處是這種，不排掉的話
    # 惡魔獵手的「著魔」（它其實是 +40% 的來源）會被標成「吃裝備技能威力」。
    KEY18_SET = re.compile(
        r'SaveReal\(hash,[A-Za-z_0-9()]+,18,\s*LoadReal\(hash,[A-Za-z_0-9()]+,18\)')
    CALLED = re.compile(r'\b(?:function|call) ([A-Za-z0-9_]+)')
    dmod = [bool(KEY18.search(l)) and not KEY18_SET.search(l) for l in lines]
    dgive = [bool(KEY18_SET.search(l)) for l in lines]      # 反過來：授予裝備技能威力
    dsp = ['udg_ItemBonusDMG' in l for l in lines]
    # 每行提到的其他函式（排除函式定義那行）
    ref = [() if l.startswith('function ') else tuple(CALLED.findall(l))
           for l in strip]

    fmod = {fn[i] for i in range(n) if dmod[i]}
    fsp = {fn[i] for i in range(n) if dsp[i]}
    fgive = {fn[i] for i in range(n) if dgive[i]}

    # --- 呼叫關係的傳遞閉包 -------------------------------------------
    calls = {}
    for i in range(n):
        if ref[i]:
            calls.setdefault(fn[i], set()).update(ref[i])
    while True:
        gm = fmod | {f for f, c in calls.items() if c & fmod}
        gs = fsp | {f for f, c in calls.items() if c & fsp}
        gg = fgive | {f for f, c in calls.items() if c & fgive}
        if gm == fmod and gs == fsp and gg == fgive:
            break
        fmod, fsp, fgive = gm, gs, gg

    def uses(lo, hi, direct, reach):
        for i in range(lo, hi):
            if direct[i] or (ref[i] and reach & set(ref[i])):
                return True
        return False

    # --- 每個技能的有效範圍（可能有多處，取聯集） ----------------------
    ABIL = re.compile(r"'(A[A-Za-z0-9]{3})'")
    NEG = re.compile(r"!=\s*'(A[A-Za-z0-9]{3})'")
    spans = {}
    for i, l in enumerate(lines):
        if 'DisplayTimedTextToPlayer' in l:
            continue
        skip = set(NEG.findall(l))
        ids = [a for a in ABIL.findall(l) if a not in skip]
        if not ids:
            continue
        if path[i]:
            # 在某個 if/elseif 分支裡 -> 只算最內層那個分支。
            # 技能分派（if Skill=='A0OA' then）與 hero pick 裡的
            # UnitAddAbility 都適用：分支在檔案裡是連續的，往前後掃即可。
            p = path[i]
            lo = i
            while lo > 0 and fn[lo - 1] == fn[i] and path[lo - 1][:len(p)] == p:
                lo -= 1
            hi = i + 1
            while hi < n and fn[hi] == fn[i] and path[hi][:len(p)] == p:
                hi += 1
        else:
            lo, hi = fspan[fn[i]]
        rngs = [(lo, hi)]
        if fn[i].endswith('_Conditions'):
            act = fn[i][:-11] + '_Actions'
            if act in fspan:
                rngs.append(fspan[act])
        for a in ids:
            spans.setdefault(a, []).extend(rngs)

    SAYS_SP = re.compile(r'сил[аыу]\s+умений', re.I)
    SAYS_MOD = re.compile(r'сил[аыу]\s+модификатор', re.I)

    out = {}
    for uid, h in heroes.items():
        mod, sp, give = [], [], []
        for a in h['abilities']:
            if a.get('opts'):                     # 技能書本身不標
                continue
            txt = a.get('text_ru') or ''
            m = bool(SAYS_MOD.search(txt))
            p = bool(SAYS_SP.search(txt))
            g = False
            for lo, hi in spans.get(a['id'], ()):
                m = m or uses(lo, hi, dmod, fmod)
                p = p or uses(lo, hi, dsp, fsp)
                g = g or uses(lo, hi, dgive, fgive)
                if m and p and g:
                    break
            if m:
                mod.append(a['id'])
            if p:
                sp.append(a['id'])
            # 只在「不是消費者」時才標成來源，避免同一個技能掛兩個標記
            if g and not m:
                give.append(a['id'])
        out[uid] = {'mod': mod, 'sp': sp, 'give': give}
    return out


def main():
    tr = json.load(io.open(os.path.join(HERE, 'heroes_zh.json'), encoding='utf-8'))
    AB = json.load(io.open(os.path.join(HERE, 'abilities_zh.json'),
                           encoding='utf-8'))['names']
    # 技能說明的翻譯（技能ID -> [中文, 英文]）；沒翻到的就三語都放俄文原文
    _tp = os.path.join(HERE, 'abilities_text_zh.json')
    TXT = json.load(io.open(_tp, encoding='utf-8'))['text']           if os.path.isfile(_tp) else {}
    # 天賦／技能書選項的翻譯（技能ID -> {n:[zh,en], t:[zh,en]}）
    # 英雄專屬配裝（綁定英雄，往往也綁定天賦）
    _bp = os.path.join(HERE, 'hero_builds.json')
    HB = json.load(io.open(_bp, encoding='utf-8'))['builds']          if os.path.isfile(_bp) else {}
    _lp = os.path.join(HERE, 'talents_zh.json')
    TAL = json.load(io.open(_lp, encoding='utf-8'))['talents']           if os.path.isfile(_lp) else {}

    def tri_name(a):
        """技能名稱三語。天賦另有自己的翻譯表，優先採用。"""
        if a['id'] in TAL:
            return TAL[a['id']]['n'] + [a['name_ru']]
        if a['name_ru'] in AB:
            return AB[a['name_ru']] + [a['name_ru']]
        return [a['name_ru']] * 3

    def tri_text(a):
        if a['id'] in TAL:
            return TAL[a['id']]['t'] + [a['text_ru']]
        if a['id'] in TXT:
            return TXT[a['id']] + [a['text_ru']]
        return [a['text_ru']] * 3

    def skin_ab(a):
        """皮膚換上／換掉的技能，欄位跟一般技能一致，網站可以共用同一個元件。"""
        return {
            'id': a['id'],
            'n': tri_name(a),
            't': tri_text(a),
            'icon': 'images/heroes/a_%s.png' % a['id'],
            **({'lvt': a['perlv']} if a.get('perlv') else {}),
        }
    H = map_heroes.load(MAP)
    jass = MPQ(MAP).read('war3map.j').decode('utf-8', 'replace')
    scale = scaling(H, jass)

    V = tr['vocab']
    names, descs = tr['names'], tr['desc']
    SKIN = tr.get('skins', {})
    out = []
    for uid in sorted(H, key=lambda k: (H[k]['attr'] or 'zz', H[k]['unlock'] or 0,
                                        names.get(k, [''])[0])):
        h = H[uid]
        p = h['profile_ru']
        stats, sts = mechanics(h)
        nm = names.get(uid)
        if not nm:
            nm = [h['name_ru'], h['name_ru']]
        roles = [r.strip() for r in (p.get('role') or '').split(',') if r.strip()]

        def tri(table, key, fallback=None):
            v = table.get(key)
            return [v[0], v[1], key] if v else [fallback or key] * 3

        rec = {
            'id': uid,
            # 地圖沒覆寫名稱的英雄（Emoo）俄文是空的，改用手動表的第三個元素
            'n': [nm[0], nm[1],
                  h['name_ru'] or (nm[2] if len(nm) > 2 else nm[1])],
            'attr': h['attr'] or 'int',      # 只有樹人長者沒被列進三個屬性池
            'unlock': h['unlock'] or 0,
            'random': h['random'],           # False = 不在隨機池，只能手動挑
            # 背包格數：3 隻英雄只有 4 格（幽魂之狼／烈焰領主／機械戰體）
            'slots': h['slots'],
            # 綁帳號名的英雄：ureq 指向的科技只發給名單內的玩家名稱，
            # 其他人選不到（占星師 6 個帳號、遠古九頭蛇 3 個）
            **({'lock': h['lock']} if h.get('lock') else {}),
            'builds': HB.get(uid, []),
            # 皮膚不只換外觀：41 個裡有 25 個會換掉一部分英雄技能。
            # add/rm 成對時就是替換，網站上並排顯示「本體 -> 皮膚」。
            'skins': [{'id': k['id'], 'on': k['on'],
                       'n': (SKIN[k['name_ru']] + [k['name_ru']])
                            if k['name_ru'] in SKIN else [k['name_ru']] * 3,
                       **({'add': [skin_ab(a) for a in k['add']]} if k['add'] else {}),
                       **({'rm': [skin_ab(a) for a in k['rm']]} if k['rm'] else {}),
                       } for k in h['skins']],
            'author': p.get('author'),       # 玩家投稿英雄的作者
            'icon': 'images/heroes/h_%s.png' % uid,
            'proper': h['proper_ru'],
            'st': h['stats'],
            'roles': [tri(V['role'], r) for r in roles],
            'sc': [stats, sts],              # 連到裝備用的
            'mod': scale[uid]['mod'],        # 吃裝備技能威力的技能
            # 反過來：會「給」裝備技能威力的技能（例如惡魔獵手的著魔）
            **({'give': scale[uid]['give']} if scale[uid]['give'] else {}),
            # 反過來：會「給」裝備技能威力的技能（例如惡魔獵手的著魔）
            **({'give': scale[uid]['give']} if scale[uid]['give'] else {}),
            'sp': scale[uid]['sp'],          # 吃技能強度的技能
            # kind: 'hero' = QWER 可升級技能；'innate' = 固有技能（被動／專屬機制／天賦入口）
            'ab': [{
                'id': a['id'],
                'kind': a['kind'],
                'n': tri_name(a),
                'k': a['hotkey'],
                'lv': a['levels'],
                # 說明三語；未翻譯的用俄文原文墊著
                't': tri_text(a),
                'icon': 'images/heroes/a_%s.png' % a['id'],
                **({'lvt': a['perlv']} if a.get('perlv') else {}),
                # 技能書的選項（每個英雄可選的天賦都不一樣）
                **({'opts': [{
                    'id': o['id'],
                    'n': tri_name(o),
                    't': tri_text(o),
                    'icon': 'images/heroes/a_%s.png' % o['id'],
                    **({'lvt': o['perlv']} if o.get('perlv') else {}),
                } for o in a['opts']]} if a.get('opts') else {}),
            } for a in h['abilities'] if a['name_ru']],
        }
        if p.get('tier'):
            rec['tier'] = tri(V['tier'], p['tier'])
        if p.get('late'):
            rec['late'] = tri(V['late'], p['late'])
        d = descs.get(uid)
        rec['d'] = [d[0], d[1], p.get('desc') or p.get('trait') or ''] if d else \
                   [p.get('desc') or '', p.get('desc') or '', p.get('desc') or '']
        out.append(rec)

    have = sum(1 for r in out
               if os.path.isfile(os.path.join(ROOT, r['icon'])))
    path = os.path.join(ROOT, 'data', 'heroes.json')
    json.dump({'heroes': out}, io.open(path, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('英雄 %d 個 -> %s (%d KB)' % (len(out), path,
                                        os.path.getsize(path) // 1024))
    print('  有圖示 %d ／ 有強度等級 %d ／ 有中文名 %d' % (
        have, sum(1 for r in out if 'tier' in r),
        sum(1 for r in out if r['id'] in names)))
    untr = sorted({a['n'][2] for r in out for a in r['ab'] if a['n'][0] == a['n'][2]})
    if untr:
        print('  技能名稱未翻譯：%d 個 %s' % (len(untr), untr[:6]))
    ab = [a for r in out for a in r['ab']]
    print('  技能 %d 個（英雄技能 %d ／ 固有 %d），吃裝備技能威力的英雄 %d 個' % (
        len(ab), sum(1 for a in ab if a['kind'] == 'hero'),
        sum(1 for a in ab if a['kind'] == 'innate'),
        sum(1 for r in out if r['mod'])))
    print('  只能手動挑的英雄 %d 個；玩家投稿 %d 個' % (
        sum(1 for r in out if not r['random']),
        sum(1 for r in out if r.get('author'))))
    notxt = sum(1 for a in ab if not a['t'][2])
    opts = [o for a in ab for o in a.get('opts', [])]
    print('  技能書 %d 個，內含天賦／選項 %d 個（不重複 %d 個）' % (
        sum(1 for a in ab if a.get('opts')), len(opts), len({o['id'] for o in opts})))
    hb = [b for r in out for b in r['builds']]
    print('  英雄專屬配裝：%d 套（%d 位英雄）' % (
        len(hb), sum(1 for r in out if r['builds'])))
    sk = [k for r in out for k in r['skins']]
    print('  皮膚 %d 個（%d 位英雄，%d 個預設關閉）；未翻譯名稱 %d 個' % (
        len(sk), sum(1 for r in out if r['skins']),
        sum(1 for k in sk if not k['on']),
        sum(1 for k in sk if k['n'][0] == k['n'][2])))
    swap = [k for k in sk if k.get('add') or k.get('rm')]
    sab = {a['id']: a for k in swap for a in k.get('add', [])}
    print('  其中會換技能的皮膚：%d 個（換上 %d 個不重複技能，未翻譯 %d 個）' % (
        len(swap), len(sab),
        sum(1 for a in sab.values() if a['n'][0] == a['n'][2])))
    nlv = sum(1 for a in ab if a.get('lvt'))
    print('  有等級數值表的技能：%d 個（共 %d 列數值）' % (
        nlv, sum(len(a['lvt']) for a in ab if a.get('lvt'))))
    untr = sum(1 for a in ab if a['t'][2] and a['t'][0] == a['t'][2])
    print('  技能說明：%d 個有原文（%d 個沒有）；其中 %d 個尚未翻譯' % (
        len(ab) - notxt, notxt, untr))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
