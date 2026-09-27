# -*- coding: utf-8 -*-
"""UD 併圖正式建置流程。每次都從原始新版地圖出發，依序套用所有階段。

階段 A：8 人（v5 腳本）+ 拓寬 + 小地圖 + 教學關改名
"""
import sys, os, re, io, struct, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\tools')
import mpq, mpq_patch
import w3minimap as mm
from w3resize import Grower, W3I
from w3i_players import W3IPlayers
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/UD_test_24_09_26_opt.w3x'
MAPS = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download'
OUTNAME = '0UD_合併底圖_E2.w3x'
# UD_RU=1：只套用遊戲內容的改動、不中文化（給網站讀俄文說明用），輸出 *_ru.w3x，不放到 Maps
RU = os.environ.get('UD_RU') == '1'
if RU:
    OUTNAME = '0UD_合併底圖_E2_ru.w3x'

ADD_Y = 96                      # 往北拓寬的格數（放舊版陵墓上層與寒冰洞窟）


def rd(tag, f):
    return open(os.path.join(BASE, tag, f), 'rb').read()


def func_span(src, name):
    m = re.search(r'^function %s takes[^\n]*\n' % re.escape(name), src, re.M)
    assert m, name
    return m.start(), src.index('\nendfunction', m.start()) + len('\nendfunction')


def sub_in_func(src, name, a, b, count=1):
    s, e = func_span(src, name)
    body = src[s:e]
    assert body.count(a) == count, (name, a, body.count(a))
    return src[:s] + body.replace(a, b) + src[e:]


LOG = []
def log(msg):
    LOG.append(msg); print(msg)


# ================================================================ 腳本
# 8 人版腳本（v5：大廳、迴圈、小幽光、存讀檔、皮膚、聊天指令全部已補）
J = rd('.', 'ud_new_8p_v5.j').decode('utf-8', 'surrogateescape')
J210 = rd('ud_210', 'war3map.j').decode('utf-8', 'surrogateescape')
log('[8人] 使用 v5 腳本（已實測：小幽光、計分板、保險箱、皮膚、-load）')

# 入侵四路（只有守右下王座的波次）移到 ud_invasion.four_lane，跟其他入侵修改一起套

# ---- 教學關改名 ----
for a, b in (('DialogAddButton(udg_ChooseLvlWindow,"Верхняя усыпальница (Обучение)",0)',
              'DialogAddButton(udg_ChooseLvlWindow,"陵墓入口（教學關）",0)'),
             ('set udg_LvlNameNT="Верхняя усыпальница (Обучение)"',
              'set udg_LvlNameNT="陵墓入口（教學關）"')):
    assert J.count(a) == 1, a
    J = J.replace(a, b)
log('[改名] 陵墓上層（教學）→ 陵墓入口（教學關）：選單按鈕 + 計分板標題')

# ---- 8 人難度基準 ----
# 新版規則：每空一個玩家槽，出怪計時 +0.7/+4.75/+9.5 秒、敵方血量 −5%、CreepsUP_cof +0.10。
# 原本以「6 格全滿」為基準；迴圈改成 8 格後，把基準往前推兩級，
# 讓 6 人剛好等於原版新版的難度，第 7、8 人各再加強一級。
BALANCE = 'B'          # 'A'：8 人滿 = 原版 6 人滿（不加強）；'B'：7、8 人各加強一級
if BALANCE == 'B':
    for a, b in (('set udg_SpawnTimerCount[1]=9.\n', 'set udg_SpawnTimerCount[1]=7.6\n'),
                 ('set udg_SpawnTimerCount[2]=70.\n', 'set udg_SpawnTimerCount[2]=60.5\n'),
                 ('set udg_SpawnTimerCount[3]=140.\n', 'set udg_SpawnTimerCount[3]=121.\n'),
                 ('set udg_Gandikap=1.00\n', 'set udg_Gandikap=1.10\n'),
                 ('real CreepsUP_cof=1.0\n', 'real CreepsUP_cof=0.8\n')):
        assert J.count(a) == 1, a
        J = J.replace(a, b)
    log('[難度] 基準前推兩級：出怪 9/70/140→7.6/60.5/121 秒、敵方血量 100%→110%、CreepsUP 1.0→0.8'
        '（6 人 = 原版新版難度，8 人再強兩級）')

# ---- 攝影機北緣（拓寬）----
old_cam = 'call SetCameraBounds(-13568.0+GetCameraMargin(CAMERA_MARGIN_LEFT),-13824.0+GetCameraMargin(CAMERA_MARGIN_BOTTOM),25856.0-GetCameraMargin(CAMERA_MARGIN_RIGHT),13312.0-GetCameraMargin(CAMERA_MARGIN_TOP),-13568.0+GetCameraMargin(CAMERA_MARGIN_LEFT),13312.0-GetCameraMargin(CAMERA_MARGIN_TOP),25856.0-GetCameraMargin(CAMERA_MARGIN_RIGHT),-13824.0+GetCameraMargin(CAMERA_MARGIN_BOTTOM))'
assert J.count(old_cam) == 1
J = J.replace(old_cam, old_cam.replace('13312.0', '%.1f' % (13312.0 + ADD_Y * 128)))
log('[拓寬] main 攝影機北緣 13312 → %.0f' % (13312.0 + ADD_Y * 128))

for a, b in (('function', 'endfunction'), ('loop', 'endloop'), ('if', 'endif')):
    na = len(re.findall(r'^\s*%s\b' % a, J, re.M)); nb = len(re.findall(r'^\s*%s\b' % b, J, re.M))
    assert na == nb, (a, na, nb)

# ================================================================ 地形
g = Grower(os.path.join(BASE, 'ud_new'))
e, p, sh, wi = g.e, g.p, g.s, g.i
# 新地先整片填成北邊外框那種黑色邊界格（不可通行），戰場再蓋上去
FILL = e.tile(200, 245)
assert struct.unpack_from('<h', FILL, 2)[0] & 0x4000, '樣板格應帶邊界旗標'
W3E_B = bytearray(e.grown(0, ADD_Y, FILL))
WPM_B = bytearray(p.grown(0, ADD_Y, b'\xce'))
SHD_B = bytearray(sh.grown(0, ADD_Y, b'\x00'))
w3i_grown, cam = wi.grown(0, ADD_Y)
W3I_B, added = W3IPlayers(w3i_grown).add_slots([6, 7], name_fmt='Игрок %d', template_pid=5)
wi2 = W3I(W3I_B)
log('[拓寬] 地格 352×%d，可玩區 %d×%d；w3i 玩家槽 %d'
    % (e.h - 1 + ADD_Y, wi2.pw, wi2.ph, len(W3IPlayers(W3I_B).players)))

# ================================================================ 階段 B：搬舊版戰場
import w3transplant as tp
from w3resize import W3E, WPM
from w3doo import DOO

OLD = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/肥羊的聖誕禮物_1.41_ty.w3x'
EO = W3E(rd('ud_old', 'war3map.w3e'))
PO = WPM(rd('ud_old', 'war3map.wpm'))
SO = mpq.MPQ(OLD).read('war3map.shd')
DO = DOO(rd('ud_old', 'war3map.doo'))
DN = DOO(rd('ud_new', 'war3map.doo'))
JO = rd('ud_old', 'war3map.j').decode('utf-8', 'surrogateescape')
E2 = W3E(bytes(W3E_B))

# 1.41 地表索引 11 是 Itbk，新圖那格是 Dlvc；Itbk 改用最接近的 Ibkb（索引 9）
assert EO.ground[11] == b'Itbk' and E2.ground[9] == b'Ibkb' and E2.ground[11] == b'Dlvc'
TEX = {11: 9}

# (名稱, 1.41 tilepoint 矩形, 新圖左下角, 舊英雄出生點)
PLACES = [
    ('陵墓上層', (1, 144, 76, 220), (40, 246), (-9471.0, 9600.0)),
    ('寒冰洞窟', (3, 59, 54, 136), (140, 246), (-10210.0, 338.0)),
]
SHIFT = {}
DEST_WRECT = []                         # (新圖世界矩形, 位移) 給小地圖用
next_eid = max(d.eid for d in DN.items) + 1
for name, rect, dest, hero in PLACES:
    dx, dy = tp.world_shift(EO, E2, rect, dest)
    SHIFT[name] = (dx, dy)
    n_t = tp.copy_w3e(EO, W3E_B, E2.body, E2.w, rect, dest, TEX)
    tp.copy_cells(PO.d, PO.HDR, PO.w, WPM_B, 16, (E2.w - 1) * 4, rect, dest)
    tp.copy_cells(SO, 0, (EO.w - 1) * 4, SHD_B, 0, (E2.w - 1) * 4, rect, dest)
    wr = tp.world_rect(EO, rect)
    items = tp.pick_doodads(DO, wr)
    for d in items:
        c = d.copy(); c.x += dx; c.y += dy; c.eid = next_eid; next_eid += 1
        DN.items.append(c)
    sps = tp.pick_special(DO, rect)
    for o in sps:
        o.x += dest[0] - rect[0]; o.y += dest[1] - rect[1]
        DN.special.append(o)
    DEST_WRECT.append(((wr[0] + dx, wr[1] + dy, wr[2] + dx, wr[3] + dy), (dx, dy)))
    log('[搬移] %s：%d×%d 地格 → 新圖 (%d,%d)，世界位移 (%+.0f, %+.0f)；裝飾物 %d、地形裝飾 %d'
        % (name, rect[2] - rect[0], rect[3] - rect[1], dest[0], dest[1], dx, dy, len(items), len(sps)))
DOO_B = DN.pack()

# ---- 預放單位：從 1.41 的腳本搬過來（不含掉寶觸發）----
def in_wr(x, y, w):
    return w[0] <= x < w[2] and w[1] <= y < w[3]

SRC_WR = [(nm, tp.world_rect(EO, rect)) for nm, rect, dest, hero in PLACES]
unit_lines, globals_add, named = [], [], []
owner, cur, skipped = None, None, 0
for l in JO.split('\n'):
    m = re.match(r'function (Create(?:NeutralHostile|NeutralPassive|NeutralHostileBuildings|NeutralPassiveBuildings)'
                 r'|Create(?:Buildings|Units)ForPlayer\d+) takes', l)
    if m:
        owner, cur = None, None
        continue
    mp = re.match(r'\s*local player p=(.*)$', l)
    if mp:
        owner = mp.group(1); continue
    if l.startswith('endfunction'):
        owner, cur = None, None; continue
    if owner is None:
        continue
    mc = re.match(r"\s*set (\w+)=CreateUnit\(p,(0x[0-9a-fA-F]{8}),(-?[\d.]+),(-?[\d.]+),(-?[\d.]+)\)", l)
    if mc:
        var, uid, x, y, f = mc.groups()
        x, y = float(x), float(y)
        cur = next((nm for nm, w in SRC_WR if in_wr(x, y, w)), None)
        if cur:
            dx, dy = SHIFT[cur]
            if var.startswith('gg_unit_'):
                nv = var.replace('gg_unit_', 'gg_unitB_')
                globals_add.append('unit %s=null' % nv); named.append((cur, var, nv))
                var = nv
            unit_lines.append('set p=%s' % owner)
            unit_lines.append('set %s=CreateUnit(p,%s,%.1f,%.1f,%s)' % (var, uid, x + dx, y + dy, f))
            if var != 'u':
                unit_lines.append('set u=%s' % var)
        continue
    if not cur:
        continue
    s = l.strip()
    if re.match(r'(set t=CreateTrigger|call TriggerRegisterUnitEvent\(t,|call TriggerAddAction\(t,)', s):
        skipped += 1; continue
    mw = re.match(r'call WaygateSetDestination\((\w+),(-?[\d.]+),(-?[\d.]+)\)', s)
    if mw:
        wx, wy = float(mw.group(2)), float(mw.group(3))
        tgt = next((nm for nm, w in SRC_WR if in_wr(wx, wy, w)), None)
        ddx, ddy = SHIFT[tgt] if tgt else (0.0, 0.0)
        log('[單位] 傳送門目的地 (%.0f,%.0f) %s' % (wx, wy, '一起平移' if tgt else '在區外，原樣保留'))
        s = 'call WaygateSetDestination(%s,%.1f,%.1f)' % (mw.group(1), wx + ddx, wy + ddy)
    if s.startswith('call WaygateSetDestination(') or s.startswith('call WaygateActivate('):
        # 1.41 寒冰洞窟的傳送門連到地下堡壘（gg_rct_Portal2）；新版那對傳送門另有用途，這裡先關掉
        if s.startswith('call WaygateActivate('):
            unit_lines.append(re.sub(r',true\)$', ',false)', s.replace('gg_unit_', 'gg_unitB_')))
            log('[單位] 傳送門 %s 原本連到地下堡壘，先設為不啟用' % re.search(r'\((\w+)', s).group(1))
        continue
    s = s.replace('gg_unit_', 'gg_unitB_')
    unit_lines.append(s)

n_units = sum(1 for x in unit_lines if '=CreateUnit(' in x)
func = ('function udB_CreateTransplantUnits takes nothing returns nothing\n'
        'local player p\nlocal unit u\nlocal integer unitID\nlocal trigger t\nlocal real life\n'
        + '\n'.join(unit_lines) + '\nendfunction\n')
log('[單位] 搬移預放單位 %d 個（有名字的 %d 個），略過掉寶觸發 %d 行'
    % (n_units, len(named), skipped))
for cur_, a, b in named:
    log('        %s：%s → %s' % (cur_, a, b))

# ---- 測試用傳送指令 -tp1 / -tp2（正式版會拿掉）----
TPS = [(nm, hero[0] + SHIFT[nm][0], hero[1] + SHIFT[nm][1]) for nm, rect, dest, hero in PLACES]
tp_func = ('function udB_TpActions takes nothing returns nothing\n'
           'local player p=GetTriggerPlayer()\nlocal integer n=GetPlayerId(p)+1\n'
           'local string s=GetEventPlayerChatString()\nlocal real x=0.\nlocal real y=0.\n')
for k, (nm, x, y) in enumerate(TPS):
    tp_func += '%sif s=="-tp%d" then\nset x=%.1f\nset y=%.1f\n' % ('' if k == 0 else 'else', k + 1, x, y)
tp_func += ('endif\nif udg_Hero[n]!=null then\ncall SetUnitPosition(udg_Hero[n],x,y)\nendif\n'
            'call PanCameraToTimedForPlayer(p,x,y,0)\n'
            'call DisplayTimedTextToPlayer(p,0,0,10,"|cFF00FF00[測試] 傳送到 "+s)\nendfunction\n'
            'function udB_InitTp takes nothing returns nothing\nlocal trigger t=CreateTrigger()\n'
            'local integer i=0\nloop\nexitwhen i>7\n')
for k in range(len(TPS)):
    tp_func += 'call TriggerRegisterPlayerChatEvent(t,Player(i),"-tp%d",true)\n' % (k + 1)
tp_func += 'set i=i+1\nendloop\ncall TriggerAddAction(t,function udB_TpActions)\nset t=null\nendfunction\n'
for nm, x, y in TPS:
    log('[測試] -tp%d → %s (%.0f, %.0f)' % (TPS.index((nm, x, y)) + 1, nm, x, y))

# 寫進腳本
J = J.replace('endglobals', '\n'.join(globals_add) + '\nendglobals', 1)
k = J.index('\nfunction main takes')
J = J[:k] + '\n' + func + tp_func.rstrip('\n') + J[k:]
a = 'call CreateAllUnits()\n'
assert J.count(a) == 1
J = J.replace(a, a + 'call udB_CreateTransplantUnits()\n')
s, e_ = func_span(J, 'main')
body = J[s:e_]
body = body[:body.rindex('endfunction')] + 'call udB_InitTp()\nendfunction'
J = J[:s] + body + J[e_:]
for a_, b_ in (('function', 'endfunction'), ('loop', 'endloop'), ('if', 'endif')):
    na = len(re.findall(r'^\s*%s\b' % a_, J, re.M)); nb = len(re.findall(r'^\s*%s\b' % b_, J, re.M))
    assert na == nb, (a_, na, nb)

# ================================================================ 階段 C：經典關卡
import json
import ud_stageC
J185 = rd('ud_vers', '000肥羊的聖誕禮物1.85_ty.w3x.j').decode('utf-8', 'replace')
CAMPS = {c['id']: c for c in json.load(open(os.path.join(BASE, 'ud_icecamps.json'), encoding='utf-8'))}
isx, isy = SHIFT['寒冰洞窟']
CAMP_DEF = [(9, ['n02Z', 'n02X', 'n02X'], 'Unit000612_DropItems'),     # 冰原熊窟：巨大北極熊（沿用新版掉寶）
            (7, ['n053', 'n02H', 'n02H'], 'udC_DropT2'),               # 雪原族長老
            (13, ['n044', 'n03M', 'n03M'], 'udC_DropT2')]              # 花崗岩魔像
ctx = dict(tomb_shift=SHIFT['陵墓上層'], ice_shift=SHIFT['寒冰洞窟'],
           tomb_zone141=(-13728.0, 4576.0, -5056.0, 13440.0), ice_zone141=(-13536.0, -6368.0, -7904.0, 2624.0),
           tomb_area=DEST_WRECT[0][0], ice_area=DEST_WRECT[1][0],
           ice_camps=[(CAMPS[i]['x'] + isx, CAMPS[i]['y'] + isy, ts, drop) for i, ts, drop in CAMP_DEF])
# 掉寶函式必須定義在選單（插入點）之前
assert J.index('function Unit000612_DropItems') < J.index('function Trig_LvlCategories_Actions')
J = ud_stageC.apply(J, J185, ctx, log)
for a_, b_ in (('function', 'endfunction'), ('loop', 'endloop'), ('if', 'endif')):
    na = len(re.findall(r'^\s*%s\b' % a_, J, re.M)); nb = len(re.findall(r'^\s*%s\b' % b_, J, re.M))
    assert na == nb, (a_, na, nb)

# ================================================================ 階段 E：中文化
import ud_translate
from w3obj_rewrite import rewrite
J23 = rd('ud_vers', '000肥羊的聖誕禮物_2.3.0_ty.w3x.j').decode('utf-8', 'replace')
# 修正：詛咒者之弩 I08I 的疾病用了未初始化的 u（應為攻擊者 a），會讓整段觸發中斷
_bug = 'call VulnerabilityUnit(a,d,1.00)\ncall DiseaseUnit(u,d,dmg,0.50)'
assert J.count(_bug) == 1
J = J.replace(_bug, 'call VulnerabilityUnit(a,d,1.00)\ncall DiseaseUnit(a,d,dmg,0.50)')
log('[修正] 詛咒者之弩 I08I：疾病的施加者 u → a')
# 修正：相位石 rre1/rhe1/rdis 是撿起即用的道具，用掉時會觸發「丟下」事件；新版的 DB_Apply
# 在丟下時把技能強度扣回去，結果等於沒加（3.82fix 只在撿起時加、丟下不處理）
_a = "if not HaveSavedInteger(hash,'ItDB',ItemID)then\n"
assert J.count(_a) == 1
J = J.replace(_a, "if sign==-1 and(ItemID=='rre1' or ItemID=='rhe1' or ItemID=='rdis')then\nreturn true\nendif\n" + _a)
log('[修正] 相位石：技能強度改回永久（用掉時不再扣回）')
import ud_princess
J = ud_princess.patch_jass(J)
import ud_invasion
J = ud_invasion.patch_jass(J)
log('[入侵] 一般難度第 11／12 波換回無序法師、大墓地之主（對齊 2.1.0）；第 7 波王「被褻瀆者」加回惡魔變身（生命 <%d%% 時變身）；軍械庫 +75%%' % ud_invasion.META_HP)
for _m, _n in ud_invasion.N4.items():
    log('[入侵] %s難度守右下王座的第 %s 波改四路：出怪點 %d 處、發怪區塊 %d 個、隨機點 %d 處'
        % (_m, '/'.join(map(str, ud_invasion.FOUR[_m][1])), _n['points'], _n['blocks'], _n['rand']))
import ud_recipefix
J = ud_recipefix.patch_jass(J)
log('[對齊網站] 神器合成：水晶項鍊、鋼鐵奉獻、泰坦神拳 換回 3.82fix 的 4 件配方，價值 5400')
log('[改版] 亡者公主 R：擊殺 → 其他技能與道具重置、R 冷卻 8 秒；未擊殺 → 50 秒')
import ud_itemfix
TR = ud_translate.Translator(J, J23)
if RU:
    TR.__class__ = type('NoTR', (ud_translate.Translator,), {'__call__': lambda self, s, strict=False: None})
MSRC = mpq.MPQ(SRC)
ITEM_ABIL = set(json.load(open(os.path.join(BASE, 'ud_item_abils.json'))))   # 道具用到的技能：嚴格模式
OBJ_EDITS = {}
for f, lv in (('war3map.w3t', False), ('war3map.w3u', False), ('war3map.w3a', True), ('war3map.w3q', True), ('war3map.w3h', False)):
    src = MSRC.read(f)
    if f == 'war3map.w3a':
        src = ud_princess.patch_w3a(src)
    if f == 'war3map.w3t':
        src = ud_recipefix.patch_w3t(src)
    if f == 'war3map.w3u':
        src = ud_invasion.patch_w3u(src)

    def _fn(k, m, i, s, f=f):
        z = TR(s, strict=(f == 'war3map.w3t' or (f == 'war3map.w3a' and k in ITEM_ABIL)))
        if RU:
            return z
        if f == 'war3map.w3t':
            z = ud_itemfix.apply(k, m, z)
        elif f == 'war3map.w3a':
            z = ud_princess.text(k, m, z)
        return z
    data, n = rewrite(src, lv, _fn)
    OBJ_EDITS[f] = data
    log('[中文化] %s：改寫 %d 個字串' % (f, n))
if not RU:
    log('[說明修正] 道具說明改成與程式一致：%d 處' % ud_itemfix.check())
    assert ud_princess.hits['r'] >= 2, '亡者公主 R 的說明沒改到'
J, nj, sk = ud_translate.jass_strings(J, TR)
import ud_menutidy
J, _nt = (J, 0) if RU else ud_menutidy.tidy(J)
log('[中文化] 選單文字統一格式：%d 處' % _nt)
log('[中文化] war3map.j：改寫 %d 個字串，%d 行屬程式邏輯（聊天指令、名稱比對）刻意不動' % (nj, sk))
OBJ_EDITS['war3map.wts'], nw = ud_translate.wts_strings(ud_invasion.patch_wts(MSRC.read('war3map.wts')), TR)
log('[中文化] war3map.wts：改寫 %d 個字串' % nw)
tot = sum(TR.used.values()) + sum(TR.missing.values())
log('[中文化] 片段 %d 個：%s；尚未翻譯 %d 個（%d 種）'
    % (tot, '、'.join('%s %d' % kv for kv in TR.used.most_common()), sum(TR.missing.values()), len(TR.missing)))
log('[中文化] 一致性修正：2.3.0 舊譯名換成網站譯名 %d 處（對照 %d 組）' % (TR.renamed, len(TR.rename)))
if not RU:
    json.dump(TR.missing.most_common(), open(os.path.join(BASE, 'ud_tr_missing.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
for a_, b_ in (('function', 'endfunction'), ('loop', 'endloop'), ('if', 'endif')):
    na = len(re.findall(r'^\s*%s\b' % a_, J, re.M)); nb = len(re.findall(r'^\s*%s\b' % b_, J, re.M))
    assert na == nb, (a_, na, nb)

W3E_B, WPM_B, SHD_B = bytes(W3E_B), bytes(WPM_B), bytes(SHD_B)

# ---- 小地圖 ----
def prect(w):
    return (e.ox + w.comp[2] * 128, e.oy + w.comp[1] * 128,
            e.ox + (w.comp[2] + w.pw) * 128, e.oy + (w.comp[1] + w.ph) * 128)
R0, R1 = prect(wi), prect(wi2)
old_img = Image.open(io.BytesIO(mpq.MPQ(SRC).read('war3mapMap.blp')))   # 新版原始小地圖
cx, cy = mm.world_to_px(R0, e.ox + 72 * 128, e.oy + 60 * 128)
px = old_img.convert('RGB').load()
cs = [px[int(cx) + dx, int(cy) + dy] for dx in range(-2, 3) for dy in range(-2, 3)]
dirt = tuple(sum(c[i] for c in cs) // len(cs) for i in range(3))
OLD_TOP = e.oy + (e.h - 1) * 128
old141 = Image.open(io.BytesIO(mpq.MPQ(OLD).read('war3mapMap.blp'))).convert('RGB')
p141 = old141.load()
def fill(wx, wy):
    for (x0, y0, x1, y1), (dx, dy) in DEST_WRECT:          # 搬過來的戰場：取 1.41 小地圖同一點
        if x0 <= wx < x1 and y0 <= wy < y1:
            u, v = mm.world_to_px(R0, wx - dx, wy - dy)
            return p141[min(255, max(0, int(u))), min(255, max(0, int(v)))]
    return None                                             # 其餘新地：黑
new_img = mm.remap(old_img, R0, R1, fill)
new_img.save(os.path.join(BASE, 'ud_build_minimap.png'))
BLP_B = mm.blp1_palette(new_img)
MMP_B = mm.remap_mmp(mpq.MPQ(SRC).read('war3map.mmp'), R0, R1)
log('[小地圖] 依新可玩區重排')

# ================================================================ 寫檔
# w3i：大廳顯示的地圖說明、玩家與勢力名稱
W3I_TR = [(u'Карта жанра Defence с возможностью сохранения игровых очков и получения доступа к новым героям и полям боя.',
           u'防守類地圖，可存檔積分並解鎖新英雄與新戰場。'),
          (u'\x00Союзники\x00', u'\x00友軍\x00'), (u'\x00Враги\x00', u'\x00敵人\x00'),
          (u'Защитники\x00', u'守護者\x00'), (u'\x002-6\x00', u'\x001-8\x00')]
for i in range(1, 9):
    W3I_TR.append((u'\x00Игрок %d\x00' % i, u'\x00玩家 %d\x00' % i))
for a, b in W3I_TR:
    W3I_B = W3I_B.replace(a.encode('utf-8'), b.encode('utf-8'))
log('[中文化] war3map.w3i：大廳文字 %d 組' % len(W3I_TR))
EDITS = {'war3map.j': J.encode('utf-8', 'surrogateescape'), 'war3map.w3i': W3I_B,
         'war3map.w3e': W3E_B, 'war3map.wpm': WPM_B, 'war3map.shd': SHD_B,
         'war3mapMap.blp': BLP_B, 'war3map.mmp': MMP_B, 'war3map.doo': DOO_B}
EDITS.update(OBJ_EDITS)
import ud_skin
EDITS['war3map.j'] = ud_skin.ver(EDITS['war3map.j'])
EDITS['war3map.w3i'] = ud_skin.ver(EDITS['war3map.w3i'])
if not RU:
    EDITS['war3mapSkin.txt'] = ud_skin.skin(MSRC.read('war3mapSkin.txt'))
log('[版本] UD test %s → %s（資源列、地圖名稱、檔頭）；遊戲介面文字中文化' % (ud_skin.OLD_VER, ud_skin.VERSION))
out = os.path.join(BASE, OUTNAME)
if os.path.exists(out):
    os.remove(out)
mpq_patch.write_files(SRC, out, EDITS)
with open(out, 'r+b') as f:
    h = bytearray(f.read(512)); z = h.index(b'\x00', 8)
    h = bytearray(ud_skin.ver(bytes(h)))
    struct.pack_into('<i', h, z + 5, 8); f.seek(0); f.write(h)
m = mpq.MPQ(out)
assert all(m.read(k) == v for k, v in EDITS.items())
if not RU:
    open(os.path.join(BASE, 'ud_build_E.j'), 'wb').write(EDITS['war3map.j'])
dst = os.path.join(MAPS, OUTNAME)
if not RU:
    shutil.copy(out, dst)
else:
    dst = out
log('[完成] %s  %.1f MB，讀回一致 → %s' % (OUTNAME, os.path.getsize(out) / 1048576,
                                         '已放到 Maps' if os.path.exists(dst) else '複製失敗'))
