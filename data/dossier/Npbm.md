# 龍戰士 `Npbm`（Воин Дракона）

主屬性 **敏捷** · 背包 **6 格** · 解鎖 500000 · 定位 戰士/刺客

| | 初始 | 每級 |
|---|---|---|
| 力量 | None | None |
| 敏捷 | 22 | 3.0 |
| 智力 | 18 | 2.0 |

> 結實的近戰英雄，強化路線很多，部分技能有獨立運作方式。

**縮放**：吃技能強度的技能 ['A08M', 'A08T', 'A08W', 'A08Y'] ／ ◈ 吃裝備技能威力 ['A08W'] ／ ⊕ 給裝備技能威力 無

---

## 火焰法球 `A08T`　—　吃技能強度

俄文原名：Огненные сферы

```
3 顆火焰法球開始環繞英雄旋轉，點燃敵人。法球起初只造成 25% 傷害，隨著遠離英雄逐漸提升自身傷害，直到進入軌道為止。

點燃：100% 機率；50 + （25% 技能強度）點傷害
法球持續時間：6 秒

冷卻：20 秒
```

每級變動：
  - 第 3 行：50 / 75 / 100 / 125 / 150

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = channel`, `acdn = 20.0`, `alev = 5`, `amcs = [90, 100, 110, 120, 130]`

實作：

`BurnUnit`　war3map.j:1837
```jass
function BurnUnit takes unit damager,unit target,real dmg,real chanse returns nothing
local timer t
local integer Id
local integer count
local integer count2
local integer i
local integer i2
local real cof
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local effect e
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)then
set chanse=chanse*0.50
elseif LoadInteger(hash,GetHandleId(target),'tkno')>=1 then
elseif LoadInteger(hash,GetHandleId(target),27)>0 and LoadInteger(hash,GetHandleId(damager),'A03M')!=1 then
if LoadInteger(hash,GetHandleId(target),27)>50 then
set chanse=0.
endif
if GetUnitTypeId(damager)=='h01A' or GetUnitTypeId(damager)=='h01B' then
if GetPlayerTechCount(GetOwningPlayer(damager),'Ropm',true)==1 then
set chanse=chanse*1.75
else
set chanse=chanse*1.00
endif
else
set chanse=chanse*0.25
endif
elseif not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 and LoadInteger(hash,GetHandleId(damager),'A03M')!=1 then
set chanse=0.
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if GetUnitAbilityLevel(target,'B042')==1 then
set chanse=chanse*(1.00+(0.50*(1.00+LoadReal(hash,GetHandleId(damager),46))))
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if LoadInteger(hash,GetHandleId(damager),'A03M')==1 then
set cof=1.0*(1.00+(0.50*(1.00+LoadReal(hash,GetHandleId(damager),46))))
if LoadInteger(hash,t_Id,'I07A')>=1 then
if UnitLifePercent(target)<=25.0 then
set cof=cof-0.50
endif
endif
if LoadInteger(hash,t_Id,'I048')>=1 then
if UnitLifePercent(target)<=30.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'tbak')>=1 then
if UnitLifePercent(target)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(target)>=75.0 then
set cof=cof-0.18
endif
endif
if LoadInteger(hash,d_Id,'gvsm')>=1 or LoadInteger(hash,d_Id,'I00S')>=1 then
if GetUnitAbilityLevel(target,'B02V')==1 then
set cof=cof+0.35
endif
endif
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,27)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
if cof<0.20 then
set cof=0.20
endif
set cof=cof-LoadReal(hash,t_Id,47)+LoadReal(hash,d_Id,27)
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\AerialExplosionV3.mdx",target,"origin"))
call EnableTrigger(gg_trg_HeroTakeDamage)
set t=null
set e=null
return
endif
set dmg=dmg/16.
set count=16
if GetUnitAbilityLevel(target,'B042')==1 then
set count=count+R2I(8.0*(1.00+(1.00+LoadReal(hash,GetHandleId(damager),46))))
endif
if GetUnitAbilityLevel(target,'A064')==1 then
set count=count/2
endif
set count2=LoadInteger(hash,t_Id,'burn')
if count2==0 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,0,target)
call SaveUnitHandle(hash,Id,1,damager)
call SaveInteger(hash,Id,1,count)
call SaveReal(hash,Id,1,dmg)
call UnitAddAbility(target,'A0Y6')
call SaveInteger(hash,t_Id,'burn',1)
call SaveTimerHandle(hash,t_Id,'burt',t)
call TimerStart(t,0.25,true,function Burn_Dmg)
else
set t=LoadTimerHandle(hash,t_Id,'burt')
set Id=GetHandleId(t)
set i2=0
set i=0
loop
set i=i+1
if LoadInteger(hash,Id,i)==0 then
call SaveUnitHandle(hash,Id,i,damager)
call SaveInteger(hash,Id,i,count)
call SaveReal(hash,Id,i,dmg)
call SaveInteger(hash,t_Id,'burn',i)
set i=count2
set i2=1
endif
exitwhen i==count2
endloop
if i2==0 then
set count2=count2+1
call SaveUnitHandle(hash,Id,count2,damager)
call SaveInteger(hash,Id,count2,count)
call SaveReal(hash,Id,count2,dmg)
call SaveInteger(hash,t_Id,'burn',count2)
endif
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
else
if LoadInteger(hash,GetHandleId(damager),'silk')>=1 then
call FlammabilityUnit(damager,target,0.35)
endif
endif
set t=null
set e=null
endfunction
```

`HeroQ45_Move`　war3map.j:60318
```jass
if dist>100 and dist<200 then
call SaveReal(hash,GetHandleId(u),'A08T',0.50)
elseif dist>200 and dist<max_dist then
call SaveReal(hash,GetHandleId(u),'A08T',0.75)
elseif dist>max_dist then
set dist=max_dist
call SaveReal(hash,GetHandleId(u),'A08T',1.00)
endif
```

`HeroQ45_Dmg`　war3map.j:60340
```jass
function HeroQ45_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2=LoadUnitHandle(hash,Id,2)
local unit u3
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local timer t2
local integer count=LoadInteger(hash,Id,3)
local real dmg=25.+25.*I2R(GetUnitAbilityLevel(u,'A08T'))+udg_ItemBonusDMG[n]*0.25
local group ug=CreateGroup()
local real cof=LoadReal(hash,GetHandleId(u),'A08T')
set dmg=dmg*cof
call GroupEnumUnitsInRange(ug,x,y,150.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call BurnUnit(u,u3,dmg,1.00)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
set count=count-1
if count==0 then
call KillUnit(u2)
set t2=LoadTimerHandle(hash,Id,3)
call FlushChildHashtable(hash,GetHandleId(t2))
call PauseTimer(t2)
call DestroyTimer(t2)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
else
call SaveInteger(hash,Id,3,count)
endif
set t=null
set t2=null
set u=null
set u2=null
set u3=null
set ug=null
set pl=null
endfunction
```

`Trig_HeroSkills45_Actions`　war3map.j:60406
```jass
if Skill=='A08T' then
set x=GetUnitX(u)
set y=GetUnitY(u)
call SaveReal(hash,GetHandleId(u),'A08T',0.25)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,2,50)
call SaveReal(hash,Id,3,0)
set angle=GetUnitFacing(u)
set x2=PolarX(x,50,angle)
set y2=PolarY(y,50,angle)
set u2=CreateUnit(pl,'h042',x2,y2,angle)
call SaveUnitHandle(hash,Id,2,u2)
call TimerStart(t,0.03,true,function HeroQ45_Move)
set t2=CreateTimer()
set Id=GetHandleId(t2)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,3,60)
call SaveTimerHandle(hash,Id,3,t)
call TimerStart(t2,0.20,true,function HeroQ45_Dmg)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,2,50)
call SaveReal(hash,Id,3,120)
set angle=GetUnitFacing(u)+120
set x2=PolarX(x,50,angle)
set y2=PolarY(y,50,angle)
set u2=CreateUnit(pl,'h042',x2,y2,angle)
call SaveUnitHandle(hash,Id,2,u2)
call TimerStart(t,0.03,true,function HeroQ45_Move)
set t2=CreateTimer()
set Id=GetHandleId(t2)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,3,60)
call SaveTimerHandle(hash,Id,3,t)
call TimerStart(t2,0.20,true,function HeroQ45_Dmg)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,2,50)
call SaveReal(hash,Id,3,240)
set angle=GetUnitFacing(u)+240
set x2=PolarX(x,50,angle)
set y2=PolarY(y,50,angle)
set u2=CreateUnit(pl,'h042',x2,y2,angle)
call SaveUnitHandle(hash,Id,2,u2)
call TimerStart(t,0.03,true,function HeroQ45_Move)
set t2=CreateTimer()
```

## 輕盈步伐 `A08M`　—　吃技能強度

俄文原名：Легкая поступь

```
提高英雄的移動速度並開始逐漸回復生命值。移動中的英雄可回復更多生命值。

移動速度加成：15%
生命值回復：18 + （5% 技能強度）點/秒
移動中的治療強化：在競技場上每 100 點移動速度使治療 +30%
持續時間：8 秒

冷卻：17 秒
```

每級變動：
  - 第 3 行：15 / 20 / 25 / 30 / 35
  - 第 4 行：18 / 27 / 36 / 45 / 54

物件欄位（原型 `Absk`）：`abuf = B03E`, `acdn = 17.0`, `adur = 8.0`, `ahdu = 8.0`, `aher = 1`, `alev = 5`, `amcs = [70, 81, 92, 103, 114]`, `bsk1 = [0.20000000298023224, 0.25, 0.30000001192092896, 0.3500000238418579, 0.15000000596046448]`, `bsk2 = 0.0`, `bsk3 = 0.0`

實作：

`Hero45_Move`　war3map.j:60272
```jass
function Hero45_Move takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local integer n=GetPlayerId(GetOwningPlayer(u))+1
local integer count=LoadInteger(hash,Id,1)
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local real dist=LoadReal(hash,Id,3)
local real x2=GetUnitX(u)
local real y2=GetUnitY(u)
local real heal
set x=DistanceNative(x,y,x2,y2)
set heal=(9+9*I2R(GetUnitAbilityLevel(u,'A08M'))+udg_ItemBonusDMG[n]*0.05)*0.10
if x>10.00 then
set y=1.00+(x-10.00)*0.03
call SetUnitState(u,UNIT_STATE_LIFE,GetUnitState(u,UNIT_STATE_LIFE)+heal*y)
else
call SetUnitState(u,UNIT_STATE_LIFE,GetUnitState(u,UNIT_STATE_LIFE)+heal)
endif
set count=count-1
if count==0 then
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
else
call SaveInteger(hash,Id,1,count)
call SaveReal(hash,Id,1,x2)
call SaveReal(hash,Id,2,y2)
call SaveReal(hash,Id,3,dist)
endif
set t=null
set u=null
endfunction
```

`Trig_HeroSkills45_Actions`　war3map.j:60464
```jass
elseif Skill=='A08M' then
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.10,true,function Hero45_Move)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,GetUnitX(u))
call SaveReal(hash,Id,2,GetUnitY(u))
call SaveReal(hash,Id,3,0)
call SaveInteger(hash,Id,1,80)
```

## 巨龍吐息 `A08Y`　—　吃技能強度

俄文原名：Дыхание дракона

```
繼承裝備技能的加成。

每第 7 次攻擊會朝被攻擊的敵人方向產生一道點燃的火焰波。

火焰波傷害：40 + （18% 技能強度）點
火焰波點燃：100% 機率，100% 傷害
```

每級變動：
  - 第 5 行：40 / 60 / 80 / 100 / 120

物件欄位（原型 `Amgl`）：`aher = 1`, `alev = 5`

實作：

`BurnUnit`　war3map.j:1837
```jass
function BurnUnit takes unit damager,unit target,real dmg,real chanse returns nothing
local timer t
local integer Id
local integer count
local integer count2
local integer i
local integer i2
local real cof
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local effect e
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)then
set chanse=chanse*0.50
elseif LoadInteger(hash,GetHandleId(target),'tkno')>=1 then
elseif LoadInteger(hash,GetHandleId(target),27)>0 and LoadInteger(hash,GetHandleId(damager),'A03M')!=1 then
if LoadInteger(hash,GetHandleId(target),27)>50 then
set chanse=0.
endif
if GetUnitTypeId(damager)=='h01A' or GetUnitTypeId(damager)=='h01B' then
if GetPlayerTechCount(GetOwningPlayer(damager),'Ropm',true)==1 then
set chanse=chanse*1.75
else
set chanse=chanse*1.00
endif
else
set chanse=chanse*0.25
endif
elseif not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 and LoadInteger(hash,GetHandleId(damager),'A03M')!=1 then
set chanse=0.
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if GetUnitAbilityLevel(target,'B042')==1 then
set chanse=chanse*(1.00+(0.50*(1.00+LoadReal(hash,GetHandleId(damager),46))))
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if LoadInteger(hash,GetHandleId(damager),'A03M')==1 then
set cof=1.0*(1.00+(0.50*(1.00+LoadReal(hash,GetHandleId(damager),46))))
if LoadInteger(hash,t_Id,'I07A')>=1 then
if UnitLifePercent(target)<=25.0 then
set cof=cof-0.50
endif
endif
if LoadInteger(hash,t_Id,'I048')>=1 then
if UnitLifePercent(target)<=30.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'tbak')>=1 then
if UnitLifePercent(target)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(target)>=75.0 then
set cof=cof-0.18
endif
endif
if LoadInteger(hash,d_Id,'gvsm')>=1 or LoadInteger(hash,d_Id,'I00S')>=1 then
if GetUnitAbilityLevel(target,'B02V')==1 then
set cof=cof+0.35
endif
endif
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,27)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
if cof<0.20 then
set cof=0.20
endif
set cof=cof-LoadReal(hash,t_Id,47)+LoadReal(hash,d_Id,27)
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\AerialExplosionV3.mdx",target,"origin"))
call EnableTrigger(gg_trg_HeroTakeDamage)
set t=null
set e=null
return
endif
set dmg=dmg/16.
set count=16
if GetUnitAbilityLevel(target,'B042')==1 then
set count=count+R2I(8.0*(1.00+(1.00+LoadReal(hash,GetHandleId(damager),46))))
endif
if GetUnitAbilityLevel(target,'A064')==1 then
set count=count/2
endif
set count2=LoadInteger(hash,t_Id,'burn')
if count2==0 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,0,target)
call SaveUnitHandle(hash,Id,1,damager)
call SaveInteger(hash,Id,1,count)
call SaveReal(hash,Id,1,dmg)
call UnitAddAbility(target,'A0Y6')
call SaveInteger(hash,t_Id,'burn',1)
call SaveTimerHandle(hash,t_Id,'burt',t)
call TimerStart(t,0.25,true,function Burn_Dmg)
else
set t=LoadTimerHandle(hash,t_Id,'burt')
set Id=GetHandleId(t)
set i2=0
set i=0
loop
set i=i+1
if LoadInteger(hash,Id,i)==0 then
call SaveUnitHandle(hash,Id,i,damager)
call SaveInteger(hash,Id,i,count)
call SaveReal(hash,Id,i,dmg)
call SaveInteger(hash,t_Id,'burn',i)
set i=count2
set i2=1
endif
exitwhen i==count2
endloop
if i2==0 then
set count2=count2+1
call SaveUnitHandle(hash,Id,count2,damager)
call SaveInteger(hash,Id,count2,count)
call SaveReal(hash,Id,count2,dmg)
call SaveInteger(hash,t_Id,'burn',count2)
endif
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
else
if LoadInteger(hash,GetHandleId(damager),'silk')>=1 then
call FlammabilityUnit(damager,target,0.35)
endif
endif
set t=null
set e=null
endfunction
```

`Trig_HeroTakeDamage_Actions`　war3map.j:19576
```jass
if LoadInteger(hash,Id,'A08Y')==1 then
if UnitAlive(d)then
call BurnUnit(a,d,r*1.00,1.00)
endif
endif
```

`HeroE45_Cd`　war3map.j:60514
```jass
function HeroE45_Cd takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
call SaveInteger(hash,GetHandleId(u),'B08Y',0)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
set t=null
set u=null
endfunction
```

`Trig_HeroAttack45_Actions`　war3map.j:60560
```jass
if GetUnitAbilityLevel(u,'A08Y')>0 and LoadInteger(hash,GetHandleId(u),'B08Y')!=1 then
set Id=LoadInteger(hash,u_Id,'A08Y')
set Id=Id+1
if Id>=7 then
set Id=0
set x=GetUnitX(u)
set y=GetUnitY(u)
set u3=CreateUnit(pl,'o010',x,y,270)
call UnitApplyTimedLife(u3,'BTLF',2.)
set dmg=20.+20.*I2R(GetUnitAbilityLevel(u,'A08Y'))+udg_ItemBonusDMG[n]*0.18
set dmg=dmg*cof
call SaveReal(hash,GetHandleId(u3),13,dmg)
call SaveInteger(hash,GetHandleId(u3),'A08Y',1)
call SaveUnitHandle(hash,GetHandleId(u3),13,u)
set x=GetUnitX(u2)
set y=GetUnitY(u2)
call UnitAddAbility(u3,'A08Z')
call IssuePointOrderById(u3,Order_carrionswarm,x,y)
endif
call SaveInteger(hash,u_Id,'A08Y',Id)
call SaveInteger(hash,u_Id,'B08Y',1)
set t=CreateTimer()
call TimerStart(t,0.30,false,function HeroE45_Cd)
call SaveUnitHandle(hash,GetHandleId(t),1,u)
endif
```

## 無錫手指扣 `A08V`

俄文原名：Пальцевой захват Уси

```
對近戰範圍內的敵人施展致命招式，造成大量傷害並同時施加多種狀態。也會波及目標周圍的敵人。

對普通士兵使用：對目標造成 600 +（350% 力量與敏捷）點傷害；其中 30% 的傷害會作用於目標周圍的區域
狀態施加：200% 機率施加易燃、虛弱、詛咒、易傷；附近的敵人有 30% 機率被施加虛弱

冷卻：80 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.4000000059604645, 1.0]`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = [0.4000000059604645, 1.0]`, `Ncl5 = 0`, `Ncl6 = ['channel', 'chemicalrage']`, `acdn = [80.0, 17.0]`, `alev = 1`, `amcs = [135, 80, 90, 100, 110, 120]`, `aran = [700.0, 128.0]`, `atar = ['air,ground,enemy,neutral,organic', 'air,ground,friend,neutral,self']`

實作：

`FlammabilityUnit`　war3map.j:1693
```jass
function FlammabilityUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)then
set chanse=chanse*0.50
elseif LoadInteger(hash,GetHandleId(target),'tkno')>=1 then
elseif LoadInteger(hash,GetHandleId(target),27)>0 then
set chanse=chanse*0.25
elseif not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B042')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B042')
call TimerStart(t,6.,false,function RemoveFlammability)
else
call UnitAddAbility(target,'S00M')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B042',t)
call TimerStart(t,6.,false,function RemoveFlammability)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

`WeakUnit`　war3map.j:2398
```jass
function WeakUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(target),30)>0 then
if LoadInteger(hash,GetHandleId(target),30)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B043')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B043')
call TimerStart(t,8.,false,function RemoveWeak)
else
call UnitAddAbility(target,'S00N')
call SaveReal(hash,GetHandleId(target),49,LoadReal(hash,GetHandleId(target),49)-0.50)
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B043',t)
call TimerStart(t,8.,false,function RemoveWeak)
endif
if UnitHasItemOfType(damager,'I044')then
call UnitDamageTarget(damager,target,I2R(GetHeroAgi(damager,true)),false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\SoulRitual.mdx",target,"origin"))
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

`CurseUnit`　war3map.j:2461
```jass
function CurseUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
local integer u_Id=GetHandleId(target)
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(target),30)>0 then
if LoadInteger(hash,GetHandleId(target),30)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B044')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B044')
call TimerStart(t,8.,false,function RemoveCurse)
else
call UnitAddAbility(target,'A0Y9')
call SaveReal(hash,GetHandleId(target),50,LoadReal(hash,GetHandleId(target),50)-0.50)
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)-0.20)
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B044',t)
call TimerStart(t,8.,false,function RemoveCurse)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

`VulnerabilityUnit`　war3map.j:2519
```jass
function VulnerabilityUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(target),30)>0 then
if LoadInteger(hash,GetHandleId(target),30)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B045')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B045')
call TimerStart(t,8.,false,function RemoveVulnerability)
else
call UnitAddAbility(target,'S014')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B045',t)
call TimerStart(t,8.,false,function RemoveVulnerability)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

`Trig_HeroSkills45_Actions`　war3map.j:60473
```jass
elseif Skill=='A08V' then
set dmg=600+I2R(GetHeroStr(u,true)+GetHeroAgi(u,true))*3.50
set x=GetUnitX(u2)
set y=GetUnitY(u2)
call DestroyEffect(AddSpecialEffect("war3mapImported\\NewDirtEXNofire.mdx",x,y))
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x,y))
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call VulnerabilityUnit(u,u2,2.00)
call WeakUnit(u,u2,2.00)
call CurseUnit(u,u2,2.00)
call FlammabilityUnit(u,u2,2.00)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,325.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)and u3 !=u2 then
call UnitDamageTarget(u,u3,dmg*0.30,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call VulnerabilityUnit(u,u2,0.30)
call WeakUnit(u,u2,0.30)
call CurseUnit(u,u2,0.30)
call FlammabilityUnit(u,u2,0.30)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
```

## 轉移／移除據點 `A03V`

俄文原名：Передать/удалить точку

```
選擇自己的據點或建築，將其轉移給其他玩家，或在不損失地基的情況下摧毀它。可從任意距離施放。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.009999999776482582, 0.8999999761581421]`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = [0.009999999776482582, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['channel', 'unburrow']`, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [95, 110, 125, 140, 155, 170]`, `aran = [99999.0, 100.0]`, `atar = ['player,structure', 'air,ground,debris,enemy,neutral,organic']`

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

## 烈焰之刃 `A08W`　—　吃技能強度、◈ 吃裝備技能威力

俄文原名：Пламенные клинки

```
繼承裝備技能的加成。

英雄的攻擊有機會造成額外的範圍傷害，並以較高的機率對敵人施加易燃。

範圍傷害：20 +（40% 力量與敏捷）+（15% 技能強度）點
「易燃」狀態：以 120% 機率施加於敵人

冷卻：10 秒
```

實作：

`FlammabilityUnit`　war3map.j:1693
```jass
function FlammabilityUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)then
set chanse=chanse*0.50
elseif LoadInteger(hash,GetHandleId(target),'tkno')>=1 then
elseif LoadInteger(hash,GetHandleId(target),27)>0 then
set chanse=chanse*0.25
elseif not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B042')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B042')
call TimerStart(t,6.,false,function RemoveFlammability)
else
call UnitAddAbility(target,'S00M')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B042',t)
call TimerStart(t,6.,false,function RemoveFlammability)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

`StartModCooldown`　war3map.j:2914
```jass
function StartModCooldown takes integer u_Id,integer i_Id,real CD returns nothing
local real CDCof=LoadReal(hash,u_Id,1)
local timer t=CreateTimer()
if CDCof<0.20 then
set CDCof=0.20
endif
set CD=CD*CDCof
call SaveReal(hash,u_Id,i_Id,1.)
set t=CreateTimer()
call SaveInteger(hash,GetHandleId(t),1,u_Id)
call SaveInteger(hash,GetHandleId(t),2,i_Id)
call TimerStart(t,CD,false,function EndModCooldown)
set t=null
endfunction
```

`Trig_HeroAttack45_Actions`　war3map.j:60539
```jass
if LoadReal(hash,u_Id,'A08W')==0. then
call StartModCooldown(u_Id,'A08W',10.)
set cof=LoadReal(hash,u_Id,18)+1.
set x=GetUnitX(u2)
set y=GetUnitY(u2)
set dmg=20+udg_ItemBonusDMG[n]*0.15+(I2R(GetHeroStr(u,true)+GetHeroAgi(u,true)))*0.40
set dmg=dmg*cof
call DestroyEffect(AddSpecialEffect("war3mapImported\\Conflagrate.mdl",x,y))
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,235.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call FlammabilityUnit(u,u3,1.20)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
```

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數
  - **3** — 對英雄傷害 +%
  - **4** — 受到傷害 −%（被減的）
  - **18** — 裝備技能威力
  - **27** — 點燃傷害 +%／（整數槽）抵抗點燃旗標
  - **44** — （狀態免疫旗標）
  - **46** — 易燃效果強化
  - **47** — 點燃抗性
  - **49** — 流血抗性
  - **50** — 疾病抗性

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
