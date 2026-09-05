# 龍戰士 `Npbm`（Воин Дракона）

主屬性 **敏捷** · 背包 **6 格** · 解鎖 500000 · 定位 戰士/刺客

| | 初始 | 每級 |
|---|---|---|
| 力量 | （未覆寫） | （未覆寫） |
| 敏捷 | 22 | 3 |
| 智力 | 18 | 2 |

> 結實的近戰英雄，強化路線很多，部分技能有獨立運作方式。

**縮放**：吃技能強度的技能 ['A08M', 'A08T', 'A08W', 'A08Y'] ／ ◈ 吃裝備技能威力 ['A08W'] ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **狀態** —— 走 `Burn_Dmg` 那條，**外面包了 DisableTrigger** → 不吃 DefCof、不帶穿透、被狀態抗性擋。該買的是「狀態傷害 +%」「易燃」「機率倍率」。
- **直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且事件數越多穿透越划算。
- **召喚物** —— 召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡明寫的屬性（通常是最大生命與技能強度）與原生光環。
- **治療／增益** —— 直接寫數值，不經傷害事件 —— 全地圖沒有「治療加成」這種屬性，只能靠技能公式裡的係數（多半是技能強度）。

細節見 `data/dossier/_engine.md`。


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

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acdn = 20.0`, `alev = 5`, `amcs = [90, 100, 110, 120, 130]`

呼叫共用引擎函式：`BurnUnit` —— 完整內容見 `_engine.md`。

實作：

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
set Id=GetHandleId(t2)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveInteger(hash,Id,3,60)
call SaveTimerHandle(hash,Id,3,t)
call TimerStart(t2,0.20,true,function HeroQ45_Dmg)
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

物件欄位（原型 `Absk`）：`abuf = B03E`, `acdn = 17.0`, `adur = 8.0`, `ahdu = 8.0`, `aher = 1`, `alev = 5`, `amcs = [70, 81, 92, 103, 114]`, `bsk1 = [0.15000000596046448, 0.20000000298023224, 0.25, 0.30000001192092896, 0.3500000238418579]`, `bsk2 = 0.0`, `bsk3 = 0.0`

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

呼叫共用引擎函式：`BurnUnit` —— 完整內容見 `_engine.md`。

實作：

`Trig_HeroTakeDamage_Actions`　war3map.j:19576
```jass
if LoadInteger(hash,Id,'A08Y')==1 then
if UnitAlive(d)then
call BurnUnit(a,d,r*1.00,1.00)
endif
endif
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

## 無錫手指扣 `A08V`

俄文原名：Пальцевой захват Уси

```
對近戰範圍內的敵人施展致命招式，造成大量傷害並同時施加多種狀態。也會波及目標周圍的敵人。

對普通士兵使用：對目標造成 600 +（350% 力量與敏捷）點傷害；其中 30% 的傷害會作用於目標周圍的區域
狀態施加：200% 機率施加易燃、虛弱、詛咒、易傷；附近的敵人有 30% 機率被施加虛弱

冷卻：80 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.4000000059604645, None, 1.0]`, `Ncl2 = [1, None]`, `Ncl3 = [1, None]`, `Ncl4 = [0.4000000059604645, None, 1.0]`, `Ncl5 = [0, None]`, `Ncl6 = ['chemicalrage', None, 'channel']`, `acdn = [80.0, None, 17.0]`, `alev = 1`, `amcs = [135, None, 80, 90, 100, 110, 120]`, `aran = [128.0, None, 700.0]`, `atar = ['air,ground,enemy,neutral,organic', None, 'air,ground,friend,neutral,self']`

呼叫共用引擎函式：`CurseUnit`, `FlammabilityUnit`, `VulnerabilityUnit`, `WeakUnit` —— 完整內容見 `_engine.md`。

實作：

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

## 烈焰之刃 `A08W`　—　吃技能強度、◈ 吃裝備技能威力

俄文原名：Пламенные клинки

```
繼承裝備技能的加成。

英雄的攻擊有機會造成額外的範圍傷害，並以較高的機率對敵人施加易燃。

範圍傷害：20 +（40% 力量與敏捷）+（15% 技能強度）點
「易燃」狀態：以 120% 機率施加於敵人

冷卻：10 秒
```

呼叫共用引擎函式：`FlammabilityUnit` —— 完整內容見 `_engine.md`。

實作：

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

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **18** — 裝備技能威力〔持有者〕道具觸發用 cof = key18 + 1

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
