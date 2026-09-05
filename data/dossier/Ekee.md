# 占星師 `Ekee`（Астромант）

主屬性 **智力** · 背包 **6 格** · 解鎖 0 · 定位 法師 · **不在隨機池**（只能手動挑） · **帳號鎖定**：Lorit, murlock227, MikeRoss, st1073741824, JEIFEJFIJ151, Koshitan

| | 初始 | 每級 |
|---|---|---|
| 力量 | 14 | 1.5 |
| 敏捷 | 19 | 2.5 |
| 智力 | 39 | 5 |

> 沒有普通攻擊的法師，靠屏障控場並殲滅大量敵人，非常吃法力。

**縮放**：吃技能強度的技能 ['A0CT', 'A0KU', 'A0L0'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

---

## 虛空充能 `A0KU`　—　吃技能強度

俄文原名：Пустотный заряд

```
朝指定方向發射一顆黑暗能量球。能量球會對附近的敵人造成週期性傷害。可透過「虛空引爆」引爆能量球。

週期性傷害：40 + （15% 技能強度） + （10% 當前法力值）點/秒。

冷卻：14 秒。
```

每級變動：
  - 第 3 行：40 / 60 / 80 / 100 / 120
  - 第 5 行：14 / 13 / 12 / 11 / 10

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acap = `, `acdn = [14.0, 13.0, 12.0, 11.0, 10.0]`, `alev = 5`, `amcs = [115, 140, 170, 205, 245]`, `aran = 800.0`

實作：

`HeroA54_Boom`　war3map.j:64905
```jass
function HeroA54_Boom takes unit u,unit u2 returns nothing
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real dmg=GetUnitState(u,UNIT_STATE_MANA)*0.25+udg_ItemBonusDMG[n]*0.50
local unit u3
local group ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,225.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,450.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call DestroyEffect(AddSpecialEffect("war3mapImported\\DarkNova.mdx",x,y))
call KillUnit(u2)
set pl=null
set ug=null
set u3=null
endfunction
```

`HeroQ54`　war3map.j:65003
```jass
function HeroQ54 takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2=LoadUnitHandle(hash,GetHandleId(u),'A0KU')
local unit u3
local real x2
local real y2
local player pl
local integer n
local real dmg
local real degrees=LoadReal(hash,Id,1)
local integer check=LoadInteger(hash,Id,1)
local integer count=LoadInteger(hash,Id,2)
local real speed=LoadReal(hash,Id,2)
local real x=PolarX(GetUnitX(u2),speed,degrees)
local real y=PolarY(GetUnitY(u2),speed,degrees)
local group ug
local integer i=0
call SetUnitX(u2,x)
call SetUnitY(u2,y)
set check=check+1
set count=count-1
if check==5 then
set check=0
set pl=GetOwningPlayer(u)
set n=GetPlayerId(pl)+1
set dmg=20.+20.*I2R(GetUnitAbilityLevel(u,'A0KU'))+udg_ItemBonusDMG[n]*0.15+GetUnitState(u,UNIT_STATE_MANA)*0.10
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,225.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg*0.15,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
call SaveInteger(hash,Id,1,check)
if count==0 or not UnitAlive(u2)then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call KillUnit(u2)
call SaveUnitHandle(hash,GetHandleId(u),'A0KU',null)
else
call SaveInteger(hash,Id,2,count)
endif
set t=null
set u=null
set u2=null
set u3=null
set pl=null
set ug=null
endfunction
```

`Trig_HeroSkills54_Actions`　war3map.j:65149
```jass
if Skill=='A0KU' then
set x=GetUnitX(u)
set y=GetUnitY(u)
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set angle=AngleXY(x,y,x2,y2)
set u3=CreateUnit(pl,'o00H',x,y,angle)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,GetHandleId(u),Skill,u3)
call SaveInteger(hash,Id,1,0)
call SaveInteger(hash,Id,2,130)
call SaveReal(hash,Id,1,angle)
call SaveReal(hash,Id,2,15.)
call TimerStart(t,0.03,true,function HeroQ54)
elseif Skill=='A0CT' then
call HeroA54_Boom(u,LoadUnitHandle(hash,GetHandleId(u),'A0KU'))
```

## 銀河 `A0KV`

俄文原名：Млечный путь

```
產生一道能量屏障，將敵人從自身推開。敵人首次撞上屏障時可能會被暈眩。

首次撞擊的暈眩：100% 機率，3 秒。
屏障持續時間：6 秒。

冷卻：20 秒。
```

每級變動：
  - 第 4 行：6 / 7 / 8 / 9 / 10

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = charm`, `acap = `, `acdn = 20.0`, `alev = 5`, `amcs = [100, 120, 140, 160, 180]`, `aran = 700.0`

實作：

`RemoveDummy`　war3map.j:2746
```jass
function RemoveDummy takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call RemoveUnit(u)
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set u=null
set t=null
endfunction
function StunUnit takes unit attacker,unit target,integer seconds,real chanse returns nothing
local integer random
local integer chanse_random
local unit u
local player pl=GetOwningPlayer(attacker)
local timer t=CreateTimer()
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random and IsUnitEnemy(target,pl)and UnitAlive(target)then
set u=CreateUnit(pl,'o010',GetUnitX(target),GetUnitY(target),0.)
call UnitAddAbility(u,'A0Y8')
call SetUnitAbilityLevel(u,'A0Y8',seconds)
call IssueTargetOrder(u,"creepthunderbolt",target)
call SaveUnitHandle(hash,GetHandleId(t),1,u)
call TimerStart(t,2.,false,function RemoveDummy)
endif
set u=null
set pl=null
set t=null
endfunction
```

`HeroW54`　war3map.j:64940
```jass
function HeroW54 takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2
local player pl=GetOwningPlayer(u)
local real x2
local real y2
local real angle
local integer i
local integer count=LoadInteger(hash,Id,1)
local group ug=CreateGroup()
local group check_ug=LoadGroupHandle(hash,Id,2)
set i=2
loop
exitwhen i>5
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,TenkaX[i],TenkaY[i],180.,null)
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if UnitAlive(u2)and IsUnitEnemy(u2,pl)and not IsUnitType(u2,UNIT_TYPE_STRUCTURE)then
set x2=GetUnitX(u2)
set y2=GetUnitY(u2)
set angle=AngleXY(TenkaX[i],TenkaY[i],x2,y2)
call KnockBackUnit(u2,85.,0.15,angle,0.03)
if not IsUnitInGroup(u2,check_ug)then
call StunUnit(u,u2,3,1.0)
call GroupAddUnit(check_ug,u2)
endif
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
set i=i+1
endloop
if UnitAlive(u)then
set count=count-1
else
set count=0
endif
if count>0 then
call SaveInteger(hash,Id,1,count)
else
call KillUnit(u)
call DestroyGroup(check_ug)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
set i=1
loop
exitwhen i>6
set TenkaX[i]=12301.
set TenkaY[i]=12274.
set i=i+1
endloop
endif
set t=null
set u=null
set u2=null
set pl=null
set ug=null
endfunction
```

`Trig_HeroSkills54_Actions`　war3map.j:65167
```jass
elseif Skill=='A0KV' then
set x=GetUnitX(u)
set y=GetUnitY(u)
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set angle=AngleXY(x,y,x2,y2)
set u3=CreateUnit(pl,'o011',x2,y2,angle)
call SetUnitX(u3,x2)
call SetUnitY(u3,y2)
set count=R2I((5.+1.*I2R(lvl))/0.15)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u3)
call SaveInteger(hash,Id,1,count)
call SaveGroupHandle(hash,Id,2,CreateGroup())
call TimerStart(t,0.15,true,function HeroW54)
set i=1
loop
exitwhen i>6
set dist=420.-I2R(i)*120.
set TenkaX[i]=PolarX(x2,dist,angle+90.)
set TenkaY[i]=PolarY(y2,dist,angle+90.)
set i=i+1
endloop
```

## 空間傳送門 `A0KY`

俄文原名：Пространственный портал

```
在英雄所在位置與指定地點之間建立傳送門。傳送門雙向運作，可讓你的部隊與友軍部隊通過。單位傳送之後會獲得強化，並在強化時間結束前無法再次傳送。建立傳送門時，英雄獲得 2 秒的傳送免疫。

單位強化：+25% 攻擊速度與移動速度，受到負面狀態的機率降低 30%，50% 反傷防護，+25% 對英雄防護
強化持續時間：20 秒。
施放距離：無限制
持續時間：10 秒。

冷卻：30 秒。
```

每級變動：
  - 第 6 行：10 / 20 / 30 / 40 / 50

物件欄位（原型 `ANcl`）：`Ncl1 = 0.5`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 0.5`, `Ncl5 = 0`, `Ncl6 = chemicalrage`, `acap = `, `acdn = 30.0`, `alev = 5`, `amcs = [100, 120, 140, 160, 180]`, `aran = 99999.0`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkillCheck_Actions`　war3map.j:45559
```jass
if Skill=='A0KY' then
set x=GetSpellTargetX()
set y=GetSpellTargetY()
if IsTerrainPathable(x,y,PATHING_TYPE_WALKABILITY)then
call IssueImmediateOrder(u,"stop")
call DisplayTimedTextToPlayer(pl,0,0,15,"|cFFFD0D05Heльзя пpимeнить в нeпpoxoдимyю зoнy!|r")
endif
endif
```

`RemovePortalBuff`　war3map.j:64878
```jass
function RemovePortalBuff takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call UnitRemoveAbility(u,'S00I')
call UnitRemoveAbility(u,'B00W')
call SaveReal(hash,GetHandleId(u),8,LoadReal(hash,GetHandleId(u),8)+0.25)
call RemoveSavedHandle(hash,GetHandleId(u),'B00W')
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set t=null
endfunction
function PortalBuffUnit takes unit target returns nothing
local timer t
if GetUnitAbilityLevel(target,'B00W')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B00W')
call TimerStart(t,20.,false,function RemovePortalBuff)
else
call UnitAddAbility(target,'S00I')
call SaveReal(hash,GetHandleId(target),8,LoadReal(hash,GetHandleId(target),8)+0.25)
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B00W',t)
call TimerStart(t,20.,false,function RemovePortalBuff)
endif
set t=null
endfunction
```

`HeroE54`　war3map.j:65078
```jass
if UnitAlive(u3)and IsUnitAlly(u3,pl)and not IsUnitType(u3,UNIT_TYPE_STRUCTURE)and GetUnitPointValue(u3)!=0 and GetUnitAbilityLevel(u3,'B00W')!=1 and LoadInteger(hash,GetHandleId(u3),'A0KY')!=1 then
call SetUnitX(u3,x2)
call SetUnitY(u3,y2)
call IssueImmediateOrder(u3,"stop")
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl",u3,"origin"))
call PortalBuffUnit(u3)
endif
```

`HeroE54`　war3map.j:65093
```jass
if UnitAlive(u3)and IsUnitAlly(u3,pl)and not IsUnitType(u3,UNIT_TYPE_STRUCTURE)and GetUnitPointValue(u3)!=0 and GetUnitAbilityLevel(u3,'B00W')!=1 and LoadInteger(hash,GetHandleId(u3),'A0KY')!=1 then
call SetUnitX(u3,x)
call SetUnitY(u3,y)
call IssueImmediateOrder(u3,"stop")
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTarget.mdl",u3,"origin"))
call PortalBuffUnit(u3)
endif
```

`HeroE54_HeroImmune`　war3map.j:65118
```jass
function HeroE54_HeroImmune takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
call SaveInteger(hash,GetHandleId(u),'A0KY',0)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
set t=null
set u=null
endfunction
```

`Trig_HeroSkills54_Actions`　war3map.j:65191
```jass
elseif Skill=='A0KY' then
set x=GetUnitX(u)
set y=GetUnitY(u)
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set count=10*lvl*5
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveEffectHandle(hash,Id,1,AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTo.mdl",x,y))
call SaveEffectHandle(hash,Id,2,AddSpecialEffect("Abilities\\Spells\\Human\\MassTeleport\\MassTeleportTo.mdl",x2,y2))
call SavePlayerHandle(hash,Id,3,pl)
call SaveInteger(hash,Id,1,count)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveReal(hash,Id,3,x2)
call SaveReal(hash,Id,4,y2)
call TimerStart(t,0.20,true,function HeroE54)
call SaveInteger(hash,GetHandleId(u),'A0KY',1)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call TimerStart(t,2.,false,function HeroE54_HeroImmune)
```

## 乳光 `A0L0`　—　吃技能強度

俄文原名：Опалесценция

```
將星辰分解成大量光團，對作用範圍內的敵人造成傷害。每次傷害跳動都會吸收英雄的法力值以造成更高的傷害。

傷害：30 + （5% 技能強度）點。
每次跳動的額外傷害：英雄當前法力值的 3%，造成傷害後消耗當前法力值的 1.5%
跳動間隔：0.15 秒。
持續時間：10 秒。

冷卻：80 秒。
```

物件欄位（原型 `ANcl`）：`Ncl1 = 0.10000000149011612`, `Ncl2 = 2`, `Ncl3 = 3`, `Ncl4 = 0.10000000149011612`, `Ncl5 = 0`, `Ncl6 = wispharvest`, `aare = 400.0`, `acap = `, `acdn = 80.0`, `alev = 1`, `amcs = 500`, `aran = 900.0`, `atar = player,structure`

實作：

`s__vector_deallocate`　war3map.j:1323
```jass
function s__vector_deallocate takes integer this returns nothing
if this==null then
return
elseif(si__vector_V[this]!=-1)then
return
endif
set si__vector_V[this]=si__vector_F
set si__vector_F=this
endfunction
```

`s__OpalescenceLib___OpalescenceS_deallocate`　war3map.j:1346
```jass
function s__OpalescenceLib___OpalescenceS_deallocate takes integer this returns nothing
if this==null then
return
elseif(si__OpalescenceLib___OpalescenceS_V[this]!=-1)then
return
endif
set si__OpalescenceLib___OpalescenceS_V[this]=si__OpalescenceLib___OpalescenceS_F
set si__OpalescenceLib___OpalescenceS_F=this
endfunction
```

`s__OpalescenceLib___OpalescenceMoveS_deallocate`　war3map.j:1370
```jass
function s__OpalescenceLib___OpalescenceMoveS_deallocate takes integer this returns nothing
if this==null then
return
elseif(si__OpalescenceLib___OpalescenceMoveS_V[this]!=-1)then
return
endif
set si__OpalescenceLib___OpalescenceMoveS_V[this]=si__OpalescenceLib___OpalescenceMoveS_F
set si__OpalescenceLib___OpalescenceMoveS_F=this
endfunction
```

`OpalescenceLib___SetUnitPositionEx`　war3map.j:3408
```jass
function OpalescenceLib___SetUnitPositionEx takes unit u,real x,real y returns nothing
if x>OpalescenceLib___MaxX then
set x=OpalescenceLib___MaxX
elseif x<OpalescenceLib___MinX then
set x=OpalescenceLib___MinX
endif
if y>OpalescenceLib___MaxY then
set y=OpalescenceLib___MaxY
elseif y<OpalescenceLib___MinY then
set y=OpalescenceLib___MinY
endif
call SetUnitX(u,x)
call SetUnitY(u,y)
endfunction
```

`s__vector_normalize`　war3map.j:3425
```jass
function s__vector_normalize takes integer this returns nothing
local real l=s__vector_length(this)
if l==0.00 then
set l=1.00
endif
set s__vector_x[this]=s__vector_x[this]/l
set s__vector_y[this]=s__vector_y[this]/l
set s__vector_z[this]=s__vector_z[this]/l
endfunction
```

`OpalescenceLib___OpalescenceMove`　war3map.j:3441
```jass
function OpalescenceLib___OpalescenceMove takes nothing returns nothing
local integer A=LoadInteger(hash,GetHandleId(GetExpiredTimer()),0)
local integer i=0
local integer k=0
local real array x
local real array y
local real array z
local real r
local unit u
set s__OpalescenceLib___OpalescenceMoveS_time[A]=s__OpalescenceLib___OpalescenceMoveS_time[A]+0.03125/s__OpalescenceLib___OpalescenceMoveS_timeMax[A]
if s__OpalescenceLib___OpalescenceMoveS_time[A]>1.00 then
set s__OpalescenceLib___OpalescenceMoveS_time[A]=1.00
endif
loop
set x[k]=s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[A]+k]]
set y[k]=s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[A]+k]]
set z[k]=s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[A]+k]]
set k=k+1
exitwhen k>=6
endloop
set k=0
loop
set i=0
loop
set x[i]=(1.00-s__OpalescenceLib___OpalescenceMoveS_time[A])*x[i]+s__OpalescenceLib___OpalescenceMoveS_time[A]*x[i+1]
set y[i]=(1.00-s__OpalescenceLib___OpalescenceMoveS_time[A])*y[i]+s__OpalescenceLib___OpalescenceMoveS_time[A]*y[i+1]
set z[i]=(1.00-s__OpalescenceLib___OpalescenceMoveS_time[A])*z[i]+s__OpalescenceLib___OpalescenceMoveS_time[A]*z[i+1]
set i=i+1
exitwhen i>6-k
endloop
set k=k+1
exitwhen k>=6-1
endloop
call OpalescenceLib___SetUnitPositionEx(s__OpalescenceLib___OpalescenceMoveS_dummy[A],x[0],y[0])
call SetUnitFlyHeight(s__OpalescenceLib___OpalescenceMoveS_dummy[A],z[0]-OpalescenceLib___GetLocZ(x[0],y[0]),0.00)
call SetUnitFacing(s__OpalescenceLib___OpalescenceMoveS_dummy[A],Atan2(y[0]-s__vector_y[s__OpalescenceLib___OpalescenceMoveS_last[A]],x[0]-s__vector_x[s__OpalescenceLib___OpalescenceMoveS_last[A]])*bj_RADTODEG)
if s__OpalescenceLib___OpalescenceMoveS_time[A]>=1.00 then
call PauseTimer(s__OpalescenceLib___OpalescenceMoveS_t[A])
call FlushChildHashtable(hash,GetHandleId(s__OpalescenceLib___OpalescenceMoveS_t[A]))
call DestroyTimer(s__OpalescenceLib___OpalescenceMoveS_t[A])
call UnitApplyTimedLife(s__OpalescenceLib___OpalescenceMoveS_dummy[A],'BTLF',2.00)
call SetUnitAnimation(s__OpalescenceLib___OpalescenceMoveS_dummy[A],"death")
set i=0
loop
call s__vector_deallocate(s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[A]+i])
set i=i+1
exitwhen i>=6
endloop
call s__vector_deallocate(s__OpalescenceLib___OpalescenceMoveS_last[A])
set s__OpalescenceLib___OpalescenceMoveS_t[A]=null
set s__OpalescenceLib___OpalescenceMoveS_dummy[A]=null
call s__OpalescenceLib___OpalescenceMoveS_deallocate(A)
else
set s__vector_x[s__OpalescenceLib___OpalescenceMoveS_last[A]]=x[0]
set s__vector_y[s__OpalescenceLib___OpalescenceMoveS_last[A]]=y[0]
set s__vector_z[s__OpalescenceLib___OpalescenceMoveS_last[A]]=z[0]
endif
endfunction
function OpalescenceLib___SetScale_1 takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer i=GetHandleId(t)
local real r=LoadReal(hash,i,1)+1.75
if r>=15.00 then
call KillUnit(LoadUnitHandle(hash,i,0))
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,i)
else
call SetUnitScale(LoadUnitHandle(hash,i,0),r,r,r)
call SetUnitVertexColor(LoadUnitHandle(hash,i,0),255,255,255,R2I(255.00*(1.00-r/15.00)))
call SaveReal(hash,i,1,r)
endif
set t=null
endfunction
function OpalescenceLib___SetScale takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer i=GetHandleId(t)
local real r=LoadReal(hash,i,1)+0.25
if r>=30.00 then
call KillUnit(LoadUnitHandle(hash,i,0))
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,i)
else
call SetUnitScale(LoadUnitHandle(hash,i,0),r,r,r)
call SaveReal(hash,i,1,r)
endif
set t=null
endfunction
function OpalescenceLib___OpalescenceDamage takes nothing returns nothing
local integer A=LoadInteger(hash,GetHandleId(GetExpiredTimer()),0)
local integer B
local unit u
local real x
local real y
local timer t
local integer i
local integer j
local real mana_dmg
if s__OpalescenceLib___OpalescenceS_timeThreshold[A]>0.00 then
set s__OpalescenceLib___OpalescenceS_timeThreshold[A]=s__OpalescenceLib___OpalescenceS_timeThreshold[A]-0.01
if s__OpalescenceLib___OpalescenceS_timeThreshold[A]==0.20 then
set OpalescenceLib___TempUnit=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___WispID,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+s__OpalescenceLib___OpalescenceS_speed[A]*20.00*s__vector_x[s__OpalescenceLib___OpalescenceS_v[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+s__OpalescenceLib___OpalescenceS_speed[A]*20.00*s__vector_y[s__OpalescenceLib___OpalescenceS_v[A]],GetRandomReal(0.00,360.00))
call OpalescenceLib___SetUnitPositionEx(OpalescenceLib___TempUnit,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+s__OpalescenceLib___OpalescenceS_speed[A]*20.00*s__vector_x[s__OpalescenceLib___OpalescenceS_v[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+s__OpalescenceLib___OpalescenceS_speed[A]*20.00*s__vector_y[s__OpalescenceLib___OpalescenceS_v[A]])
call SetUnitFlyHeight(OpalescenceLib___TempUnit,300.00,0.00)
call SetUnitScale(OpalescenceLib___TempUnit,2.00,2.00,2.00)
call SetUnitTimeScale(OpalescenceLib___TempUnit,2.00)
call UnitApplyTimedLife(OpalescenceLib___TempUnit,'BTLF',2.)
endif
set s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]=s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+s__OpalescenceLib___OpalescenceS_speed[A]*s__vector_x[s__OpalescenceLib___OpalescenceS_v[A]]
set s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]=s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+s__OpalescenceLib___OpalescenceS_speed[A]*s__vector_y[s__OpalescenceLib___OpalescenceS_v[A]]
set s__vector_z[s__OpalescenceLib___OpalescenceS_l[A]]=s__vector_z[s__OpalescenceLib___OpalescenceS_l[A]]+s__OpalescenceLib___OpalescenceS_speed[A]*s__vector_z[s__OpalescenceLib___OpalescenceS_v[A]]
call OpalescenceLib___SetUnitPositionEx(s__OpalescenceLib___OpalescenceS_dummy[A],s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]])
call SetUnitFlyHeight(s__OpalescenceLib___OpalescenceS_dummy[A],s__vector_z[s__OpalescenceLib___OpalescenceS_l[A]]-OpalescenceLib___GetLocZ(s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]),0.00)
if s__OpalescenceLib___OpalescenceS_timeThreshold[A]<=0.00 then
call UnitApplyTimedLife(s__OpalescenceLib___OpalescenceS_dummy[A],'BTLF',0.30)
call SetUnitAnimation(s__OpalescenceLib___OpalescenceS_dummy[A],"death")
call TimerStart(s__OpalescenceLib___OpalescenceS_t[A],0.15,true,function OpalescenceLib___OpalescenceDamage)
set OpalescenceLib___TempUnit=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___PhaseID,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]],GetRandomReal(0.00,360.00))
call OpalescenceLib___SetUnitPositionEx(OpalescenceLib___TempUnit,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]])
call SetUnitFlyHeight(OpalescenceLib___TempUnit,300.00,0.00)
call SetUnitScale(OpalescenceLib___TempUnit,3.00,3.00,3.00)
call SetUnitAnimation(s__OpalescenceLib___OpalescenceS_dummy[A],"birth")
call QueueUnitAnimation(s__OpalescenceLib___OpalescenceS_dummy[A],"stand")
call UnitApplyTimedLife(OpalescenceLib___TempUnit,'BTLF',0.50)
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),0,OpalescenceLib___TempUnit)
call SaveReal(hash,GetHandleId(t),1,2.00)
call TimerStart(t,0.05,true,function OpalescenceLib___SetScale)
set OpalescenceLib___TempUnit=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___HealingID,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]],GetRandomReal(0.00,360.00))
call OpalescenceLib___SetUnitPositionEx(OpalescenceLib___TempUnit,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]])
call SetUnitScale(OpalescenceLib___TempUnit,2.00,2.00,2.00)
call SetUnitAnimation(OpalescenceLib___TempUnit,"death")
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),0,OpalescenceLib___TempUnit)
call SaveReal(hash,GetHandleId(t),1,2.00)
call TimerStart(t,0.05,true,function OpalescenceLib___SetScale_1)
set OpalescenceLib___TempUnit=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___PhaseID,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]],GetRandomReal(0.00,360.00))
call OpalescenceLib___SetUnitPositionEx(OpalescenceLib___TempUnit,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]])
call SetUnitFlyHeight(OpalescenceLib___TempUnit,300.00,0.00)
call SetUnitScale(OpalescenceLib___TempUnit,2.00,2.00,2.00)
call SetUnitAnimation(s__OpalescenceLib___OpalescenceS_dummy[A],"birth")
call QueueUnitAnimation(s__OpalescenceLib___OpalescenceS_dummy[A],"stand")
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),0,OpalescenceLib___TempUnit)
call SaveReal(hash,GetHandleId(t),1,2.00)
call TimerStart(t,0.05,true,function OpalescenceLib___SetScale)
set t=null
set i=10
loop
set B=s__OpalescenceLib___OpalescenceMoveS__allocate()
set s__OpalescenceLib___OpalescenceMoveS_t[B]=CreateTimer()
set s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]=s__vector_create(s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*0.25,s__OpalescenceLib___OpalescenceS_radius[A]*1.25)*Cos(GetRandomReal(-bj_PI,bj_PI)),s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*0.25,s__OpalescenceLib___OpalescenceS_radius[A]*1.25)*Sin(GetRandomReal(-bj_PI,bj_PI)),0.00)
set OpalescenceLib___TempUnit=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___FaerieID,s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],GetRandomReal(0.00,360.00))
call OpalescenceLib___SetUnitPositionEx(OpalescenceLib___TempUnit,s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]])
call SetUnitFlyHeight(OpalescenceLib___TempUnit,GetRandomReal(0.00,100.00),0.00)
call SetUnitAnimation(OpalescenceLib___TempUnit,"death")
call UnitApplyTimedLife(OpalescenceLib___TempUnit,'BTLF',1.00)
set s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]=s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(15.00,50.00)*Cos(GetRandomReal(-bj_PI,bj_PI))
set s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]=s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(15.00,50.00)*Sin(GetRandomReal(-bj_PI,bj_PI))
set s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]=OpalescenceLib___GetLocZ(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]])+GetRandomReal(400.00,600.00)
set j=1
loop
set s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]=s__vector_create(s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*1.80,s__OpalescenceLib___OpalescenceS_radius[A]*2.00)*Cos(GetRandomReal(-bj_PI,bj_PI)),s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*1.80,s__OpalescenceLib___OpalescenceS_radius[A]*2.00)*Sin(GetRandomReal(-bj_PI,bj_PI)),0.00)
set s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]]=OpalescenceLib___GetLocZ(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]])+GetRandomReal(-100.00,650.00)
set j=j+1
exitwhen j>=5
endloop
set s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]=s__vector_create(s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*0.80,s__OpalescenceLib___OpalescenceS_radius[A])*Cos(GetRandomReal(-bj_PI,bj_PI)),s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*0.80,s__OpalescenceLib___OpalescenceS_radius[A])*Sin(GetRandomReal(-bj_PI,bj_PI)),0.00)
set s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]]=OpalescenceLib___GetLocZ(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]])+GetRandomReal(50.00,100.00)
set s__OpalescenceLib___OpalescenceMoveS_last[B]=s__vector_create(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]])
set s__OpalescenceLib___OpalescenceMoveS_time[B]=0.00
set s__OpalescenceLib___OpalescenceMoveS_timeMax[B]=0.70
set s__OpalescenceLib___OpalescenceMoveS_dummy[B]=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___FaerieID,s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],GetRandomReal(0.00,360.00))
call OpalescenceLib___SetUnitPositionEx(s__OpalescenceLib___OpalescenceMoveS_dummy[B],s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]])
call SetUnitFlyHeight(s__OpalescenceLib___OpalescenceMoveS_dummy[B],s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]-OpalescenceLib___GetLocZ(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]),0.00)
call SetUnitAnimation(s__OpalescenceLib___OpalescenceMoveS_dummy[B],"birth")
call QueueUnitAnimation(s__OpalescenceLib___OpalescenceMoveS_dummy[B],"stand")
call SetUnitVertexColor(s__OpalescenceLib___OpalescenceMoveS_dummy[B],255,255,255,0)
call SaveInteger(hash,GetHandleId(s__OpalescenceLib___OpalescenceMoveS_t[B]),0,B)
call TimerStart(s__OpalescenceLib___OpalescenceMoveS_t[B],0.03125,true,function OpalescenceLib___OpalescenceMove)
set i=i-1
exitwhen i<0
endloop
endif
else
set s__OpalescenceLib___OpalescenceS_time[A]=s__OpalescenceLib___OpalescenceS_time[A]-0.15
call GroupEnumUnitsInRange(OpalescenceLib___TempGroup,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]],s__OpalescenceLib___OpalescenceS_radius[A]+200.00,null)
set mana_dmg=GetUnitState(s__OpalescenceLib___OpalescenceS_caster[A],UNIT_STATE_MANA)*0.03
call SetUnitState(s__OpalescenceLib___OpalescenceS_caster[A],UNIT_STATE_MANA,GetUnitState(s__OpalescenceLib___OpalescenceS_caster[A],UNIT_STATE_MANA)-mana_dmg*0.50)
loop
set u=FirstOfGroup(OpalescenceLib___TempGroup)
exitwhen u==null
call GroupRemoveUnit(OpalescenceLib___TempGroup,u)
if IsUnitInRangeXY(u,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]],s__OpalescenceLib___OpalescenceS_radius[A])then
if UnitAlive(u)and IsUnitEnemy(u,s__OpalescenceLib___OpalescenceS_p[A])then
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Items\\WandOfNeutralization\\NeutralizationMissile.mdl",u,OpalescenceLib___AttachPointName[GetRandomInt(0,5)]))
if s__OpalescenceLib___OpalescenceS_damage[A]>=0.00 then
call UnitDamageTarget(s__OpalescenceLib___OpalescenceS_caster[A],u,s__OpalescenceLib___OpalescenceS_damage[A],false,false,null,null,null)
endif
endif
endif
endloop
if s__OpalescenceLib___OpalescenceS_time[A]>=0.70 then
set B=s__OpalescenceLib___OpalescenceMoveS__allocate()
set s__OpalescenceLib___OpalescenceMoveS_t[B]=CreateTimer()
set s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]=s__vector_create(s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*0.25,s__OpalescenceLib___OpalescenceS_radius[A]*1.25)*Cos(GetRandomReal(-bj_PI,bj_PI)),s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*0.25,s__OpalescenceLib___OpalescenceS_radius[A]*1.25)*Sin(GetRandomReal(-bj_PI,bj_PI)),0.00)
set OpalescenceLib___TempUnit=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___FaerieID,s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],GetRandomReal(0.00,360.00))
call OpalescenceLib___SetUnitPositionEx(OpalescenceLib___TempUnit,s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]])
call SetUnitFlyHeight(OpalescenceLib___TempUnit,GetRandomReal(0.00,100.00),0.00)
call SetUnitAnimation(OpalescenceLib___TempUnit,"death")
call UnitApplyTimedLife(OpalescenceLib___TempUnit,'BTLF',1.00)
set s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]=s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(15.00,50.00)*Cos(GetRandomReal(-bj_PI,bj_PI))
set s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]=s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(15.00,50.00)*Sin(GetRandomReal(-bj_PI,bj_PI))
set s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]=OpalescenceLib___GetLocZ(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]])+GetRandomReal(400.00,600.00)
set j=1
loop
set s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]=s__vector_create(s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*1.80,s__OpalescenceLib___OpalescenceS_radius[A]*2.00)*Cos(GetRandomReal(-bj_PI,bj_PI)),s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*1.80,s__OpalescenceLib___OpalescenceS_radius[A]*2.00)*Sin(GetRandomReal(-bj_PI,bj_PI)),0.00)
set s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]]=OpalescenceLib___GetLocZ(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]])+GetRandomReal(-100.00,650.00)
set j=j+1
exitwhen j>=5
endloop
set s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]=s__vector_create(s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*0.80,s__OpalescenceLib___OpalescenceS_radius[A])*Cos(GetRandomReal(-bj_PI,bj_PI)),s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]]+GetRandomReal(s__OpalescenceLib___OpalescenceS_radius[A]*0.80,s__OpalescenceLib___OpalescenceS_radius[A])*Sin(GetRandomReal(-bj_PI,bj_PI)),0.00)
set s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]]=OpalescenceLib___GetLocZ(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]+j]])+GetRandomReal(50.00,100.00)
set s__OpalescenceLib___OpalescenceMoveS_last[B]=s__vector_create(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]])
set s__OpalescenceLib___OpalescenceMoveS_time[B]=0.00
set s__OpalescenceLib___OpalescenceMoveS_timeMax[B]=0.70
set s__OpalescenceLib___OpalescenceMoveS_dummy[B]=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___FaerieID,s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],GetRandomReal(0.00,360.00))
call OpalescenceLib___SetUnitPositionEx(s__OpalescenceLib___OpalescenceMoveS_dummy[B],s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]])
call SetUnitFlyHeight(s__OpalescenceLib___OpalescenceMoveS_dummy[B],s__vector_z[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]-OpalescenceLib___GetLocZ(s__vector_x[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]],s__vector_y[s___OpalescenceLib___OpalescenceMoveS_l[s__OpalescenceLib___OpalescenceMoveS_l[B]]]),0.00)
call SetUnitAnimation(s__OpalescenceLib___OpalescenceMoveS_dummy[B],"birth")
call QueueUnitAnimation(s__OpalescenceLib___OpalescenceMoveS_dummy[B],"stand")
call SetUnitVertexColor(s__OpalescenceLib___OpalescenceMoveS_dummy[B],255,255,255,0)
call SaveInteger(hash,GetHandleId(s__OpalescenceLib___OpalescenceMoveS_t[B]),0,B)
call TimerStart(s__OpalescenceLib___OpalescenceMoveS_t[B],0.03125,true,function OpalescenceLib___OpalescenceMove)
elseif s__OpalescenceLib___OpalescenceS_time[A]<=0.00 then
call PauseTimer(s__OpalescenceLib___OpalescenceS_t[A])
call FlushChildHashtable(hash,GetHandleId(s__OpalescenceLib___OpalescenceS_t[A]))
call DestroyTimer(s__OpalescenceLib___OpalescenceS_t[A])
set s__OpalescenceLib___OpalescenceS_t[A]=null
set s__OpalescenceLib___OpalescenceS_dummy[A]=null
set s__OpalescenceLib___OpalescenceS_caster[A]=null
call s__vector_deallocate(s__OpalescenceLib___OpalescenceS_l[A])
call s__vector_deallocate(s__OpalescenceLib___OpalescenceS_v[A])
call s__vector_deallocate(s__OpalescenceLib___OpalescenceS_endPos[A])
call s__OpalescenceLib___OpalescenceS_deallocate(A)
endif
endif
endfunction
function Opalescence_Actions takes nothing returns nothing
local integer A=s__OpalescenceLib___OpalescenceS__allocate()
set s__OpalescenceLib___OpalescenceS_t[A]=CreateTimer()
set s__OpalescenceLib___OpalescenceS_caster[A]=GetTriggerUnit()
set s__OpalescenceLib___OpalescenceS_p[A]=GetOwningPlayer(s__OpalescenceLib___OpalescenceS_caster[A])
set s__OpalescenceLib___OpalescenceS_damage[A]=30.+udg_ItemBonusDMG[GetPlayerId(s__OpalescenceLib___OpalescenceS_p[A])+1]*0.05
set s__OpalescenceLib___OpalescenceS_radius[A]=400.00
set s__OpalescenceLib___OpalescenceS_time[A]=10.00
set s__OpalescenceLib___OpalescenceS_timeThreshold[A]=0.70
set s__OpalescenceLib___OpalescenceS_l[A]=s__vector_create(GetUnitX(s__OpalescenceLib___OpalescenceS_caster[A]),GetUnitY(s__OpalescenceLib___OpalescenceS_caster[A]),0.00)
set s__vector_z[s__OpalescenceLib___OpalescenceS_l[A]]=OpalescenceLib___GetLocZ(s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]])
set s__OpalescenceLib___OpalescenceS_endPos[A]=s__vector_create(GetSpellTargetX(),GetSpellTargetY(),0.00)
set s__vector_z[s__OpalescenceLib___OpalescenceS_endPos[A]]=OpalescenceLib___GetLocZ(s__vector_x[s__OpalescenceLib___OpalescenceS_endPos[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_endPos[A]])+300.00
set s__OpalescenceLib___OpalescenceS_v[A]=s__vector_create(s__vector_x[s__OpalescenceLib___OpalescenceS_endPos[A]]-s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_endPos[A]]-s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_z[s__OpalescenceLib___OpalescenceS_endPos[A]]-s__vector_z[s__OpalescenceLib___OpalescenceS_l[A]])
set s__OpalescenceLib___OpalescenceS_speed[A]=s__vector_length(s__OpalescenceLib___OpalescenceS_v[A])*1.30*0.01
call s__vector_normalize(s__OpalescenceLib___OpalescenceS_v[A])
set s__OpalescenceLib___OpalescenceS_dummy[A]=CreateUnit(s__OpalescenceLib___OpalescenceS_p[A],OpalescenceLib___AbolishID,s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]],Atan2(s__vector_y[s__OpalescenceLib___OpalescenceS_v[A]],s__vector_x[s__OpalescenceLib___OpalescenceS_v[A]])*bj_RADTODEG)
call SetUnitX(s__OpalescenceLib___OpalescenceS_dummy[A],s__vector_x[s__OpalescenceLib___OpalescenceS_l[A]])
call SetUnitY(s__OpalescenceLib___OpalescenceS_dummy[A],s__vector_y[s__OpalescenceLib___OpalescenceS_l[A]])
call SetUnitScale(s__OpalescenceLib___OpalescenceS_dummy[A],2.00,2.00,2.00)
call UnitApplyTimedLife(s__OpalescenceLib___OpalescenceS_dummy[A],'BTLF',1.00)
call SetUnitAnimation(s__OpalescenceLib___OpalescenceS_dummy[A],"birth")
call QueueUnitAnimation(s__OpalescenceLib___OpalescenceS_dummy[A],"stand")
call SaveInteger(hash,GetHandleId(s__OpalescenceLib___OpalescenceS_t[A]),0,A)
call TimerStart(s__OpalescenceLib___OpalescenceS_t[A],0.01,true,function OpalescenceLib___OpalescenceDamage)
endfunction
function Opalescence_Conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0L0'
endfunction
```

## 虛空引爆 `A0CT`　—　吃技能強度

俄文原名：Пустотный подрыв

```
引爆生效中的「虛空充能」，造成範圍傷害。內圈範圍造成全額傷害，外圈範圍造成 50% 傷害。

全額傷害：50% 英雄當前法力值 + 100% 技能強度
內圈範圍：225 點
外圈範圍：450 點

冷卻：10 秒。
```

物件欄位（原型 `ANcl`）：`Ncl1 = 0.8999999761581421`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = 0.8999999761581421`, `Ncl5 = 0`, `Ncl6 = ['drain', 'channel']`, `acap = `, `acdn = [10.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [125, 95, 110, 140, 155, 170]`, `aran = [None, 100.0]`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`HeroA54_Boom`　war3map.j:64905
```jass
function HeroA54_Boom takes unit u,unit u2 returns nothing
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real dmg=GetUnitState(u,UNIT_STATE_MANA)*0.25+udg_ItemBonusDMG[n]*0.50
local unit u3
local group ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,225.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,450.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call DestroyEffect(AddSpecialEffect("war3mapImported\\DarkNova.mdx",x,y))
call KillUnit(u2)
set pl=null
set ug=null
set u3=null
endfunction
```

`Trig_HeroSkills54_Actions`　war3map.j:65165
```jass
elseif Skill=='A0CT' then
call HeroA54_Boom(u,LoadUnitHandle(hash,GetHandleId(u),'A0KU'))
```

## 知識傳承 `A0YT`

俄文原名：Унаследование знаний

```
繼承所選敵方英雄的一項技能。

使用「-clear skill」指令可以重新選擇敵方英雄。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [1.2000000476837158, 0.8999999761581421]`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = [1.2000000476837158, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['setrally', 'channel']`, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = [1000.0, 100.0]`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills54_Actions`　war3map.j:65213
```jass
elseif Skill=='A0YT' then
set u3=GetSpellTargetUnit()
if IsUnitType(u3,UNIT_TYPE_HERO)then
set Id=GetHandleId(u)
set lvl=LoadInteger(hash,GetUnitTypeId(u3),1)
call UnitRemoveAbility(u,Skill)
call UnitAddAbility(u,lvl)
call SaveInteger(hash,GetHandleId(pl),'A0YT',lvl)
if lvl=='A07C' then
call SaveReal(hash,Id,29,LoadReal(hash,Id,29)+0.30)
endif
if lvl=='A0CL' then
call SaveReal(hash,Id,45,LoadReal(hash,Id,45)+0.30)
endif
if lvl=='A0CK' then
call UnitAddAbility(u,'S002')
endif
if lvl=='A0N8' then
call UnitAddAbility(u,'ACat')
endif
if lvl=='A0OL' then
call UnitAddAbility(u,'A0FD')
endif
if lvl=='A0Z5' then
call SaveReal(hash,Id,45,LoadReal(hash,Id,45)+0.50)
call SaveInteger(hash,Id,45,LoadInteger(hash,Id,45)+1)
endif
if lvl=='A0ZK' then
call SaveReal(hash,Id,46,LoadReal(hash,Id,46)+0.50)
endif
if lvl=='A0BM' then
call SaveReal(hash,Id,47,LoadReal(hash,Id,47)-0.50)
call SaveReal(hash,Id,48,LoadReal(hash,Id,48)-0.50)
call SaveReal(hash,Id,49,LoadReal(hash,Id,49)-0.50)
call SaveReal(hash,Id,50,LoadReal(hash,Id,50)-0.50)
endif
endif
endif
```

`Trig_SkillsInfo54_Actions`　war3map.j:65267
```jass
if GetUnitAbilityLevel(udg_Hero[n],'A0YT')!=1 then
call UnitRemoveAbility(udg_Hero[n],LoadInteger(hash,pl_Id,'A0YT'))
call UnitAddAbility(udg_Hero[n],'A0YT')
if LoadInteger(hash,pl_Id,'A0YT')=='A07C' then
call SaveReal(hash,u_Id,29,LoadReal(hash,u_Id,29)-0.30)
endif
if LoadInteger(hash,pl_Id,'A0YT')=='A0CL' then
call SaveReal(hash,u_Id,45,LoadReal(hash,u_Id,45)-0.30)
endif
if LoadInteger(hash,pl_Id,'A0YT')=='A0CK' then
call UnitRemoveAbility(udg_Hero[n],'S002')
endif
if LoadInteger(hash,pl_Id,'A0YT')=='A0N8' then
call UnitRemoveAbility(udg_Hero[n],'ACat')
endif
if LoadInteger(hash,pl_Id,'A0YT')=='A0OL' then
call UnitRemoveAbility(udg_Hero[n],'A0FD')
endif
if LoadInteger(hash,pl_Id,'A0YT')=='A0Z5' then
call SaveReal(hash,u_Id,45,LoadReal(hash,u_Id,45)-0.50)
call SaveInteger(hash,u_Id,45,LoadInteger(hash,u_Id,45)-1)
endif
if LoadInteger(hash,pl_Id,'A0YT')=='A0ZK' then
call SaveReal(hash,u_Id,46,LoadReal(hash,u_Id,46)-0.50)
endif
if LoadInteger(hash,pl_Id,'A0YT')=='A0BM' then
call SaveReal(hash,u_Id,47,LoadReal(hash,u_Id,47)+0.50)
call SaveReal(hash,u_Id,48,LoadReal(hash,u_Id,48)+0.50)
call SaveReal(hash,u_Id,49,LoadReal(hash,u_Id,49)+0.50)
call SaveReal(hash,u_Id,50,LoadReal(hash,u_Id,50)+0.50)
endif
endif
```

## 耀目法光 `A0BQ`


```
英雄以及地圖上你所有的部隊與友軍獲得 1% 法力值回復。
```

物件欄位（原型 `ACba`）：`Hab1 = 0.009999999776482582`, `Hab2 = 1`, `aare = 99999.0`, `abuf = B00L`

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

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

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它
  - **8** — 對英雄減傷〔受害者〕
  - **29** — 實數＝流血傷害 +%〔施加者〕／整數＝抵抗流血旗標〔受害者〕（加成寫錯變數，實際無效 —— 見 地圖問題回報 A-4）
  - **45** — 實數＝疾病傷害 +%〔施加者〕／整數＝抵抗疾病旗標〔受害者〕（加成同樣寫錯變數）
  - **46** — 易燃效果強化〔施加者〕影響易燃的機率倍率與跳數加成
  - **47** — 點燃抗性〔受害者〕係數減去它；電擊讓它 −1.00
  - **48** — 冰凍抗性〔受害者〕；電擊 −1.00
  - **49** — 流血抗性〔受害者〕；電擊 −1.00
  - **50** — 疾病抗性〔受害者〕；電擊 −1.00

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
