# 莫爾格 `Ocbh`（Мо'арг）

主屬性 **力量** · 背包 **6 格** · 解鎖 4000000 · 定位 戰士/坦克/法師

| | 初始 | 每級 |
|---|---|---|
| 力量 | 34 | 5 |
| 敏捷 | 14 | 2 |
| 智力 | 26 | 3.5 |

> 強力的近戰英雄，能累積力量來釋放強大技能。

**縮放**：吃技能強度的技能 ['A01D', 'A0MR'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **狀態** —— 走 `Burn_Dmg` 那條，**外面包了 DisableTrigger** → 不吃 DefCof、不帶穿透、被狀態抗性擋。該買的是「狀態傷害 +%」「易燃」「機率倍率」。
- **直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且事件數越多穿透越划算。
- **召喚物** —— 召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡明寫的屬性（通常是最大生命與技能強度）與原生光環。
- **治療／增益** —— 直接寫數值，不經傷害事件 —— 全地圖沒有「治療加成」這種屬性，只能靠技能公式裡的係數（多半是技能強度）。

細節見 `data/dossier/_engine.md`。


---

## 殲滅噴發 `A0MR`　—　吃技能強度

俄文原名：Уничтожающий выброс

```
技能會逐漸吸收惡魔之力，並產生一顆火球，當英雄的惡魔之力耗盡時便會發射出去。吸收力量的速度為「力量蓄積」技能累積力量速度的 135%。火球可以點燃敵人。

傷害：175 +（600% 已吸收力量）點
點燃：50% 機率；50% 傷害
火球大小（作用範圍）：150 +（80% 已吸收力量）點
飛行距離：600 +（175% 已吸收力量）點

冷卻：100 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = [10.0, None, 1.0]`, `Ncl2 = [2, None, 1]`, `Ncl3 = [1, None]`, `Ncl4 = [1.899999976158142, None, 1.0]`, `Ncl5 = [None, 0]`, `Ncl6 = ['darkportal', None, 'channel']`, `acap = `, `acdn = [100.0, None, 17.0]`, `alev = 1`, `amcs = [225, None, 80, 90, 100, 110, 120]`, `aran = [600.0, None, 700.0]`, `atar = ['air,ground,friend,neutral,self', None]`

呼叫共用引擎函式：`BurnUnit` —— 完整內容見 `_engine.md`。

實作：

`Hero52SkillsStart2_conditions`　war3map.j:63969
```jass
function Hero52SkillsStart2_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0MR'
endfunction
```

`Trig_Hero52SkillsStart2_Actions`　war3map.j:64022
```jass
function Trig_Hero52SkillsStart2_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local player pl=GetOwningPlayer(u)
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2=GetSpellTargetX()
local real y2=GetSpellTargetY()
local real angle=AngleXY(x,y,x2,y2)
set x2=PolarX(x,150,angle)
set y2=PolarY(y,150,angle)
call SaveUnitHandle(hash,Id,1,u)
call SaveTextTagHandle(hash,GetHandleId(u),26,CreateTextTag())
call SaveTimerHandle(hash,GetHandleId(u),'A0MR',t)
call SaveUnitHandle(hash,Id,2,CreateUnit(pl,'o024',x2,y2,angle))
call SaveReal(hash,Id,2,0)
call TimerStart(t,0.15,false,function Hero52R)
set u=null
set pl=null
set t=null
endfunction
```

`Hero52SkillsStop2_conditions`　war3map.j:64049
```jass
function Hero52SkillsStop2_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0MR'
endfunction
```

`Trig_Hero52SkillsStop2_Actions`　war3map.j:64112
```jass
function Trig_Hero52SkillsStop2_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local unit u2
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local integer Id
local timer t
local texttag text
local force f=CreateForce()
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real power
local real limit
local integer check_1
local integer check_3
set t=LoadTimerHandle(hash,GetHandleId(u),'A0MR')
set Id=GetHandleId(t)
call ForceAddPlayer(f,pl)
set text=LoadTextTagHandle(hash,GetHandleId(u),26)
call DestroyTextTag(text)
set power=LoadReal(hash,GetHandleId(u),26)
set limit=40+10*I2R(GetHeroLevel(u))+udg_ItemBonusDMG[n]*0.10
set text=CreateTextTagUnitBJ("|cFFFF7D00"+I2S(R2I(power))+"/"+I2S(R2I(limit)),u,0,13.00,100,100,100,0)
call ShowTextTagForceBJ(false,text,bj_FORCE_ALL_PLAYERS)
call ShowTextTagForceBJ(true,text,f)
call SetTextTagVelocityBJ(text,75.00,90.00)
call SetTextTagSuspended(text,false)
call SetTextTagPermanent(text,false)
call SetTextTagLifespan(text,4.00)
call SetTextTagFadepoint(text,3.00)
set u2=LoadUnitHandle(hash,Id,2)
set power=LoadReal(hash,Id,2)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveGroupHandle(hash,Id,3,CreateGroup())
call SaveReal(hash,Id,1,power)
call SaveInteger(hash,Id,1,15+R2I(power*1.75/40.0))
call SaveInteger(hash,Id,2,2)
call TimerStart(t,0.04,true,function Hero52R_Move)
call DestroyForce(f)
set f=null
set u=null
set pl=null
set t=null
set text=null
endfunction
```

`Hero52SkillsStart2_conditions`　war3map.j:63969
```jass
function Hero52SkillsStart2_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0MR'
endfunction
function Hero52R takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2=LoadUnitHandle(hash,Id,2)
local real used_power=LoadReal(hash,Id,2)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real dmg
local texttag text=LoadTextTagHandle(hash,GetHandleId(u),26)
local force f=CreateForce()
local unit u3
local group ug
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real power=LoadReal(hash,GetHandleId(u),26)
local real limit=40+10*I2R(GetHeroLevel(u))+udg_ItemBonusDMG[n]*0.10
if power>limit then
set power=limit
endif
if power<(3.0+I2R(GetHeroInt(u,true))*0.20+GetUnitManaRegeneration(u)*0.30)*0.20 then
set used_power=used_power+power
set power=0
else
set used_power=used_power+(3.0+I2R(GetHeroInt(u,true))*0.20+GetUnitManaRegeneration(u)*0.30)*0.20
set power=power-(3.0+I2R(GetHeroInt(u,true))*0.20+GetUnitManaRegeneration(u)*0.30)*0.20
endif
call SaveReal(hash,GetHandleId(u),26,power)
call ForceAddPlayer(f,pl)
call DestroyTextTag(text)
set text=CreateTextTagUnitBJ("|cFFFF7D00"+I2S(R2I(power))+"/"+I2S(R2I(limit)),u,0,13.00,100,100,100,0)
call ShowTextTagForceBJ(false,text,bj_FORCE_ALL_PLAYERS)
call ShowTextTagForceBJ(true,text,f)
call SaveTextTagHandle(hash,GetHandleId(u),26,text)
set dmg=2.0+used_power*0.016
call SetUnitScale(u2,dmg,dmg,dmg)
call SaveReal(hash,Id,2,used_power)
if power==0 then
call IssueImmediateOrderById(u,Order_stop)
endif
call DestroyForce(f)
call TimerStart(t,0.15,false,function Hero52R)
set f=null
set t=null
set u=null
set pl=null
set u3=null
set ug=null
set text=null
endfunction
function Trig_Hero52SkillsStart2_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local player pl=GetOwningPlayer(u)
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2=GetSpellTargetX()
local real y2=GetSpellTargetY()
local real angle=AngleXY(x,y,x2,y2)
set x2=PolarX(x,150,angle)
set y2=PolarY(y,150,angle)
call SaveUnitHandle(hash,Id,1,u)
call SaveTextTagHandle(hash,GetHandleId(u),26,CreateTextTag())
call SaveTimerHandle(hash,GetHandleId(u),'A0MR',t)
call SaveUnitHandle(hash,Id,2,CreateUnit(pl,'o024',x2,y2,angle))
call SaveReal(hash,Id,2,0)
call TimerStart(t,0.15,false,function Hero52R)
set u=null
set pl=null
set t=null
endfunction
```

`Hero52SkillsStop2_conditions`　war3map.j:64049
```jass
function Hero52SkillsStop2_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0MR'
endfunction
function Hero52R_Move takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local unit u2=LoadUnitHandle(hash,Id,2)
local unit u3
local group CheckGroup
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local integer count=LoadInteger(hash,Id,1)
local integer check=LoadInteger(hash,Id,2)
local real power=LoadReal(hash,Id,1)
local group ug
local real dmg
local real r=GetUnitFacing(u2)
set x=PolarX(x,40,r)
set y=PolarY(y,40,r)
call SetUnitX(u2,x)
call SetUnitY(u2,y)
set check=check+1
if check==3 then
set check=0
set CheckGroup=LoadGroupHandle(hash,Id,3)
set dmg=175+power*6.00
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,150+power*0.80,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if IsUnitEnemy(u3,pl)and UnitAlive(u3)and IsUnitInGroup(u3,CheckGroup)==false then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
call BurnUnit(u,u3,dmg*0.50,0.50)
call GroupAddUnit(CheckGroup,u3)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
call SaveInteger(hash,Id,2,check)
call SaveGroupHandle(hash,Id,3,CheckGroup)
set count=count-1
if count==0 then
call KillUnit(u2)
call DestroyGroup(LoadGroupHandle(hash,Id,3))
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SaveInteger(hash,Id,1,count)
endif
set t=null
set u=null
set u2=null
set pl=null
set u3=null
set ug=null
set CheckGroup=null
endfunction
function Trig_Hero52SkillsStop2_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local unit u2
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local integer Id
local timer t
local texttag text
local force f=CreateForce()
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real power
local real limit
local integer check_1
local integer check_3
set t=LoadTimerHandle(hash,GetHandleId(u),'A0MR')
set Id=GetHandleId(t)
call ForceAddPlayer(f,pl)
set text=LoadTextTagHandle(hash,GetHandleId(u),26)
call DestroyTextTag(text)
set power=LoadReal(hash,GetHandleId(u),26)
set limit=40+10*I2R(GetHeroLevel(u))+udg_ItemBonusDMG[n]*0.10
set text=CreateTextTagUnitBJ("|cFFFF7D00"+I2S(R2I(power))+"/"+I2S(R2I(limit)),u,0,13.00,100,100,100,0)
call ShowTextTagForceBJ(false,text,bj_FORCE_ALL_PLAYERS)
call ShowTextTagForceBJ(true,text,f)
call SetTextTagVelocityBJ(text,75.00,90.00)
call SetTextTagSuspended(text,false)
call SetTextTagPermanent(text,false)
call SetTextTagLifespan(text,4.00)
call SetTextTagFadepoint(text,3.00)
set u2=LoadUnitHandle(hash,Id,2)
set power=LoadReal(hash,Id,2)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveGroupHandle(hash,Id,3,CreateGroup())
call SaveReal(hash,Id,1,power)
call SaveInteger(hash,Id,1,15+R2I(power*1.75/40.0))
call SaveInteger(hash,Id,2,2)
call TimerStart(t,0.04,true,function Hero52R_Move)
call DestroyForce(f)
set f=null
set u=null
set pl=null
set t=null
set text=null
endfunction
```

## 點燃 `A0K7`

俄文原名：Поджог

```
半徑 400 點內的敵人會被減速並獲得點燃效果。

點燃機率：125%
點燃傷害：80 +（110% 惡魔之力）點／秒
攻擊速度減速：20%
移動速度減速：30%
減速持續時間（部隊）：6 秒
減速持續時間（英雄）：3 秒

冷卻：15 秒

額外加成資訊請見指令「-w」。
```

每級變動：
  - 第 4 行：80 / 120 / 160 / 200 / 240
  - 第 5 行：20 / 25 / 30 / 35 / 40
  - 第 6 行：30 / 38 / 46 / 54 / 62

物件欄位（原型 `AHtc`）：`Htc1 = 0.009999999776482582`, `Htc3 = [0.30000001192092896, 0.3799999952316284, 0.4599999785423279, 0.5399999618530273, 0.6199999451637268]`, `Htc4 = [0.20000000298023224, 0.25, 0.30000001192092896, 0.3500000238418579, 0.40000003576278687]`, `aare = 400.0`, `abuf = B03O`, `acdn = 15.0`, `adur = 6.0`, `alev = 5`, `amcs = [80, None, 100, 110, 120]`, `atar = ground,neutral,organic`

呼叫共用引擎函式：`BurnUnit` —— 完整內容見 `_engine.md`。

實作：

`Trig_UKills_Actions`　war3map.j:21143
```jass
if GetUnitAbilityLevel(u,'A0K7')>=1 then
call SetUnitLifePercentBJ(u,UnitLifePercent(u)+1.00)
endif
```

`Trig_HeroSkills52_Actions`　war3map.j:63665
```jass
elseif Skill=='A0K7' then
call SaveReal(hash,GetHandleId(u),26,0)
set dmg=40.+40.*I2R(GetUnitAbilityLevel(u,Skill))+power*1.10
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,400,null)
if power>=225 then
call SaveReal(hash,GetHandleId(u),30,LoadReal(hash,GetHandleId(u),30)+3.)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call BurnUnit(u,u3,dmg,1.25)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call SaveReal(hash,GetHandleId(u),30,LoadReal(hash,GetHandleId(u),30)-3.)
else
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call BurnUnit(u,u3,dmg,1.25)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
if power>=50 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SetUnitLifeRegeneration(u,GetUnitLifeRegeneration(u)+power*0.30)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,power*0.30)
call TimerStart(t,10,false,function Hero52W_Buff)
endif
if power>=100 then
call DestroyEffect(AddSpecialEffect("war3mapImported\\NewDirtEXNofire.mdx",x,y))
set dmg=I2R(GetHeroStr(u,true))*3.50
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,250,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
if power>=150 then
set L=0
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,400,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
set L=L+2
if power>=300 then
call SetUnitExtraArmor(u3,GetUnitExtraArmor(u3)-5)
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
set t=CreateTimer()
set Id=GetHandleId(t)
call SetUnitExtraArmor(u,GetUnitExtraArmor(u)+L)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,L)
call TimerStart(t,10,false,function Hero52W_Buff2)
endif
if power>=300 then
call SetUnitState(u,UNIT_STATE_LIFE,GetUnitState(u,UNIT_STATE_LIFE)+(GetUnitState((u),UNIT_STATE_MAX_LIFE))*0.10)
endif
```

`Hero52W_Buff`　war3map.j:63475
```jass
function Hero52W_Buff takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
local real bonus=LoadReal(hash,GetHandleId(t),1)
call SetUnitLifeRegeneration(u,GetUnitLifeRegeneration(u)-bonus)
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set u=null
set t=null
endfunction
function Hero52W_Buff2 takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
local integer bonus=LoadInteger(hash,GetHandleId(t),1)
call SetUnitExtraArmor(u,GetUnitExtraArmor(u)-bonus)
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set u=null
set t=null
endfunction
```

## 灼燒法球 `A06N`

俄文原名：Выжигающая сфера

```
在指定地點創造一顆火焰法球。法球會週期性地對附近隨機一名敵人造成傷害。此外法球還會額外灼燒身邊的敵人，造成 50% 傷害。

傷害：30 +（30% 惡魔之力）點
傷害觸發間隔：0.4 秒
持續時間：11 秒

冷卻：30 秒

額外加成資訊請見指令「-е」。
```

每級變動：
  - 第 3 行：30 / 45 / 60 / 75 / 90

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = charm`, `acdn = 30.0`, `alev = 5`, `amcs = [110, 130, 150, 170, 190]`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills52_Actions`　war3map.j:63742
```jass
elseif Skill=='A06N' then
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set dmg=15+15*I2R(GetUnitAbilityLevel(u,Skill))+power*0.30
if power>=100 then
set dmg=dmg+I2R(GetHeroInt(u,true))*0.25
endif
set dummy=CreateUnit(pl,'o02R',x2,y2,270)
call SetUnitAnimation(dummy,"birth")
if power>=225 then
call UnitApplyTimedLife(dummy,'BTLF',17.00)
call UnitAddAbility(dummy,'A0C7')
elseif power>=50 then
call UnitApplyTimedLife(dummy,'BTLF',14.00)
else
call UnitApplyTimedLife(dummy,'BTLF',11.00)
endif
if power>=150 then
call SaveReal(hash,GetHandleId(u),26,power*0.50)
call SetUnitAbilityLevel(dummy,'A086',2)
elseif power>=100 then
call SaveReal(hash,GetHandleId(u),26,power*0.25)
call SetUnitAbilityLevel(dummy,'A0MS',2)
else
call SaveReal(hash,GetHandleId(u),26,0)
endif
call SaveReal(hash,GetHandleId(dummy),13,dmg*0.5)
call SaveUnitHandle(hash,GetHandleId(dummy),13,u)
if power>=300 then
call SetUnitAbilityLevel(dummy,'A086',3)
call SaveInteger(hash,GetHandleId(u),26,1)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call TimerStart(t,5,false,function Hero52E_Buff)
endif
endif
```

`Hero52E_Buff`　war3map.j:63497
```jass
function Hero52E_Buff takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call SaveInteger(hash,GetHandleId(u),26,0)
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set u=null
set t=null
endfunction
```

## 粉碎打擊 `A04L`

俄文原名：Сокрушительный удар

```
對指定目標發動強力一擊，造成範圍傷害並暈眩被擊中的目標。

對目標的傷害：120 +（115% 惡魔之力）點
對目標周圍敵人的傷害：主傷害公式的 50%
目標暈眩（部隊）：4 秒
目標暈眩（英雄）：2 秒

冷卻：18 秒

額外加成資訊請見指令「-q」。
```

每級變動：
  - 第 3 行：120 / 180 / 240 / 300 / 360
  - 第 5 行：4 / 5 / 6 / 7 / 8
  - 第 6 行：2 / 2.5 / 3 / 3.5 / 4

物件欄位（原型 `ANcl`）：`Ncl1 = 0.9399999976158142`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = 0.9399999976158142`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acdn = 18.0`, `alev = 5`, `amcs = [90, 102, 114, 126, 138]`, `aran = 130.0`, `atar = air,enemies,ground,neutral,organic,item,debris`

呼叫共用引擎函式：`FlammabilityUnit` —— 完整內容見 `_engine.md`。

實作：

`Trig_HeroSkills52_Actions`　war3map.j:63570
```jass
if Skill=='A04L' then
set x=GetUnitX(u2)
set y=GetUnitY(u2)
call SaveReal(hash,GetHandleId(u),26,0)
set dmg=60+60*I2R(GetUnitAbilityLevel(u,Skill))+power*1.10
set aoe_cof=0.50
set chance=0.
set aoe=250
if power>=50 then
set chance=0.50
set aoe=aoe+62.5
endif
if power>=100 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SetUnitAttackSpeed(u,GetUnitAttackSpeed(u)+80)
call SaveUnitHandle(hash,Id,1,u)
call TimerStart(t,8,false,function Hero52Q_Buff)
endif
if power>=225 then
set chance=1.0
set aoe=aoe+62.5
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
call FlammabilityUnit(u,u2,chance)
else
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call FlammabilityUnit(u,u2,chance)
endif
if power>=150 then
set dummy=CreateUnit(pl,'o010',x,y,0.00)
call UnitAddAbility(dummy,'A04Q')
call SetUnitAbilityLevel(dummy,'A04Q',GetUnitAbilityLevel(u,Skill)+5)
call IssueTargetOrderById(dummy,Order_thunderbolt,u2)
call UnitApplyTimedLife(dummy,'BTLF',2.00)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)and u3 !=u2 then
set dummy=CreateUnit(pl,'o010',x,y,0.00)
call UnitAddAbility(dummy,'A04Q')
call SetUnitAbilityLevel(dummy,'A04Q',GetUnitAbilityLevel(u,Skill))
call IssueTargetOrderById(dummy,Order_thunderbolt,u3)
call UnitApplyTimedLife(dummy,'BTLF',2.00)
call UnitDamageTarget(u,u3,dmg*aoe_cof,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call FlammabilityUnit(u,u3,chance)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
else
set dummy=CreateUnit(pl,'o010',x,y,0.00)
call UnitAddAbility(dummy,'A04Q')
call SetUnitAbilityLevel(dummy,'A04Q',GetUnitAbilityLevel(u,Skill))
call IssueTargetOrderById(dummy,Order_thunderbolt,u2)
call UnitApplyTimedLife(dummy,'BTLF',2.00)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)and u3 !=u2 then
call UnitDamageTarget(u,u3,dmg*aoe_cof,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call FlammabilityUnit(u,u3,chance)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
set L=1
set L2=R2I(aoe)/20
loop
exitwhen L>L2
set x2=PolarX(x,aoe-10,I2R(L*(360/L2)))
set y2=PolarY(y,aoe-10,I2R(L*(360/L2)))
call DestroyEffect(AddSpecialEffect("war3mapImported\\AerialExplosionV3.mdx",x2,y2))
set L=L+1
endloop
if power>=300 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveReal(hash,Id,3,dmg)
call TimerStart(t,2,false,function Hero52Q_Dmg)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveReal(hash,Id,3,dmg)
call TimerStart(t,4,false,function Hero52Q_Dmg)
endif
```

`Hero52Q_Buff`　war3map.j:63465
```jass
function Hero52Q_Buff takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call SetUnitAttackSpeed(u,GetUnitAttackSpeed(u)-80)
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set u=null
set t=null
endfunction
```

`Hero52Q_Dmg`　war3map.j:63507
```jass
function Hero52Q_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
local player pl=GetOwningPlayer(u)
local real x=LoadReal(hash,GetHandleId(t),1)
local real y=LoadReal(hash,GetHandleId(t),2)
local real dmg=LoadReal(hash,GetHandleId(t),3)
local unit u3
local real x2
local real y2
local integer L
local integer L2
local group ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,375,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg*0.50,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
set L=1
set L2=R2I(300)/20
loop
exitwhen L>L2
set x2=PolarX(x,290,I2R(L*(360/L2)))
set y2=PolarY(y,290,I2R(L*(360/L2)))
call DestroyEffect(AddSpecialEffect("war3mapImported\\AerialExplosionV3.mdx",x2,y2))
set L=L+1
endloop
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set u=null
set u3=null
set ug=null
set pl=null
set t=null
endfunction
```

## 力量蓄積 `A01D`　—　吃技能強度

俄文原名：Накопление силы

```
莫爾格開始蓄積「惡魔之力」，這股力量會在使用英雄其他技能時消耗。技能持續期間，英雄會回復自身生命值。

惡魔之力蓄積速度：3 +（20% 智力）+（30% MP regen）點／秒
惡魔之力上限：40 +（10*英雄等級）+（10% 技能強度）點
生命值回復：每秒 1%
技能最長維持時間：30 秒

冷卻：10 秒

額外加成資訊請見指令「-d」。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [30.0, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [2.0, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['absorb', 'channel']`, `acap = `, `acdn = [10.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [35, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Hero52SkillsStart_conditions`　war3map.j:63791
```jass
function Hero52SkillsStart_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A01D'
endfunction
```

`Trig_Hero52SkillsStart_Actions`　war3map.j:63892
```jass
function Trig_Hero52SkillsStart_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local player pl=GetOwningPlayer(u)
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,300)
call SaveInteger(hash,Id,2,0)
call SaveInteger(hash,Id,4,0)
call SaveTextTagHandle(hash,GetHandleId(u),26,CreateTextTag())
call SaveTimerHandle(hash,GetHandleId(u),'A01D',t)
call TimerStart(t,0.20,true,function Hero52D)
set u=null
set pl=null
set t=null
endfunction
```

`Hero52SkillsStop_conditions`　war3map.j:63913
```jass
function Hero52SkillsStop_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A01D'
endfunction
function Trig_Hero52SkillsStop_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local integer Id
local timer t
local texttag text
local force f=CreateForce()
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real power
local real limit
local integer check_1
local integer check_3
set t=LoadTimerHandle(hash,GetHandleId(u),'A01D')
set Id=GetHandleId(t)
set check_1=LoadInteger(hash,Id,2)
set check_3=LoadInteger(hash,Id,4)
if check_1==1 then
call SaveReal(hash,GetHandleId(u),4,LoadReal(hash,GetHandleId(u),4)-0.12)
endif
if check_3==1 then
call UnitRemoveAbility(u,'A02P')
call UnitRemoveAbility(u,'A036')
endif
call ForceAddPlayer(f,pl)
set text=LoadTextTagHandle(hash,GetHandleId(u),26)
call DestroyTextTag(text)
set power=LoadReal(hash,GetHandleId(u),26)
set limit=40+10*I2R(GetHeroLevel(u))+udg_ItemBonusDMG[n]*0.10
set text=CreateTextTagUnitBJ("|cFFFF7D00"+I2S(R2I(power))+"/"+I2S(R2I(limit)),u,0,13.00,100,100,100,0)
call ShowTextTagForceBJ(false,text,bj_FORCE_ALL_PLAYERS)
call ShowTextTagForceBJ(true,text,f)
call SetTextTagVelocityBJ(text,75.00,90.00)
call SetTextTagSuspended(text,false)
call SetTextTagPermanent(text,false)
call SetTextTagLifespan(text,4.00)
call SetTextTagFadepoint(text,3.00)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call DestroyForce(f)
set f=null
set u=null
set pl=null
set t=null
set text=null
endfunction
```

`Hero52SkillsStart_conditions`　war3map.j:63791
```jass
function Hero52SkillsStart_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A01D'
endfunction
function Hero52D takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local integer count=LoadInteger(hash,Id,1)
local real dmg
local texttag text=LoadTextTagHandle(hash,GetHandleId(u),26)
local force f=CreateForce()
local unit u3
local group ug
local group ug2
local integer check_1=LoadInteger(hash,Id,2)
local integer check_3=LoadInteger(hash,Id,4)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real power=LoadReal(hash,GetHandleId(u),26)
local real limit=40+10*I2R(GetHeroLevel(u))+udg_ItemBonusDMG[n]*0.10
if LoadInteger(hash,GetHandleId(u),26)==1 then
set power=power+(3.0+I2R(GetHeroInt(u,true))*0.20+GetUnitManaRegeneration(u)*0.30)*0.40
call SetUnitState(u,UNIT_STATE_LIFE,GetUnitState(u,UNIT_STATE_LIFE)+(GetUnitState((u),UNIT_STATE_MAX_LIFE))*0.004)
if UnitHasItemOfType(u,'shas')and UnitLifePercent(u)>=75.00 then
set power=power+3.0
endif
if GetUnitAbilityLevel(u,'B02O')==1 then
set power=power+0.9
endif
else
set power=power+(3.0+I2R(GetHeroInt(u,true))*0.20+GetUnitManaRegeneration(u)*0.30)*0.20
call SetUnitState(u,UNIT_STATE_LIFE,GetUnitState(u,UNIT_STATE_LIFE)+(GetUnitState((u),UNIT_STATE_MAX_LIFE))*0.002)
if UnitHasItemOfType(u,'shas')and UnitLifePercent(u)>=75.00 then
set power=power+1.5
endif
if GetUnitAbilityLevel(u,'B02O')==1 then
set power=power+0.3
endif
endif
if power>limit then
set power=limit
endif
if power>=75 and check_1 !=1 then
call SaveInteger(hash,Id,2,1)
call SaveReal(hash,GetHandleId(u),4,LoadReal(hash,GetHandleId(u),4)+0.12)
endif
if power>=125 then
set dmg=power*0.50
set ug=CreateGroup()
set ug2=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,500,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call GroupAddUnit(ug2,u3)
endif
call GroupRemoveUnit(ug,u3)
endloop
set ug2=GetRandomSubGroup(1,ug2)
loop
set u3=FirstOfGroup(ug2)
exitwhen u3==null
call UnitDamageTarget(u,u3,dmg,true,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\Incinerate\\FireLordDeathExplode.mdl",u3,"origin"))
call GroupRemoveUnit(ug2,u3)
endloop
call DestroyGroup(ug)
call DestroyGroup(ug2)
endif
if power>=200 and check_3 !=1 then
call SaveInteger(hash,Id,4,1)
call UnitAddAbility(u,'A02P')
call UnitAddAbility(u,'A036')
endif
call SaveReal(hash,GetHandleId(u),26,power)
call ForceAddPlayer(f,pl)
call DestroyTextTag(text)
set text=CreateTextTagUnitBJ("|cFFFF7D00"+I2S(R2I(power))+"/"+I2S(R2I(limit)),u,0,13.00,100,100,100,0)
call ShowTextTagForceBJ(false,text,bj_FORCE_ALL_PLAYERS)
call ShowTextTagForceBJ(true,text,f)
call SaveTextTagHandle(hash,GetHandleId(u),26,text)
set count=count-1
if count==0 then
call SaveInteger(hash,Id,1,count)
else
call SaveInteger(hash,Id,1,count)
endif
call SaveInteger(hash,Id,1,count)
call DestroyForce(f)
set f=null
set t=null
set u=null
set pl=null
set u3=null
set ug=null
set ug2=null
set text=null
endfunction
function Trig_Hero52SkillsStart_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local player pl=GetOwningPlayer(u)
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,300)
call SaveInteger(hash,Id,2,0)
call SaveInteger(hash,Id,4,0)
call SaveTextTagHandle(hash,GetHandleId(u),26,CreateTextTag())
call SaveTimerHandle(hash,GetHandleId(u),'A01D',t)
call TimerStart(t,0.20,true,function Hero52D)
set u=null
set pl=null
set t=null
endfunction
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

---

## 這隻召喚／製造的單位

（技能程式碼裡的 `CreateUnit` 目標。數值取自 war3map.w3u，
沒列出的欄位代表地圖沒覆寫、沿用原型。）

### `o02R` FireOrb（原型 `ocat`）
  - 生命 1 ／ 骰面 1 ／ 攻擊範圍 1200 ／ 技能 A0MS,A086,Aloc
  - 技能 `A0MS` (выжигающая сфера, жар)　`Eim1 = 0.009999999776482582`, `aare = [180.0, 240.0]`, `abuf = [None, 'Bpig']`, `adur = [None, 1.0]`, `ahdu = [None, 1.0]`, `alev = 2`, `atar = [None, 'ground,enemy,neutral,organic']`
  - 技能 `A086` (выжигающая сфера, атака)　`aare = 400.0`, `acdn = [0.4000000059604645, 0.30000001192092896, 0.20000000298023224]`, `adur = 0.009999999776482582`, `ahdu = 0.009999999776482582`, `aite = 1`, `alev = 3`, `amat = Abilities\Weapons\PhoenixMissile\Phoenix_Missile_mini.mdl`, `amsp = 800`, `atar = ground,air,enemy`, `pxf1 = 0.009999999776482582`, `pxf2 = 0.0`

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
