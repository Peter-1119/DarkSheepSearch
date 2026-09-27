# -*- coding: utf-8 -*-
"""階段 C：經典關卡（選單分頁 + 開場掛鉤 + 1.85 出怪 + 骨灰寒冰野怪營地）。

做法：經典模式沿用原本的關卡編號（1/11/23/4/14），加一個 udC_Classic 旗標。
開場時把 gg_rct_Zone1／Zone4、Event_1~4 搬到北邊經典戰場，主堡變數指向搬過去的主堡，
新版關卡函式本身原封不動，只在出怪點、英雄出生點、啟用哪套出怪觸發這幾處掛鉤。
"""
import re, struct, json, os

PAGE = 7                                   # 每頁最多幾關


def _hex2id(J):
    def rep(m):
        b = struct.pack('>I', int(m.group(1), 16))
        ok = all(48 <= c <= 57 or 65 <= c <= 90 or 97 <= c <= 122 for c in b)
        return "'%s'" % b.decode('latin-1') if ok else m.group(0)
    return re.sub(r'0x([0-9a-fA-F]{8})', rep, J)


def _after_locals(body, add):
    """在函式的 local 宣告之後插入敘述（JASS 規定 local 必須在最前面）。"""
    lines = body.split('\n')
    k = 1
    while k < len(lines) and lines[k].startswith('local '):
        k += 1
    return '\n'.join(lines[:k] + [add.rstrip('\n')] + lines[k:])


def _span(J, name):
    m = re.search(r'^function %s takes[^\n]*\n' % re.escape(name), J, re.M)
    assert m, name
    return m.start(), J.index('\nendfunction', m.start()) + len('\nendfunction')


def _body(J, name):
    a, b = _span(J, name)
    return J[a:b]


def _sub_func(J, name, fn):
    a, b = _span(J, name)
    return J[:a] + fn(J[a:b]) + J[b:]


def _f(x):
    return '%.1f' % x


# ============================================================ 1.85 的經典關卡資料
def classic_data(J185, tomb_shift, ice_shift):
    def lv(n):
        return _body(J185, 'Trig_Lvl_%d_Actions' % n)

    def pts(b):
        return [(float(x), float(y)) for x, y in
                re.findall(r'set udg_SpawnPoints\[\d+\]=Location\((-?[\d.]+),(-?[\d.]+)\)', b)]

    def sh(p, s):
        return (p[0] + s[0], p[1] + s[1])

    d = {}
    b1, b23, b4 = lv(1), lv(23), lv(4)
    hero_t = tuple(map(float, re.search(r'SpawnHeroPoint\[[^]]*\]=Location\((-?[\d.]+),(-?[\d.]+)\)', b1).groups()))
    d['tomb_spawns'] = [sh(p, tomb_shift) for p in pts(b1)]
    d['tomb23_spawns'] = [sh(p, tomb_shift) for p in pts(b23)]
    d['tomb_hero'] = sh(hero_t, tomb_shift)
    hs = [tuple(map(float, x)) for x in re.findall(r'SpawnHeroPoint\[[^]]*\]=Location\((-?[\d.]+),(-?[\d.]+)\)', b4)]
    d['ice_hero_top'], d['ice_hero_bot'] = sh(hs[0], ice_shift), sh(hs[1], ice_shift)
    d['ice_spawns'] = [sh(p, ice_shift) for p in pts(b4)]
    ev = {}
    for k in range(1, 5):
        x1, y1, x2, y2 = map(float, re.search(r'set gg_rct_Event_%d=Rect\(([^)]*)\)' % k, J185).group(1).split(','))
        ev[k] = (x1 + tomb_shift[0], y1 + tomb_shift[1], x2 + tomb_shift[0], y2 + tomb_shift[1])
    d['events'] = ev
    return d


# ============================================================ 1.85 出怪觸發搬移
def port_waves(J185, trg, newname, idmap=None, family=None):
    """把 1.85 的某個觸發（含 InitTrig 與所有 Trig_<trg>_* 函式）改名搬過來，建怪改用 SpawnEnemy。
    family：同一家族的其他觸發改名對照（例如 SSS1 會直接執行 S1）。"""
    J = _hex2id(J185)
    funcs = []
    for m in re.finditer(r'^function ((?:Trig_%s_\w+)|InitTrig_%s) takes.*?^endfunction' % (re.escape(trg), re.escape(trg)),
                         J, re.M | re.S):
        funcs.append(m.group(0))
    assert funcs, trg
    # InitTrig 放最後
    funcs.sort(key=lambda s: s.startswith('function InitTrig_'))
    code = '\n'.join(funcs)
    code = re.sub(r'\bTrig_%s_' % re.escape(trg), 'Trig_%s_' % newname, code)
    code = re.sub(r'\bInitTrig_%s\b' % re.escape(trg), 'InitTrig_%s' % newname, code)
    code = re.sub(r'\bgg_trg_%s\b' % re.escape(trg), 'gg_trg_%s' % newname, code)
    for o, n in (family or {}).items():
        if o != trg:
            code = re.sub(r'\bgg_trg_%s\b' % re.escape(o), 'gg_trg_%s' % n, code)

    lines = code.split('\n')
    out, i, n_conv = [], 0, 0
    pair = {'udg_AttackGroup': 'udg_DefPoint', 'udg_AttackGroup2': 'udg_DefPoint2', 'udg_AttackGroup3': 'udg_DefPoint3'}
    while i < len(lines):
        a = lines[i].strip()
        b = lines[i + 1].strip() if i + 1 < len(lines) else ''
        c = lines[i + 2].strip() if i + 2 < len(lines) else ''
        m1 = re.match(r"call CreateNUnitsAtLoc\((\d+),'(\w{4})',ForcePickRandomPlayer\(udg_AI\),(.+),bj_UNIT_FACING\)$", a)
        m2 = re.match(r'call GroupAddUnitSimple\(GetLastCreatedUnit\(\),(udg_AttackGroup\d?)\)$', b)
        m3 = re.match(r'call IssuePointOrder(?:LocBJ\(GetLastCreatedUnit\(\),"attack"|ByIdLoc\(GetLastCreatedUnit\(\),Order_attack),'
                      r'(udg_DefPoint\d?)\)$', c)
        if m1 and m2 and m3 and pair[m2.group(1)] == m3.group(1):
            uid = (idmap or {}).get(m1.group(2), m1.group(2))
            for _ in range(int(m1.group(1))):
                out.append("call SpawnEnemy('%s',%s,%s,0)" % (uid, m1.group(3), m2.group(1)))
            n_conv += 1; i += 3; continue
        m1 = re.match(r"set u=CreateUnitAtLoc\(AI\[\w+\],'(\w{4})',(.+),[-\d.]+\)$", a)
        m2 = re.match(r'call GroupAddUnit\((udg_AttackGroup\d?),u\)$', b)
        m3 = re.match(r'call IssuePointOrder(?:Loc\(u,"attack"|ByIdLoc\(u,Order_attack),(udg_DefPoint\d?)\)$', c)
        if m1 and m2 and m3 and pair[m2.group(1)] == m3.group(1):
            uid = (idmap or {}).get(m1.group(1), m1.group(1))
            out.append("call SpawnEnemy('%s',%s,%s,0)" % (uid, m1.group(2), m2.group(1)))
            n_conv += 1; i += 3; continue
        out.append(lines[i]); i += 1
    code = '\n'.join(out)
    left = len(re.findall(r'CreateN?Units?AtLoc\(', code))
    other_trg = sorted(set(re.findall(r'gg_trg_\w+', code)) - {'gg_trg_' + newname})
    return code, n_conv, left, other_trg


# ============================================================ 選單
def parse_menu(J):
    """回傳 {分頁: {'msg':..., 'entries':[{btn, gate, label, grey, action}]}}"""
    cats = {}
    lc = _body(J, 'Trig_LvlCategories_Actions')
    blocks = re.split(r'\n(?:if|elseif) b==udg_Button\[(\d)\]then\n', lc)
    for k in range(1, len(blocks), 2):
        cat = int(blocks[k]); blk = blocks[k + 1]
        msg = re.search(r'call DialogSetMessage\(udg_ChooseLvlWindow,(.+)\)\n', blk).group(1)
        ents = []
        L = blk.split('\n')
        j = 0
        while j < len(L):
            m = re.match(r'if udg_AllPoints>=(\d+) then$', L[j])
            mb = re.match(r'set udg_Button\[(\d+)\]=DialogAddButton\(udg_ChooseLvlWindow,("(?:[^"\\]|\\.)*"),0\)$', L[j])
            if m and j + 3 < len(L) and re.match(r'set udg_Button\[(\d+)\]', L[j + 1]) and L[j + 2] == 'else':
                m1 = re.match(r'set udg_Button\[(\d+)\]=DialogAddButton\(udg_ChooseLvlWindow,("(?:[^"\\]|\\.)*"),0\)$', L[j + 1])
                m2 = re.match(r'set udg_Button\[(\d+)\]=DialogAddButton\(udg_ChooseLvlWindow,("(?:[^"\\]|\\.)*"),0\)$', L[j + 3])
                if m1 and int(m1.group(1)) >= 21:
                    ents.append(dict(btn=int(m1.group(1)), gate=int(m.group(1)), label=m1.group(2), grey=m2.group(2)))
                j += 5; continue
            if mb and int(mb.group(1)) >= 21:
                ents.append(dict(btn=int(mb.group(1)), gate=0, label=mb.group(2), grey=mb.group(2)))
            j += 1
        cats[cat] = dict(msg=msg, entries=ents)
    handlers = {1: 'Trig_CommonLevelsCategory_Actions', 2: 'Trig_HardcoreLevelsCategory_Actions',
                3: 'Trig_ChallengeLevelsCategory_Actions'}
    for cat, fn in handlers.items():
        hb = _body(J, fn)
        parts = re.split(r'\n(?:if|elseif) b==udg_Button\[(\d+)\]then\n', hb)
        acts = {}
        for k in range(1, len(parts), 2):
            body = parts[k + 1]
            s = body.index('call DisableTrigger(GetTriggeringTrigger())\n') + len('call DisableTrigger(GetTriggeringTrigger())\n')
            e = body.index('call CreatePreStart_Function()') + len('call CreatePreStart_Function()')
            acts[int(parts[k])] = body[s:e]
        for en in cats[cat]['entries']:
            en['action'] = acts[en['btn']]
            en['lvl'] = int(re.search(r'set udg_Lvl=(\d+)', en['action']).group(1))
    return cats


def build_menu(cats, extra):
    """extra：{分頁: [(插在第幾個之後, entry)]}；回傳 (JASS, 每分頁的最終清單)"""
    final = {}
    for cat in (1, 2, 3):
        es = [dict(e, classic=False) for e in cats[cat]['entries']]
        for after_lvl, ent in extra.get(cat, []):
            idx = next(i for i, e in enumerate(es) if e['lvl'] == after_lvl and not e.get('classic'))
            es.insert(idx + 1, ent)
        final[cat] = es
    eid, all_e = 0, []
    for cat in (1, 2, 3):
        for e in final[cat]:
            eid += 1; e['id'] = eid; all_e.append(e)

    J = []
    J.append('function udC_ShowPage takes integer cat,integer page returns nothing')
    J.append('call DialogClear(udg_ChooseLvlWindow)\nset udC_Cat=cat\nset udC_Page=page\nset udC_BtnN=0\n'
             'set udC_Next=null\nset udC_Prev=null')
    for ci, cat in enumerate((1, 2, 3)):
        J.append(('if' if ci == 0 else 'elseif') + ' cat==%d then' % cat)
        J.append('call DialogSetMessage(udg_ChooseLvlWindow,%s)' % cats[cat]['msg'])
        es = final[cat]
        pages = [es[i:i + PAGE] for i in range(0, len(es), PAGE)]
        for pi, pg in enumerate(pages):
            J.append(('if' if pi == 0 else 'elseif') + ' page==%d then' % pi)
            for e in pg:
                J.append('set udC_BtnN=udC_BtnN+1')
                if e['gate']:
                    J.append('if udg_AllPoints>=%d then' % e['gate'])
                    J.append('set udC_Btn[udC_BtnN]=DialogAddButton(udg_ChooseLvlWindow,%s,0)' % e['label'])
                    J.append('else')
                    J.append('set udC_Btn[udC_BtnN]=DialogAddButton(udg_ChooseLvlWindow,%s,0)' % e['grey'])
                    J.append('endif')
                else:
                    J.append('set udC_Btn[udC_BtnN]=DialogAddButton(udg_ChooseLvlWindow,%s,0)' % e['label'])
                J.append('set udC_BtnE[udC_BtnN]=%d' % e['id'])
            # 翻頁鈕一律放在最後：上一頁 → 下一頁 →（迴圈外的）返回
            if pi > 0:
                J.append('set udC_Prev=DialogAddButton(udg_ChooseLvlWindow,"|cFF90EDEA<< 上一頁|r",0)')
            if pi < len(pages) - 1:
                J.append('set udC_Next=DialogAddButton(udg_ChooseLvlWindow,"|cFF90EDEA下一頁 >>|r",0)')
        J.append('endif')
    J.append('endif')
    J.append('set udC_Back=DialogAddButton(udg_ChooseLvlWindow,"|cFFBF93D4Назад|r",0)')
    J.append('call EnableTrigger(gg_trg_udC_Menu)\nendfunction')

    J.append('function udC_Pick takes integer e returns boolean')
    for i, e in enumerate(all_e):
        J.append(('if' if i == 0 else 'elseif') + ' e==%d then' % e['id'])
        if e['gate']:
            J.append('if udg_AllPoints<%d then\nreturn false\nendif' % e['gate'])
        J.append('call DialogClear(udg_ChooseLvlWindow)\ncall DisableTrigger(gg_trg_udC_Menu)')
        J.append('set udC_Classic=%s' % ('true' if e['classic'] else 'false'))
        J.append(e['action'])
    J.append('endif\nreturn true\nendfunction')

    J.append('''function Trig_udC_Menu_Actions takes nothing returns nothing
local player pl=GetTriggerPlayer()
local button b=GetClickedButton()
local integer i=1
local boolean done=false
if b==udC_Next and b!=null then
call udC_ShowPage(udC_Cat,udC_Page+1)
elseif b==udC_Prev and b!=null then
call udC_ShowPage(udC_Cat,udC_Page-1)
elseif b==udC_Back then
call DisableTrigger(GetTriggeringTrigger())
call DialogClear(udg_ChooseLvlWindow)
call BackToLvlCategories_Function()
else
loop
exitwhen i>udC_BtnN or done
if b==udC_Btn[i] then
set done=true
if not udC_Pick(udC_BtnE[i]) then
call udC_ShowPage(udC_Cat,udC_Page)
endif
endif
set i=i+1
endloop
endif
call DialogDisplay(pl,udg_ChooseLvlWindow,true)
set b=null
set pl=null
endfunction''')
    return '\n'.join(J), final


NEW_LVLCAT = '''function Trig_LvlCategories_Actions takes nothing returns nothing
local player pl=GetTriggerPlayer()
local button b=GetClickedButton()
call DialogClear(udg_ChooseLvlWindow)
if b==udg_Button[1]then
call udC_ShowPage(1,0)
call DisableTrigger(GetTriggeringTrigger())
elseif b==udg_Button[2] and udg_AllPoints>=50000 then
call udC_ShowPage(2,0)
call DisableTrigger(GetTriggeringTrigger())
elseif b==udg_Button[3] and udg_AllPoints>=1000000 then
call udC_ShowPage(3,0)
call DisableTrigger(GetTriggeringTrigger())
else
call BackToLvlCategories_Function()
endif
call DialogDisplay(pl,udg_ChooseLvlWindow,true)
set b=null
set pl=null
endfunction'''


# ============================================================ 主流程
def apply(J, J185, ctx, log):
    TS, IS = ctx['tomb_shift'], ctx['ice_shift']
    CD = classic_data(J185, TS, IS)
    tomb_rect = tuple(v + (TS[0] if k % 2 == 0 else TS[1]) for k, v in enumerate(ctx['tomb_zone141']))
    ice_rect = tuple(v + (IS[0] if k % 2 == 0 else IS[1]) for k, v in enumerate(ctx['ice_zone141']))
    tomb_all, ice_all = ctx['tomb_area'], ctx['ice_area']            # 整塊搬過去的範圍（清除用）
    log('[C] 經典陵墓上層：出怪點 %d（黑暗墓地 %d）、英雄出生 (%.0f,%.0f)'
        % (len(CD['tomb_spawns']), len(CD['tomb23_spawns']), CD['tomb_hero'][0], CD['tomb_hero'][1]))
    log('[C] 寒冰洞窟：出怪點 %d、上方出生 (%.0f,%.0f)、下方出生 (%.0f,%.0f)'
        % (len(CD['ice_spawns']), CD['ice_hero_top'][0], CD['ice_hero_top'][1],
           CD['ice_hero_bot'][0], CD['ice_hero_bot'][1]))

    # ---------------- 1. 搬 1.85 出怪觸發 ----------------
    TIER = {'n02H': 'n03M', 'n04Z': 'n05I', 'u00I': 'u01E', 'n024': 'n02U'}       # 骨灰寒冰的換怪
    FAMILIES = [({'S1': 'udC_S1', 'SS1': 'udC_SS1', 'SSS1': 'udC_SSS1'}, None),
                ({'Hard_S1': 'udC_Hard_S1', 'Hard_SS1': 'udC_Hard_SS1', 'Hard_SSS1': 'udC_Hard_SSS1'}, None),
                ({'S23': 'udC_S23', 'SS23': 'udC_SS23', 'SSS23': 'udC_SSS23'}, None),
                ({'S4': 'udC_S4', 'SS4': 'udC_SS4', 'SSS4': 'udC_SSS4'}, None),
                ({'S4': 'udC_IS4', 'SS4': 'udC_ISS4', 'SSS4': 'udC_ISSS4'}, TIER)]
    PORT = [(o, n, idm, fam) for fam, idm in FAMILIES for o, n in fam.items()]
    wave_code, trg_globals, inits = [], [], []
    for old, new, idm, fam in PORT:
        code, n, left, other = port_waves(J185, old, new, idm, fam)
        wave_code.append(code)
        trg_globals.append('trigger gg_trg_%s=null' % new)
        inits.append('call InitTrig_%s()' % new)
        log('[C] 搬 1.85 %-9s → %-12s 轉成 SpawnEnemy %3d 組，剩下直接建怪 %d 處%s'
            % (old, new, n, left, ('，引用其他觸發 %s' % other) if other else ''))

    # ---------------- 2. 全域 ----------------
    G = ['boolean udC_Classic=false', 'integer udC_Area=0', 'integer udC_Lanes=0',
         'integer udC_Cat=0', 'integer udC_Page=0', 'integer udC_BtnN=0',
         'button array udC_Btn', 'integer array udC_BtnE',
         'button udC_Next=null', 'button udC_Prev=null', 'button udC_Back=null',
         'trigger gg_trg_udC_Menu=null', 'rect udC_TombAll=null', 'rect udC_IceAll=null'] + trg_globals
    J = J.replace('endglobals', '\n'.join(G) + '\nendglobals', 1)

    # ---------------- 3. 執行期輔助函式（放在選單之前，所有關卡函式之前）----------------
    def locs(pts, lanes_var=True):
        s = ''.join('set udg_SpawnPoints[%d]=Location(%s,%s)\n' % (k + 1, _f(x), _f(y)) for k, (x, y) in enumerate(pts))
        return s + 'set udC_Lanes=%d\n' % len(pts)

    camps = ctx['ice_camps']            # [(x,y,[types], boss_drop)]
    camp_code = []
    for (cx, cy, types, drop) in camps:
        for k, t in enumerate(types):
            dx, dy = [(0, 0), (-160, -120), (160, -120)][k % 3]
            camp_code.append("set u=CreateUnit(Player(PLAYER_NEUTRAL_AGGRESSIVE),'%s',%s,%s,%d)"
                             % (t, _f(cx + dx), _f(cy + dy), 270))
            camp_code.append('call SetUnitAcquireRange(u,400.0)')
            if k == 0 and drop:
                camp_code.append('set t=CreateTrigger()\ncall TriggerRegisterUnitEvent(t,u,EVENT_UNIT_DEATH)\n'
                                 'call TriggerAddAction(t,function %s)' % drop)

    ev = CD['events']
    H = '''function udC_L takes integer k returns integer
if udC_Classic and udC_Lanes>0 then
return udC_Lanes
endif
return k
endfunction
function udC_Enable takes trigger a,trigger b returns nothing
if udC_Classic then
if b!=null then
call EnableTrigger(b)
endif
else
call EnableTrigger(a)
endif
endfunction
function udC_RemoveIn takes rect r,boolean creepsOnly returns nothing
local group g=CreateGroup()
local unit u
call GroupEnumUnitsInRect(g,r,null)
loop
set u=FirstOfGroup(g)
exitwhen u==null
call GroupRemoveUnit(g,u)
if not creepsOnly or(GetOwningPlayer(u)==Player(PLAYER_NEUTRAL_AGGRESSIVE) and not IsUnitType(u,UNIT_TYPE_STRUCTURE))then
call RemoveUnit(u)
endif
endloop
call DestroyGroup(g)
set g=null
endfunction
function udC_DropT2 takes nothing returns nothing
local unit u=GetTriggerUnit()
call CreateItem(T2_CreateItem(),GetUnitX(u),GetUnitY(u))
call DestroyTrigger(GetTriggeringTrigger())
set u=null
endfunction
function udC_Camps takes nothing returns nothing
local unit u
local trigger t
''' + '\n'.join(camp_code) + '''
set u=null
set t=null
endfunction
function udC_Setup takes nothing returns nothing
if udg_Lvl==1 or udg_Lvl==11 or udg_Lvl==23 then
set udC_Area=1
call udC_RemoveIn(gg_rct_Zone1,false)
call SetRect(gg_rct_Zone1,%s,%s,%s,%s)
''' % tuple(_f(v) for v in tomb_rect) + ''.join(
        'call SetRect(gg_rct_Event_%d,%s,%s,%s,%s)\n' % ((k,) + tuple(_f(v) for v in ev[k])) for k in (1, 2, 3, 4)) + '''set gg_unit_h000_0002=gg_unitB_h000_0002
elseif udg_Lvl==4 or udg_Lvl==14 then
set udC_Area=2
call udC_RemoveIn(gg_rct_Zone4,false)
call SetRect(gg_rct_Zone4,%s,%s,%s,%s)
''' % tuple(_f(v) for v in ice_rect) + '''set gg_unit_h000_0238=gg_unitB_h000_0239
set gg_unit_nwgt_0168=gg_unitB_nwgt_0871
call SetUnitOwner(gg_unitB_h000_0238,Player(9),true)
set udg_DefPoint2=GetUnitLoc(gg_unitB_h000_0238)
call udC_RemoveIn(udC_IceAll,true)
if udg_Lvl==14 then
call SetPlayerHandicap(Player(PLAYER_NEUTRAL_AGGRESSIVE),udg_Gandikap)
call udC_Camps()
endif
endif
endfunction
function udC_ClearNorth takes nothing returns nothing
if not(udC_Classic and udC_Area==1)then
call udC_RemoveIn(udC_TombAll,false)
endif
if not(udC_Classic and udC_Area==2)then
call udC_RemoveIn(udC_IceAll,false)
endif
endfunction
function udC_SetSpawns takes nothing returns nothing
if udC_Area==1 and udg_Lvl==23 then
''' + locs(CD['tomb23_spawns']) + '''elseif udC_Area==1 then
''' + locs(CD['tomb_spawns']) + '''elseif udC_Area==2 then
''' + locs(CD['ice_spawns']) + '''endif
endfunction
function udC_SetHeroPts takes nothing returns nothing
local integer i=1
loop
exitwhen i>8
if udC_Area==1 then
set udg_SpawnHeroPoint[i]=Location(%s,%s)
elseif i<=4 then
set udg_SpawnHeroPoint[i]=Location(%s,%s)
else
set udg_SpawnHeroPoint[i]=Location(%s,%s)
endif
set i=i+1
endloop
endfunction
''' % tuple(_f(v) for v in (CD['tomb_hero'] + CD['ice_hero_top'] + CD['ice_hero_bot']))

    # ---------------- 4. 選單 ----------------
    cats = parse_menu(J)
    def clone(cat, lvl, name, label_color, gate, grey):
        src = next(e for e in cats[cat]['entries'] if e['lvl'] == lvl)
        act = re.sub(r'set udg_LvlNameNT="(?:[^"\\]|\\.)*"', 'set udg_LvlNameNT="%s"' % name, src['action'])
        return dict(btn=0, gate=gate, label='"%s%s%s"' % (label_color, name, '|r' if label_color else ''),
                    grey=grey or '"%s%s%s"' % (label_color, name, '|r' if label_color else ''),
                    action=act, lvl=lvl, classic=True)
    extra = {
        1: [(1, clone(1, 1, '陵墓上層（經典）', '', 2500, '"|cff808080需要 2 500 積分"')),
            (3, clone(1, 4, '寒冰洞窟（130% 難度）', '', 15000, '"|cff808080需要 15 000 積分"'))],
        2: [(11, clone(2, 11, '陵墓上層（經典·150% 難度）', '|cFFFF3232', 0, None)),
            (4 + 10, clone(2, 14, '寒冰洞窟（190% 難度）', '|cFFFF3232', 600000, '"|cff808080需要 600 000 積分"'))],
        3: [(23, clone(3, 23, '黑暗墓地（經典·260% 難度）', '|cFFFF9600', 4000000, '"|cff808080需要 4 000 000 積分"'))],
    }
    # 寒冰洞窟 130% 放在陵墓西側(Lvl3)之後、淹沒神廟之前；寒冰 190% 放在淹沒神廟 190%(Lvl14)之後
    # 骨灰分頁的「陵墓上層 150%」（新地形）改名陵墓入口
    for e in cats[2]['entries']:
        if e['lvl'] == 11:
            e['label'] = '"|cFFFF3232陵墓入口（150% 難度）|r"'
            e['action'] = re.sub(r'set udg_LvlNameNT="(?:[^"\\]|\\.)*"', 'set udg_LvlNameNT="陵墓入口（150% 難度）"', e['action'])
    menu, final = build_menu(cats, extra)
    for cat in (1, 2, 3):
        names = [re.sub(r'\|c[0-9A-Fa-f]{8}|\|r|"', '', e['label']) for e in final[cat]]
        pages = [names[i:i + PAGE] for i in range(0, len(names), PAGE)]
        log('[C] 選單 分頁%d：%s' % (cat, '  ｜下一頁｜  '.join(' → '.join(p) for p in pages)))

    a, b = _span(J, 'Trig_LvlCategories_Actions')
    J = J[:a] + H + menu + '\n' + NEW_LVLCAT + J[b:]

    # ---------------- 5. 關卡函式掛鉤 ----------------
    ENABLE = {1: {'S1': 'udC_S1', 'SS1': 'udC_SS1', 'SSS1': 'udC_SSS1'},
              11: {'Hard_S1': 'udC_Hard_S1', 'Hard_SS1': 'udC_Hard_SS1', 'Hard_SSS1': 'udC_Hard_SSS1'},
              23: {'S23': 'udC_S23', 'SS23': 'udC_SS23', 'SSS23': 'udC_SSS23'},
              4: {'S4': 'udC_S4', 'SS4': 'udC_SS4', 'SSS4': 'udC_SSS4', 'OldGodsAltar': None},
              14: {'S14': 'udC_IS4', 'SS14': 'udC_ISS4', 'SSS14': 'udC_ISSS4', 'OldGodsAltar': None}}
    for lv, emap in ENABLE.items():
        name = 'Trig_Lvl_%d_Actions' % lv

        def hook(body, lv=lv, emap=emap):
            body = _after_locals(body, 'if udC_Classic then\ncall udC_Setup()\nendif')
            # 出怪點區塊後
            ms = list(re.finditer(r'^set udg_SpawnPoints\[\d+\]=Location\([^)]*\)\n', body, re.M))
            assert ms, lv
            k = ms[-1].end()
            body = body[:k] + 'if udC_Classic then\ncall udC_SetSpawns()\nendif\n' + body[k:]
            m = re.search(r'set bj_forLoopAIndexEnd=(\d+)\n', body[k:])
            body = body[:k + m.start()] + 'set bj_forLoopAIndexEnd=udC_L(%s)\n' % m.group(1) + body[k + m.end():]
            # 英雄出生點迴圈後
            m = re.search(r'set udg_SpawnHeroPoint\[GetForLoopIndexA\(\)\]=Location\([^)]*\)\n.*?endloop\n', body, re.S)
            body = body[:m.end()] + 'if udC_Classic then\ncall udC_SetHeroPts()\nendif\n' + body[m.end():]
            body = re.sub(r'udg_SpawnPoints\[GetRandomInt\(1,(\d+)\)\]', r'udg_SpawnPoints[GetRandomInt(1,udC_L(\1))]', body)
            for old, new in emap.items():
                a_ = 'call EnableTrigger(gg_trg_%s)' % old
                assert body.count(a_) == 1, (lv, old, body.count(a_))
                body = body.replace(a_, 'call udC_Enable(gg_trg_%s,%s)' % (old, ('gg_trg_' + new) if new else 'null'))
            # 寒冰：第二個主堡跟著移除同樣的技能
            if lv in (4, 14):
                body = re.sub(r"(call UnitRemoveAbility\(gg_unit_h000_0238,('\w{4}')\)\n)",
                              r"\1if udC_Classic then\ncall UnitRemoveAbility(gg_unitB_h000_0238,\2)\nendif\n", body)
            return body
        J = _sub_func(J, name, hook)
        log('[C] 掛鉤 Lvl %d：開場搬區域、出怪點、出生點、出怪觸發 %s' % (lv, ','.join('%s→%s' % (a_, b_ or '停用') for a_, b_ in emap.items())))

    for hn in ('Trig_CreateHero1_Actions', 'Trig_CreateHero1_Hard_Actions', 'Trig_CreateHero23_Actions',
               'Trig_CreateHero4_Actions', 'Trig_CreateHero14_Actions'):
        n0 = len(re.findall(r'udg_SpawnPoints\[GetRandomInt\(1,\d+\)\]', _body(J, hn)))
        J = _sub_func(J, hn, lambda b: re.sub(r'udg_SpawnPoints\[GetRandomInt\(1,(\d+)\)\]',
                                              r'udg_SpawnPoints[GetRandomInt(1,udC_L(\1))]', b))
        log('[C] 敵方英雄 %s：隨機出怪點 %d 處改成跟著經典路數' % (hn.replace('Trig_', '').replace('_Actions', ''), n0))

    J = _sub_func(J, 'Trig_ClearUnusedLevels_Actions',
                  lambda b: _after_locals(b, 'call udC_ClearNorth()'))

    # ---------------- 6. 出怪觸發與初始化放到 main 前 ----------------
    init = ('function udC_Init takes nothing returns nothing\n'
            'set udC_TombAll=Rect(%s,%s,%s,%s)\nset udC_IceAll=Rect(%s,%s,%s,%s)\n'
            % tuple(_f(v) for v in tomb_all + ice_all) +
            'set gg_trg_udC_Menu=CreateTrigger()\ncall DisableTrigger(gg_trg_udC_Menu)\n'
            'call TriggerRegisterDialogEvent(gg_trg_udC_Menu,udg_ChooseLvlWindow)\n'
            'call TriggerAddAction(gg_trg_udC_Menu,function Trig_udC_Menu_Actions)\n'
            + '\n'.join(inits) + '\nendfunction\n')
    k = J.index('\nfunction main takes')
    J = J[:k] + '\n' + '\n'.join(wave_code) + '\n' + init.rstrip('\n') + J[k:]
    a, b = _span(J, 'main')
    body = J[a:b]
    body = body[:body.rindex('endfunction')] + 'call udC_Init()\nendfunction'
    J = J[:a] + body + J[b:]
    return J
