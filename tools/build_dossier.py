# -*- coding: utf-8 -*-
"""產生「英雄卷宗」：每隻英雄一份 markdown，把設計配裝需要的東西一次備齊。

為什麼要有這個
--------------
war3map.j 有 66226 行、2.1 MB。以前每個配裝 agent 都要自己對它反覆 grep、
讀片段，一隻英雄就燒掉 17~30 萬 token，而且 57 隻英雄會把同樣的解析重複 57 次。

卷宗把「這隻英雄的技能實際上怎麼運作」預先抽好：技能的三語說明、每級數值表、
**實作它的那段 JASS 原始碼**、原生技能的物件欄位、皮膚差異、以及它碰到的
hash key。agent 只要讀自己那一份（約 8~20 KB）就能開始算數字。

怎麼決定「哪段程式碼屬於哪個技能」
--------------------------------
跟 build_heroes.scaling() 同一套：技能 ID 出現在 if/elseif 條件式裡就取那個
分支，否則取整個函式；`Foo_Conditions` 接到 `Foo_Actions`；再跟著
`TimerStart(..., function X)` 與 `call X(` 往下追一層，因為傷害常常丟給回呼。

用法
----
    python tools/build_dossier.py            # 全部 57 隻
    python tools/build_dossier.py Hamg E00S  # 只做指定的
"""
import io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
import map_heroes, w3obj
from mpq import MPQ

OUT = os.path.join(ROOT, 'data', 'dossier')
MAXCODE = 260          # 每個技能最多附幾行程式碼，避免整份函式灌進來

# 這些函式太巨大又什麼都提到，附上去只是雜訊
NOISE_FN = {'Trig_HeroPick_Actions', 'Trig_i_Actions', 'Trig_NewInit_Actions',
            'Trig_AllBossesSkillsActivate_Actions', 'InitCustomTriggers',
            'Trig_CheckLvl_Actions', 'Trig_ClearUnusedLevels_Actions'}

# 這些是「設定某個數值」的共用包裝，內容是位元展開的樣板（SetUnitLife 一支就
# 104 行）。技能呼叫它們只代表「這裡改了生命/護甲/攻速」，把整份貼進卷宗
# 會佔掉六成篇幅卻等於沒資訊。跟到它們就停，只在程式碼裡看得到呼叫那一行。
UTIL_FN = {
    'SetUnitLife', 'GetUnitLife', 'SetUnitMana', 'SetUnitExtraArmor',
    'GetUnitExtraArmor', 'SetUnitAttackSpeed', 'GetUnitAttackSpeed',
    'SetUnitLifeRegeneration', 'GetUnitLifeRegeneration',
    'SetUnitManaRegeneration', 'GetUnitManaRegeneration',
    'ClearUnit', 'StartCooldown', 'StartModCooldown', 'EndCooldown',
    'DistanceNative', 'PolarX', 'PolarY', 'AngleXY', 'UnitLifePercent',
    'GetRandomSubGroup', 'CreateProjectile', 'KnockBackUnit', 'KnockBackUnit2',
}

# hash key 的意義。方向很重要 —— 同一個 key 在「施加者」與「受害者」身上
# 是完全不同的東西，先前就有天賦把「點燃抗性」寫進「點燃傷害 +%」的例子。
KEYS = {
    1:  '裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20',
    3:  '對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof',
    4:  '受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它',
    5:  '對 0-1 級敵人傷害 +%〔攻擊者〕',
    6:  '造成傷害 +%〔攻擊者〕；電擊會扣它 → 目標輸出下降',
    8:  '對英雄減傷〔受害者〕',
    9:  '對亡靈傷害 +%〔攻擊者〕',
    10: '金幣加成〔擊殺者〕Trig_gold_Actions 讀擊殺者 handle',
    16: '穿透〔攻擊者〕每次傷害事件後**另外**打一段 CHAOS/UNIVERSAL，不吃減傷',
    17: '反傷〔被攻擊者〕整數槽 ≥1 則免疫反傷',
    18: '裝備技能威力〔持有者〕道具觸發用 cof = key18 + 1',
    19: '反傷加成〔被攻擊者〕',
    27: '實數＝點燃傷害 +%〔施加者〕／整數＝抵抗點燃旗標〔受害者〕**兩者不同表**',
    28: '實數＝冰凍傷害 +%〔施加者〕／整數＝抵抗冰凍旗標〔受害者〕',
    29: '實數＝流血傷害 +%〔施加者〕／整數＝抵抗流血旗標〔受害者〕'
        '（加成寫錯變數，實際無效 —— 見 地圖問題回報 A-4）',
    35: '額外護甲〔單位〕SetUnitExtraArmor 的儲存槽，可為負',
    37: '生命上限增量〔單位〕只存「最後一次呼叫的差值」，不是總量',
    44: '狀態免疫旗標〔受害者〕>0 則所有狀態函式開頭直接 return，完全不判定',
    45: '實數＝疾病傷害 +%〔施加者〕／整數＝抵抗疾病旗標〔受害者〕'
        '（加成同樣寫錯變數）',
    46: '易燃效果強化〔施加者〕影響易燃的機率倍率與跳數加成',
    47: '點燃抗性〔受害者〕係數減去它；電擊讓它 −1.00',
    48: '冰凍抗性〔受害者〕；電擊 −1.00',
    49: '流血抗性〔受害者〕；電擊 −1.00',
    50: '疾病抗性〔受害者〕；電擊 −1.00',
    52: '（全腳本沒有任何地方讀它 —— 死碼）',
}

CLR = re.compile(r'\|c[0-9A-Fa-f]{8}|\|r')
IFLINE = re.compile(r'(else)?if\b.*\bthen$')
ABIL = re.compile(r"'(A[A-Za-z0-9]{3})'")
NEG = re.compile(r"!=\s*'(A[A-Za-z0-9]{3})'")
CALLED = re.compile(r'\b(?:function|call) ([A-Za-z0-9_]+)')
HASHKEY = re.compile(r'(?:Save|Load)(?:Real|Integer)\(hash,[A-Za-z_0-9()]+,(\d+)[,)]')
CREATE = re.compile(r"CreateUnit\([^,]+,'(.{4})'")


def index_jass(jass):
    """把 JASS 切成「行 -> 函式 / 分支路徑」的索引。"""
    lines = jass.split('\n')
    strip = [l.strip() for l in lines]
    n = len(lines)

    fn, fspan, cur, start = [], {}, '?', 0
    for i, l in enumerate(lines):
        m = re.match(r'function ([A-Za-z0-9_]+) ', l)
        if m:
            fspan[cur] = (start, i)
            cur, start = m.group(1), i
        fn.append(cur)
    fspan[cur] = (start, n)

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
        path.append(tuple(stack))
        if t == 'endif' and stack:
            stack.pop()
    return lines, strip, fn, fspan, path


def ability_spans(idx):
    """技能 ID -> [(起, 迄)]，語意跟 build_heroes.scaling() 一致。"""
    lines, strip, fn, fspan, path = idx
    n = len(lines)
    spans = {}
    for i, l in enumerate(lines):
        if 'DisplayTimedTextToPlayer' in l:
            continue
        skip = set(NEG.findall(l))
        ids = [a for a in ABIL.findall(l) if a not in skip]
        if not ids:
            continue
        if path[i]:
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
    return spans


def follow_callbacks(idx, rngs, depth=1):
    """跟著 TimerStart(...,function X) 與 call X( 往下追，傷害常寫在回呼裡。"""
    lines, strip, fn, fspan, path = idx
    out = list(rngs)
    seen = {fn[lo] for lo, hi in rngs}
    frontier = list(rngs)
    for _ in range(depth):
        nxt = []
        for lo, hi in frontier:
            for i in range(lo, hi):
                if strip[i].startswith('function '):
                    continue
                for name in CALLED.findall(strip[i]):
                    if (name in fspan and name not in seen
                            and name not in NOISE_FN and name not in UTIL_FN):
                        seen.add(name)
                        nxt.append(fspan[name])
        out += nxt
        frontier = nxt
    return out


def merge(rngs):
    """合併重疊區段，順便丟掉雜訊函式。"""
    rngs = sorted(set(rngs))
    out = []
    for lo, hi in rngs:
        if out and lo <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], hi))
        else:
            out.append((lo, hi))
    return out


def code_for(idx, aid, spans):
    """回傳 [(函式名, 起行, [程式碼…])]，總行數受 MAXCODE 限制。"""
    lines, strip, fn, fspan, path = idx
    rngs = spans.get(aid)
    if not rngs:
        return []
    rngs = [r for r in rngs if fn[r[0]] not in NOISE_FN]
    if not rngs:
        return []
    rngs = merge(follow_callbacks(idx, merge(rngs)))
    out, used = [], 0
    for lo, hi in rngs:
        if used >= MAXCODE:
            break
        take = min(hi - lo, MAXCODE - used)
        body = [l for l in lines[lo:lo + take] if l.strip()]
        if not body:
            continue
        out.append((fn[lo], lo + 1, body))
        used += take
    return out


def w3a_fields(a):
    """原生技能的數值欄位。JASS 找不到的效果都在這裡。"""
    skip = {'anam', 'aret', 'atp1', 'aub1', 'arut', 'ansf', 'aart', 'arar',
            'auar', 'ausu', 'atat', 'ata0', 'ata1', 'aeat', 'acat', 'aani',
            'arac', 'areq', 'abpx', 'abpy', 'arpx', 'arpy', 'ahky', 'arhk',
            'alsk', 'arlv', 'aord', 'atac', '_base'}
    out = []
    for k in sorted(a):
        if k in skip or k.startswith('_'):
            continue
        v = a[k]
        if isinstance(v, list):
            u = []
            for x in v:
                if x not in u:
                    u.append(x)
            v = u[0] if len(u) == 1 else u
        out.append('%s = %s' % (k, v))
    return out


def _f(d, k):
    v = d.get(k)
    return v[0] if isinstance(v, list) else v


def hero_doc(h, rec, idx, A, U, spans):
    """組出一隻英雄的 markdown。"""
    L = []
    n = rec['n']
    L.append('# %s `%s`（%s）' % (n[0], rec['id'], n[2]))
    L.append('')
    attr = {'str': '力量', 'agi': '敏捷', 'int': '智力'}.get(rec['attr'], rec['attr'])
    bits = ['主屬性 **%s**' % attr,
            '背包 **%d 格**' % rec.get('slots', 6),
            '解鎖 %s' % (rec['unlock'] or 0),
            '定位 %s' % '/'.join(r[0] for r in rec['roles']) if rec['roles'] else '']
    if rec['random'] is False:
        bits.append('**不在隨機池**（只能手動挑）')
    if rec.get('lock'):
        bits.append('**帳號鎖定**：%s' % ', '.join(rec['lock']))
    L.append(' · '.join(b for b in bits if b))
    st = rec['st']
    L.append('')
    L.append('| | 初始 | 每級 |')
    L.append('|---|---|---|')
    def _sv(v):
        # None 代表地圖沒覆寫這個欄位、沿用原型的預設值，不是 0
        return '（未覆寫）' if v is None else ('%g' % v if isinstance(v, float) else v)
    for k, lab in (('str', '力量'), ('agi', '敏捷'), ('int', '智力')):
        L.append('| %s | %s | %s |' % (lab, _sv(st.get(k)), _sv(st.get(k + '_lv'))))
    L.append('')
    if rec.get('d') and rec['d'][0]:
        L.append('> %s' % rec['d'][0].replace('\n', ' '))
        L.append('')

    mod, give, sp = set(rec.get('mod') or []), set(rec.get('give') or []), set(rec.get('sp') or [])
    L.append('**縮放**：吃技能強度的技能 %s ／ ◈ 吃裝備技能威力 %s ／ ⊕ 給裝備技能威力 %s'
             % (sorted(sp) or '無', sorted(mod) or '無', sorted(give) or '無'))
    L.append('')
    L.append('---')
    L.append('')

    # 要抽程式碼的技能：本體技能 + 天賦選項 + 皮膚換上的技能。
    # 少了後兩者的話，召喚師／有換技能皮膚的英雄會缺掉三分之一的內容。
    ablist = list(rec['ab'])
    seen_ab = {a['id'] for a in ablist}
    for a in rec['ab']:
        for o in a.get('opts') or []:
            if o['id'] not in seen_ab:
                seen_ab.add(o['id'])
                ablist.append(dict(o, _from='天賦「%s」' % a['n'][0]))
    for k in rec['skins']:
        for x in k.get('add') or []:
            if x['id'] not in seen_ab:
                seen_ab.add(x['id'])
                ablist.append(dict(x, _from='皮膚「%s」' % k['n'][0]))

    keys_seen, summons = set(), set()
    for a in ablist:
        aid = a['id']
        tag = []
        if aid in sp:
            tag.append('吃技能強度')
        if aid in mod:
            tag.append('◈ 吃裝備技能威力')
        if aid in give:
            tag.append('⊕ 給裝備技能威力')
        if a.get('_from'):
            tag.insert(0, '來自' + a['_from'])
        L.append('## %s `%s`%s' % (a['n'][0], aid, '　—　' + '、'.join(tag) if tag else ''))
        L.append('')
        if a['n'][2] and a['n'][2] != a['n'][0]:
            L.append('俄文原名：%s' % a['n'][2])
        txt = (a['t'][0] or '').strip()
        if txt:
            L.append('')
            L.append('```')
            L.append(txt)
            L.append('```')
        if a.get('lvt'):
            L.append('')
            L.append('每級變動：')
            for row in a['lvt']:
                L.append('  - 第 %d 行：%s' % (row['i'] + 1, ' / '.join(map(str, row['v']))))
        if a.get('opts'):
            L.append('')
            L.append('**天賦選項**：')
            for o in a['opts']:
                L.append('  - `%s` %s' % (o['id'], o['n'][0]))
                ot = (o['t'][0] or '').replace('\n', ' ').strip()
                if ot:
                    L.append('    %s' % ot[:400])

        obj = A.get(aid, {})
        f = w3a_fields(obj)
        if f:
            L.append('')
            L.append('物件欄位（原型 `%s`）：`%s`' % (obj.get('_base'), '`, `'.join(f)))

        blocks = code_for(idx, aid, spans)
        if blocks:
            L.append('')
            L.append('實作：')
            for fname, ln, body in blocks:
                L.append('')
                L.append('`%s`　war3map.j:%d' % (fname, ln))
                L.append('```jass')
                L.extend(body)
                L.append('```')
                joined = '\n'.join(body)
                for m in HASHKEY.finditer(joined):
                    keys_seen.add(int(m.group(1)))
                summons.update(CREATE.findall(joined))
        else:
            L.append('')
            L.append('*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*')
        L.append('')

    # 召喚出來的單位。召喚師的一半戰力在這裡，而這些數值只在 w3u 裡，
    # 光看技能程式碼看不到（守衛有沒有魔法減免、憎惡有沒有大地重擊…）。
    summons.discard(rec['id'])
    def _is_dummy(u2):
        # 只有 Aloc（不可選取）又幾乎沒血的，是純特效載體，不是戰力
        ab = str(_f(u2, 'uabi') or '')
        return ab.strip() in ('Aloc', '') and (_f(u2, 'uhpm') or 0) <= 5
    real = [u for u in sorted(summons) if u in U and not _is_dummy(U[u])]
    if real:
        L.append('---')
        L.append('')
        L.append('## 這隻召喚／製造的單位')
        L.append('')
        L.append('（技能程式碼裡的 `CreateUnit` 目標。數值取自 war3map.w3u，')
        L.append('沒列出的欄位代表地圖沒覆寫、沿用原型。）')
        L.append('')
        for uid2 in real:
            u2 = U[uid2]
            nm = map_heroes.clean(_f(u2, 'unam') or '') or uid2
            L.append('### `%s` %s（原型 `%s`）' % (uid2, nm, u2.get('_base')))
            row = []
            for k, lab in (('uhpm', '生命'), ('umpm', '法力'), ('udty', '防禦型'),
                           ('udef', '護甲'), ('ua1b', '攻擊力'), ('ua1d', '骰子數'),
                           ('ua1s', '骰面'), ('ua1c', '攻擊間隔'), ('ua1r', '射程'),
                           ('ua1z', '攻擊範圍'), ('umvs', '移速'),
                           ('uabi', '技能'), ('uhab', '英雄技能')):
                v = _f(u2, k)
                if v not in (None, '', 0):
                    row.append('%s %s' % (lab, v))
            if row:
                L.append('  - ' + ' ／ '.join(row))
            for aid2 in str(_f(u2, 'uabi') or '').split(','):
                aid2 = aid2.strip()
                a2 = A.get(aid2)
                if not a2:
                    continue
                nm2 = map_heroes.clean(str(_f(a2, 'anam') or _f(a2, 'aret') or ''))
                fl = w3a_fields(a2)
                if nm2 or fl:
                    L.append('  - 技能 `%s` %s　`%s`'
                             % (aid2, nm2, '`, `'.join(fl[:12])))
            L.append('')

    sk = [k for k in rec['skins'] if k.get('add') or k.get('rm')]
    if rec['skins']:
        L.append('---')
        L.append('')
        L.append('## 皮膚')
        L.append('')
        plain = [k['n'][0] for k in rec['skins'] if not (k.get('add') or k.get('rm'))]
        if plain:
            L.append('純外觀：%s' % '、'.join(plain))
            L.append('')
        for k in sk:
            L.append('### %s `%s`%s —— **會換技能**'
                     % (k['n'][0], k['id'], '' if k['on'] else '（預設未開放）'))
            for i, x in enumerate(k.get('rm') or []):
                add = (k.get('add') or [])
                if i < len(add):
                    L.append('  - %s `%s` → **%s** `%s`'
                             % (x['n'][0], x['id'], add[i]['n'][0], add[i]['id']))
                else:
                    L.append('  - 失去 %s `%s`' % (x['n'][0], x['id']))
            for x in (k.get('add') or [])[len(k.get('rm') or []):]:
                L.append('  - 額外獲得 %s `%s`' % (x['n'][0], x['id']))
            L.append('')

    if keys_seen:
        L.append('---')
        L.append('')
        L.append('## 這隻碰到的 hash key')
        L.append('')
        for k in sorted(keys_seen):
            if k in KEYS:
                L.append('  - **%d** — %s' % (k, KEYS[k]))
        L.append('')

    L.append('---')
    L.append('')
    L.append('*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*')
    L.append('*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*')
    L.append('*道具數值見 `data/dossier/_items.md`。*')
    return '\n'.join(L) + '\n'


def main():
    want = set(sys.argv[1:])
    mp = json.load(io.open(os.path.join(HERE, 'version.json'),
                           encoding='utf-8'))['map_file']
    m = MPQ(mp)
    jass = m.read('war3map.j').decode('utf-8', 'replace')
    A = w3obj.parse(m.read('war3map.w3a'), True)
    U = w3obj.parse(m.read('war3map.w3u'))
    recs = {h['id']: h for h in json.load(
        io.open(os.path.join(ROOT, 'data', 'heroes.json'),
                encoding='utf-8'))['heroes']}
    H = map_heroes.load(mp, jass)

    idx = index_jass(jass)
    spans = ability_spans(idx)

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    tot = 0
    for uid, rec in recs.items():
        if want and uid not in want:
            continue
        doc = hero_doc(H.get(uid, {}), rec, idx, A, U, spans)
        p = os.path.join(OUT, uid + '.md')
        io.open(p, 'w', encoding='utf-8').write(doc)
        tot += len(doc.encode('utf-8'))
    n = len(want or recs)
    print('英雄卷宗 %d 份 -> %s，共 %.0f KB（平均 %.0f KB／隻）'
          % (n, os.path.relpath(OUT, ROOT), tot / 1024, tot / 1024 / max(n, 1)))


if __name__ == '__main__':
    main()
