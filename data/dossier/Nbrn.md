# 女武神 `Nbrn`（Валькирия）

主屬性 **敏捷** · 背包 **6 格** · 解鎖 0 · 定位 刺客 · **不在隨機池**（只能手動挑）

| | 初始 | 每級 |
|---|---|---|
| 力量 | 12 | 1.3 |
| 敏捷 | 24 | 4 |
| 智力 | 20 | （未覆寫） |

> 遠程英雄，能對單體與集群穩定輸出魔法傷害，並可持續累積敏捷。

**縮放**：吃技能強度的技能 無 ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **狀態** —— 走 `Burn_Dmg` 那條，**外面包了 DisableTrigger** → 不吃 DefCof、不帶穿透、被狀態抗性擋。該買的是「狀態傷害 +%」「易燃」「機率倍率」。
- **直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且事件數越多穿透越划算。
- **召喚物** —— 召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡明寫的屬性（通常是最大生命與技能強度）與原生光環。
- **治療／增益** —— 直接寫數值，不經傷害事件 —— 全地圖沒有「治療加成」這種屬性，只能靠技能公式裡的係數（多半是技能強度）。

細節見 `data/dossier/_engine.md`。


---

## 貫穿之光 `A07H`

俄文原名：Пронзающий свет

```
重置「星光閃耀」的冷卻，並強化下一次「閃耀」，移除其範圍傷害，但大幅提升單體傷害。

「星光閃耀」的懲罰：不造成範圍傷害
單體傷害提升：+60%
附加條件：處於「易傷」效果下的目標會受到「星光閃耀」的純粹傷害

冷卻：3 秒
```

每級變動：
  - 第 4 行：60 / 90 / 120 / 150 / 180

物件欄位（原型 `ANcl`）：`Ncl1 = 0.20000000298023224`, `Ncl3 = 1`, `Ncl4 = 0.20000000298023224`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acap = `, `acdn = 3.0`, `alev = 5`, `amcs = [20, 25, 30, 35, 40]`

實作：

`Trig_HeroSkills56_Actions`　war3map.j:64681
```jass
if Skill=='A07H' then
set t=LoadTimerHandle(hash,GetHandleId(u),'A0AB')
call PauseTimer(t)
call DestroyTimer(t)
call SaveInteger(hash,GetHandleId(u),'PASS',1)
call SaveInteger(hash,GetHandleId(u),'A0AB',0)
```

## 散射之光 `A0BD`

俄文原名：Рассеянный свет

```
重置「星光閃耀」的冷卻，並強化下一次「閃耀」，降低對主要目標的傷害並提升範圍傷害。

「星光閃耀」的懲罰：主要目標受到與範圍傷害相同的傷害
範圍傷害提升：+30%
作用範圍提升：+15%
額外範圍效果：20% 機率對敵人施加「易傷」狀態

冷卻：3 秒
```

每級變動：
  - 第 4 行：30 / 45 / 60 / 75 / 90
  - 第 5 行：15 / 20 / 25 / 30 / 35
  - 第 6 行：20 / 40 / 60 / 80 / 100

物件欄位（原型 `ANcl`）：`Ncl1 = 0.20000000298023224`, `Ncl3 = 1`, `Ncl4 = 0.20000000298023224`, `Ncl5 = 0`, `Ncl6 = charm`, `acap = `, `acdn = 3.0`, `alev = 5`, `amcs = [20, 25, 30, 35, 40]`

實作：

`Trig_HeroSkills56_Actions`　war3map.j:64687
```jass
elseif Skill=='A0BD' then
set t=LoadTimerHandle(hash,GetHandleId(u),'A0AB')
call PauseTimer(t)
call DestroyTimer(t)
call SaveInteger(hash,GetHandleId(u),'PASS',2)
call SaveInteger(hash,GetHandleId(u),'A0AB',0)
endif
```

## 星光閃耀 `A0AB`

俄文原名：Звёздный блик

```
女武神的攻擊會對目標與目標周圍的敵人造成額外物理傷害。若此技能擊殺目標，英雄有 50% 機率使自身敏捷提升 1 點。

傷害：對目標（120% 敏捷）點；附近的敵人受到 50% 的傷害

冷卻：5 秒
```

每級變動：
  - 第 3 行：120 / 160 / 200 / 240 / 280

物件欄位（原型 `Amgl`）：`aher = 1`, `alev = 5`

呼叫共用引擎函式：`VulnerabilityUnit` —— 完整內容見 `_engine.md`。

實作：

`Trig_HeroSkills56_Actions`　war3map.j:64681
```jass
if Skill=='A07H' then
set t=LoadTimerHandle(hash,GetHandleId(u),'A0AB')
call PauseTimer(t)
call DestroyTimer(t)
call SaveInteger(hash,GetHandleId(u),'PASS',1)
call SaveInteger(hash,GetHandleId(u),'A0AB',0)
elseif Skill=='A0BD' then
set t=LoadTimerHandle(hash,GetHandleId(u),'A0AB')
call PauseTimer(t)
call DestroyTimer(t)
call SaveInteger(hash,GetHandleId(u),'PASS',2)
call SaveInteger(hash,GetHandleId(u),'A0AB',0)
endif
```

`Trig_HeroAttack56_Actions`　war3map.j:64761
```jass
if GetUnitAbilityLevel(u,'A0AB')>=1 and LoadInteger(hash,u_Id,'A0AB')==0 and IsUnitEnemy(u2,pl)then
call SaveInteger(hash,u_Id,'A0AB',1)
call SaveInteger(hash,u_Id,'PASS',0)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveInteger(hash,Id,1,GetHandleId(u))
call SaveInteger(hash,Id,2,'A0AB')
call TimerStart(t,5.,false,function EndCooldown)
call SaveTimerHandle(hash,GetHandleId(u),'A0AB',t)
set dmg=I2R(GetHeroAgi(u,true))*(0.80+0.40*I2R(GetUnitAbilityLevel(u,'A0AB')))
if check==0 then
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_HERO,DAMAGE_TYPE_NORMAL,WEAPON_TYPE_WHOKNOWS)
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\Smite Blue.mdx",u2,"origin"))
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x2,y2))
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x2,y2,250.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)and u3 !=u2 then
call UnitDamageTarget(u,u3,dmg*0.50,false,false,ATTACK_TYPE_HERO,DAMAGE_TYPE_NORMAL,WEAPON_TYPE_WHOKNOWS)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
elseif check==1 then
set dmg=dmg*(1.3+0.3*I2R(GetUnitAbilityLevel(u,'A0AB')))
if GetUnitAbilityLevel(u2,'B045')==1 then
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
else
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_HERO,DAMAGE_TYPE_NORMAL,WEAPON_TYPE_WHOKNOWS)
endif
call DestroyEffect(AddSpecialEffect("war3mapImported\\WispQ.mdx",x2,y2))
elseif check==2 then
set dmg=dmg*(1.15+0.15*I2R(GetUnitAbilityLevel(u,'A0AB')))
set aoe=250.*(1.1+0.05*I2R(GetUnitAbilityLevel(u,'A0AB')))
set chance=0.20*I2R(GetUnitAbilityLevel(u,'A0AB'))
call DestroyEffect(AddSpecialEffect("AncientExplode.mdx",x2,y2))
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x2,y2,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg*0.50,false,false,ATTACK_TYPE_HERO,DAMAGE_TYPE_NORMAL,WEAPON_TYPE_WHOKNOWS)
call VulnerabilityUnit(u,u3,chance)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
if not UnitAlive(u2)then
set n=GetRandomInt(1,2)
if n==1 then
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Items\\AIsm\\AIsmTarget.mdl",u,"origin"))
call SetHeroAgi(u,GetHeroAgi(u,false)+1,true)
endif
endif
if GetUnitAbilityLevel(u,'A0AL')==1 then
if check==0 then
set n=GetRandomInt(1,2)
if n==1 then
set u2=CreateUnit(pl,'h044',x2,y2,GetRandomReal(0,360))
call SetUnitScale(u2,1.50,1.50,1.50)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.7,false,function Hero56R)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,1,check)
call SaveInteger(hash,Id,2,2)
call SaveReal(hash,Id,1,dmg*0.75)
call SaveReal(hash,Id,2,250.)
endif
elseif check==1 then
set u2=CreateUnit(pl,'h044',x2,y2,GetRandomReal(0,360))
call SetUnitScale(u2,1.50,1.50,1.50)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.7,false,function Hero56R)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,1,check)
call SaveInteger(hash,Id,2,5)
call SaveReal(hash,Id,1,dmg*0.50)
call SaveReal(hash,Id,2,150.)
elseif check==2 then
set n=GetRandomInt(1,2)
if n==1 then
set u2=CreateUnit(pl,'h044',x2,y2,GetRandomReal(0,360))
call SetUnitScale(u2,1.50,1.50,1.50)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.7,false,function Hero56R)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,1,check)
call SaveInteger(hash,Id,2,2)
call SaveReal(hash,Id,1,dmg*0.75)
call SaveReal(hash,Id,2,aoe)
endif
endif
endif
endif
```

`Hero56R`　war3map.j:64709
```jass
function Hero56R takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,2)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local unit u3
local unit hero=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(hero)
local real dmg=LoadReal(hash,Id,1)
local real aoe=LoadReal(hash,Id,2)
local integer check=LoadInteger(hash,Id,1)
local integer armor=LoadInteger(hash,Id,2)
local group ug=CreateGroup()
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x,y))
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(hero,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call SetUnitExtraArmor(u3,GetUnitExtraArmor(u3)-armor)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call KillUnit(u)
call PauseTimer(t)
call DestroyTimer(t)
set t=null
set u=null
set u3=null
set ug=null
set hero=null
set pl=null
endfunction
```

## 流星 `A0AL`

俄文原名：Падающая звезда

```
「星光閃耀」技能有機率召喚一顆流星，造成額外的範圍傷害並永久降低被擊中敵人的護甲。

一般星光閃耀：50% 機率，星光閃耀傷害的 75%，範圍 250 點，護甲降低 2 點
處於「貫穿之光」效果下：100% 機率，星光閃耀傷害的 50%，範圍 150 點，護甲降低 5 點
處於「散射之光」效果下：50% 機率，星光閃耀傷害的 75%，範圍等同於提升後的星光閃耀範圍，護甲降低 2 點
```

物件欄位（原型 `Amgl`）：`aher = 1`

實作：

`Trig_HeroAttack56_Actions`　war3map.j:64819
```jass
if GetUnitAbilityLevel(u,'A0AL')==1 then
if check==0 then
set n=GetRandomInt(1,2)
if n==1 then
set u2=CreateUnit(pl,'h044',x2,y2,GetRandomReal(0,360))
call SetUnitScale(u2,1.50,1.50,1.50)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.7,false,function Hero56R)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,1,check)
call SaveInteger(hash,Id,2,2)
call SaveReal(hash,Id,1,dmg*0.75)
call SaveReal(hash,Id,2,250.)
endif
elseif check==1 then
set u2=CreateUnit(pl,'h044',x2,y2,GetRandomReal(0,360))
call SetUnitScale(u2,1.50,1.50,1.50)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.7,false,function Hero56R)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,1,check)
call SaveInteger(hash,Id,2,5)
call SaveReal(hash,Id,1,dmg*0.50)
call SaveReal(hash,Id,2,150.)
elseif check==2 then
set n=GetRandomInt(1,2)
if n==1 then
set u2=CreateUnit(pl,'h044',x2,y2,GetRandomReal(0,360))
call SetUnitScale(u2,1.50,1.50,1.50)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.7,false,function Hero56R)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,1,check)
call SaveInteger(hash,Id,2,2)
call SaveReal(hash,Id,1,dmg*0.75)
call SaveReal(hash,Id,2,aoe)
endif
endif
endif
```

`Hero56R`　war3map.j:64709
```jass
function Hero56R takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,2)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local unit u3
local unit hero=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(hero)
local real dmg=LoadReal(hash,Id,1)
local real aoe=LoadReal(hash,Id,2)
local integer check=LoadInteger(hash,Id,1)
local integer armor=LoadInteger(hash,Id,2)
local group ug=CreateGroup()
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x,y))
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(hero,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call SetUnitExtraArmor(u3,GetUnitExtraArmor(u3)-armor)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call KillUnit(u)
call PauseTimer(t)
call DestroyTimer(t)
set t=null
set u=null
set u3=null
set ug=null
set hero=null
set pl=null
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

## 純血 `A064`

俄文原名：Чистокровность

```
造成傷害的狀態在英雄身上的持續時間減少 50%。
```

實作：

`BurnUnit`　war3map.j:1939
```jass
if GetUnitAbilityLevel(target,'A064')==1 then
set count=count/2
endif
```

`BleedUnit`　war3map.j:2146
```jass
if GetUnitAbilityLevel(target,'A064')==1 then
set count=8
```

`DiseaseUnit`　war3map.j:2335
```jass
if GetUnitAbilityLevel(target,'A064')==1 then
set count=8
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

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
