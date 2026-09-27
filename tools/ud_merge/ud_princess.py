# -*- coding: utf-8 -*-
"""亡者公主 R「致命切割」（A0X7）改版：
   擊殺目標 → 重置其他技能與道具冷卻，R 只冷卻 8 秒；沒擊殺 → 照物件資料冷卻 50 秒。

地圖不用 Blz 原生函式（1.26 相容），沒辦法直接把冷卻設成任意秒數，所以擊殺時：
  1. UnitResetCooldown（連 R 一起重置）
  2. 用 SetPlayerAbilityAvailable 把 R 藏 8 秒，同一格放一個灰色的被動圖示 A2UR「冷卻中」
  3. 8 秒後移除 A2UR、R 恢復可用
被動圖示不會觸發任何施法事件，所以不會誤觸發「使用技能時…」類的道具效果。
原本「重置效果有 10 秒內部冷卻」由這個 8 秒冷卻取代。"""
import w3a_poke

HOLD = 'A2UR'
HOLD_SEC = 8

_OLD_START = "elseif Skill=='A0X7' then\nset dmg=200."
_NEW_START = "elseif Skill=='A0X7' then\nset count=0\nset dmg=200."

_OLD_KILL = """if not UnitAlive(u2)and LoadInteger(hash,GetHandleId(u),'A0X7')==0 then
call UnitResetCooldown(u)
call SaveInteger(hash,GetHandleId(u),'A0X7',1)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveInteger(hash,Id,1,GetHandleId(u))
call SaveInteger(hash,Id,2,'A0X7')
call TimerStart(t,10.,false,function EndCooldown)
endif
call TriggerSleepAction(0.1)
call UnitRemoveAbility(u,'A0X8')
call PauseUnit(u,false)
call SetUnitAnimation(u,"stand")
"""
_NEW_KILL = """if not UnitAlive(u2)then
call UnitResetCooldown(u)
set count=1
endif
call TriggerSleepAction(0.1)
call UnitRemoveAbility(u,'A0X8')
call PauseUnit(u,false)
call SetUnitAnimation(u,"stand")
if count==1 then
call SetPlayerAbilityAvailable(pl,'A0X7',false)
call UnitAddAbility(u,'%s')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,u)
call TimerStart(t,%d.,false,function udP_RBack)
endif
""" % (HOLD, HOLD_SEC)

_FUNC = """function udP_RBack takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call UnitRemoveAbility(u,'%s')
call SetPlayerAbilityAvailable(GetOwningPlayer(u),'A0X7',true)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set t=null
set u=null
endfunction
""" % HOLD


def patch_jass(J):
    for a in (_OLD_START, _OLD_KILL):
        assert J.count(a) == 1, '亡者公主 R：找不到要改的程式段'
    J = J.replace(_OLD_START, _NEW_START).replace(_OLD_KILL, _NEW_KILL)
    anchor = 'function Trig_HeroSkills53_Actions takes nothing returns nothing'
    assert J.count(anchor) == 1
    return J.replace(anchor, _FUNC + anchor)


def patch_w3a(data):
    """複製天生被動 A0X9（Amgl 底，公主身上已有兩個同底的被動，不會多出效果）當成佔位圖示。"""
    data, _ = w3a_poke.clone(data, 'A0X9', [HOLD])
    data, _ = w3a_poke.poke(data, {(HOLD, 'abpx', 0): 3, (HOLD, 'abpy', 0): 2})
    data, _ = w3a_poke.poke_str(data, {(HOLD, 'aart', 0): r'ReplaceableTextures\CommandButtonsDisabled\DISBTNGwenR.blp'})
    return data


# 翻譯之後套用的文字（物件 ID → {欄位: 函式(原譯文) → 新譯文}）
_R_OLD = '擊殺目標時重置技能與道具的冷卻，此效果有 10 秒的內部冷卻。'
_R_NEW = '若這一擊擊殺目標：重置其他技能與道具的冷卻時間，致命割裂本身的冷卻時間只有 8 秒；沒有擊殺則為 50 秒。'
_CD_OLD = '50 秒|r'
_CD_NEW = '50 秒（擊殺時 8 秒）|r'
hits = {'r': 0}


def text(k, m, s):
    if k == HOLD:
        return {'anam': '致命割裂（冷卻中）',
                'atp1': '致命割裂（冷卻中）',
                'aub1': '致命割裂擊殺目標後的短冷卻時間，%d 秒後恢復可用。' % HOLD_SEC}.get(m, s)
    if k == 'A0X7' and m in ('aub1', 'arut') and s and _R_OLD in s:
        hits['r'] += 1
        return s.replace(_R_OLD, _R_NEW).replace(_CD_OLD, _CD_NEW)
    return s
