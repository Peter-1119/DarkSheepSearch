# 超重型坦克 `Nsjs`（Сверхтяжёлый танк）

主屬性 **力量** · 背包 **6 格** · 解鎖 0 · 定位 戰士/坦克 · **不在隨機池**（只能手動挑）

| | 初始 | 每級 |
|---|---|---|
| 力量 | 38 | 6 |
| 敏捷 | 6 | 1 |
| 智力 | 20 | 2.2 |

> 結實的遠程英雄，防禦類型為「強化」，側翼砲塔會自動射擊前方敵人，可累積點燃強化。

**縮放**：吃技能強度的技能 ['A0XO', 'A0XS'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **狀態** —— 走 `Burn_Dmg` 那條，**外面包了 DisableTrigger** → 不吃 DefCof、不帶穿透、被狀態抗性擋。該買的是「狀態傷害 +%」「易燃」「機率倍率」。
- **直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且事件數越多穿透越划算。
- **召喚物** —— 召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡明寫的屬性（通常是最大生命與技能強度）與原生光環。

細節見 `data/dossier/_engine.md`。


---

## 衝擊火箭 `A0XO`　—　吃技能強度

俄文原名：Ударная ракета

```
向指定區域發射一枚火箭，造成傷害並以 100% 機率暈眩敵人。具有點燃效果。

傷害：80 +（30% 技能強度）
點燃效果：50% 機率，100% 傷害
暈眩：3 秒（英雄 2 秒）
英雄 25 級：每 8 秒一次，攻擊會發射一枚火箭，造成 50% 傷害並暈眩 2 秒（英雄 1 秒）

冷卻：18 秒
```

每級變動：
  - 第 3 行：80 / 120 / 160 / 200 / 240

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 2`, `Ncl3 = 3`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `aare = 230.0`, `acap = `, `acdn = 18.0`, `alev = 5`, `amcs = [100, 120, 140, 160, 180]`, `aran = 800.0`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`FrostUnit`　war3map.j:1539
```jass
function FrostUnit takes unit damager,unit target,real chanse returns nothing
local real dmg
local real cof=1.0
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,t_Id,44)>0 then
set t=null
return
endif
if LoadInteger(hash,t_Id,28)>0 and LoadInteger(hash,GetHandleId(damager),'I07G')==0 then
set chanse=chanse*0.25
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
if GetUnitAbilityLevel(damager,'A0AQ')==1 and GetUnitAbilityLevel(target,'B046')==1 then
if IsUnitType(target,UNIT_TYPE_HERO)then
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.25
else
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.05
endif
if LoadInteger(hash,d_Id,'I00R')>=1 then
set dmg=dmg+150.
endif
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\CrushingWave\\CrushingWaveDamage.mdl",target,"chest"))
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,48)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
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
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.18
endif
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
set cof=cof-LoadReal(hash,t_Id,48)+LoadReal(hash,d_Id,28)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call EnableTrigger(gg_trg_HeroTakeDamage)
endif
if GetUnitAbilityLevel(target,'B02V')==1 then
set cof=1.00
if IsUnitType(target,UNIT_TYPE_HERO)then
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.25
else
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.05
endif
if LoadInteger(hash,d_Id,'I00R')>=1 then
set dmg=dmg+150.
endif
if GetPlayerTechCount(GetOwningPlayer(damager),'Rufb',true)==1 then
if GetUnitTypeId(damager)=='n041' or GetUnitTypeId(damager)=='n06L' or GetUnitTypeId(damager)=='n06S' or GetUnitTypeId(damager)=='n06U' or GetUnitTypeId(damager)=='n06V' then
set dmg=dmg+100.
endif
endif
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\CrushingWave\\CrushingWaveDamage.mdl",target,"chest"))
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,48)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
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
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.18
endif
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
set cof=cof-LoadReal(hash,t_Id,48)+LoadReal(hash,d_Id,28)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call EnableTrigger(gg_trg_HeroTakeDamage)
set t=LoadTimerHandle(hash,t_Id,'B02V')
call TimerStart(t,0.,false,function RemoveFrost)
else
call UnitAddAbility(target,'S00G')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,t_Id,'B02V',t)
call TimerStart(t,6.,false,function RemoveFrost)
endif
endif
set t=null
endfunction
```

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
function Burn_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local integer u_Id
local unit u2=LoadUnitHandle(hash,Id,0)
local integer u2_Id=GetHandleId(u2)
local integer count=LoadInteger(hash,u2_Id,'burn')
local integer i=0
local integer check=0
local integer L
local real dmg
local real dmg_cof=1.0
local real cof
if not UnitAlive(u2)then
call SaveInteger(hash,u2_Id,'burn',0)
call UnitRemoveAbility(u2,'A0Y6')
call UnitRemoveAbility(u2,'B040')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'burt')
set u=null
set u2=null
set t=null
return
endif
if LoadInteger(hash,u2_Id,'I07A')>=1 then
if UnitLifePercent(u2)<=25.0 then
set dmg_cof=dmg_cof-0.50
endif
endif
if LoadInteger(hash,u2_Id,'I048')>=1 then
if UnitLifePercent(u2)<=30.0 then
set dmg_cof=dmg_cof-0.25
endif
endif
if LoadInteger(hash,u2_Id,'tbak')>=1 then
if UnitLifePercent(u2)>=75.0 then
set dmg_cof=dmg_cof-0.25
endif
endif
if LoadInteger(hash,u2_Id,'pman')>=1 then
if UnitLifePercent(u2)>=75.0 then
set dmg_cof=dmg_cof-0.18
endif
endif
set dmg_cof=dmg_cof-LoadReal(hash,u2_Id,47)
call DisableTrigger(gg_trg_HeroTakeDamage)
loop
set i=i+1
set L=LoadInteger(hash,Id,i)
if L>0 then
set u=LoadUnitHandle(hash,Id,i)
set u_Id=GetHandleId(u)
set dmg=LoadReal(hash,Id,i)
set cof=dmg_cof
if LoadInteger(hash,u_Id,'gvsm')>=1 or LoadInteger(hash,u_Id,'I00S')>=1 then
if GetUnitAbilityLevel(u2,'B02V')==1 then
set cof=cof+0.35
endif
endif
if LoadInteger(hash,u_Id,'I086')>=1 then
if LoadInteger(hash,u_Id,27)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(u,'B01H')==1 then
set cof=cof+0.50
endif
set cof=cof+LoadReal(hash,u_Id,27)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(u,u2,dmg*cof,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
if LoadInteger(hash,u2_Id,'I068')>=1 then
call UnitDamageTarget(u2,u,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
set L=L-1
if L>0 then
set check=1
else
call RemoveSavedHandle(hash,Id,i)
endif
call SaveInteger(hash,Id,i,L)
endif
exitwhen i==count
endloop
call EnableTrigger(gg_trg_HeroTakeDamage)
if check==0 then
call SaveInteger(hash,u2_Id,'burn',0)
call UnitRemoveAbility(u2,'A0Y6')
call UnitRemoveAbility(u2,'B040')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'burt')
endif
set u=null
set u2=null
set t=null
endfunction
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
```

## 衝撞 `A0XQ`

俄文原名：Таран

```
朝指定地點加速衝刺，對路徑上的敵人造成傷害並將其推開。坦克會一路移動到技能指定的地點。

傷害：100 +（100% 力量）

冷卻：20 秒
```

每級變動：
  - 第 3 行：100 / 150 / 200 / 250 / 300

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = charm`, `acap = `, `acdn = 20.0`, `alev = 5`, `amcs = [90, 105, 120, 135, 150]`, `aran = 1200.0`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`HeroW55_Dmg`　war3map.j:64433
```jass
function HeroW55_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local unit u3
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2
local real y2
local real angle
local integer count=LoadInteger(hash,Id,1)
local group check_ug=LoadGroupHandle(hash,Id,2)
local group ug=CreateGroup()
local real dmg=LoadReal(hash,Id,1)
call DestroyEffect(AddSpecialEffect("Objects\\Spawnmodels\\Undead\\ImpaleTargetDust\\ImpaleTargetDust.mdl",x,y))
call GroupEnumUnitsInRange(ug,x,y,215.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)and not IsUnitInGroup(u3,check_ug)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
if UnitAlive(u3)and not IsUnitType(u3,UNIT_TYPE_STRUCTURE)then
set x2=GetUnitX(u3)
set y2=GetUnitY(u3)
set angle=AngleXY(x,y,x2,y2)
call KnockBackUnit(u3,400.,0.45,angle,0.03)
call GroupAddUnit(check_ug,u3)
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
set count=count-1
if count==0 then
call DestroyGroup(check_ug)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SaveInteger(hash,Id,1,count)
endif
set t=null
set u=null
set pl=null
set u3=null
set ug=null
endfunction
```

`Trig_HeroSkills55_Actions`　war3map.j:64518
```jass
elseif Skill=='A0XQ' then
set dmg=50.+50.*I2R(lvl)+I2R(GetHeroStr(u,true))
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set angle=AngleXY(x,y,x2,y2)
set dist=DistanceNative(x,y,x2,y2)
set x3=dist/1000.
call KnockBackUnit(u,dist,x3,angle,0.03)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,R2I(dist*0.01))
call SaveReal(hash,Id,1,dmg)
call SaveGroupHandle(hash,Id,2,CreateGroup())
call TimerStart(t,0.10,true,function HeroW55_Dmg)
```

## 燃燒砲塔 `A0XT`

俄文原名：Поджигающие турели

```
砲塔的投射物有機率點燃敵人。

點燃（砲塔投射物）：40% 機率；傷害等於英雄力量的 60%
```

每級變動：
  - 第 3 行：40% шанс; урон равен 60 / 45% шанс; урон равен 70 / 50% шанс; урон равен 80 / 55% шанс; урон равен 90 / 60% шанс; урон равен 100

物件欄位（原型 `Amgl`）：`aher = 1`, `alev = 5`

實作：

`RemoveFrost`　war3map.j:1527
```jass
function RemoveFrost takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call UnitRemoveAbility(u,'S00G')
call UnitRemoveAbility(u,'B02V')
call RemoveSavedHandle(hash,GetHandleId(u),'B02V')
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set t=null
set u=null
endfunction
function FrostUnit takes unit damager,unit target,real chanse returns nothing
local real dmg
local real cof=1.0
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,t_Id,44)>0 then
set t=null
return
endif
if LoadInteger(hash,t_Id,28)>0 and LoadInteger(hash,GetHandleId(damager),'I07G')==0 then
set chanse=chanse*0.25
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
if GetUnitAbilityLevel(damager,'A0AQ')==1 and GetUnitAbilityLevel(target,'B046')==1 then
if IsUnitType(target,UNIT_TYPE_HERO)then
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.25
else
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.05
endif
if LoadInteger(hash,d_Id,'I00R')>=1 then
set dmg=dmg+150.
endif
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\CrushingWave\\CrushingWaveDamage.mdl",target,"chest"))
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,48)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
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
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.18
endif
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
set cof=cof-LoadReal(hash,t_Id,48)+LoadReal(hash,d_Id,28)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call EnableTrigger(gg_trg_HeroTakeDamage)
endif
if GetUnitAbilityLevel(target,'B02V')==1 then
set cof=1.00
if IsUnitType(target,UNIT_TYPE_HERO)then
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.25
else
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.05
endif
if LoadInteger(hash,d_Id,'I00R')>=1 then
set dmg=dmg+150.
endif
if GetPlayerTechCount(GetOwningPlayer(damager),'Rufb',true)==1 then
if GetUnitTypeId(damager)=='n041' or GetUnitTypeId(damager)=='n06L' or GetUnitTypeId(damager)=='n06S' or GetUnitTypeId(damager)=='n06U' or GetUnitTypeId(damager)=='n06V' then
set dmg=dmg+100.
endif
endif
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\CrushingWave\\CrushingWaveDamage.mdl",target,"chest"))
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,48)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
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
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.18
endif
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
set cof=cof-LoadReal(hash,t_Id,48)+LoadReal(hash,d_Id,28)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call EnableTrigger(gg_trg_HeroTakeDamage)
set t=LoadTimerHandle(hash,t_Id,'B02V')
call TimerStart(t,0.,false,function RemoveFrost)
else
call UnitAddAbility(target,'S00G')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,t_Id,'B02V',t)
call TimerStart(t,6.,false,function RemoveFrost)
endif
endif
set t=null
endfunction
function RemoveFlammability takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call UnitRemoveAbility(u,'S00M')
call UnitRemoveAbility(u,'B042')
call RemoveSavedHandle(hash,GetHandleId(u),'B042')
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set t=null
set u=null
endfunction
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
function Burn_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local integer u_Id
local unit u2=LoadUnitHandle(hash,Id,0)
local integer u2_Id=GetHandleId(u2)
local integer count=LoadInteger(hash,u2_Id,'burn')
local integer i=0
local integer check=0
local integer L
local real dmg
local real dmg_cof=1.0
local real cof
if not UnitAlive(u2)then
call SaveInteger(hash,u2_Id,'burn',0)
call UnitRemoveAbility(u2,'A0Y6')
call UnitRemoveAbility(u2,'B040')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'burt')
set u=null
set u2=null
set t=null
return
endif
if LoadInteger(hash,u2_Id,'I07A')>=1 then
if UnitLifePercent(u2)<=25.0 then
set dmg_cof=dmg_cof-0.50
endif
endif
if LoadInteger(hash,u2_Id,'I048')>=1 then
if UnitLifePercent(u2)<=30.0 then
set dmg_cof=dmg_cof-0.25
endif
endif
if LoadInteger(hash,u2_Id,'tbak')>=1 then
if UnitLifePercent(u2)>=75.0 then
set dmg_cof=dmg_cof-0.25
endif
endif
if LoadInteger(hash,u2_Id,'pman')>=1 then
if UnitLifePercent(u2)>=75.0 then
set dmg_cof=dmg_cof-0.18
endif
endif
set dmg_cof=dmg_cof-LoadReal(hash,u2_Id,47)
call DisableTrigger(gg_trg_HeroTakeDamage)
loop
set i=i+1
set L=LoadInteger(hash,Id,i)
if L>0 then
set u=LoadUnitHandle(hash,Id,i)
set u_Id=GetHandleId(u)
set dmg=LoadReal(hash,Id,i)
set cof=dmg_cof
if LoadInteger(hash,u_Id,'gvsm')>=1 or LoadInteger(hash,u_Id,'I00S')>=1 then
if GetUnitAbilityLevel(u2,'B02V')==1 then
set cof=cof+0.35
endif
endif
if LoadInteger(hash,u_Id,'I086')>=1 then
if LoadInteger(hash,u_Id,27)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(u,'B01H')==1 then
set cof=cof+0.50
endif
set cof=cof+LoadReal(hash,u_Id,27)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(u,u2,dmg*cof,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
if LoadInteger(hash,u2_Id,'I068')>=1 then
call UnitDamageTarget(u2,u,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
set L=L-1
if L>0 then
set check=1
else
call RemoveSavedHandle(hash,Id,i)
endif
call SaveInteger(hash,Id,i,L)
endif
exitwhen i==count
endloop
call EnableTrigger(gg_trg_HeroTakeDamage)
if check==0 then
call SaveInteger(hash,u2_Id,'burn',0)
call UnitRemoveAbility(u2,'A0Y6')
call UnitRemoveAbility(u2,'B040')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'burt')
endif
set u=null
set u2=null
set t=null
endfunction
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
```

## 砲兵轟擊 `A0XS`　—　吃技能強度

俄文原名：Артиллерийский обстрел

```
向指定區域發射 3 波砲彈。每一枚砲彈都會造成範圍傷害並點燃敵人。

砲彈傷害：35 +（35% 技能強度）點
點燃：50% 機率；50% 傷害
施放距離：無限制

冷卻：90 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.20000000298023224, None, 1.0]`, `Ncl2 = [2, None, 1]`, `Ncl3 = [3, None, 1]`, `Ncl4 = [0.20000000298023224, None, 1.0]`, `Ncl5 = [0, None]`, `Ncl6 = ['darkportal', None, 'channel']`, `aare = 450.0`, `acap = `, `acdn = [90.0, None, 17.0]`, `alev = 1`, `amcs = [250, None, 80, 90, 100, 110, 120]`, `aran = [99999.0, None, 700.0]`, `atar = ['air,ground,friend,neutral,self', None]`

實作：

`HeroR55_Dmg`　war3map.j:64335
```jass
function HeroR55_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local unit u3
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real x2=LoadReal(hash,Id,1)
local real y2=LoadReal(hash,Id,2)
local real x3
local real y3
local integer count=LoadInteger(hash,Id,1)
local real dmg=35.+udg_ItemBonusDMG[n]*0.35
local real dist
local real angle
local integer i=0
loop
exitwhen i>11
set dist=GetRandomReal(0.,435.)
set angle=GetRandomReal(0.,360.)
set x3=PolarX(x2,dist,angle)
set y3=PolarY(y2,dist,angle)
set u3=CreateUnit(pl,'o02O',x,y,0.00)
call SaveReal(hash,GetHandleId(u3),13,dmg)
call SaveUnitHandle(hash,GetHandleId(u3),13,u)
call UnitApplyTimedLife(u3,'BTLF',DistanceNative(x,y,x3,y3)/1200.+2.)
call IssuePointOrderById(u3,Order_attackground,x3,y3)
set i=i+1
endloop
set count=count-1
if count==0 then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SaveInteger(hash,Id,1,count)
endif
set t=null
set u=null
set u3=null
set pl=null
endfunction
```

`Trig_HeroSkills55_Actions`　war3map.j:64533
```jass
elseif Skill=='A0XS' then
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,x2)
call SaveReal(hash,Id,2,y2)
call SaveInteger(hash,Id,1,3)
call TimerStart(t,0.1,true,function HeroR55_Dmg)
endif
```

## 側翼砲塔 `A0XR`

俄文原名：Боковые турели

```
坦克上裝設了側翼砲塔，會掃描英雄兩側的區域並向敵人開火。砲塔的射速與其掃描頻率相關聯。每座砲塔的掃描各自獨立進行。

掃描頻率：每 1-2 秒
砲塔砲彈傷害：（90% 力量）點

「魔法齒輪」道具加成：砲塔攻擊速度 +100%

每達成 100 次擊殺，點燃傷害會額外乘上 2%。層數之間不會互相相乘。
```

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
  - **27** — 實數＝點燃傷害 +%〔施加者〕／整數＝抵抗點燃旗標〔受害者〕**兩者不同表**
  - **28** — 實數＝冰凍傷害 +%〔施加者〕／整數＝抵抗冰凍旗標〔受害者〕
  - **44** — 狀態免疫旗標〔受害者〕>0 則所有狀態函式開頭直接 return，完全不判定
  - **46** — 易燃效果強化〔施加者〕影響易燃的機率倍率與跳數加成
  - **47** — 點燃抗性〔受害者〕係數減去它；電擊讓它 −1.00
  - **48** — 冰凍抗性〔受害者〕；電擊 −1.00

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
