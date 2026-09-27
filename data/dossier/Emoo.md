# 月之女祭司 `Emoo`（Жрица Луны）

主屬性 **敏捷** · 背包 **6 格** · 解鎖 50000 · 定位 刺客

| | 初始 | 每級 |
|---|---|---|
| 力量 | 12 | 1.3 |
| 敏捷 | 24 | 3.5 |
| 智力 | 20 | （未覆寫） |

> 刺客型英雄，物理與魔法傷害兼具，泛用性高。

**縮放**：吃技能強度的技能 ['A0JS', 'A0JU'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **狀態** —— 走 `Burn_Dmg` 那條，**外面包了 DisableTrigger** → 不吃 DefCof、不帶穿透、被狀態抗性擋。該買的是「狀態傷害 +%」「易燃」「機率倍率」。
- **技能直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且傷害事件數越多，穿透越划算。
- **普攻** —— 有「攻擊時觸發」的機制 → 攻擊力／攻速／穿透有價值，但注意那類技能常有自己的內部冷卻，攻速超過內冷就沒用了。
- **召喚物** —— 召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡明寫的屬性（通常是最大生命與技能強度）與原生光環。**注意**：若上面同時列出「假單位中繼」，那 `CreateUnit` 可能只是中繼用的空殼，不是真召喚物 —— 要看該單位有沒有自己的攻擊力與 timed life。
- **屬性增益** —— 直接改屬性。注意有些是**永久**的（死亡不歸零），長局會滾雪球。

細節見 `data/dossier/_engine.md`。


---

## 充能之箭 `A0JS`　—　吃技能強度

俄文原名：Заряженная стрела

```
以充能之箭擊中敵人，暈眩目標並對範圍造成額外傷害。

主要目標傷害：70 + （40% 技能強度）點
範圍傷害：主要傷害的 60%
暈眩（一般部隊）：3.6 秒
暈眩（英雄）：1.2 秒
技能強度 250 以上：永久降低被擊中敵人 3 點防禦力

冷卻時間：10 秒
```

每級變動：
  - 第 3 行：70 / 110 / 150 / 190 / 230
  - 第 4 行：50 / 55 / 60 / 65 / 70
  - 第 5 行：3.6 / 4 / 4.4 / 4.8 / 5.2
  - 第 6 行：1.2 / 1.4 / 1.6 / 1.8 / 2
  - 第 7 行：100 / 125 / 150 / 175 / 200

物件欄位（原型 `AHtb`）：`Htb1 = 1.0`, `acdn = 10.0`, `adur = [3.5999999046325684, 4.0, 4.400000095367432, 4.800000190734863, 5.200000286102295]`, `ahdu = [1.2000000476837158, 1.4000000953674316, 1.6000001430511475, 1.8000001907348633, 2.000000238418579]`, `alev = 5`, `amac = 0.05000000074505806`, `amat = war3mapImported\Azul Arrow Defrosted.mdx`, `amcs = [65, None, 85, 95, 105]`, `amsp = 1200`

呼叫共用引擎函式：`VulnerabilityUnit` —— 完整內容見 `_engine.md`。

實作：

`Hero36Q`　war3map.j:58536
```jass
function Hero36Q takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real dmg=30+40*GetUnitAbilityLevel(u,'A0JS')+udg_ItemBonusDMG[n]*0.40
local real aoe_cof=0.45+0.05*GetUnitAbilityLevel(u,'A0JS')
local real chanse=0.75+0.25*GetUnitAbilityLevel(u,'A0JS')
local unit u2=LoadUnitHandle(hash,Id,2)
local unit u3
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local group ug=CreateGroup()
call DestroyEffect(AddSpecialEffect("AncientExplode.mdx",x,y))
call GroupEnumUnitsInRange(ug,x,y,280.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
if u3==u2 then
call Hero36_dmg(u,u3,dmg)
else
call Hero36_dmg(u,u3,dmg*aoe_cof)
endif
call VulnerabilityUnit(u,u3,chanse)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
set t=null
set u=null
set u2=null
set u3=null
set ug=null
set pl=null
endfunction
```

`Trig_HeroSkills36_Actions`　war3map.j:58660
```jass
if Skill=='A0JS' then
set u3=GetSpellTargetUnit()
set x=GetUnitX(u)
set y=GetUnitY(u)
set x2=GetUnitX(u3)
set y2=GetUnitY(u3)
set x=DistanceNative(x,y,x2,y2)/1200.
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u3)
call TimerStart(t,x,true,function Hero36Q)
```

`Hero36_dmg`　war3map.j:58519
```jass
function Hero36_dmg takes unit u,unit u2,real dmg returns nothing
local timer t
local integer u2_Id
if GetUnitAbilityLevel(u2,'B045')==1 and GetUnitAbilityLevel(u,'A0XN')!=1 then
set u2_Id=GetHandleId(u2)
call UnitRemoveAbility(u2,'S014')
call UnitRemoveAbility(u2,'B045')
set t=LoadTimerHandle(hash,u2_Id,'B045')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'B045')
call SetUnitExtraArmor(u2,GetUnitExtraArmor(u2)-3)
endif
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
set t=null
endfunction
function Hero36Q takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real dmg=30+40*GetUnitAbilityLevel(u,'A0JS')+udg_ItemBonusDMG[n]*0.40
local real aoe_cof=0.45+0.05*GetUnitAbilityLevel(u,'A0JS')
local real chanse=0.75+0.25*GetUnitAbilityLevel(u,'A0JS')
local unit u2=LoadUnitHandle(hash,Id,2)
local unit u3
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local group ug=CreateGroup()
call DestroyEffect(AddSpecialEffect("AncientExplode.mdx",x,y))
call GroupEnumUnitsInRange(ug,x,y,280.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
if u3==u2 then
call Hero36_dmg(u,u3,dmg)
else
call Hero36_dmg(u,u3,dmg*aoe_cof)
endif
call VulnerabilityUnit(u,u3,chanse)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
set t=null
set u=null
set u2=null
set u3=null
set ug=null
set pl=null
endfunction
```

## 群星隕落 `A0JU`　—　吃技能強度

俄文原名：Звездопад

```
女祭司標記指定區域，區域內每次觸發時會有 3 名隨機敵人受到墜落之星的傷害。每顆星會使敵人受到「月光閃爍」技能的傷害提高 5%。

星辰傷害：30 + （10% 技能強度） + （50% 敏捷）點
觸發間隔：0.4 秒
持續時間：16 秒

冷卻時間：80 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = 0.5`, `Ncl2 = 2`, `Ncl3 = 3`, `Ncl4 = 0.5`, `Ncl5 = 0`, `Ncl6 = wispharvest`, `aare = 400.0`, `acap = `, `acdn = 80.0`, `alev = 1`, `amcs = 200`, `aran = 700.0`, `atar = player,structure`

實作：

`Trig_HeroSkills36_Actions`　war3map.j:58680
```jass
elseif Skill=='A0JU' then
set x=GetSpellTargetX()
set y=GetSpellTargetY()
set t=CreateTimer()
set Id=GetHandleId(t)
set u3=CreateUnit(pl,'o01V',x,y,270)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u3)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveInteger(hash,Id,1,40)
call TimerStart(t,0.4,true,function Hero36R)
```

`Hero36_dmg`　war3map.j:58519
```jass
function Hero36_dmg takes unit u,unit u2,real dmg returns nothing
local timer t
local integer u2_Id
if GetUnitAbilityLevel(u2,'B045')==1 and GetUnitAbilityLevel(u,'A0XN')!=1 then
set u2_Id=GetHandleId(u2)
call UnitRemoveAbility(u2,'S014')
call UnitRemoveAbility(u2,'B045')
set t=LoadTimerHandle(hash,u2_Id,'B045')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'B045')
call SetUnitExtraArmor(u2,GetUnitExtraArmor(u2)-3)
endif
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
set t=null
endfunction
```

`Hero36R`　war3map.j:58576
```jass
function Hero36R takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local integer count=LoadInteger(hash,Id,1)
local unit u3
local real dmg=30+udg_ItemBonusDMG[n]*0.10+I2R(GetHeroAgi(u,true))*0.50
local group ug=CreateGroup()
local group ug2=CreateGroup()
set ug=CreateGroup()
set ug2=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,405,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call GroupAddUnit(ug2,u3)
endif
call GroupRemoveUnit(ug,u3)
endloop
set ug2=GetRandomSubGroup(3,ug2)
loop
set u3=FirstOfGroup(ug2)
exitwhen u3==null
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\NightElf\\Starfall\\StarfallTarget.mdl",u3,"origin"))
call Hero36_dmg(u,u3,dmg)
call SaveReal(hash,GetHandleId(u3),'A02C',LoadReal(hash,GetHandleId(u3),'A02C')+0.05)
call GroupRemoveUnit(ug2,u3)
endloop
call DestroyGroup(ug)
call DestroyGroup(ug2)
set count=count-1
if count<=0 then
set u3=LoadUnitHandle(hash,Id,2)
call RemoveUnit(u3)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SaveInteger(hash,Id,1,count)
endif
set t=null
set u=null
set u3=null
set ug=null
set ug2=null
set pl=null
endfunction
```

## 精準射擊光環 `A0JQ`

俄文原名：Аура меткого выстрела

```
女祭司在 12 秒內提升自身的攻擊速度與移動速度，並散發一道光環（範圍 400），提高友方部隊的攻擊力。

移動速度提升：10%
攻擊速度提升：20%
攻擊力提升（光環）：20%

冷卻時間：26 秒
```

每級變動：
  - 第 3 行：10 / 15 / 20 / 25 / 30
  - 第 4 行：20 / 30 / 40 / 50 / 60
  - 第 5 行：20 / 26 / 32 / 38 / 44

物件欄位（原型 `Absk`）：`abuf = B025`, `acdn = 26.0`, `adur = [None, 12.0]`, `ahdu = [None, 12.0]`, `aher = 1`, `alev = 5`, `amcs = [100, 115, 130, 145, 160]`, `bsk1 = [0.10000000149011612, 0.15000000596046448, 0.20000000298023224, 0.25, 0.30000001192092896]`, `bsk2 = [0.20000000298023224, 0.30000001192092896, 0.4000000059604645, 0.5, 0.6000000238418579]`, `bsk3 = 0.0`

實作：

`Trig_HeroSkills36_Actions`　war3map.j:58672
```jass
elseif Skill=='A0JQ' then
call UnitAddAbility(u,'A0JR')
call SetUnitAbilityLevel(u,'A0JR',GetUnitAbilityLevel(u,Skill))
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,2,'A0JR')
call TimerStart(t,12.,false,function RemoveBuff)
```

`RemoveBuff`　war3map.j:3078
```jass
function RemoveBuff takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local integer Buff=LoadInteger(hash,Id,2)
call UnitRemoveAbility(u,Buff)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
set t=null
set u=null
endfunction
```

## 月光閃爍 `A02C`

俄文原名：Лунный блик

```
女祭司的攻擊對目標造成額外的魔法傷害，並使目標受到本技能的傷害提高 10%。

傷害：（100% 敏捷）點

冷卻時間：5 秒
```

每級變動：
  - 第 3 行：100 / 130 / 160 / 190 / 220

物件欄位（原型 `Amgl`）：`aher = 1`, `alev = 5`

呼叫共用引擎函式：`VulnerabilityUnit` —— 完整內容見 `_engine.md`。

實作：

`Hero36R`　war3map.j:58576
```jass
function Hero36R takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local integer count=LoadInteger(hash,Id,1)
local unit u3
local real dmg=30+udg_ItemBonusDMG[n]*0.10+I2R(GetHeroAgi(u,true))*0.50
local group ug=CreateGroup()
local group ug2=CreateGroup()
set ug=CreateGroup()
set ug2=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,405,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call GroupAddUnit(ug2,u3)
endif
call GroupRemoveUnit(ug,u3)
endloop
set ug2=GetRandomSubGroup(3,ug2)
loop
set u3=FirstOfGroup(ug2)
exitwhen u3==null
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\NightElf\\Starfall\\StarfallTarget.mdl",u3,"origin"))
call Hero36_dmg(u,u3,dmg)
call SaveReal(hash,GetHandleId(u3),'A02C',LoadReal(hash,GetHandleId(u3),'A02C')+0.05)
call GroupRemoveUnit(ug2,u3)
endloop
call DestroyGroup(ug)
call DestroyGroup(ug2)
set count=count-1
if count<=0 then
set u3=LoadUnitHandle(hash,Id,2)
call RemoveUnit(u3)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SaveInteger(hash,Id,1,count)
endif
set t=null
set u=null
set u3=null
set ug=null
set ug2=null
set pl=null
endfunction
```

`Trig_HeroAttack36_Actions`　war3map.j:58754
```jass
if GetUnitAbilityLevel(u,'A02C')>=1 and LoadInteger(hash,Id,'A02C')==0 and IsUnitEnemy(u3,pl)then
call SaveInteger(hash,Id,'A02C',1)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveInteger(hash,Id,1,GetHandleId(u))
call SaveInteger(hash,Id,2,'A02C')
call TimerStart(t,5.,false,function EndCooldown)
set dmg=I2R(GetHeroAgi(u,true))*(0.70+0.30*I2R(GetUnitAbilityLevel(u,'A02C')))
if GetUnitAbilityLevel(u,'A11A')==1 then
if LoadInteger(hash,GetHandleId(u3),'A02C')==0 then
set dmg=dmg*2.0
call SaveInteger(hash,GetHandleId(u3),'A02C',1)
endif
call Hero36_dmg(u,u3,dmg)
call VulnerabilityUnit(u,u3,1.00)
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\Smite Blue.mdx",u3,"origin"))
else
set dmg=dmg*(1+LoadReal(hash,GetHandleId(u3),'A02C'))
call Hero36_dmg(u,u3,dmg)
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\Smite Blue.mdx",u3,"origin"))
if UnitAlive(u3)then
call SaveReal(hash,GetHandleId(u3),'A02C',LoadReal(hash,GetHandleId(u3),'A02C')+0.1)
endif
endif
```

`Hero36_dmg`　war3map.j:58519
```jass
function Hero36_dmg takes unit u,unit u2,real dmg returns nothing
local timer t
local integer u2_Id
if GetUnitAbilityLevel(u2,'B045')==1 and GetUnitAbilityLevel(u,'A0XN')!=1 then
set u2_Id=GetHandleId(u2)
call UnitRemoveAbility(u2,'S014')
call UnitRemoveAbility(u2,'B045')
set t=LoadTimerHandle(hash,u2_Id,'B045')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'B045')
call SetUnitExtraArmor(u2,GetUnitExtraArmor(u2)-3)
endif
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
set t=null
endfunction
```

## 選擇天賦 `A116`

俄文原名：Выбрать талант

```
При должном количестве очков опыта игрока вы можете выбрать талант, который значительно усилит героя до нового ранга силы.
```

**天賦選項**：
  - `A119` Пронзительный свет
    Ранг силы: Т3 Бонус к характеристикам/бонус к приросту характеристик за уровень: +0 / +0 +3 / +1 +1 / +0  Умение "Лунный блик" больше не накапливает бонус к урону на целях (умение "Звездопад" также утрачивает накопительный бонус для "блика"). Первый такт "блика" на цели наносит сразу 200% урона, последующие такты наносят обычный урон без бонуса. Также умение "Лунный блик" теперь применяет к врагам
  - `A117` Дар Лунарис
    Ранг силы: Т3+ Бонус к характеристикам/бонус к приросту характеристик за уровень: +1 / +0 +4 / +2 +3 / +1  Вы можете переместить во второй инвентарь (F2) предмет, являющийся кольцом. Таким образом можно иметь 1 предмет во втором инвентаре.

物件欄位（原型 `Aspb`）：`aite = 0`, `spb1 = A119,A117`, `spb2 = 0`, `spb3 = 2`, `spb4 = 2`

實作：

`Trig_HeroSkills36_Actions`　war3map.j:58643
```jass
if Skill=='A119' then
call SetHeroAgi(u,GetHeroAgi(u,false)+3,true)
call SetHeroInt(u,GetHeroInt(u,false)+1,true)
call SaveInteger(hash,GetHandleId(u),'aAGI',1)
call UnitRemoveAbility(u,'A116')
call UnitAddAbility(u,'A11A')
call SaveInteger(hash,GetHandleId(pl),15,1)
elseif Skill=='A117' then
call SetHeroStr(u,GetHeroStr(u,false)+1,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+4,true)
call SetHeroInt(u,GetHeroInt(u,false)+3,true)
call SaveInteger(hash,GetHandleId(u),'aAGI',2)
call SaveInteger(hash,GetHandleId(u),'aINT',1)
call UnitRemoveAbility(u,'A116')
call UnitAddAbility(u,'A118')
call SaveInteger(hash,GetHandleId(pl),15,1)
endif
```

## 轉移／移除據點 `A03V`

俄文原名：Передать/удалить точку

```
選擇自己的據點或建築，將其轉移給其他玩家，或在不損失地基的情況下摧毀它。可從任意距離施放。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.009999999776482582, 0.8999999761581421]`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = [0.009999999776482582, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['unburrow', 'channel']`, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = [99999.0, 100.0]`, `atar = ['player,structure', 'air,ground,debris,enemy,neutral,organic']`

實作：

`Trig_ChangePoints_Actions`　war3map.j:18929
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

## Свет Лунарис `A115`


```
Умения героя перед нанесением урона снимают с врагов статус "уязвимость", взамен снижая защиту на 3 ед. на неограниченный срок.
```

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

## Пронзительный свет `A119`　—　來自天賦「選擇天賦」


```
Ранг силы: Т3
Бонус к характеристикам/бонус к приросту характеристик за уровень:
+0 / +0
+3 / +1
+1 / +0

Умение "Лунный блик" больше не накапливает бонус к урону на целях (умение "Звездопад" также утрачивает накопительный бонус для "блика"). Первый такт "блика" на цели наносит сразу 200% урона, последующие такты наносят обычный урон без бонуса. Также умение "Лунный блик" теперь применяет к врагам уязвимость с 100% шансом.
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [0.5, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['faeriefireon', 'channel']`, `acap = `, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `arqa = 24`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills36_Actions`　war3map.j:58643
```jass
if Skill=='A119' then
call SetHeroAgi(u,GetHeroAgi(u,false)+3,true)
call SetHeroInt(u,GetHeroInt(u,false)+1,true)
call SaveInteger(hash,GetHandleId(u),'aAGI',1)
call UnitRemoveAbility(u,'A116')
call UnitAddAbility(u,'A11A')
call SaveInteger(hash,GetHandleId(pl),15,1)
```

## Дар Лунарис `A117`　—　來自天賦「選擇天賦」


```
Ранг силы: Т3+
Бонус к характеристикам/бонус к приросту характеристик за уровень:
+1 / +0
+4 / +2
+3 / +1

Вы можете переместить во второй инвентарь (F2) предмет, являющийся кольцом. Таким образом можно иметь 1 предмет во втором инвентаре.
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [0.5, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['acolyteharvest', 'channel']`, `acap = `, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `arqa = 32`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills36_Actions`　war3map.j:58650
```jass
elseif Skill=='A117' then
call SetHeroStr(u,GetHeroStr(u,false)+1,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+4,true)
call SetHeroInt(u,GetHeroInt(u,false)+3,true)
call SaveInteger(hash,GetHandleId(u),'aAGI',2)
call SaveInteger(hash,GetHandleId(u),'aINT',1)
call UnitRemoveAbility(u,'A116')
call UnitAddAbility(u,'A118')
call SaveInteger(hash,GetHandleId(pl),15,1)
endif
```

## 毀滅齊射 `A0VN`　—　來自皮膚「黑月騎士」

俄文原名：Губительный залп

```
英雄的攻擊會射出一輪額外的箭矢，命中路徑上的敵人。

每支箭矢的傷害：（40% 敏捷）點
箭矢數量：8 +（2% 技能強度）支

冷卻時間：6 秒
```

每級變動：
  - 第 3 行：40 / 50 / 60 / 70 / 80

物件欄位（原型 `Amgl`）：`aher = 1`, `alev = 5`

實作：

`ProjectilesSkill36`　war3map.j:58716
```jass
function ProjectilesSkill36 takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local real angle=LoadReal(hash,Id,3)
local integer count=LoadInteger(hash,Id,1)
local real dmg=I2R(GetHeroAgi(u,true))*(0.30+0.10*I2R(GetUnitAbilityLevel(u,'A0VN')))
if count>0 then
set count=count-1
call SaveInteger(hash,Id,1,count)
set angle=angle+GetRandomReal(-20.,20.)
call CreateProjectile(u,'o01Y',33.,1400.,x,y,angle,dmg,45.,45.,"none","Abilities\\Spells\\Other\\BlackArrow\\BlackArrowMissile.mdl")
else
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
endif
set t=null
set u=null
endfunction
```

`Trig_HeroAttack36_Actions`　war3map.j:58778
```jass
elseif GetUnitAbilityLevel(u,'A0VN')>=1 and LoadInteger(hash,Id,'A0VN')==0 and IsUnitEnemy(u3,pl)then
call SaveInteger(hash,Id,'A0VN',1)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveInteger(hash,Id,1,GetHandleId(u))
call SaveInteger(hash,Id,2,'A0VN')
call TimerStart(t,5.,false,function EndCooldown)
set x=GetUnitX(u)
set y=GetUnitY(u)
set angle=AngleXY(x,y,x3,y3)
set count=8+R2I(udg_ItemBonusDMG[GetPlayerId(pl)+1]*0.02)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.04,true,function ProjectilesSkill36)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,count)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveReal(hash,Id,3,angle)
endif
```

## Ритуал Чёрной Луны `A0XN`　—　來自皮膚「黑月騎士」


```
造成傷害會給予英雄加成：

每對任意敵人造成 500 點傷害：+0.5 穿透；下一次強化所需的傷害量 +35 點
```

實作：

`VulnerabilityUnit`　war3map.j:2728
```jass
if GetUnitAbilityLevel(damager,'A0XN')==1 then
set time=time+2.
endif
```

`Hero36_dmg`　war3map.j:58522
```jass
if GetUnitAbilityLevel(u2,'B045')==1 and GetUnitAbilityLevel(u,'A0XN')!=1 then
set u2_Id=GetHandleId(u2)
call UnitRemoveAbility(u2,'S014')
call UnitRemoveAbility(u2,'B045')
set t=LoadTimerHandle(hash,u2_Id,'B045')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'B045')
call SetUnitExtraArmor(u2,GetUnitExtraArmor(u2)-3)
endif
```

---

## 皮膚

### 黑月騎士 `E00J` —— **會換技能**
  - 月光閃爍 `A02C` → **毀滅齊射** `A0VN`
  - 選擇天賦 `A116` → **Ритуал Чёрной Луны** `A0XN`
  - 失去 Свет Лунарис `A115`

---

## 同一組的其他實作函式

英雄的實作散在同編號的一組函式裡，上面按技能抽取時抓不到的補在這裡
（常見的是決定門檻、結算加成、清理 buff 的那幾支）。

`Trig_HeroAttack36_Conditions`　war3map.j:58713
```jass
function Trig_HeroAttack36_Conditions takes nothing returns boolean
return GetUnitTypeId(GetAttacker())=='Emoo' or GetUnitTypeId(GetAttacker())=='E00J'
endfunction
```

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof

---

*由 `tools/build_dossier.py` 從 UD test 24.09.27（合併版） 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
