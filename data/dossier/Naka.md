# 最古老的先知 `Naka`（Старейший прорицатель）

主屬性 **智力** · 背包 **6 格** · 解鎖 500000 · 定位 法師/輔助

| | 初始 | 每級 |
|---|---|---|
| 力量 | 18 | 2.5 |
| 敏捷 | （未覆寫） | 1.6 |
| 智力 | 28 | 3.5 |

> 能提升友方建築防禦並為其套上魔法屏障，具備獨特機制。

**縮放**：吃技能強度的技能 ['A0WP', 'A0WR', 'A0WS'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

---

## 塌方 `A0WR`　—　吃技能強度

俄文原名：Обвал

```
朝指定方向發射 3 顆巨石，每顆巨石在撞上敵人或障礙物時造成範圍傷害。

傷害：50 +（25% 技能強度）點

冷卻：13 秒
```

每級變動：
  - 第 3 行：50 / 75 / 100 / 125 / 150

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = channel`, `acdn = 13.0`, `alev = 5`, `amcs = [90, 105, 120, 135, 150]`, `aran = 700.0`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`HeroQ48`　war3map.j:61199
```jass
function HeroQ48 takes nothing returns nothing
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
local real dmg2
local real degrees=LoadReal(hash,Id,4)
local integer check=LoadInteger(hash,Id,2)
local integer count=LoadInteger(hash,Id,3)
local group ug
local integer B=0
local real r
call SetUnitX(u2,PolarX(x,20,degrees))
call SetUnitY(u2,PolarY(y,20,degrees))
set check=check+1
set count=count-1
if check==2 and count !=0 then
set check=0
set u=LoadUnitHandle(hash,Id,1)
set pl=GetOwningPlayer(u)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,70,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null or B>0
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
set B=1
set u4=u3
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
if IsTerrainPathable(x,y,PATHING_TYPE_WALKABILITY)==true and B==0 then
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,200,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call KillUnit(u2)
set t=null
set u=null
set u2=null
set u3=null
set u4=null
set pl=null
return
endif
if B>0 then
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,200,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call KillUnit(u2)
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
call KillUnit(u2)
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
```

`Trig_HeroSkills48_Actions`　war3map.j:61465
```jass
if Skill=='A0WR' then
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set angle=AngleXY(x,y,x2,y2)
set x=PolarX(x,30,angle)
set y=PolarY(y,30,angle)
set dmg=25.+25.*lvl+udg_ItemBonusDMG[n]*0.25
set L=3
set r=12.
set angle=angle-r*2.
set i=0
loop
set i=i+1
set angle=angle+r
set u3=CreateUnit(pl,'o034',x,y,angle)
call SetUnitX(u3,x)
call SetUnitY(u3,y)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u3)
call SaveReal(hash,Id,1,dmg)
call SaveInteger(hash,Id,2,-1)
call SaveInteger(hash,Id,3,80)
call SaveReal(hash,Id,4,angle)
call TimerStart(t,0.03,true,function HeroQ48)
exitwhen i==L
endloop
```

## 大地德魯伊 `AHad`

俄文原名：Друид земли

```
提升英雄附近建築的護甲。

護甲加成：3 點
光環作用範圍：800
```

每級變動：
  - 第 3 行：3 / 5 / 7 / 9 / 11

物件欄位（原型 `None`）：`Had1 = [3.0, 5.0, 7.0, 9.0, 11.0]`, `aare = 800.0`, `abuf = B03R`, `adur = 4.0`, `alev = 5`, `atar = air,structure,notself,allies`

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

## 地震 `A0WP`　—　吃技能強度

俄文原名：Землетрясение

```
開始持續施法，期間指定範圍內的敵人會被減速並受到傷害。

傷害：30 +（15% 技能強度）點/秒
敵人減速：-30% 移動速度，-15% 攻擊速度
持續時間：7 秒

冷卻：25 秒
```

每級變動：
  - 第 3 行：30 / 45 / 60 / 75 / 90
  - 第 4 行：30% скорость бега, -15 / 35% скорость бега, -20 / 40% скорость бега, -25 / 45% скорость бега, -30 / 50% скорость бега, -35

物件欄位（原型 `ANcl`）：`Ncl1 = 7.099999904632568`, `Ncl2 = 2`, `Ncl3 = 3`, `Ncl4 = 1.3300000429153442`, `Ncl5 = 0`, `Ncl6 = charm`, `aare = 270.0`, `acdn = 25.0`, `alev = 5`, `amcs = [125, 150, 175, 200, 225]`, `aran = 800.0`

實作：

`HeroW48_conditions`　war3map.j:61525
```jass
function HeroW48_conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0WP'
endfunction
function HeroW48_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local real x2
local real y2
local real dist
local real angle
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local unit u3
local real dmg=(15.+15.*I2R(GetUnitAbilityLevel(u,'A0WP'))+udg_ItemBonusDMG[n]*0.15)*0.50
local group ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,275.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
set n=1
loop
exitwhen n>4
set dist=GetRandomReal(10.,270.)
set angle=GetRandomReal(0.,360.)
set x2=PolarX(x,dist,angle)
set y2=PolarY(y,dist,angle)
call DestroyEffect(AddSpecialEffect("Objects\\Spawnmodels\\Undead\\ImpaleTargetDust\\ImpaleTargetDust.mdl",x2,y2))
set n=n+1
endloop
set t=null
set u=null
set pl=null
set u3=null
set ug=null
endfunction
function Trig_HeroW48_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local unit u2
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
local real x=GetSpellTargetX()
local real y=GetSpellTargetY()
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call TimerStart(t,0.50,true,function HeroW48_Dmg)
call SaveTimerHandle(hash,GetHandleId(u),'A0WP',t)
set u2=CreateUnit(GetOwningPlayer(u),'o038',x,y,270.)
call SetUnitX(u2,x)
call SetUnitY(u2,y)
call SetUnitAbilityLevel(u2,'S00W',GetUnitAbilityLevel(u,'A0WP'))
call SaveUnitHandle(hash,Id,3,u2)
set u=null
set u2=null
set t=null
endfunction
```

`Trig_HeroW48_Stop_Conditions`　war3map.j:61595
```jass
function Trig_HeroW48_Stop_Conditions takes nothing returns boolean
return GetSpellAbilityId()=='A0WP'
endfunction
function Trig_HeroW48_Stop_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local integer Id=GetHandleId(u)
local timer t=LoadTimerHandle(hash,Id,'A0WP')
local integer Id_t=GetHandleId(t)
call RemoveUnit(LoadUnitHandle(hash,Id_t,3))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,Id,'A0WP')
call FlushChildHashtable(hash,Id_t)
set u=null
set t=null
endfunction
```

## 碎裂 `A0WT`

俄文原名：Раскол

```
朝指定方向撕裂大地，生成持續 9-18 秒的岩漿團，對附近的敵人造成傷害。每次傷害跳動都有機率對敵人施加點燃效果。

岩漿團出現時的傷害：60 + （60% 智力）點。
岩漿團的持續傷害：20 + （20% 智力）點/秒。
點燃效果：20% 機率；持續傷害為所造成傷害的 25%

冷卻：90 秒。
```

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = [1, 2]`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = ['channel', 'chemicalrage']`, `acdn = [90.0, 17.0]`, `alev = 1`, `amcs = [250, 80, 90, 100, 110, 120]`, `aran = [700.0, 800.0]`, `atar = air,ground,friend,neutral,self`

實作：

`Hero48R`　war3map.j:61344
```jass
function Hero48R takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2
local unit u3
local real x=LoadReal(hash,Id,2)
local real y=LoadReal(hash,Id,3)
local player pl=GetOwningPlayer(u)
local real angle=LoadReal(hash,Id,1)
local real dmg=60.+I2R(GetHeroInt(u,true))*0.60
local integer count=LoadInteger(hash,Id,1)
local group ug
local real dist
local timer t2
local integer Id2
set count=count-1
set x=PolarX(x,60,angle)
set y=PolarY(y,60,angle)
call SaveReal(hash,Id,2,x)
call SaveReal(hash,Id,3,y)
set dist=GetRandomReal(0.,125.)
set angle=GetRandomReal(0.,360.)
set x=PolarX(x,dist,angle)
set y=PolarY(y,dist,angle)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,150,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
call BurnUnit(u,u3,dmg*0.25,0.20)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Other\\Volcano\\VolcanoDeath.mdl",x,y))
set Id2=GetRandomInt(1,3)
if Id2==1 then
set Id2='o035'
elseif Id2==2 then
set Id2='o036'
else
set Id2='o037'
endif
set u2=CreateUnit(pl,Id2,x,y,GetRandomReal(0.,360.))
call SetUnitX(u2,x)
call SetUnitY(u2,y)
set t2=CreateTimer()
set Id2=GetHandleId(t2)
call SaveUnitHandle(hash,Id2,1,u)
call SaveUnitHandle(hash,Id2,2,u2)
call SaveInteger(hash,Id2,1,GetRandomInt(18,36))
call TimerStart(t2,0.50,true,function Hero48R_dmg)
if count==0 then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SaveInteger(hash,GetHandleId(t),1,count)
endif
set t=null
set t2=null
set u=null
set u2=null
set u3=null
set pl=null
set ug=null
endfunction
```

`Trig_HeroSkills48_Actions`　war3map.j:61493
```jass
elseif Skill=='A0WT' then
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set angle=AngleXY(x,y,x2,y2)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,30)
call SaveReal(hash,Id,1,angle)
call SaveReal(hash,Id,2,x)
call SaveReal(hash,Id,3,y)
call TimerStart(t,0.04,true,function Hero48R)
```

## 強化 `A0WS`　—　吃技能強度

俄文原名：Укрепление

```
在指定建築上建立一道屏障，吸收所有進入的傷害。

屏障強度：100 +（200% 智力）+（50% 技能強度）點
屏障持續時間：無限制

冷卻：20 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = cloudoffog`, `acap = `, `acdn = 20.0`, `aher = 0`, `alev = 1`, `amcs = 50`, `aran = 700.0`, `atar = friend,structure`

實作：

`Trig_ButtonChangePoints_Actions`　war3map.j:17774
```jass
if b==udg_CTButton[9]then
set n2=0
set n3=GetUnitLevel(udg_CTPoint[n])
set x=GetUnitX(udg_CTPoint[n])
set y=GetUnitY(udg_CTPoint[n])
set UT=GetUnitTypeId(udg_CTPoint[n])
set NoBuildingExplosions=1
call SaveReal(hash,GetHandleId(udg_CTPoint[n]),'A0WS',0.)
call SaveInteger(hash,GetHandleId(udg_CTPoint[n]),'A0WS',0)
call DestroyTextTag(LoadTextTagHandle(hash,GetHandleId(udg_CTPoint[n]),26))
call KillUnit(udg_CTPoint[n])
call ShowUnit(udg_CTPoint[n],false)
set NoBuildingExplosions=0
if n3==1 then
call CreateUnit(pl,'n000',x,y,270.00)
elseif n3==2 then
call CreateUnit(pl,'n002',x,y,270.00)
elseif n3==3 then
call CreateUnit(pl,'n001',x,y,270.00)
elseif n3==4 then
call CreateUnit(pl,'n003',x,y,270.00)
elseif n3==5 then
call CreateUnit(pl,'n01U',x,y,270.00)
elseif n3==6 then
call CreateUnit(pl,'h01X',x,y,270.00)
elseif n3==7 then
call CreateUnit(pl,'n068',x,y,270.00)
endif
set pl=null
set b=null
return
endif
```

`Trig_HeroTakeDamage_Actions`　war3map.j:19541
```jass
elseif LoadInteger(hash,GetHandleId(d),'A0WS')==1 then
set r=LoadReal(hash,GetHandleId(d),'A0WS')
if r>dmg then
call SetWidgetLife(d,life+dmg)
call SaveReal(hash,GetHandleId(d),'A0WS',r-dmg)
elseif r==dmg then
call SetWidgetLife(d,life+dmg)
call SaveReal(hash,GetHandleId(d),'A0WS',0.)
call SaveInteger(hash,GetHandleId(d),'A0WS',0)
call DestroyTextTag(LoadTextTagHandle(hash,GetHandleId(d),26))
elseif r<dmg then
call SetWidgetLife(d,life+r)
call SaveReal(hash,GetHandleId(d),'A0WS',0.)
call SaveInteger(hash,GetHandleId(d),'A0WS',0)
call DestroyTextTag(LoadTextTagHandle(hash,GetHandleId(d),26))
endif
set a=null
set d=null
set Item=null
set t=null
return
endif
```

`Hero48D`　war3map.j:61414
```jass
function Hero48D takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local real dmg=LoadReal(hash,GetHandleId(u),'A0WS')
local texttag text=LoadTextTagHandle(hash,GetHandleId(u),26)
local force f=CreateForce()
call ForceAddPlayer(f,pl)
call DestroyTextTag(text)
set udg_p=GetUnitLoc(u)
set text=CreateTextTagLocBJ("|cFF9ED1D8"+I2S(R2I(dmg)),udg_p,0,12.00,100,100,100,0)
call ShowTextTagForceBJ(true,text,bj_FORCE_ALL_PLAYERS)
call RemoveLocation(udg_p)
call SaveTextTagHandle(hash,GetHandleId(u),26,text)
call DestroyForce(f)
if not UnitAlive(u)or dmg<=0. then
call SaveInteger(hash,GetHandleId(u),'A0WS',0)
call DestroyTextTag(text)
call RemoveSavedHandle(hash,GetHandleId(u),'A0WS')
call RemoveSavedHandle(hash,GetHandleId(u),26)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
endif
set f=null
set t=null
set u=null
set pl=null
set text=null
endfunction
```

`Trig_HeroSkills48_Actions`　war3map.j:61505
```jass
elseif Skill=='A0WS' then
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Items\\TomeOfRetraining\\TomeOfRetrainingCaster.mdl",u2,"origin"))
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,u2)
call TimerStart(t,0.25,true,function Hero48D)
set dmg=100.+I2R(GetHeroInt(u,true))*2.0+udg_ItemBonusDMG[n]*0.50
call SaveInteger(hash,GetHandleId(u2),Skill,1)
call SaveReal(hash,GetHandleId(u2),Skill,dmg)
call SaveTimerHandle(hash,GetHandleId(u2),Skill,t)
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

---

## 這隻召喚／製造的單位

（技能程式碼裡的 `CreateUnit` 目標。數值取自 war3map.w3u，
沒列出的欄位代表地圖沒覆寫、沿用原型。）

### `h01X` Магический куб（原型 `hvlt`）
  - 生命 1000 ／ 技能 A0A9
  - 技能 `A0A9` Магический куб　`Hab1 = 1.5`, `aare = 99999.0`, `abuf = B00U`

### `n000` Базовая точка（原型 `ncop`）
  - 生命 100

### `n001` Точка прибыли（原型 `ncp2`）
  - 生命 200

### `n002` Точка производства（原型 `ncp2`）
  - 生命 200

### `n003` Стратегическая точка（原型 `ncp3`）
  - 生命 400

### `n01U` Точка обороны（原型 `ncp3`）
  - 生命 400

### `n068` Точка поддержки（原型 `ncop`）
  - 生命 100

### `o038` Землетрясение（原型 `ocat`）
  - 技能 S00W,Aloc
  - 技能 `S00W` (землетрясение)　`Oae1 = [-0.30000001192092896, -0.3499999940395355, -0.4000000059604645, -0.44999998807907104, -0.5]`, `Oae2 = [-0.15000000596046448, -0.20000000298023224, -0.25, -0.30000001192092896, -0.3499999940395355]`, `aare = 270.0`, `abuf = B03S`, `alev = 5`, `atar = enemies`

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
