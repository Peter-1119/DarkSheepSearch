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
MAXCODE = 420          # 每個技能最多附幾行程式碼，避免整份函式灌進來

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

# 狀態的施加／結算是所有英雄共用的，完整版在 _engine.md。
# 不排除的話會出事：它們的行號很小（1539、1693…），排序後排在前面，
# 把 MAXCODE 預算吃光 —— 最古老的先知的大絕就整段被擠掉，只剩兩支
# 跟她沒關係的狀態函式。這裡只留「有呼叫到」的一行指標。
ENGINE_FN = {
    'BurnUnit', 'FlammabilityUnit', 'FrostUnit', 'ShockUnit', 'BleedUnit',
    'DiseaseUnit', 'CurseUnit', 'WeakUnit', 'VulnerabilityUnit', 'CharmUnit',
    'SliceUnit', 'AnathemaUnit', 'Burn_Dmg', 'Bleed_Dmg', 'Disease_Dmg',
    'RemoveShock', 'RemoveFlammability', 'RemoveFrost', 'ProjectileMove',
    'Trig_HeroTakeDamage_Actions',
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
# 技能 ID 也被拿來當**雜湊表的 key 名稱**（76 個 ID 有這種用法），例如
# LoadInteger(hash,GetHandleId(u),'A0IG')。那只是借用字串當欄位名，不代表
# 這段程式碼在實作那個技能 —— 不排掉的話整支函式會被錯誤歸屬給它。
HKEY = re.compile(r"(?:Save|Load|Remove)\w*\(hash,[A-Za-z_0-9()]+,'(A[A-Za-z0-9]{3})'")
CALLED = re.compile(r'\b(?:function|call) ([A-Za-z0-9_]+)')
HASHKEY = re.compile(r'(?:Save|Load)(?:Real|Integer)\(hash,[A-Za-z_0-9()]+,(\d+)[,)]')
CREATE = re.compile(r"CreateUnit\([^,]+,'(.{4})'")
# 英雄的實作函式有一致的命名慣例：Trig_HeroSkills51_Actions、HeroQ51_Move、
# HeroW51_Dmg2、Trig_HeroR51_Actions… 中間的數字就是英雄編號。
# 抓到其中一支就把同編號的全部收進來 —— 不然像魔法大師那樣，
# 9 個技能有 4 個只抽到 _conditions，實作整段缺席。
HERONUM = re.compile(r'Hero[A-Za-z_]*?(\d+)')


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


def follow_callbacks(idx, rngs, depth=3):
    """跟著 TimerStart(...,function X) 與 call X( 往下追，傷害常寫在回呼裡。

    深度要夠：獅鷲守護者的球狀閃電是 Actions -> Create -> Move1 -> Move2，
    真正的傷害公式在第三層；只跟一層的話那隻最大的輸出來源整個看不到。
    UTIL_FN 黑名單擋住了樣板函式，所以加深不會爆量。
    """
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
                            and name not in NOISE_FN and name not in UTIL_FN
                            and name not in ENGINE_FN):
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


def engine_calls(idx, aid, spans):
    """這個技能呼叫了哪些共用引擎函式（完整版在 _engine.md）。"""
    lines, strip, fn, fspan, path = idx
    hit = set()
    own = merge(spans.get(aid) or [])
    # 也要看回呼裡的呼叫 —— 狀態多半是在計時器回呼裡施加的
    for lo, hi in merge(follow_callbacks(idx, own)):
        for i in range(lo, hi):
            for nm in CALLED.findall(strip[i]):
                if nm in ENGINE_FN:
                    hit.add(nm)
    return sorted(hit)


def siblings(idx, rngs):
    """同一個英雄編號的其他實作函式（Hero*51_* 那一組）。"""
    lines, strip, fn, fspan, path = idx
    nums = set()
    for lo, hi in rngs:
        m = HERONUM.search(fn[lo] or '')
        if m:
            nums.add(m.group(1))
    if not nums:
        return []
    out = []
    for name, sp in fspan.items():
        if name in NOISE_FN or name in UTIL_FN or name in ENGINE_FN:
            continue
        m = HERONUM.search(name or '')
        if m and m.group(1) in nums:
            out.append(sp)
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
    own = merge(rngs)                       # 技能 ID 直接出現的那幾段
    extra = [r for r in merge(follow_callbacks(idx, own)) if r not in own]
    out, used = [], 0
    for lo, hi in own + extra:              # 自己的先貼，回呼排後面
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


# 傷害／效果走哪條管線。這一行決定了穿透、DefCof、狀態抗性三大類裝備
# 對這隻有沒有用，所以寧可少標也不要標錯 —— 標錯會把配裝方向整個帶歪。
PIPE = [
    ('狀態', re.compile(r'(BurnUnit|FrostUnit|BleedUnit|DiseaseUnit|ShockUnit'
                        r'|FlammabilityUnit|CurseUnit|WeakUnit|VulnerabilityUnit'
                        r'|CharmUnit|SliceUnit|AnathemaUnit)\('),
     '走 `Burn_Dmg` 那條，**外面包了 DisableTrigger** → 不吃 DefCof、不帶穿透、'
     '被狀態抗性擋。該買的是「狀態傷害 +%」「易燃」「機率倍率」。'),
    ('技能直接傷害', re.compile(r'UnitDamageTarget\('),
     '走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）'
     '也吃穿透**，而且傷害事件數越多，穿透越划算。'),
    ('普攻', None,          # 另外判定：有沒有掛在 GetAttacker() 的觸發器上
     '有「攻擊時觸發」的機制 → 攻擊力／攻速／穿透有價值，'
     '但注意那類技能常有自己的內部冷卻，攻速超過內冷就沒用了。'),
    ('召喚物', re.compile(r'CreateUnit\('),
     '召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡'
     '明寫的屬性（通常是最大生命與技能強度）與原生光環。'),
    ('治療', re.compile(r'SetWidgetLife\(|UNIT_STATE_LIFE\s*,\s*GetUnitState'),
     '直接寫血量，不經傷害事件 —— 全地圖沒有「治療加成」這種屬性，'
     '只能靠技能公式裡的係數（多半是技能強度）。'),
    ('屬性增益', re.compile(r'SetHero(Str|Agi|Int)\('),
     '直接改屬性。注意有些是**永久**的（死亡不歸零），長局會滾雪球。'),
]


def inline_branches(idx, uid):
    """以「單位型號」為條件內聯在共用函式裡的實作。

    有些英雄的被動不是靠技能 ID 分派，而是直接寫在傷害管線裡：
      if a_type=='Hmgd' then … / elseif d_type=='Hmgd' then …
    亡者公主的「適應」整段就是這樣，照技能 ID 抽完全抓不到，
    卷宗會誤標成「JASS 裡沒有對應實作」。
    """
    lines, strip, fn, fspan, path = idx
    n = len(lines)
    pat = "=='%s'" % uid
    out = []
    for i, t in enumerate(strip):
        if pat not in t or not IFLINE.match(t):
            continue
        if fn[i] in NOISE_FN:
            continue
        p = path[i] or ()
        if not p:
            continue
        lo = i
        while lo > 0 and fn[lo - 1] == fn[i] and path[lo - 1][:len(p)] == p:
            lo -= 1
        hi = i + 1
        while hi < n and fn[hi] == fn[i] and path[hi][:len(p)] == p:
            hi += 1
        out.append((lo, hi))
    return merge(out)


def attacks_trigger(idx, uid):
    """這隻有沒有掛在「攻擊時」的觸發器上。

    純普攻英雄的技能程式碼裡不會出現 EVENT_PLAYER_UNIT_ATTACKED
    （那寫在 InitTrig 裡），只能反過來找 `GetUnitTypeId(GetAttacker())=='<ID>'`。
    """
    lines = idx[0]
    pat = "GetAttacker())=='%s'" % uid
    return any(pat in l for l in lines)


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
    PIPE_AT = len(L)          # 傷害管線摘要待會兒補在這裡（要先掃完程式碼）
    L.append('')
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
    allcode = []
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

        eng = engine_calls(idx, aid, spans)
        if eng:
            L.append('')
            L.append('呼叫共用引擎函式：`%s` —— 完整內容見 `_engine.md`。'
                     % '`, `'.join(eng))
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
                allcode.append(joined)
                for m in HASHKEY.finditer(joined):
                    keys_seen.add(int(m.group(1)))
                summons.update(CREATE.findall(joined))
        else:
            L.append('')
            L.append('*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*')
        L.append('')

    # 這隻的傷害走哪條管線 —— 這一句就決定了穿透、DefCof、狀態抗性
    # 三大類裝備對它有沒有用，放在最前面讓人先看到。
    blob = '\n'.join(allcode)
    hit = []
    for nm, rx, note in PIPE:
        # rx 是 None 的那一條（普攻）另外判定：技能程式碼裡看不到攻擊事件，
        # 要反過來找腳本有沒有 GetUnitTypeId(GetAttacker())=='<這隻的ID>'
        ok = attacks_trigger(idx, rec['id']) if rx is None else bool(rx.search(blob))
        if ok:
            hit.append((nm, note))
    if hit:
        pl = ['**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：', '']
        for nm, note in hit:
            pl.append('- **%s** —— %s' % (nm, note))
        pl.append('')
        pl.append('細節見 `data/dossier/_engine.md`。')
        L[PIPE_AT:PIPE_AT] = pl

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

    # 上面按技能貼過的函式，後面兩節都要用來去重
    shown = set()
    for a in ablist:
        for f2, _, _ in code_for(idx, a['id'], spans):
            shown.add(f2)

    inl = [r for r in inline_branches(idx, rec['id'])
           if idx[2][r[0]] not in shown]
    if inl:
        L.append('---')
        L.append('')
        L.append('## 以「單位型號」內聯的實作')
        L.append('')
        L.append('這幾段不是靠技能 ID 分派的，而是直接用單位型號 `%s` '
                 '寫在共用函式的條件式裡' % rec['id'])
        L.append('（常見於寫進傷害管線的被動）。照技能抽取抓不到，所以單獨列出來。')
        L.append('')
        for lo, hi in inl[:6]:
            L.append('`%s`　war3map.j:%d' % (idx[2][lo], lo + 1))
            L.append('```jass')
            L.extend([x for x in idx[0][lo:hi] if x.strip()][:120])
            L.append('```')
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

    # 同編號但上面沒貼到的實作函式。英雄的實作散在 Trig_HeroSkills51_Actions、
    # HeroQ51_Move、HeroW51_Dmg2… 這一組裡，而有些（例如決定門檻的那支）
    # 不含任何技能 ID 字面量，前面的抽取抓不到。整份放一次，不要每個技能重複。
    sib = []
    for lo, hi in sorted(set(siblings(idx, [(i, i + 1) for i in range(len(idx[0]))
                                            if idx[2][i] in shown]))):
        nm2 = idx[2][lo]
        # InitTrig_* 只是把觸發器接上事件的 5 行樣板，沒有數值
        if nm2 not in shown and not nm2.startswith('InitTrig_'):
            sib.append((nm2, lo, [x for x in idx[0][lo:hi] if x.strip()]))
    if sib:
        L.append('---')
        L.append('')
        L.append('## 同一組的其他實作函式')
        L.append('')
        L.append('英雄的實作散在同編號的一組函式裡，上面按技能抽取時抓不到的補在這裡')
        L.append('（常見的是決定門檻、結算加成、清理 buff 的那幾支）。')
        L.append('')
        for name, ln, body in sib[:20]:
            L.append('`%s`　war3map.j:%d' % (name, ln + 1))
            L.append('```jass')
            L.extend(body[:200])
            L.append('```')
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
