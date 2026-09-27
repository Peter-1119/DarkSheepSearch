# -*- coding: utf-8 -*-
"""修復「弓箭手小生存 2.0.8」的脫機版。

這份 2.0.8 已經被人脫機化過（平台的 DzAPI／EX* 函式被換成寫死的空殼），
但擴充的 unit state（攻擊力／攻擊範圍／攻速／護甲…）沒辦法用空殼補，
所以一整套屬性系統在脫機下是壞的。這支工具逐項把它補回來。

用法：
    python tools/patch_archer.py                       # 用預設路徑，輸出 *_fix.w3x
    python tools/patch_archer.py 來源.w3x 目標.w3x

每一項改動都在下面的 FIXES 裡，各自獨立、可以單獨關掉。
改完會驗證：改過的檔讀得回來、其他檔案逐位元組沒變。
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mpq import MPQ
import mpq_patch

SRC = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/弓箭手小生存2.0.8.w3x'


# --------------------------------------------------------------- 各項修正
def fix_plunder_tooltip(w3a, m):
    """掠奪箭矢：說明寫「敵人怪物等級×3」，程式實際是波數／分鐘數。

    Trig_j13Actions 7151-7158：
        if udg_moshi==2 then  金錢 += udg_fen*5/4      （防守模式，udg_fen＝遊戲分鐘數）
        else                  金錢 += udg_boshu*3      （無盡模式，udg_boshu＝波數）
    照使用者的決定：只改說明、不動數值。
    """
    old = ('|cffFFFF00攻击有15%几率获得敌人怪物等级*3金钱。'
           '|r|n|n|cff808080点击可以重新随机箭矢')
    new = ('|cffFFFF00攻击有15%几率获得金钱。无尽模式：波数*3；防守模式：游戏分钟数*1.25。'
           '|r|n|n|cff808080点击可以重新随机箭矢')
    ob, nb = old.encode('utf-8'), new.encode('utf-8')
    if w3a.count(ob) != 1:
        raise SystemExit('掠奪箭矢說明找到 %d 次（要剛好 1 次）' % w3a.count(ob))
    return w3a.replace(ob, nb, 1), '掠奪箭矢說明 -> 波數／分鐘數'



def fix_str_perm(jass, m):
    """剩下 6 處 SetHeroStr(...,false) 全部改成 true。

    false 的意思是「設定總力量」，不是「加基礎力量」：
        SetHeroStr(英雄, GetHeroStr(英雄,false)+N, false)
    讀的是基礎值、寫的是總值，所以第二次再加同樣會變成「基礎+N」——
    加成不累加，而且把別的來源給的綠字力量一起洗掉。

    這 6 處旁邊就是同一段的敏捷與智力，作者那兩個都寫 true。
    連「撿起／丟掉裝備」那種正負成對的寫法，敏捷智力也是 true（加基礎、
    減基礎，兩邊對稱），所以這 6 處是同一個筆誤。
    """
    lines = jass.split('\n')
    hits = []
    for i, l in enumerate(lines):
        k = l.find('call SetHeroStr(')
        if k < 0:
            continue
        k += len('call SetHeroStr(')
        d, j = 1, k
        while d:
            if l[j] == '(':
                d += 1
            elif l[j] == ')':
                d -= 1
            j += 1
        if l[k:j - 1].rsplit(',', 1)[1] == 'false':
            lines[i] = l[:j - len('false)')] + 'true)' + l[j:]
            hits.append(i + 1)
    if len(hits) != 6:
        raise SystemExit('SetHeroStr(...,false) 找到 %d 處（預期 6 處）' % len(hits))
    return '\n'.join(lines), '力量加成 false -> true：%d 處（裝備、翅膀、吞噬）' % len(hits)


def fix_str_arrow(jass, m):
    """力量箭矢：加成與還原都用 SetHeroStr(...,false)，敏捷／智力用的是 true。

    false ＝ 不是永久加成，英雄升級時屬性會重算、把加成抹掉；
    3 秒後的還原卻照扣，力量就永久少一截。改成跟另外兩個一致。
    """
    # 整行比對，避免正規式把括號結構寫錯。只改「最後那個」false —— 中間
    # GetHeroStr(...,false) 讀的是基礎值，那個 false 是對的，不能動。
    T = 'GetHandleId(GetTriggeringTrigger())*ydl_localvar_step'
    E = 'GetHandleId(GetExpiredTimer())'
    add = ('call SetHeroStr(LoadUnitHandle(YDLOC,%s,0x911D5DC2),'
           '(GetHeroStr(LoadUnitHandle(YDLOC,%s,0x911D5DC2),false)'
           '+LoadInteger(YDLOC,%s,0x1B5C932E)),false)' % (T, T, T))
    rem = ('call SetHeroStr(LoadUnitHandle(YDLOC,%s,0x911D5DC2),'
           '(GetHeroStr(LoadUnitHandle(YDLOC,%s,0x911D5DC2),false)'
           '-LoadInteger(YDLOC,%s,0x1B5C932E)),false)' % (E, E, E))
    out = jass
    for line in (add, rem):
        if out.count(line) != 1:
            raise SystemExit('力量箭矢這一行找到 %d 次（要剛好 1 次）：%s'
                             % (out.count(line), line[:60]))
        out = out.replace(line, line[:-len('false)')] + 'true)', 1)
    return out, '力量箭矢 SetHeroStr false -> true（加成與還原各一處）'


# ------------------------------------------------- 屬性帳本（第 2 步的核心）
# 平台的擴充 unit state 在脫機下讀寫都無效（讀到 0、寫進去沒作用），
# 整個商店升級、買裝備、六個天賦、兩種箭矢都因此壞掉。
# 這裡改成自己記一本帳，再用 1.29.2 就有的原生 API 套用到單位上。
#
#   0x11/0x12 最大/最小攻擊 —— 這兩個是「寫入端」，地圖拿來記加成的帳
#   0x13/0x14/0x15 綠字/總最小/總最大 —— 這三個原地圖只讀不寫，是平台算好
#     的「含屬性在內的實際總攻擊」。所以 0x14/0x15 要回報單位當下的真實數值，
#     不能回報帳本 —— 不然冰霜（攻擊×2.2）與「攻擊力+X%」的基數會少掉屬性那份。
#   0x16 攻擊範圍  0x20 護甲      0x25 攻擊間隔  0x51 攻速倍率（1.0＝基準）
#
# 攻擊力**不寫「基礎傷害」欄位** —— 那一欄的合法上限只有 1000，弓一升階就爆，
# 而且硬寫會把英雄屬性帶來的攻擊一起蓋掉。改成：
#   最小與最大共通的那一段  -> 科技加成（白字，上限 50990）
#   最大比最小多出來的那段  -> 骰面（骰面不是從屬性算的，引擎不會重算）
# 兩者相加就是帳本要的 [最小, 最大]，而且完全不碰引擎自己管的基礎傷害。
#
# 帳本的 hash 子鍵用 0x415243xx（'ARC' + 狀態編號），跟地圖原本用的鍵不會撞。
LEDGER = """
function ArcherApplyBlink takes unit u returns nothing
local integer n
if u==null then
return
endif
if GetUnitAbilityLevel(u,'A01B')<=0 then
return
endif
set n=GetPlayerTechCount(GetOwningPlayer(u),'R00M',true)+1
if n<1 then
set n=1
endif
if n>11 then
set n=11
endif
if GetUnitAbilityLevel(u,'A01B')==n then
return
endif
call SetUnitAbilityLevel(u,'A01B',n)
endfunction
function ArcherStateInit takes unit u returns nothing
local integer id=GetHandleId(u)
local integer b
local integer k
local integer t
local real r
if LoadBoolean(YDHT,id,0x41524300) then
return
endif
call SaveBoolean(YDHT,id,0x41524300,true)
set t=GetUnitTypeId(u)
set k=0
if BlzGetUnitDiceSides(u,0)<=0 then
set k=1
endif
call SaveReal(YDHT,id,0x41524323,I2R(k))
set r=ArcherSlkReal(t,7)
if r<=0. then
set b=BlzGetUnitBaseDamage(u,k)
set r=I2R(b+BlzGetUnitDiceNumber(u,k))
call SaveReal(YDHT,id,0x41524311,I2R(b+BlzGetUnitDiceNumber(u,k)*BlzGetUnitDiceSides(u,k)))
else
call SaveReal(YDHT,id,0x41524311,ArcherSlkReal(t,8))
endif
call SaveReal(YDHT,id,0x41524312,r)
call SaveReal(YDHT,id,0x41524319,LoadReal(YDHT,id,0x41524312))
call SaveReal(YDHT,id,0x4152431C,LoadReal(YDHT,id,0x41524311))
call SaveReal(YDHT,id,0x4152431D,I2R(BlzGetUnitDiceSides(u,k)))
call SaveReal(YDHT,id,0x4152431E,I2R(BlzGetUnitDiceNumber(u,k)))
call SaveReal(YDHT,id,0x41524313,0.)
set r=ArcherSlkReal(t,6)
if r<=0. then
set r=GetUnitAcquireRange(u)
endif
call SaveReal(YDHT,id,0x41524316,r)
set r=ArcherSlkReal(t,10)
call SaveReal(YDHT,id,0x4152431A,r)
call SaveReal(YDHT,id,0x41524320,r)
call SaveReal(YDHT,id,0x4152431B,0.)
set r=ArcherSlkReal(t,9)
if r<=0. then
set r=BlzGetUnitAttackCooldown(u,k)
endif
call SaveReal(YDHT,id,0x41524321,r)
call SaveReal(YDHT,id,0x41524325,r)
call SaveReal(YDHT,id,0x41524322,0.)
call SaveReal(YDHT,id,0x41524351,1.00)
call ArcherApplyBlink(u)
endfunction
function ArcherStateApplyAttack takes unit u returns nothing
local integer id=GetHandleId(u)
local integer dmin=R2I(LoadReal(YDHT,id,0x41524312)-LoadReal(YDHT,id,0x41524319))
local integer dmax=R2I(LoadReal(YDHT,id,0x41524311)-LoadReal(YDHT,id,0x4152431C))
local integer d0=R2I(LoadReal(YDHT,id,0x4152431E))
local integer cur=R2I(LoadReal(YDHT,id,0x41524313))
local integer s
local integer want
local integer k
local integer lo
local integer hi
if d0<1 then
set d0=1
endif
if dmin<0 then
set dmin=0
endif
if dmax<dmin then
set dmax=dmin
endif
set k=R2I(LoadReal(YDHT,id,0x41524323))
set lo=R2I(LoadReal(YDHT,id,0x4152431D))
set hi=(dmax-dmin)/d0+lo
if hi<1 then
set hi=1
endif
if hi>10000 then
set hi=10000
endif
call BlzSetUnitDiceSides(u,hi,k)
if BlzGetUnitDiceSides(u,k)==hi then
set want=dmin
else
set want=dmin+(dmax-dmin)/2
endif
if want<0 then
set want=0
endif
if want>50999 then
set want=50999
endif
if want==cur then
return
endif
call SaveReal(YDHT,id,0x41524313,I2R(want))
set s=want
call SetPlayerTechResearched(GetOwningPlayer(u),'R00P',s/1000)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00Q',(s/100)-(s/1000)*10)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00R',(s/10)-(s/100)*10)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00U',s-(s/10)*10)
endfunction
function ArcherStateApplyArmor takes unit u returns nothing
local integer id=GetHandleId(u)
local integer want=R2I(LoadReal(YDHT,id,0x41524320)-LoadReal(YDHT,id,0x4152431A))
local integer cur=R2I(LoadReal(YDHT,id,0x4152431B))
if want==cur then
return
endif
call YDWEGeneralBounsSystemUnitSetBonus(u,2,0,want-cur)
call SaveReal(YDHT,id,0x4152431B,I2R(want))
endfunction
function ArcherSpAbil takes integer i returns integer
if i==0 then
return 'ASp1'
elseif i==1 then
return 'ASp2'
elseif i==2 then
return 'ASp3'
elseif i==3 then
return 'ASp4'
elseif i==4 then
return 'ASp5'
elseif i==5 then
return 'ASp6'
elseif i==6 then
return 'ASp7'
elseif i==7 then
return 'ASp8'
endif
return 'ASp9'
endfunction
function ArcherStateApplySpeed takes unit u returns nothing
local integer id=GetHandleId(u)
local real cd=LoadReal(YDHT,id,0x41524325)
local real sp=LoadReal(YDHT,id,0x41524351)
local real cd0=LoadReal(YDHT,id,0x41524321)
local integer pct
local integer v
local integer i
local real rate
if sp<0.10 then
set sp=0.10
endif
if cd<0.05 then
set cd=0.05
endif
if cd0<=0. then
return
endif
set rate=(cd0*sp)/cd
if rate<0.05 then
set rate=0.05
endif
set pct=R2I((rate-1.)*100.)
if pct>511 then
set pct=511
endif
if pct==R2I(LoadReal(YDHT,id,0x41524322)) then
return
endif
call SaveReal(YDHT,id,0x41524322,I2R(pct))
if pct<0 then
call BlzSetUnitAttackCooldown(u,cd0/rate,R2I(LoadReal(YDHT,id,0x41524323)))
set pct=0
else
call BlzSetUnitAttackCooldown(u,cd0,R2I(LoadReal(YDHT,id,0x41524323)))
endif
set v=pct
set i=0
loop
exitwhen i>8
if ModuloInteger(v,2)==1 then
call UnitAddAbility(u,ArcherSpAbil(i))
call UnitMakeAbilityPermanent(u,true,ArcherSpAbil(i))
else
call UnitRemoveAbility(u,ArcherSpAbil(i))
endif
set v=v/2
set i=i+1
endloop
endfunction
function ArcherApplyRange takes unit u,real v returns nothing
local real base=ArcherSlkReal(GetUnitTypeId(u),6)
local integer e
if base<=0. then
return
endif
set e=R2I((v-base)/10.)
if e<0 then
set e=0
endif
if e>209 then
set e=209
endif
call SetPlayerTechResearched(GetOwningPlayer(u),'R00N',e/10)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00O',e-(e/10)*10)
endfunction
function ArcherGetState takes unit u,integer st returns real
local integer id
local integer b
if u==null then
return 0.
endif
call ArcherStateInit(u)
set id=GetHandleId(u)
if st==0x11 then
return LoadReal(YDHT,id,0x41524311)
endif
if st==0x12 then
return LoadReal(YDHT,id,0x41524312)
endif
if st==0x15 or st==0x14 then
set b=R2I(LoadReal(YDHT,id,0x41524323))
if st==0x15 then
return I2R(BlzGetUnitBaseDamage(u,b)+BlzGetUnitDiceNumber(u,b)*BlzGetUnitDiceSides(u,b))
endif
return I2R(BlzGetUnitBaseDamage(u,b)+BlzGetUnitDiceNumber(u,b))
endif
if st==0x16 then
return LoadReal(YDHT,id,0x41524316)
endif
if st==0x20 then
return LoadReal(YDHT,id,0x41524320)
endif
if st==0x25 then
return LoadReal(YDHT,id,0x41524325)
endif
if st==0x51 then
return LoadReal(YDHT,id,0x41524351)
endif
return 0.
endfunction
function ArcherSetState takes unit u,integer st,real v returns nothing
local integer id
if u==null then
return
endif
call ArcherStateInit(u)
call ArcherApplyBlink(u)
set id=GetHandleId(u)
if st==0x11 then
call SaveReal(YDHT,id,0x41524311,v)
call ArcherStateApplyAttack(u)
elseif st==0x12 then
call SaveReal(YDHT,id,0x41524312,v)
call ArcherStateApplyAttack(u)
elseif st==0x16 then
call SaveReal(YDHT,id,0x41524316,v)
call SetUnitAcquireRange(u,v)
call ArcherApplyRange(u,v)
elseif st==0x20 then
call SaveReal(YDHT,id,0x41524320,v)
call ArcherStateApplyArmor(u)
elseif st==0x25 then
call SaveReal(YDHT,id,0x41524325,v)
call ArcherStateApplySpeed(u)
elseif st==0x51 then
call SaveReal(YDHT,id,0x41524351,v)
call ArcherStateApplySpeed(u)
endif
endfunction
function ArcherSpeedPct takes unit u returns real
return (ArcherGetState(u,0x51)-1.)*100.+I2R(GetHeroAgi(u,true))*%AGI%
endfunction
"""

# 帳本要插在第一個用到它的函式之前（JASS 規定先宣告後使用）。
# 帳本要排在「虛擬技能加成系統」（原檔第 2042 行）之後才呼叫得到，又要排在所有
# 用到它的觸發之前 —— 最早的是 Trig_x6Actions（第 5031 行，撿道具）。
# Trig_c2Actions 在第 3236 行，剛好夾在中間。
LEDGER_ANCHOR = 'function Trig_c2Actions takes nothing returns nothing\n'

EXT_STATES = (0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x20, 0x25, 0x51)


def _args(s, i):
    """i 指到 '('，回傳 (頂層參數清單, 右括號位移)。"""
    d, cur, out = 0, '', []
    for k in range(i, len(s)):
        c = s[k]
        if c == '(':
            d += 1
            if d == 1:
                continue
        elif c == ')':
            d -= 1
            if d == 0:
                out.append(cur)
                return out, k
        if d == 1 and c == ',':
            out.append(cur)
            cur = ''
            continue
        cur += c
    raise SystemExit('括號沒配對')


def fix_ledger(jass, m):
    """插入帳本，並把所有擴充狀態的讀寫換成呼叫帳本。"""
    if jass.count(LEDGER_ANCHOR) != 1:
        raise SystemExit('帳本的插入點出現 %d 次' % jass.count(LEDGER_ANCHOR))
    out = jass.replace(LEDGER_ANCHOR, LEDGER + LEDGER_ANCHOR, 1)

    conv = re.compile(r'^ConvertUnitState\((0x[0-9A-Fa-f]+)\)$')
    changed, skipped = [], 0
    for fname, new in (('GetUnitState', 'ArcherGetState'),
                       ('SetUnitState', 'ArcherSetState')):
        while True:
            i = out.find(fname + '(')
            hit = False
            pos = 0
            while True:
                i = out.find(fname + '(', pos)
                if i < 0:
                    break
                a, end = _args(out, i + len(fname))
                m = conv.match(a[1].strip()) if len(a) >= 2 else None
                if m and int(m.group(1), 16) in EXT_STATES:
                    st = int(m.group(1), 16)
                    rest = [a[0]] + ['0x%02X' % st] + [x for x in a[2:]]
                    out = out[:i] + new + '(' + ','.join(rest) + ')' + out[end + 1:]
                    changed.append((fname, st))
                    hit = True
                    break
                pos = i + 1
            if not hit:
                break
    left = sum(1 for m in re.finditer(r'ConvertUnitState\((0x[0-9A-Fa-f]+)\)', out)
               if int(m.group(1), 16) in EXT_STATES)
    if left:
        raise SystemExit('還有 %d 處擴充狀態沒換掉' % left)
    g = sum(1 for f, _ in changed if f == 'GetUnitState')
    s = len(changed) - g
    return out, ('屬性帳本：插入 5 支函式，換掉 %d 處（讀 %d／寫 %d）' % (len(changed), g, s))


# ------------------------------------------------- 本機存檔（第 5 步）
# 原本的進度存在平台伺服器，脫機後 DzAPI_Map_GetServerValue 回傳 ""、
# 而錯誤碼回傳 0 讓地圖以為「存檔成功」—— 所以看得到成功訊息，下一場卻是空的。
#
# 這裡做兩件事：
#   1. 把平台的 key-value 儲存換成地圖自己的 hashtable（同一場內先變得一致）
#   2. 加 -save / -load，把進度變成一串可以抄下來的代碼
#
# 時序：進度在開場 0.11 秒就被讀走（Trig_c5Func013A），玩家來不及打字，
# 所以把「套用加成」那一段（Trig_c5Func015A）延後到 45 秒，
# 並讓 -load 重跑一次讀取。45 秒內選模式還來得及，第一波是 100~150 秒後。
SAVE_KEYS = ['FENGMANG', 'WUJIN', 'FSCS', 'JIANHUN', 'JIANBAO',
             'banben', 'FM2', 'JH2', 'JB2', 'zixuan']

SAVECODE = """
function ArcherB32 takes integer n returns string
local string s=""
local integer d
if n<=0 then
return "0"
endif
loop
exitwhen n<=0
set d=n-(n/32)*32
set s=SubString("0123456789ABCDEFGHJKMNPQRSTUVWXY",d,d+1)+s
set n=n/32
endloop
return s
endfunction
function ArcherUnB32 takes string s returns integer
local integer i=0
local integer n=0
local integer d
local string c
if StringLength(s)==0 then
return -1
endif
loop
exitwhen i>=StringLength(s)
set c=SubString(s,i,i+1)
set d=0
loop
exitwhen d>=32
exitwhen SubString("0123456789ABCDEFGHJKMNPQRSTUVWXY",d,d+1)==c
set d=d+1
endloop
if d>=32 then
return -1
endif
set n=n*32+d
set i=i+1
endloop
return n
endfunction
function ArcherField takes string s,integer want returns string
local integer i=0
local integer f=0
local string out=""
local string c
loop
exitwhen i>=StringLength(s)
set c=SubString(s,i,i+1)
if c=="-" then
set f=f+1
if f>want then
return out
endif
else
if f==want then
set out=out+c
endif
endif
set i=i+1
endloop
return out
endfunction
function ArcherSaveCode takes player p returns string
local string s=""
local integer sum=0
local integer v
local integer i=0
loop
exitwhen i>%(N)d
set v=DzAPI_Map_GetStoredInteger(p,ArcherKeyName(i))
if v<0 then
set v=0
endif
set sum=sum+v*(i+1)
set s=s+ArcherB32(v)+"-"
set i=i+1
endloop
return s+ArcherB32(sum-(sum/7777)*7777)
endfunction
function ArcherLoadCode takes player p,string sv returns boolean
local integer i=0
local integer sum=0
local integer v
loop
exitwhen i>%(N)d
set v=ArcherUnB32(ArcherField(sv,i))
if v<0 then
return false
endif
set sum=sum+v*(i+1)
set i=i+1
endloop
if ArcherUnB32(ArcherField(sv,%(N)d+1))!=sum-(sum/7777)*7777 then
return false
endif
set i=0
loop
exitwhen i>%(N)d
call DzAPI_Map_StoreInteger(p,ArcherKeyName(i),ArcherUnB32(ArcherField(sv,i)))
set i=i+1
endloop
return true
endfunction
function ArcherSaveCmd takes nothing returns nothing
local player p=GetTriggerPlayer()
call DisplayTimedTextToPlayer(p,0,0,600.,"|cffFFCC00[存檔]|r 抄下這串，下一場開頭輸入 -load 加上它：")
call DisplayTimedTextToPlayer(p,0,0,600.,"|cff80FF80"+ArcherSaveCode(p)+"|r")
set p=null
endfunction
function ArcherLoadCmd takes nothing returns nothing
local player p=GetTriggerPlayer()
local string c=SubString(GetEventPlayerChatString(),6,StringLength(GetEventPlayerChatString()))
local force f
if ArcherLoadCode(p,c) then
set f=CreateForce()
call ForceAddPlayer(f,p)
call ForForce(f,function Trig_c5Func013A)
call DestroyForce(f)
set f=null
call DisplayTimedTextToPlayer(p,0,0,20.,"|cff80FF80[讀檔] 成功，進度已套用。|r")
else
call DisplayTimedTextToPlayer(p,0,0,20.,"|cffFF4040[讀檔] 代碼錯誤或抄錯了。|r")
endif
set p=null
endfunction
function ArcherSaveInit takes nothing returns nothing
local trigger t1=CreateTrigger()
local trigger t2=CreateTrigger()
local integer i=0
loop
exitwhen i>5
call TriggerRegisterPlayerChatEvent(t1,Player(i),"-save",true)
call TriggerRegisterPlayerChatEvent(t2,Player(i),"-load",false)
set i=i+1
endloop
call TriggerAddAction(t1,function ArcherSaveCmd)
call TriggerAddAction(t2,function ArcherLoadCmd)
set t1=null
set t2=null
endfunction
function ArcherApplyPerks takes nothing returns nothing
call ForForce(udg_wanjiazu,function Trig_c5Func015A)
call DestroyTimer(GetExpiredTimer())
endfunction
"""

KEYNAME = """
function ArcherKeyName takes integer i returns string
%(BODY)s
return ""
endfunction
"""

# 本機 key-value 儲存：取代平台那兩支空殼
LOCALSTORE_OLD = ('function DzAPI_Map_GetServerValue takes player whichPlayer, '
                  'string key returns string\nreturn ""\nendfunction\n')


def fix_savecode(jass, m):
    """換掉平台儲存的空殼，加上 -save / -load，並把套用加成延後到 45 秒。"""
    # 1) 本機儲存
    got = re.search(r'function DzAPI_Map_GetServerValue takes .*?\nendfunction\n',
                    jass, re.S)
    sav = re.search(r'function DzAPI_Map_SaveServerValue takes .*?\nendfunction\n',
                    jass, re.S)
    if not got or not sav:
        raise SystemExit('找不到平台儲存的空殼')
    new_get = ('function DzAPI_Map_GetServerValue takes player whichPlayer,'
               'string key returns string\n'
               'return LoadStr(YDHT,GetHandleId(whichPlayer),StringHash("ARCS"+key))\n'
               'endfunction\n')
    new_sav = ('function DzAPI_Map_SaveServerValue takes player whichPlayer,'
               'string key,string value returns boolean\n'
               'call SaveStr(YDHT,GetHandleId(whichPlayer),StringHash("ARCS"+key),value)\n'
               'return true\n'
               'endfunction\n')
    out = jass.replace(got.group(0), new_get, 1).replace(sav.group(0), new_sav, 1)

    # 2) 套用加成延後到 45 秒，讓玩家來得及 -load。
    #    這一步要在插入存檔區塊「之前」做 —— 區塊裡的 ArcherApplyPerks
    #    自己也有同一行，先插入的話就會數到兩次。
    old = 'call ForForce(udg_wanjiazu,function Trig_c5Func015A)\n'
    if out.count(old) != 1:
        raise SystemExit('套用加成那一行出現 %d 次' % out.count(old))
    out = out.replace(
        old,
        'call TimerStart(CreateTimer(),45.,false,function ArcherApplyPerks)\n'
        'call ArcherSaveInit()\n'
        'call DisplayTimedTextToForce(udg_wanjiazu,45.,'
        '"|cffFFCC00[本機存檔]|r 45 秒內可輸入 |cff80FF80-load 存檔碼|r 讀取進度；'
        '結束前輸入 |cff80FF80-save|r 取得存檔碼。")\n', 1)

    # 3) key 名稱查表（JASS 沒有字串陣列常數，用 if 鏈）＋存檔函式
    body = '\n'.join('if i==%d then\nreturn "%s"\nendif' % (i, k)
                     for i, k in enumerate(SAVE_KEYS))
    block = (KEYNAME % {'BODY': body}) + (SAVECODE % {'N': len(SAVE_KEYS) - 1})

    # 要放在 Trig_c5Func013A / Trig_c5Func015A 之後（會呼叫它們）
    anchor = 'function Trig_c5Actions takes nothing returns nothing\n'
    if out.count(anchor) != 1:
        raise SystemExit('存檔區塊的插入點出現 %d 次' % out.count(anchor))
    out = out.replace(anchor, block + anchor, 1)
    return out, ('本機存檔：-save/-load（%d 項進度）、平台儲存改成本機、'
                 '加成套用延後 45 秒' % len(SAVE_KEYS))


# ------------------------------------------------- SLK 查表橋（第 2 步：成長）
# 地圖用 EXExecuteScript("(require'jass.slk').unit[id].STRplus") 這種寫法，
# 在平台上會轉進 Lua 去讀物件編輯器的原始欄位。脫機版那支函式回傳空字串，
# 所以成長、道具售價、天賦圖示全部讀到 0 / 空白。
#
# 資料其實都在封包裡 —— Units\UnitBalance.slk 等檔只是被從 (listfile) 拿掉
# 名字而已。這裡把需要的欄位在編譯期抄出來，生成一張 JASS 查表。
#
# 子鍵：1=STRplus 2=AGIplus 3=INTplus 4=goldcost 5=技能圖示 6=攻擊距離
SLK_KEY = {'STRplus': 1, 'AGIplus': 2, 'INTplus': 3}

# 吞噬裝備的花費 ＝ 那件裝備的售價。脫機版原本讀不到售價（永遠 0），所以一直是
# 免費的；把查表接回去之後就恢復成要付費。使用者選擇維持免費，所以這裡直接回 0。
# 想恢復原價把這個改成 False 就好 —— 其他地方都沒有用到售價。
DEVOUR_FREE = True

SLK_FUNCS = """
function ArcherSlkInit takes nothing returns nothing
if ARCSLK!=null then
return
endif
set ARCSLK=InitHashtable()
%s
endfunction
function ArcherSlkReal takes integer t,integer k returns real
call ArcherSlkInit()
return LoadReal(ARCSLK,t,k)
endfunction
function ArcherSlkUnitGrowth takes integer t,integer k returns string
return R2S(ArcherSlkReal(t,k))
endfunction
function ArcherSlkItemGold takes integer t returns string
call ArcherSlkInit()
return I2S(LoadInteger(ARCSLK,t,4))
endfunction
function ArcherSlkAbilArt takes integer t returns string
call ArcherSlkInit()
return LoadStr(ARCSLK,t,5)
endfunction
"""

GLOBALS_ADD = """hashtable ARCSLK=null
integer array ARCDCA
integer array ARCDCD
integer ARCDCN=0
"""

ID4 = re.compile(r'^[A-Za-z0-9]{4}$')


def _slk_rows(m):
    import slk
    B = chr(92)
    bal, _ = slk.loads(m.read('Units' + B + 'UnitBalance.slk'))
    wep, _ = slk.loads(m.read('Units' + B + 'UnitWeapons.slk'))
    itm, _ = slk.loads(m.read('Units' + B + 'ItemData.slk'))
    return bal, wep, itm


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def fix_slk_bridge(jass, m):
    """把 Lua 查表換成編譯期抄好的 JASS 查表。"""
    import w3obj
    bal, wep, itm = _slk_rows(m)

    lines = []
    heroes = 0
    for uid, rec in sorted(bal.items()):
        if not ID4.match(uid):
            continue
        g = [_num(rec.get(k)) for k in ('STRplus', 'AGIplus', 'INTplus')]
        if not any(g):
            continue
        heroes += 1
        for k, v in zip((1, 2, 3), g):
            lines.append("call SaveReal(ARCSLK,'%s',%d,%.4f)" % (uid, k, v))
        w = wep.get(uid, {})
        rng = _num(w.get('rangeN1'))
        if rng > 0:
            lines.append("call SaveReal(ARCSLK,'%s',6,%.2f)" % (uid, rng))
        # 1.29.2 讀不到單位的武器資料，起始值只能在編譯期從資料表抄。
        # 真正的最大傷害要自己算 —— maxdmg1 那一欄是編輯器的過期快取，不能用
        # （H000 寫 12，實際打出來是 2）。
        dice, sides = _num(w.get('dice1')), _num(w.get('sides1'))
        lo = _num(w.get('mindmg1'))
        if lo > 0:
            hi = (lo - dice) + dice * sides
            lines.append("call SaveReal(ARCSLK,'%s',7,%.2f)" % (uid, lo))
            lines.append("call SaveReal(ARCSLK,'%s',8,%.2f)" % (uid, hi))
        cool = _num(w.get('cool1'))
        if cool > 0:
            lines.append("call SaveReal(ARCSLK,'%s',9,%.3f)" % (uid, cool))
        dfn = _num(bal.get(uid, {}).get('def'))
        if dfn != 0:
            lines.append("call SaveReal(ARCSLK,'%s',10,%.2f)" % (uid, dfn))

    items = 0
    for iid, rec in sorted(itm.items()):
        if not ID4.match(iid):
            continue
        gold = int(_num(rec.get('goldcost')))
        if gold <= 0:
            continue
        items += 1
        lines.append("call SaveInteger(ARCSLK,'%s',4,%d)" % (iid, gold))

    # 天賦多面板的圖示：只有多面板迴圈用得到的那十幾個
    a = w3obj.parse(m.read('war3map.w3a'), True)
    icons = 0
    for aid in sorted(set(re.findall(r"set udg_jn\[1[01][0-9]\]='([A-Za-z0-9]{4})'", jass))):
        art = a.get(aid, {}).get('aart')
        if isinstance(art, list):
            art = next((x for x in art if x), None)
        if not art:
            continue
        icons += 1
        lines.append('call SaveStr(ARCSLK,\'%s\',5,"%s")'
                     % (aid, art.replace(chr(92), chr(92) * 2).replace('"', '')))

    out = jass
    if out.count('\nendglobals\n') != 1:
        raise SystemExit('globals 區塊找不到（或不只一個）')
    out = out.replace('\nendglobals\n', '\n' + GLOBALS_ADD + 'endglobals\n', 1)

    anchor = 'function EXGetEventDamageData takes integer edd_type returns integer\n'
    if out.count(anchor) != 1:
        raise SystemExit('查表橋的插入點出現 %d 次' % out.count(anchor))
    out = out.replace(anchor, (SLK_FUNCS % '\n'.join(lines)) + anchor, 1)

    # 改寫呼叫端。EXExecuteScript 的引數長這樣：
    #   "(require'jass.slk').unit["+I2S(<運算式>)+"].STRplus"
    pat = re.compile(r'^"\(require\'jass\.slk\'\)\.(unit|item|ability)\['
                     r'"\+I2S\((?P<e>.*)\)\+"\]\.(?P<f>\w+)"$', re.S)
    done = []
    pos = 0
    while True:
        i = out.find('EXExecuteScript(', pos)
        if i < 0:
            break
        a, end = _args(out, i + len('EXExecuteScript'))
        mm = pat.match(a[0].strip()) if len(a) == 1 else None
        if mm is None:
            pos = i + 1
            continue
        kind, expr, field = mm.group(1), mm.group('e'), mm.group('f')
        if kind == 'unit' and field in SLK_KEY:
            rep = 'ArcherSlkUnitGrowth(%s,%d)' % (expr, SLK_KEY[field])
        elif kind == 'item' and field == 'goldcost':
            # 外面包的是 S2I(...)，所以回傳字串 "0" 就等於花費 0
            rep = '"0"' if DEVOUR_FREE else 'ArcherSlkItemGold(%s)' % expr
        elif kind == 'ability' and field == 'Art':
            rep = 'ArcherSlkAbilArt(%s)' % expr
        else:
            # Missileart 之類的：接收端本身也是空殼，補了也沒用，留著不動
            pos = i + 1
            continue
        out = out[:i] + rep + out[end + 1:]
        done.append(field)
        pos = i

    return out, ('SLK 查表橋：%d 個英雄的成長／射程、%d 件道具售價、%d 個天賦圖示；'
                 '換掉 %d 處查詢（%s）'
                 % (heroes, items, icons, len(done), '、'.join(sorted(set(done)))))


# ------------------------------------------------- 傷害類型（第 4 步：兩種暴擊）
# 「這次傷害是什麼類型」在脫機版被換成「不管問什麼都回答 100」。
# 100 不等於任何一個合法的攻擊／傷害類型，所以：
#   法術暴擊（要 ATTACK_TYPE_NORMAL＝法術）永遠不觸發
#   致命一擊（要 DAMAGE_TYPE_NORMAL＝物理）永遠不觸發
#   攻擊回血（要「是普攻」）反而永遠觸發，連法術傷害也吸血
#
# 修法：地圖自己造成傷害的 27 個地方，每一處呼叫時都已經把類型寫在參數裡，
# 只要在呼叫前後記下來就行。傷害事件是在 UnitDamageTarget 裡同步觸發的，
# 所以「現在堆疊頂端是什麼」就是「這次傷害是什麼」。堆疊空的＝引擎的普攻。
ATTACK_TYPE = {'ATTACK_TYPE_NORMAL': 0, 'ATTACK_TYPE_MELEE': 1, 'ATTACK_TYPE_PIERCE': 2,
               'ATTACK_TYPE_SIEGE': 3, 'ATTACK_TYPE_MAGIC': 4, 'ATTACK_TYPE_CHAOS': 5,
               'ATTACK_TYPE_HERO': 6}
DAMAGE_TYPE = {'UNKNOWN': 0, 'NORMAL': 4, 'ENHANCED': 5, 'FIRE': 8, 'COLD': 9,
               'LIGHTNING': 10, 'POISON': 11, 'DISEASE': 12, 'DIVINE': 13, 'MAGIC': 14,
               'SONIC': 15, 'ACID': 16, 'FORCE': 17, 'DEATH': 18, 'MIND': 19,
               'PLANT': 20, 'DEFENSIVE': 21, 'DEMOLITION': 22, 'SLOW_POISON': 23,
               'SPIRIT_LINK': 24, 'SHADOW_STRIKE': 25, 'UNIVERSAL': 26}

DMG_OLD = ('function EXGetEventDamageData takes integer edd_type returns integer\n'
           'return 100\n'
           'endfunction\n')

# edd_type：0=有效 1=是物理 2=是普攻 3=是遠程 4=傷害類型 5=武器類型 6=攻擊類型
DMG_NEW = """function ArcherDmgPush takes integer at,integer dt returns nothing
set ARCDCN=ARCDCN+1
set ARCDCA[ARCDCN]=at
set ARCDCD[ARCDCN]=dt
endfunction
function ArcherDmgPop takes nothing returns nothing
if ARCDCN>0 then
set ARCDCN=ARCDCN-1
endif
endfunction
function EXGetEventDamageData takes integer edd_type returns integer
if edd_type==0 then
return 1
endif
if ARCDCN>0 then
if edd_type==1 then
if ARCDCD[ARCDCN]==4 or ARCDCD[ARCDCN]==5 then
return 1
endif
return 0
endif
if edd_type==4 then
return ARCDCD[ARCDCN]
endif
if edd_type==6 then
return ARCDCA[ARCDCN]
endif
return 0
endif
if edd_type==4 then
return 4
endif
if edd_type==6 then
if IsUnitType(GetEventDamageSource(),UNIT_TYPE_HERO) then
return 6
endif
return 1
endif
return 1
endfunction
"""


def fix_damage_type(jass, m):
    """補回「這次傷害是什麼類型」，並在 27 處傷害呼叫前後記錄類型。"""
    if jass.count(DMG_OLD) != 1:
        raise SystemExit('傷害類型空殼找到 %d 次' % jass.count(DMG_OLD))
    out = jass.replace(DMG_OLD, DMG_NEW, 1)

    pat = 'call UnitDamageTarget('
    wrapped, seen = 0, {}
    pos = 0
    while True:
        i = out.find(pat, pos)
        if i < 0:
            break
        if i and out[i - 1] != '\n':
            raise SystemExit('第 %d 處傷害呼叫不在行首，無法安全包裝' % (wrapped + 1))
        a, end = _args(out, i + len('call UnitDamageTarget'))
        if len(a) != 8:
            raise SystemExit('傷害呼叫參數有 %d 個（預期 8 個）' % len(a))
        at = a[5].strip()
        dt = a[6].strip()
        if at not in ATTACK_TYPE or not dt.startswith('DAMAGE_TYPE_'):
            raise SystemExit('看不懂的傷害類型：%s / %s' % (at, dt))
        dk = dt[len('DAMAGE_TYPE_'):]
        if dk not in DAMAGE_TYPE:
            raise SystemExit('看不懂的傷害類型：%s' % dt)
        head = 'call ArcherDmgPush(%d,%d)\n' % (ATTACK_TYPE[at], DAMAGE_TYPE[dk])
        tail = '\ncall ArcherDmgPop()'
        out = out[:i] + head + out[i:end + 1] + tail + out[end + 1:]
        seen[(at, dt)] = seen.get((at, dt), 0) + 1
        wrapped += 1
        pos = i + len(head) + (end + 1 - i) + len(tail)
    if wrapped != 27:
        raise SystemExit('包裝了 %d 處傷害呼叫（預期 27 處）' % wrapped)
    return out, ('傷害類型：補回判斷、包裝 %d 處傷害呼叫（%d 種組合）；'
                 '法術暴擊／致命一擊／攻擊回血恢復' % (wrapped, len(seen)))


# ------------------------------------------------- 傷害寫回、特效（第 1、5 步）
STUBS = [
    # 傷害算完之後要寫回去才算數 —— 這支是空殼，所以會心一擊、蓄力 +50%、
    # 各種加成、對方減傷、後期衰減全部算完就丟掉。玩家受到的傷害也一樣：
    # 本來要除以 10 再封頂，現在是全額吃下。
    ('function EXSetEventDamage takes real amount returns boolean\n'
     'return true\n'
     'endfunction\n',
     'function EXSetEventDamage takes real amount returns boolean\n'
     'call BlzSetEventDamage(amount)\n'
     'return true\n'
     'endfunction\n',
     '傷害寫回（會心／蓄力／減傷／玩家受傷都恢復）'),

    ('function EXSetEffectSize takes effect e, real size returns nothing\n'
     'endfunction\n',
     'function EXSetEffectSize takes effect e, real size returns nothing\n'
     'call BlzSetSpecialEffectScale(e,size)\n'
     'endfunction\n',
     '特效大小'),

    ('function EXSetEffectZ takes effect e, real z returns nothing\n'
     'endfunction\n',
     'function EXSetEffectZ takes effect e, real z returns nothing\n'
     'call BlzSetSpecialEffectZ(e,z)\n'
     'endfunction\n',
     '特效高度'),

    # 地圖傳進來的是角度，原生 API 要的是弧度
    ('function EXEffectMatRotateZ takes effect e, real angle returns nothing\n'
     'endfunction\n',
     'function EXEffectMatRotateZ takes effect e, real angle returns nothing\n'
     'call BlzSetSpecialEffectYaw(e,angle*0.01745329)\n'
     'endfunction\n',
     '特效朝向'),

    ('function EXSetEffectXY takes effect e, real x, real y returns nothing\n'
     'endfunction\n',
     'function EXSetEffectXY takes effect e, real x, real y returns nothing\n'
     'call BlzSetSpecialEffectX(e,x)\n'
     'call BlzSetSpecialEffectY(e,y)\n'
     'endfunction\n',
     '特效位置'),

    # 平台可以三軸各自縮放，1.29.2 只有等比縮放。地圖唯一一處呼叫是
    # (0.70*(1+0.1*等級), 0.50, 0.50) —— 只有 x 會隨等級變大，取它當等比值，
    # 形狀會跟平台版略有差異，但「越高級越大」這個設計意圖保得住。
    ('function EXEffectMatScale takes effect e, real x, real y, real z returns nothing\n'
     'endfunction\n',
     'function EXEffectMatScale takes effect e, real x, real y, real z returns nothing\n'
     'call BlzSetSpecialEffectScale(e,x)\n'
     'endfunction\n',
     '特效縮放（等比近似）'),

    ('function EXSetEffectSpeed takes effect e, real speed returns nothing\n'
     'endfunction\n',
     'function EXSetEffectSpeed takes effect e, real speed returns nothing\n'
     'call BlzSetSpecialEffectTimeScale(e,speed)\n'
     'endfunction\n',
     '特效播放速度'),
]


def fix_stubs(jass, m):
    """把幾支「呼叫得到但什麼都不做」的空殼換成 1.29.2 就有的原生 API。"""
    out, done = jass, []
    for old, new, name in STUBS:
        if out.count(old) != 1:
            raise SystemExit('空殼「%s」找到 %d 次' % (name, out.count(old)))
        out = out.replace(old, new, 1)
        done.append(name)
    return out, '補回空殼：' + '、'.join(done)


# ------------------------------------------------- 攻擊範圍（第 3 步）
def fix_range_upgrade(w3q, m):
    """做兩個「加攻擊距離」的科技出來，交給腳本驅動。

    攻擊距離的來源有三個：商店升級（每級 +50，滿 10 級 +500）、
    弓（+60 到 +660）、空間天賦（+110）。地圖把三者加總記在同一格，
    平台再把那一格套成真正的武器射程；脫機版那一段是空的。

    魔獸的科技系統有個效果叫 ratr ＝ 攻擊距離加成，官方「長管步槍」
    「精良弓箭」用的就是它。但科技是一級一級跳的，要覆蓋 0～2000 又要
    夠細，單一科技得開兩百級（物件檔只有 50 級的資料，開太多級不保險）。
    所以拆成兩個：一個一級 100，一個一級 10，加起來就是任意的 10 的倍數。
    地圖裡所有範圍來源（60/120/…/660、50 的倍數、110）都是 10 的倍數，
    剛好不會有誤差。

    不直接改商店那個 R002 —— 它是玩家真的會去研究的科技，腳本若去改它的
    等級，商店顯示的級數與價格就會跟著亂掉。複製兩份出來自己用最乾淨。
    """
    import w3a_poke
    out, n0 = w3a_poke.clone(w3q, 'R002', ['R00N', 'R00O'], True)
    out, n1 = w3a_poke.poke(out, {('R00N', 'gba1', 0): 100.0,     # 粗：一級 100
                                  ('R00N', 'gmo1', 0): 100.0,
                                  ('R00N', 'glvl', 0): 20,        # 上限 +2000
                                  ('R00O', 'gba1', 0): 10.0,      # 細：一級 10
                                  ('R00O', 'gmo1', 0): 10.0,
                                  ('R00O', 'glvl', 0): 9}, True)  # 上限 +90
    out, n2 = w3a_poke.poke_str(out, {('R00N', 'gef1', 0): 'ratr',
                                      ('R00O', 'gef1', 0): 'ratr'}, True)
    return out, '攻擊距離科技：' + '；'.join(n0 + n1 + n2)


# 掛在英雄身上的科技：R00N/R00O ＝ 攻擊距離（腳本驅動），R00A ＝ 生命值（商店升級）
HERO_UPGRADES = 'R00N,R00O,R00A,R00P,R00Q,R00R,R00U'


def fix_range_units(bal, m):
    """科技效果只會套用在「有列出這個科技」的單位上（步槍兵列了長管步槍才吃得到）。
    地圖英雄這一欄是空的，把 R002 加進去。"""
    import slk
    rows, _ = slk.loads(bal)
    col = slk.col_index(bal, 'upgrades')
    cells, who = [], []
    for uid, rec in sorted(rows.items()):
        if not ID4.match(uid) or not uid.startswith('H0'):
            continue                        # 只有地圖自己的英雄，不動暴雪的
        if str(rec.get('Primary', '_')) not in ('STR', 'AGI', 'INT'):
            continue
        cur = str(rec.get('upgrades') or '').strip('-_ ')
        new = HERO_UPGRADES if not cur else (cur if 'R00N' in cur else cur + ',' + HERO_UPGRADES)
        if new == cur:
            continue
        cells.append((rec['_row'], col, new))
        who.append(uid)
    if not cells:
        raise SystemExit('沒有任何英雄需要掛上攻擊距離科技')
    out = slk.set_cells(bal, cells)

    # 自我檢查：SLK 的標題列會跳號，寫錯一欄就會覆蓋掉隔壁（例如主屬性）。
    # 直接把改完的檔讀回來核對，順便確認沒有動到別人。
    back, _ = slk.loads(out)
    before, _ = slk.loads(bal)
    for uid in who:
        if str(back[uid].get('upgrades')) != HERO_UPGRADES:
            raise SystemExit('%s 的 upgrades 沒寫進去（讀回來是 %r）'
                             % (uid, back[uid].get('upgrades')))
    for uid, rec in before.items():
        for k, v in rec.items():
            if k == 'upgrades' and uid in who:
                continue
            if back[uid].get(k) != v:
                raise SystemExit('%s 的 %s 被改到了：%r -> %r'
                                 % (uid, k, v, back[uid].get(k)))
    return out, ('科技掛載：%d 個英雄掛上 %s（%s）；其餘 %d 列逐欄核對無誤'
                 % (len(who), HERO_UPGRADES, ' '.join(who), len(before) - len(who)))



# ------------------------------------------------- 閃爍距離（商店升級 R00M）
# 說明寫「每级提升200点闪烁距离」，實際做法是平台專用的「即時改技能欄位」，
# 脫機版那支是空殼，所以永遠停在 1050。
#
# 1.29.2 沒辦法在遊戲中改技能的數值欄位，但可以改**等級**。閃爍技能本來就有
# 12 級、每一級都能各自設距離（現在 12 級全是 1050），所以把等級 2～12 設成
# 1050、1250、…、3050，再讓腳本照升級次數選等級就行。
#   0 次升級 -> 2 級 -> 1050
#  10 次升級 -> 12 級 -> 3050   （1050 + 200×10，跟說明一致）
# 1 級不動 —— 物件檔裡 1 級沒有自己的數值，改不了也不需要。
BLINK_BASE, BLINK_STEP, BLINK_LEVELS = 1050.0, 200.0, 12

CHANNEL_FUNC = """function ArcherBlinkChannel takes nothing returns nothing
if GetSpellAbilityId()=='A01B' then
call ArcherApplyBlink(GetTriggerUnit())
endif
endfunction
"""

OLD_INIT_J14 = """function InitTrig_j14 takes nothing returns nothing
set gg_trg_j14=CreateTrigger()
call TriggerRegisterAnyUnitEventBJ(gg_trg_j14,EVENT_PLAYER_UNIT_SPELL_EFFECT)
call TriggerAddCondition(gg_trg_j14,Condition(function Trig_j14Conditions))
call TriggerAddAction(gg_trg_j14,function Trig_j14Actions)
endfunction"""

NEW_INIT_J14 = """function InitTrig_j14 takes nothing returns nothing
local trigger t=CreateTrigger()
set gg_trg_j14=CreateTrigger()
call TriggerRegisterAnyUnitEventBJ(gg_trg_j14,EVENT_PLAYER_UNIT_SPELL_EFFECT)
call TriggerAddCondition(gg_trg_j14,Condition(function Trig_j14Conditions))
call TriggerAddAction(gg_trg_j14,function Trig_j14Actions)
call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_CHANNEL)
call TriggerAddAction(t,function ArcherBlinkChannel)
set t=null
endfunction"""


def fix_blink_range(w3a, m):
    """把閃爍技能 2～12 級的距離設成每級 +200。"""
    import w3a_poke
    # 1 級沒有自己的數值，繼承基礎技能的 1050 —— 剛好就是「沒升級」要的值，
    # 所以 2～11 級接著往上排。12 級留白：地圖拿它當說明的乾淨範本在讀。
    edits = {('A01B', 'Ebl1', lv): BLINK_BASE + BLINK_STEP * (lv - 1)
             for lv in range(2, BLINK_LEVELS)}
    out, notes = w3a_poke.poke(w3a, edits, True)
    return out, ('閃爍距離：%d 級 %.0f～%.0f（每級 +%.0f，12 級留給說明範本）'
                 % (len(edits), BLINK_BASE,
                    BLINK_BASE + BLINK_STEP * (BLINK_LEVELS - 2), BLINK_STEP))


def fix_blink_script(jass, m):
    """研究完成時改成調技能等級，取代改不動的平台函式。

    還有一處：使用閃爍會觸發 Trig_j14Actions，裡面有一行
        SetUnitAbilityLevel(英雄, GetSpellAbilityId(), 玩家編號)
    平台是拿「技能等級」當每個玩家的資料槽（1 號玩家的資料放在 1 級），離線版沒有
    那套資料機制，只剩下「把等級改成玩家編號」這個副作用 —— 1 號玩家閃一次就被
    設成 1 級，而 1 級是唯一沒有距離設定的等級。所以那一行也要換成重新套用距離。
    """
    hit = [l for l in jass.split('\n')
           if 'YDWESetUnitAbilityDataReal' in l and "'A01B'" in l and ',108,' in l]
    if len(hit) != 1:
        raise SystemExit('閃爍距離那一行找到 %d 次（要剛好 1 次）' % len(hit))
    hero = ('LoadUnitHandle(YDLOC,'
            'GetHandleId(GetTriggeringTrigger())*ydl_localvar_step,0x911D5DC2)')
    # 買完升級時回報一次目前距離，免得又要靠感覺猜有沒有生效
    tell = ('call DisplayTimedTextToPlayer(GetOwningPlayer(%s),0,0,8.,'
            '"|cffFFCC00闪烁距离|r："+I2S(%d+%d*GetPlayerTechCount('
            "GetOwningPlayer(%s),'R00M',true)))"
            % (hero, int(BLINK_BASE), int(BLINK_STEP), hero))
    out = jass.replace(hit[0],
                       'call ArcherApplyBlink(%s)' % hero + '\n' + tell, 1)

    # Trig_j14Actions（施放閃爍時觸發）裡有兩行會動到技能等級：
    #   SetUnitAbilityLevel(英雄, 技能, 12)        <- 先跳到 12 級
    #   SetUnitAbilityLevel(英雄, 技能, 玩家編號)   <- 寫完說明再設回玩家編號
    # 平台是拿「技能等級」當每個玩家的資料槽（1 號玩家的說明放在 1 級），
    # 中間那支寫說明的函式在脫機版是空殼，只剩下改等級這個副作用。
    # 兩行都得換掉：留著前面那行，閃爍距離會一直是 12 級的上限；
    # 留著後面那行，1 號玩家閃一次就被設成 1 級（唯一沒有距離設定的等級）。
    lines = out.split('\n')
    a = next(i for i, l in enumerate(lines) if l.startswith('function Trig_j14Actions'))
    b = next(i for i in range(a, len(lines)) if lines[i] == 'endfunction')
    fixed = 0
    for i in range(a, b + 1):
        if 'SetUnitAbilityLevel' in lines[i] and '0xF374F3BD' in lines[i]:
            lines[i] = 'call ArcherApplyBlink(%s)' % hero
            fixed += 1
    if fixed != 2:
        raise SystemExit('閃爍施放時改等級的行找到 %d 處（要剛好 2 處）' % fixed)
    out = '\n'.join(lines)

    # 再保一層：引擎是在「開始施法」就算好要傳送多遠，而 Trig_j14Actions 掛的是
    # 「技能生效」，兩者誰先誰後沒有保證。多掛一個「開始施法」的觸發，
    # 確保等級在引擎讀之前就已經是對的。
    anchor = "call SetUnitAbilityLevel(u,'A01B',n)\nendfunction\n"
    if out.count(anchor) != 1:
        raise SystemExit('找不到 ArcherApplyBlink 的結尾')
    out = out.replace(anchor, anchor + CHANNEL_FUNC, 1)

    if out.count(OLD_INIT_J14) != 1:
        raise SystemExit('InitTrig_j14 長得跟預期不一樣')
    out = out.replace(OLD_INIT_J14, NEW_INIT_J14, 1)
    return out, '閃爍距離：開始施法時套用，並拿掉施放中把等級改成 12／玩家編號的兩行'



# ------------------------------------------------- 生命值升級（商店 R00A）
# 說明是「每級 +400 生命」，做法是 SetUnitState(最大生命, +400)。那個呼叫本身
# 有效（怪物血量也是這樣設的），但**對英雄不持久**：
# war3mapMisc.txt 裡 StrHitPointBonus=15，英雄的最大生命是「基礎 + 力量×15」
# 算出來的，力量一變動引擎就重算，硬寫上去的 +400 就被蓋掉。
# 而這張地圖升一級、換一件裝備、拿翅膀都在改力量 —— 等於買完馬上失效。
#
# 而且整份腳本裡 R00A 只出現一次（就是買的那一刻），從來沒有重新套用過。
#
# 改法跟攻擊距離同一套：交給引擎的科技效果。rhpx ＝ 生命上限加成，
# 官方「馴獸術」(+150 生命) 用的就是它。科技加成是引擎算完衍生屬性之後才加的，
# 不會被力量重算洗掉。
HP_PER_LEVEL = 400.0


def fix_hp_upgrade(w3q, m):
    """把生命值升級的引擎效果填回去（rhpx，每級 +400）。"""
    import w3a_poke
    out, n1 = w3a_poke.poke(w3q, {('R00A', 'gba1', 0): HP_PER_LEVEL,
                                  ('R00A', 'gmo1', 0): HP_PER_LEVEL}, True)
    out, n2 = w3a_poke.poke_str(out, {('R00A', 'gef1', 0): 'rhpx'}, True)
    return out, '生命值科技：' + '；'.join(n1 + n2)


def fix_hp_script(jass, m):
    """拿掉腳本那一行硬寫的 +400，改由科技效果提供，免得加兩次。"""
    hit = [l for l in jass.split('\n')
           if 'UNIT_STATE_MAX_LIFE' in l and l.rstrip().endswith('+400.00))')]
    if len(hit) != 1:
        raise SystemExit('生命值那一行找到 %d 次（要剛好 1 次）' % len(hit))
    out = jass.replace(hit[0] + '\n', '', 1)
    return out, '生命值：拿掉會被洗掉的那一行，改由科技效果提供'



# ------------------------------------------------- 地圖名稱
# 修好的圖跟原圖同名，大廳與地圖清單裡完全分不出來 —— 已經發生過有人載到舊圖
# 的情況。在名稱後面加一個版本標記，換版時把 FIX_TAG 改掉就好。
FIX_TAG = '修復13'


def fix_mapname(w3i, m):
    """w3i 開頭是版本／存檔次數／編輯器版本各 4 bytes，接著就是名稱字串。

    這是順序讀取的格式（沒有存位移），所以字串變長變短都沒關係，
    直接把那一段換掉就行。
    """
    import struct
    head = 12
    end = w3i.index(b'\x00', head)
    old = w3i[head:end].decode('utf-8', 'replace')
    tag = ' |cffFFCC00' + FIX_TAG + '|r'
    if tag in old:
        return w3i, '地圖名稱：已經有標記，不動'
    new = old + tag
    out = w3i[:head] + new.encode('utf-8') + w3i[end:]
    # 確認改完還讀得回來
    e2 = out.index(b'\x00', head)
    if out[head:e2].decode('utf-8') != new:
        raise SystemExit('地圖名稱寫壞了')
    ver, saves, edv = struct.unpack_from('<iii', out, 0)
    if ver != struct.unpack_from('<i', w3i, 0)[0]:
        raise SystemExit('w3i 檔頭被動到了')
    return out, '地圖名稱：%r -> %r' % (old, new)



# ------------------------------------------------- 攻速技能階梯
# BlzSetUnitAttackCooldown 當初傳錯武器索引所以沒作用（實測間隔讀回來是 0），
# 所以攻速與攻擊間隔的升級完全無效。改用「道具攻速加成」技能 —— 弓身上用的
# 就是這種，確定有效。做成 1%,2%,4%,…,256% 的二進位階梯，九個技能就能組出
# 0～511% 的任何整數百分比。
SPEED_IDS = ['ASp1', 'ASp2', 'ASp3', 'ASp4', 'ASp5', 'ASp6', 'ASp7', 'ASp8', 'ASp9']


def fix_speed_abils(w3a, m):
    """從既有的攻速技能複製九個出來，數值設成 2 的次方百分比。"""
    import w3a_poke
    out, notes = w3a_poke.clone(w3a, 'A00U', SPEED_IDS, True)
    edits = {}
    for i, aid in enumerate(SPEED_IDS):
        edits[(aid, 'Isx1', 1)] = (2 ** i) / 100.0
    out, n2 = w3a_poke.poke(out, edits, True)
    return out, ('攻速技能：複製 %d 個（%d%%～%d%%，可組出 0～511%%）'
                 % (len(SPEED_IDS), 1, 2 ** (len(SPEED_IDS) - 1)))



# ------------------------------------------------- 攻擊力科技（白字）
# 效果碼是查 War3Patch.mpq 裡的 UpgradeEffectMetaData.slk 確認的，別憑印象：
#   ratx ＝ 攻擊傷害加成（加基礎值）    ratd ＝ 攻擊骰子加成（加骰子數量）
# 兩種都算白字。技能／道具加的才是綠字，而綠字會被「攻擊力 +X%」的基數扣掉，
# 所以攻擊力一定要走科技。這裡要的是加基礎值，用 ratx。
ATK_UPGRADES = [('R00P', 1000.0, 50), ('R00Q', 100.0, 9),
                ('R00R', 10.0, 9), ('R00U', 1.0, 9)]


def fix_atk_upgrade(w3q, m):
    """複製三個攻擊力科技出來組成階梯（×1000／×100／×10）。"""
    import w3a_poke
    ids = [i for i, _, _ in ATK_UPGRADES]
    out, n0 = w3a_poke.clone(w3q, 'R002', ids, True)
    edits = {}
    for aid, step, lv in ATK_UPGRADES:
        edits[(aid, 'gba1', 0)] = step
        edits[(aid, 'gmo1', 0)] = step
        edits[(aid, 'glvl', 0)] = lv
    out, n1 = w3a_poke.poke(out, edits, True)
    out, n2 = w3a_poke.poke_str(out, {(i, 'gef1', 0): 'ratx' for i in ids}, True)
    top = sum(step * lv for _, step, lv in ATK_UPGRADES)
    return out, '攻擊力科技：%s，合計上限 +%d（每 10 一階）' % ('／'.join(ids), int(top))



# ------------------------------------------------- 攻速百分比（含敏捷）
def fix_speed_pct(jass, m):
    """把「(攻速倍率-1)*100」換成含敏捷的真實攻速百分比。

    敏捷每點給多少攻速寫在地圖自己的 war3mapMisc.txt 裡（AgiAttackSpeedBonus），
    所以從那邊讀，不要寫死。
    """
    misc = m.read('war3mapMisc.txt').decode('utf-8', 'replace')
    hit = re.search(r'^AgiAttackSpeedBonus=([0-9.]+)', misc, re.M)
    if not hit:
        raise SystemExit('war3mapMisc.txt 裡找不到 AgiAttackSpeedBonus')
    per_point = float(hit.group(1)) * 100.0      # 0.001 -> 每點 0.1%

    out = jass.replace('%AGI%', '%.4f' % per_point)
    if '%AGI%' in out:
        raise SystemExit('敏捷係數沒有代入')

    pat = re.compile(r'\(\(ArcherGetState\((.+?),0x51\)-1(?:\.00)?\)\*100\.00\)')
    found = pat.findall(out)
    if len(found) != 2:
        raise SystemExit('「攻速換百分比」找到 %d 處（預期 2 處）' % len(found))
    out = pat.sub(lambda mm: 'ArcherSpeedPct(%s)' % mm.group(1), out)
    return out, ('攻速百分比：敏捷每點 +%.2f%%，換掉 2 處（時間之箭傷害、屬性面板）'
                 % per_point)



# ------------------------------------------------- 蓄力箭矢
# 說明：「攻击有15%几率减少自身一半攻速，使得自身伤害提升50%，持续3秒。」
# 原本寫的是 V = (攻速倍率 − 1) / 2 —— 砍的是「加成」。沒買攻速升級時倍率是 1，
# V 就是 0，完全不會變慢，等於白拿 +50% 傷害。改成砍總攻速。
# 還原那一行（攻速 += V）不用動，因為 V 還是「被扣掉的量」。
def fix_charge_arrow(jass, m):
    """把蓄力箭矢的「砍一半」從加成改成總攻速。"""
    pat = re.compile(r'(SaveReal\(YDLOC,[^,]*,0x\w+,)'
                     r'\(\(ArcherGetState\((.+?),0x51\)-1\)/2\.00\)\)')
    hits = pat.findall(jass)
    if len(hits) != 1:
        raise SystemExit('蓄力箭矢那一行找到 %d 處（預期 1 處）' % len(hits))
    out = pat.sub(lambda mm: '%s(ArcherGetState(%s,0x51)/2.00))'
                  % (mm.group(1), mm.group(2)), jass)
    return out, '蓄力箭矢：改成真的砍一半總攻速（原本只砍加成）'



# ------------------------------------------------- 弓的最大攻擊
# 11 把弓的說明都是「攻擊力 +X ~ +2X」，但腳本裡每把弓只存一個數字（就是 X），
# 然後把同一個 X 同時加到最小（0x12）與最大（0x11）—— 最小是對的，最大只給一半，
# 間距永遠拉不開。兩句是相鄰的，加的是同一個變數，把最大那句乘 2 就對上說明了。
def fix_bow_max(jass, m):
    """弓的最大攻擊加成 ×2。"""
    lines = jass.split('\n')
    hits = []
    for i in range(len(lines) - 1):
        lo, hi = lines[i], lines[i + 1]
        if 'ArcherSetState' not in lo or ',0x12,' not in lo or '0x8B1FFFFC' not in lo:
            continue
        # 下一句必須是「同一句話、只把 0x12 換成 0x11」，否則不是這一對
        if hi != lo.replace(',0x12,', ',0x11,').replace(',0x12)', ',0x11)'):
            continue
        k = hi.index('+I2R(') + len('+I2R(')
        d, j = 1, k
        while d:
            if hi[j] == '(':
                d += 1
            elif hi[j] == ')':
                d -= 1
            j += 1
        lines[i + 1] = hi[:j] + '*2.' + hi[j:]
        hits.append(i + 2)
    if len(hits) != 2:
        raise SystemExit('弓的最大攻擊找到 %d 處（預期 2 處：穿脫裝備、讀檔重算）'
                         % len(hits))
    return '\n'.join(lines), '弓的最大攻擊：加成 ×2，照說明的 +X ~ +2X（2 處）'



# ------------------------------------------------- 技能說明文字
# 地圖到處在改技能說明：翅膀的「需要 N 木頭」、閃爍上掛的整面屬性面板、
# 吞噬的箭魂點數……全都走平台的 EXSetAbilityDataString，而那支是空殼，
# 所以說明永遠停在物件編輯器裡的原始文字。
#
# 1.29 其實就有原生的 BlzSetAbilityTooltip／BlzSetAbilityExtendedTooltip，
# 只是它改的是「技能 + 等級」而不是「單位」。剛好這張地圖本來就用
# 「技能等級 = 玩家編號」當每個玩家的資料槽，所以直接對上，語意不變。
#
# 欄位編號是看內容認的：215 收的是「翅膀 +5[C]|n點擊升級，需要 480 木頭」
# 這種按鈕標題，217／218 收的是整段說明本文。209 是彈道模型，不是文字，
# 沒有對應的原生函式，留著空殼。
#
# 閃爍是例外：它的等級被我拿去代表距離了，不會等於玩家編號，
# 所以 1～11 級全部寫一遍（12 級留白，地圖拿它當乾淨範本在讀）。
TIP_FUNCS = """function ArcherSetTip takes integer a,integer lv,integer dt,string v returns nothing
local integer i
if a=='A01B' then
set i=1
loop
exitwhen i>11
if dt==215 then
call BlzSetAbilityTooltip(a,v,i)
else
call BlzSetAbilityExtendedTooltip(a,v,i)
endif
set i=i+1
endloop
return
endif
if lv<1 then
set lv=1
endif
if dt==215 then
call BlzSetAbilityTooltip(a,v,lv)
else
call BlzSetAbilityExtendedTooltip(a,v,lv)
endif
endfunction
"""


def fix_ability_tips(jass, m):
    """把技能說明的讀寫接到 1.29 的原生函式上。"""
    setter = ("function YDWESetUnitAbilityDataString takes unit u,integer abilcode,"
              "integer level,integer data_type,string value returns boolean\n"
              "return EXSetAbilityDataString(EXGetUnitAbility(u,abilcode),level,"
              "data_type,value)\nendfunction")
    getter = ("function YDWEGetUnitAbilityDataString takes unit u,integer abilcode,"
              "integer level,integer data_type returns string\n"
              "return EXGetAbilityDataString(EXGetUnitAbility(u,abilcode),level,"
              "data_type)\nendfunction")
    for name, block in (('寫入', setter), ('讀取', getter)):
        if jass.count(block) != 1:
            raise SystemExit('技能說明的%s空殼找到 %d 次（要剛好 1 次）'
                             % (name, jass.count(block)))

    out = jass.replace(getter, TIP_FUNCS + (
        "function YDWEGetUnitAbilityDataString takes unit u,integer abilcode,"
        "integer level,integer data_type returns string\n"
        "if data_type==215 then\n"
        "return BlzGetAbilityTooltip(abilcode,level)\n"
        "endif\n"
        "if data_type==217 or data_type==218 then\n"
        "return BlzGetAbilityExtendedTooltip(abilcode,level)\n"
        "endif\n"
        "return EXGetAbilityDataString(EXGetUnitAbility(u,abilcode),level,"
        "data_type)\nendfunction"), 1)

    out = out.replace(setter, (
        "function YDWESetUnitAbilityDataString takes unit u,integer abilcode,"
        "integer level,integer data_type,string value returns boolean\n"
        "if data_type==215 or data_type==217 or data_type==218 then\n"
        "call ArcherSetTip(abilcode,level,data_type,value)\n"
        "return true\n"
        "endif\n"
        "return EXSetAbilityDataString(EXGetUnitAbility(u,abilcode),level,"
        "data_type,value)\nendfunction"), 1)

    n = len([1 for l in out.split('\n') if 'YDWESetUnitAbilityDataString(' in l
             and 'function ' not in l])
    return out, '技能說明：接上原生函式，%d 處寫入恢復（翅膀木頭需求、屬性面板、吞噬）' % n


FIXES = [
    ('war3map.w3i', fix_mapname),
    ('war3map.w3a', fix_plunder_tooltip),
    ('war3map.w3a', fix_blink_range),
    ('war3map.w3a', fix_speed_abils),
    ('war3map.j', fix_ability_tips),
    ('war3map.j', fix_str_arrow),
    ('war3map.j', fix_str_perm),
    ('war3map.j', fix_slk_bridge),
    ('war3map.j', fix_ledger),
    ('war3map.j', fix_bow_max),
    ('war3map.j', fix_damage_type),
    ('war3map.j', fix_speed_pct),
    ('war3map.j', fix_charge_arrow),
    ('war3map.j', fix_stubs),
    ('war3map.j', fix_blink_script),
    ('war3map.j', fix_hp_script),
    ('war3map.j', fix_savecode),
    ('war3map.w3q', fix_range_upgrade),
    ('war3map.w3q', fix_hp_upgrade),
    ('war3map.w3q', fix_atk_upgrade),
    ('Units' + chr(92) + 'UnitBalance.slk', fix_range_units),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    src = args[0] if args else SRC
    dst = args[1] if len(args) > 1 else re.sub(r'\.w3x$', '_fix.w3x', src)

    m = MPQ(src)
    cur = {}
    notes = []
    for name, fn in FIXES:
        data = cur.get(name)
        if data is None:
            data = m.read(name)
            if name.endswith('.j'):
                data = data.decode('utf-8', 'surrogateescape')
        data, note = fn(data, m)
        cur[name] = data
        notes.append(note)

    edits = {k: (v.encode('utf-8', 'surrogateescape') if isinstance(v, str) else v)
             for k, v in cur.items()}
    where = mpq_patch.write_files(src, dst, edits)
    ok, msg = mpq_patch.verify(src, dst, edits)

    print('%s -> %s' % (os.path.basename(src), os.path.basename(dst)))
    for t in notes:
        print('  ✓ %s' % t)
    for name, w in where.items():
        print('  %-14s %s' % (name, w))
    for line in msg:
        print(line)
    if not ok:
        raise SystemExit('驗證失敗，請不要用這份檔案')
    print('  完成。')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
