# 宇宙巨龍 `Nalc`（Космический дракон）

主屬性 **智力** · 背包 **6 格** · 解鎖 4000000 · 定位 法師

| | 初始 | 每級 |
|---|---|---|
| 力量 | 19 | 2.2 |
| 敏捷 | 16 | 2 |
| 智力 | 31 | 4 |

> 強大的遠程法師，擁有自己的累積型資源來強化技能。

**縮放**：吃技能強度的技能 ['A0VQ'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且事件數越多穿透越划算。
- **召喚物** —— 召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡明寫的屬性（通常是最大生命與技能強度）與原生光環。
- **治療／增益** —— 直接寫數值，不經傷害事件 —— 全地圖沒有「治療加成」這種屬性，只能靠技能公式裡的係數（多半是技能強度）。

細節見 `data/dossier/_engine.md`。


---

## 烈日吐息 `A0VS`

俄文原名：Дыхание солнца

```
英雄開始朝指定方向噴射火焰，對被波及的敵人造成傷害。

傷害：火焰內每顆彈體 8 + （4% 星辰物質）點
維持的法力消耗：14 點/秒，維持 8 秒後消耗每秒增加 20%
最大持續時間：無限制

冷卻：20 秒

星辰物質可提升火焰的飛行距離。
```

每級變動：
  - 第 3 行：8 / 12 / 16 / 20 / 24
  - 第 4 行：14 / 18 / 22 / 26 / 30

物件欄位（原型 `ANcl`）：`Ncl1 = 99999.0`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 6.0`, `Ncl5 = 0`, `Ncl6 = controlmagic`, `acap = `, `acdn = 20.0`, `alev = 5`, `amcs = [14, 18, 22, 26, 30]`, `aran = 800.0`

實作：

`HeroW50_Dmg`　war3map.j:61996
```jass
function HeroW50_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local unit u2=LoadUnitHandle(hash,Id,2)
local unit u3
local unit u4
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local player pl
local real dmg=LoadReal(hash,Id,1)
local real degrees=LoadReal(hash,Id,4)
local integer check=LoadInteger(hash,Id,2)
local integer count=LoadInteger(hash,Id,3)
local group ug
local boolean B=false
local real r
set degrees=degrees+GetRandomReal(-3.0,3.0)+LoadReal(hash,Id,5)
call SaveReal(hash,Id,4,degrees)
call SetUnitX(u2,PolarX(x,30,degrees))
call SetUnitY(u2,PolarY(y,30,degrees))
call SetUnitFacing(u2,degrees)
set check=check+1
set count=count-1
if check==2 and count !=0 then
set check=0
set u=LoadUnitHandle(hash,Id,1)
set pl=GetOwningPlayer(u)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,55,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null or B==true
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
set B=true
set u4=u3
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
if IsTerrainPathable(x,y,PATHING_TYPE_WALKABILITY)==true and B !=true then
call RemoveUnit(u2)
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
return
endif
if B==true then
call UnitDamageTarget(u,u4,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
if not UnitAlive(u4)then
if IsUnitType(u4,UNIT_TYPE_HERO)then
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+8.)
else
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+(0.20*I2R(GetUnitLevel(u4))))
endif
endif
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveUnit(u2)
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
return
endif
endif
call SaveInteger(hash,GetHandleId(t),2,check)
if count==0 then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveUnit(u2)
else
call SaveInteger(hash,GetHandleId(t),3,count)
endif
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
set ug=null
endfunction
function HeroW50_Create takes nothing returns nothing
local timer t=GetExpiredTimer()
local timer t2
local integer Id=GetHandleId(t)
local integer L
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2
local real degrees=GetUnitFacing(u)
local real angle
local real dist
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2
local real y2
local real dmg
local real spd=LoadReal(hash,GetHandleId(u),'Nalc')
local player pl=GetOwningPlayer(u)
set dmg=(4.+4.*I2R(GetUnitAbilityLevel(u,'A0VS'))+spd*0.04)*6.0
set angle=degrees+90.
set u2=CreateUnit(pl,'o02T',x,y,angle)
set t2=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t2),1,u)
call SaveUnitHandle(hash,GetHandleId(t2),2,u2)
call SaveReal(hash,GetHandleId(t2),1,dmg)
call SaveInteger(hash,GetHandleId(t2),2,0)
call SaveInteger(hash,GetHandleId(t2),3,30)
call SaveReal(hash,GetHandleId(t2),4,angle)
call SaveReal(hash,GetHandleId(t2),5,GetRandomReal(-2.,2.))
call TimerStart(t2,0.03,true,function HeroW50_Dmg)
set angle=degrees-90.
set u2=CreateUnit(pl,'o02T',x,y,angle)
set t2=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t2),1,u)
call SaveUnitHandle(hash,GetHandleId(t2),2,u2)
call SaveReal(hash,GetHandleId(t2),1,dmg)
call SaveInteger(hash,GetHandleId(t2),2,0)
call SaveInteger(hash,GetHandleId(t2),3,30)
call SaveReal(hash,GetHandleId(t2),4,angle)
call SaveReal(hash,GetHandleId(t2),5,GetRandomReal(-2.,2.))
call TimerStart(t2,0.03,true,function HeroW50_Dmg)
set u=null
set u2=null
set t=null
set t2=null
set pl=null
endfunction
```

`HeroQ50_conditions`　war3map.j:62376
```jass
function HeroQ50_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0VS' or GetSpellAbilityId()=='A0VT'
endfunction
function HeroQ50_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local unit u2=LoadUnitHandle(hash,Id,2)
local unit u3
local unit u4
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local player pl
local real dmg=LoadReal(hash,Id,1)
local real degrees=LoadReal(hash,Id,4)
local integer check=LoadInteger(hash,Id,2)
local integer count=LoadInteger(hash,Id,3)
local group ug
local boolean B=false
local real r
call SetUnitX(u2,PolarX(x,35,degrees))
call SetUnitY(u2,PolarY(y,35,degrees))
set check=check+1
set count=count-1
if check==2 and count !=0 then
set check=0
set u=LoadUnitHandle(hash,Id,1)
set pl=GetOwningPlayer(u)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,55,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null or B==true
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
set B=true
set u4=u3
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
if IsTerrainPathable(x,y,PATHING_TYPE_WALKABILITY)==true and B !=true then
call RemoveUnit(u2)
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
return
endif
if B==true then
call UnitDamageTarget(u,u4,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
if not UnitAlive(u4)then
if IsUnitType(u4,UNIT_TYPE_HERO)then
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+8.)
else
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+(0.25*I2R(GetUnitLevel(u4))))
endif
endif
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveUnit(u2)
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
return
endif
endif
call SaveInteger(hash,GetHandleId(t),2,check)
if count==0 then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveUnit(u2)
else
call SaveInteger(hash,GetHandleId(t),3,count)
endif
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
set ug=null
endfunction
function HeroQ50_Create takes nothing returns nothing
local timer t=GetExpiredTimer()
local timer t2
local integer Id=GetHandleId(t)
local integer L
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2
local real degrees=LoadReal(hash,Id,3)
local real dist
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local real x2
local real y2
local real dmg
local real spd=LoadReal(hash,GetHandleId(u),'Nalc')
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real count=LoadReal(hash,Id,4)
set dmg=4.+4.*I2R(GetUnitAbilityLevel(u,'A0VS'))+spd*0.04
set x2=PolarX(x,60.,degrees)
set y2=PolarY(y,60.,degrees)
set dist=GetRandomReal(-40.,40.)
set x=PolarX(x2,dist,degrees+90.)
set y=PolarY(y2,dist,degrees+90.)
set u2=CreateUnit(pl,'o02T',x,y,degrees)
set t2=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t2),1,u)
call SaveUnitHandle(hash,GetHandleId(t2),2,u2)
call SaveReal(hash,GetHandleId(t2),1,dmg)
call SaveInteger(hash,GetHandleId(t2),2,0)
call SaveInteger(hash,GetHandleId(t2),3,30+R2I(spd*0.04))
call SaveReal(hash,GetHandleId(t2),4,degrees)
call TimerStart(t2,0.03,true,function HeroQ50_Dmg)
call SaveReal(hash,Id,4,count+0.01)
set dmg=(10+4*I2R(GetUnitAbilityLevel(u,'A0VS')))*0.05
if count>1.60 then
set dmg=dmg*(count-0.60)
endif
if GetUnitState(u,UNIT_STATE_MANA)<dmg then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveSavedHandle(hash,GetHandleId(u),20)
call IssueImmediateOrderById(u,Order_stop)
else
call SetUnitState(u,UNIT_STATE_MANA,GetUnitState(u,UNIT_STATE_MANA)-dmg)
endif
set u=null
set u2=null
set t=null
set t2=null
set pl=null
endfunction
```

`Trig_HeroQ50_Actions`　war3map.j:62528
```jass
if GetSpellAbilityId()=='A0VS' then
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set Id_u=GetHandleId(u)
set t=CreateTimer()
set Id_t=GetHandleId(t)
call SaveTimerHandle(hash,Id_u,'A0VS',t)
call SaveUnitHandle(hash,Id_t,1,u)
call SaveReal(hash,Id_t,1,x)
call SaveReal(hash,Id_t,2,y)
set x=bj_RADTODEG*Atan2(y2-y,x2-x)
call SaveReal(hash,Id_t,3,x)
call SaveReal(hash,Id_t,4,0.)
call TimerStart(t,0.05,true,function HeroQ50_Create)
```

`Trig_HeroQ50_Stop_Conditions`　war3map.j:62559
```jass
function Trig_HeroQ50_Stop_Conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0VS'
endfunction
function Trig_HeroQ50_Stop_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local integer Id=GetHandleId(u)
local timer t=LoadTimerHandle(hash,Id,'A0VS')
local integer Id_t=GetHandleId(t)
call FlushChildHashtable(hash,Id_t)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,Id,'A0VS')
set u=null
set t=null
endfunction
```

## 宇宙飛行 `A0VT`

俄文原名：Космический полёт

```
英雄向指定地點衝刺，飛行過程中回復生命值並散布魔法火焰，依「烈日吐息」技能的公式造成 X6 傷害。

治療：每 100 點距離 10 + （5% 星辰物質）點
施放距離：1000 點

冷卻：15 秒

星辰物質可提升飛行過程中散發的火焰數量。
```

每級變動：
  - 第 3 行：10 / 15 / 20 / 25 / 30
  - 第 4 行：1000 / 1200 / 1400 / 1600 / 1800

物件欄位（原型 `ANcl`）：`Ncl1 = 0.20000000298023224`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 0.20000000298023224`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acap = `, `acdn = 15.0`, `alev = 5`, `amcs = [50, 55, 60, 65, 70]`, `aran = [1000.0, 1200.0, 1400.0, 1600.0, 1800.0]`

實作：

`Trig_HeroSkillCheck_Actions`　war3map.j:45568
```jass
if Skill=='A0VT' then
set x=GetSpellTargetX()
set y=GetSpellTargetY()
if IsTerrainPathable(x,y,PATHING_TYPE_WALKABILITY)then
call IssueImmediateOrder(u,"stop")
call DisplayTimedTextToPlayer(pl,0,0,15,"|cFFFD0D05Heльзя пpимeнить в нeпpoxoдимyю зoнy!|r")
endif
endif
```

`HeroW50_Dmg`　war3map.j:61996
```jass
function HeroW50_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local unit u2=LoadUnitHandle(hash,Id,2)
local unit u3
local unit u4
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local player pl
local real dmg=LoadReal(hash,Id,1)
local real degrees=LoadReal(hash,Id,4)
local integer check=LoadInteger(hash,Id,2)
local integer count=LoadInteger(hash,Id,3)
local group ug
local boolean B=false
local real r
set degrees=degrees+GetRandomReal(-3.0,3.0)+LoadReal(hash,Id,5)
call SaveReal(hash,Id,4,degrees)
call SetUnitX(u2,PolarX(x,30,degrees))
call SetUnitY(u2,PolarY(y,30,degrees))
call SetUnitFacing(u2,degrees)
set check=check+1
set count=count-1
if check==2 and count !=0 then
set check=0
set u=LoadUnitHandle(hash,Id,1)
set pl=GetOwningPlayer(u)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,55,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null or B==true
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
set B=true
set u4=u3
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
if IsTerrainPathable(x,y,PATHING_TYPE_WALKABILITY)==true and B !=true then
call RemoveUnit(u2)
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
return
endif
if B==true then
call UnitDamageTarget(u,u4,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
if not UnitAlive(u4)then
if IsUnitType(u4,UNIT_TYPE_HERO)then
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+8.)
else
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+(0.20*I2R(GetUnitLevel(u4))))
endif
endif
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveUnit(u2)
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
return
endif
endif
call SaveInteger(hash,GetHandleId(t),2,check)
if count==0 then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveUnit(u2)
else
call SaveInteger(hash,GetHandleId(t),3,count)
endif
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
set ug=null
endfunction
function HeroW50_Create takes nothing returns nothing
local timer t=GetExpiredTimer()
local timer t2
local integer Id=GetHandleId(t)
local integer L
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2
local real degrees=GetUnitFacing(u)
local real angle
local real dist
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2
local real y2
local real dmg
local real spd=LoadReal(hash,GetHandleId(u),'Nalc')
local player pl=GetOwningPlayer(u)
set dmg=(4.+4.*I2R(GetUnitAbilityLevel(u,'A0VS'))+spd*0.04)*6.0
set angle=degrees+90.
set u2=CreateUnit(pl,'o02T',x,y,angle)
set t2=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t2),1,u)
call SaveUnitHandle(hash,GetHandleId(t2),2,u2)
call SaveReal(hash,GetHandleId(t2),1,dmg)
call SaveInteger(hash,GetHandleId(t2),2,0)
call SaveInteger(hash,GetHandleId(t2),3,30)
call SaveReal(hash,GetHandleId(t2),4,angle)
call SaveReal(hash,GetHandleId(t2),5,GetRandomReal(-2.,2.))
call TimerStart(t2,0.03,true,function HeroW50_Dmg)
set angle=degrees-90.
set u2=CreateUnit(pl,'o02T',x,y,angle)
set t2=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t2),1,u)
call SaveUnitHandle(hash,GetHandleId(t2),2,u2)
call SaveReal(hash,GetHandleId(t2),1,dmg)
call SaveInteger(hash,GetHandleId(t2),2,0)
call SaveInteger(hash,GetHandleId(t2),3,30)
call SaveReal(hash,GetHandleId(t2),4,angle)
call SaveReal(hash,GetHandleId(t2),5,GetRandomReal(-2.,2.))
call TimerStart(t2,0.03,true,function HeroW50_Dmg)
set u=null
set u2=null
set t=null
set t2=null
set pl=null
endfunction
function Skill50W takes nothing returns nothing
local timer t=GetExpiredTimer()
local timer t2
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2=LoadReal(hash,Id,2)
local real y2=LoadReal(hash,Id,3)
local real degrees=LoadReal(hash,Id,1)
local real heal=(5.+5.*I2R(GetUnitAbilityLevel(u,'A0VT'))+LoadReal(hash,GetHandleId(u),'Nalc')*0.05)*0.35
set x=x+35.*Cos(degrees*bj_DEGTORAD)
set y=y+35.*Sin(degrees*bj_DEGTORAD)
call SetUnitState(u,UNIT_STATE_LIFE,GetUnitState(u,UNIT_STATE_LIFE)+heal)
if DistanceNative(x,y,x2,y2)<=40. then
call SetUnitX(u,x2)
call SetUnitY(u,y2)
set t2=LoadTimerHandle(hash,GetHandleId(u),'A0VT')
call PauseTimer(t2)
call FlushChildHashtable(hash,GetHandleId(t2))
call DestroyTimer(t2)
call RemoveSavedHandle(hash,GetHandleId(u),'A0VT')
call PauseTimer(t)
call FlushChildHashtable(hash,Id)
call DestroyTimer(t)
call PauseUnit(u,false)
call SetUnitAnimation(u,"stand")
call IssueImmediateOrderById(u,Order_stop)
else
call SetUnitX(u,x)
call SetUnitY(u,y)
endif
set t=null
set t2=null
set u=null
endfunction
```

`Trig_HeroSkills50_Actions`　war3map.j:62323
```jass
elseif Skill=='A0VT' then
set x=GetUnitX(u)
set y=GetUnitY(u)
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set x=bj_RADTODEG*Atan2(y2-y,x2-x)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.03,true,function Skill50W)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,x2)
call SaveReal(hash,Id,3,y2)
call PauseUnit(u,true)
call SetUnitFacing(u,x)
call SetUnitAnimationByIndex(u,3)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveTimerHandle(hash,GetHandleId(u),'A0VT',t)
call SaveUnitHandle(hash,Id,1,u)
set dmg=0.03*(1.+1./(LoadReal(hash,GetHandleId(u),'Nalc')*0.001+0.5))
call TimerStart(t,dmg,true,function HeroW50_Create)
```

`HeroQ50_conditions`　war3map.j:62376
```jass
function HeroQ50_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0VS' or GetSpellAbilityId()=='A0VT'
endfunction
```

`Trig_HeroQ50_Actions`　war3map.j:62542
```jass
elseif GetSpellAbilityId()=='A0VT' then
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
if IsTerrainPathable(x2,y2,PATHING_TYPE_WALKABILITY)==true then
call IssueImmediateOrderById(u,Order_stop)
call DisplayTimedTextToPlayer(pl,0,0,10,"|cFFFF4B39Невозможно применить в непроходимую зону!|r")
endif
endif
```

## 奇點 `A0VP`

俄文原名：Сингулярность

```
奧瑞利安·索爾製造一個黑洞，緩慢將敵人拉向其中心，並在作用範圍內造成傷害。生命值在 10% 及以下的敵人受到黑洞 300% 的傷害。

傷害：30 + （15% 星辰物質）點/秒
持續時間：12 秒

冷卻：25 秒

星辰物質可提升作用範圍與吸引力度。
```

每級變動：
  - 第 3 行：30 / 45 / 60 / 75 / 90

物件欄位（原型 `ANcl`）：`Ncl1 = 2.799999952316284`, `Ncl2 = 2`, `Ncl3 = 3`, `Ncl4 = 2.799999952316284`, `Ncl5 = 0`, `Ncl6 = chemicalrage`, `aare = 200.0`, `acdn = 25.0`, `alev = 5`, `amcs = [100, 120, 140, 160, 180]`, `aran = 700.0`

實作：

`Hero50E`　war3map.j:61922
```jass
function Hero50E takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2
local player pl=GetOwningPlayer(u)
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local real x2
local real y2
local real r
local real dmg
local real spd=LoadReal(hash,GetHandleId(u),'Nalc')
local integer count=LoadInteger(hash,Id,1)
local group ug=CreateGroup()
set dmg=400.+spd*0.45
call GroupEnumUnitsInRange(ug,x,y,dmg,null)
set dmg=75.+spd*0.05
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if UnitAlive(u2)and IsUnitEnemy(u2,pl)and not IsUnitType(u2,UNIT_TYPE_STRUCTURE)and not IsUnitType(u2,UNIT_TYPE_ANCIENT)and GetUnitAbilityLevel(u2,'A0GN')!=1 then
set x2=GetUnitX(u2)
set y2=GetUnitY(u2)
if DistanceNative(x,y,x2,y2)>dmg then
set r=bj_RADTODEG*Atan2(y-y2,x-x2)
if IsUnitType(u2,UNIT_TYPE_HERO)then
call KnockBackUnit(u2,dmg*0.75,0.5,r,0.05)
else
call KnockBackUnit(u2,dmg,0.5,r,0.05)
endif
endif
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
set dmg=(15.+15.*I2R(GetUnitAbilityLevel(u,'A0VP'))+spd*0.15)*0.50
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,200.,null)
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if UnitAlive(u2)and IsUnitEnemy(u2,pl)then
if UnitLifePercent(u2)<=10.00 then
call UnitDamageTarget(u,u2,dmg*3.00,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
else
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
endif
if not UnitAlive(u2)then
if IsUnitType(u2,UNIT_TYPE_HERO)then
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+8.)
else
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+(0.20*I2R(GetUnitLevel(u2))))
endif
endif
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
set count=count-1
if count>0 then
call SaveInteger(hash,Id,1,count)
else
call DestroyEffect(LoadEffectHandle(hash,Id,2))
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
endif
set t=null
set u=null
set u2=null
set pl=null
set ug=null
endfunction
```

`Trig_HeroSkills50_Actions`　war3map.j:62345
```jass
elseif Skill=='A0VP' then
set x=GetSpellTargetX()
set y=GetSpellTargetY()
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveUnitHandle(hash,Id,1,u)
call SaveEffectHandle(hash,Id,2,AddSpecialEffect("war3mapImported\\Void Disc.mdx",x,y))
call SaveInteger(hash,Id,1,24)
call TimerStart(t,0.5,true,function Hero50E)
```

## 流星 `A0VU`

俄文原名：Падающая звезда

```
奧瑞利安．索爾朝指定區域降下一顆星辰，對敵人造成極大傷害並短暫暈眩敵人。

傷害：300 + （100% 星辰物質）點
暈眩（英雄）：4 秒
暈眩（單位）：6 秒

冷卻：120 秒

星辰物質會產生衝擊波，對被波及的敵人造成此技能傷害的 10%。衝擊波概略分為「波次」，每產生一個波次需要 125 點星辰物質。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [2.799999952316284, None, 1.0]`, `Ncl2 = [2, None, 1]`, `Ncl3 = [3, None, 1]`, `Ncl4 = [2.799999952316284, None, 1.0]`, `Ncl5 = [0, None]`, `Ncl6 = ['dismount', None, 'channel']`, `aare = 300.0`, `acap = `, `acdn = [120.0, None, 17.0]`, `alev = 1`, `amcs = [300, None, 80, 90, 100, 110, 120]`, `aran = [1200.0, None, 700.0]`, `atar = ['air,ground,friend,neutral,self', None]`

實作：

`Hero50R_Wave`　war3map.j:62167
```jass
function Hero50R_Wave takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u3
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local real x2
local real y2
local player pl=GetOwningPlayer(u)
local real dmg=LoadReal(hash,Id,3)
local integer count=LoadInteger(hash,Id,1)
local group ug
local real dist=LoadReal(hash,Id,4)
local real dist2=dist
local integer i
local integer L
call SaveReal(hash,Id,4,dist+150)
set i=4
loop
exitwhen dist2<400
set i=i+1
set dist2=dist2-75
endloop
set L=1
loop
exitwhen L>i
set x2=x+dist*Cos(L*(360/i)*bj_DEGTORAD)
set y2=y+dist*Sin(L*(360/i)*bj_DEGTORAD)
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x2,y2))
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x2,y2,225,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
if not UnitAlive(u3)then
if IsUnitType(u3,UNIT_TYPE_HERO)then
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+8.)
else
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+(0.20*I2R(GetUnitLevel(u3))))
endif
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
set L=L+1
endloop
set count=count-1
if count==0 then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SaveInteger(hash,GetHandleId(t),1,count)
endif
set t=null
set u=null
set u3=null
set pl=null
set ug=null
endfunction
function Hero50R takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2
local real y2
local integer L
local unit u3
local unit hero=LoadUnitHandle(hash,Id,2)
local player pl=GetOwningPlayer(hero)
local integer n=GetPlayerId(pl)+1
local real spd=LoadReal(hash,GetHandleId(hero),'Nalc')
local real dmg=300.+spd
local group ug=CreateGroup()
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x,y))
set L=1
loop
exitwhen L>6
set x2=x+250*Cos(60*I2R(L)*bj_DEGTORAD)
set y2=y+250*Sin(60*I2R(L)*bj_DEGTORAD)
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x2,y2))
set L=L+1
endloop
call GroupEnumUnitsInRange(ug,x,y,305,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(hero,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
if not UnitAlive(u3)then
if IsUnitType(u3,UNIT_TYPE_HERO)then
call SaveReal(hash,GetHandleId(hero),'Nalc',LoadReal(hash,GetHandleId(hero),'Nalc')+8.)
else
call SaveReal(hash,GetHandleId(hero),'Nalc',LoadReal(hash,GetHandleId(hero),'Nalc')+(0.20*I2R(GetUnitLevel(u3))))
endif
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call KillUnit(u)
set u3=CreateUnit(pl,'o010',x,y,0.00)
call UnitAddAbility(u3,'A0VV')
call IssueImmediateOrderById(u3,Order_stomp)
call UnitApplyTimedLife(u3,'BTLF',2.00)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
if spd>=125. then
set L=R2I(spd/125.)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,hero)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveReal(hash,Id,3,dmg*0.10)
call SaveReal(hash,Id,4,400)
call SaveInteger(hash,Id,1,L)
call TimerStart(t,0.10,true,function Hero50R_Wave)
endif
set t=null
set u=null
set u3=null
set ug=null
set hero=null
set pl=null
endfunction
```

`Trig_HeroSkills50_Actions`　war3map.j:62356
```jass
elseif Skill=='A0VU' then
set x=GetSpellTargetX()
set y=GetSpellTargetY()
set u2=CreateUnit(pl,'h044',x,y,GetRandomReal(0,360))
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.7,false,function Hero50R)
call SaveUnitHandle(hash,Id,1,u2)
call SaveUnitHandle(hash,Id,2,u)
endif
```

## 轉移／移除據點 `A03V`

俄文原名：Передать/удалить точку

```
選擇自己的據點或建築，將其轉移給其他玩家，或在不損失地基的情況下摧毀它。可從任意距離施放。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.009999999776482582, 0.8999999761581421]`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = [0.009999999776482582, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['unburrow', 'channel']`, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = [99999.0, 100.0]`, `atar = ['player,structure', 'air,ground,debris,enemy,neutral,organic']`

實作：

`Trig_ChangePoints_Actions`　war3map.j:17734
```jass
if GetSpellAbilityId()=='A03V' and GetUnitLevel(GetSpellTargetUnit())>0 then
set udg_CTPoint[n]=GetSpellTargetUnit()
call DialogClear(udg_CTWindow[n])
call DialogSetMessage(udg_CTWindow[n],"Передать/удалить")
set L=1
loop
exitwhen L>8
if Player(L-1)!=pl and GetPlayerController(Player(L-1))==MAP_CONTROL_USER and GetPlayerSlotState(Player(L-1))==PLAYER_SLOT_STATE_PLAYING then
set udg_CTButton[L+(n-1)*9]=DialogAddButton(udg_CTWindow[n],PlayerName[L],0)
endif
set L=L+1
endloop
set udg_CTButton[9]=DialogAddButton(udg_CTWindow[n],"|cFFFFDC00Удалить строение|r",0)
set udg_CTButton[72]=DialogAddButton(udg_CTWindow[n],"|cFFFFDC00Отмена|r",0)
call DialogDisplay(pl,udg_CTWindow[n],true)
endif
```

## 宇宙創造者 `A0VQ`　—　吃技能強度

俄文原名：Вселенский творец

```
被動效果：

英雄的技能會因擁有「星辰物質」而變強。目前的星辰物質數量可透過指令「-i」查詢。

星辰物質累積：以英雄技能擊殺敵人可增加（敵人等級 * 0.20）點星辰物質。擊殺敵方英雄可獲得 8 點星辰物質

啟動時：

英雄暫時獲得「星辰物質」。

星辰物質：100 + （X8 英雄等級） + （140% 技能強度）
持續時間：4 秒後英雄會逐漸失去額外的星辰物質

冷卻：20 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = 0.8999999761581421`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = 0.8999999761581421`, `Ncl5 = 0`, `Ncl6 = ['charm', 'channel']`, `acap = `, `acdn = [20.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [75, 95, 110, 125, 140, 155, 170]`, `aran = [None, 100.0]`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Hero50D`　war3map.j:61883
```jass
function Hero50D takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer count=LoadInteger(hash,Id,1)
local real dmg=LoadReal(hash,GetHandleId(u),'Nalc')
local texttag text=LoadTextTagHandle(hash,GetHandleId(u),'Nalc')
local force f=CreateForce()
local location p
call ForceAddPlayer(f,pl)
call DestroyTextTag(text)
set p=GetUnitLoc(u)
set text=CreateTextTagLocBJ("|cFF00C8AF"+I2S(R2I(dmg)),p,0,12.00,100,100,100,0)
call ShowTextTagForceBJ(false,text,bj_FORCE_ALL_PLAYERS)
call ShowTextTagForceBJ(true,text,f)
call RemoveLocation(p)
call SaveTextTagHandle(hash,GetHandleId(u),'Nalc',text)
set count=count-1
if count==0 then
call DestroyTextTag(text)
call DestroyEffect(LoadEffectHandle(hash,Id,2))
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
else
call SaveInteger(hash,Id,1,count)
if count<=200 then
call SaveReal(hash,GetHandleId(u),'Nalc',dmg-LoadReal(hash,Id,1))
endif
endif
call DestroyForce(f)
set f=null
set t=null
set u=null
set pl=null
set text=null
set p=null
endfunction
```

`Trig_HeroSkills50_Actions`　war3map.j:62314
```jass
if Skill=='A0VQ' then
set dmg=100.+I2R(GetHeroLevel(u))*8.+udg_ItemBonusDMG[n]*1.40
call SaveReal(hash,GetHandleId(u),'Nalc',LoadReal(hash,GetHandleId(u),'Nalc')+dmg)
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,u)
call SaveInteger(hash,GetHandleId(t),1,300)
call SaveReal(hash,GetHandleId(t),1,dmg/200.)
call SaveEffectHandle(hash,GetHandleId(t),2,AddSpecialEffectTarget("war3mapImported\\Radiance Psionic.mdx",u,"chest"))
call TimerStart(t,0.04,true,function Hero50D)
```

---

## 這隻召喚／製造的單位

（技能程式碼裡的 `CreateUnit` 目標。數值取自 war3map.w3u，
沒列出的欄位代表地圖沒覆寫、沿用原型。）

### `h044` Падающая звезда（原型 `hpea`）
  - 技能 Avul,Aloc

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它
  - **5** — 對 0-1 級敵人傷害 +%〔攻擊者〕

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
