# 拜火者 `Hamg`（Огнепоклонник）

主屬性 **智力** · 背包 **6 格** · 解鎖 50000 · 定位 法師

| | 初始 | 每級 |
|---|---|---|
| 力量 | （未覆寫） | 2.3 |
| 敏捷 | 15 | 1.2 |
| 智力 | 28 | 3.5 |

> 戰鬥法師，只有攻擊性法術，專精於「點燃」狀態。

**縮放**：吃技能強度的技能 ['A02J', 'A03F', 'A03O', 'AHfs'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **狀態** —— 走 `Burn_Dmg` 那條，**外面包了 DisableTrigger** → 不吃 DefCof、不帶穿透、被狀態抗性擋。該買的是「狀態傷害 +%」「易燃」「機率倍率」。
- **技能直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且傷害事件數越多，穿透越划算。
- **召喚物** —— 召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡明寫的屬性（通常是最大生命與技能強度）與原生光環。
- **屬性增益** —— 直接改屬性。注意有些是**永久**的（死亡不歸零），長局會滾雪球。

細節見 `data/dossier/_engine.md`。


---

## 火山爆破 `A03F`　—　吃技能強度

俄文原名：Вулканический подрыв

```
英雄朝指定方向引發一連串接續的爆破，造成範圍傷害。最後一次爆破造成更高的傷害、更大的作用範圍，並施加點燃效果。

爆破傷害：30 +（12% 技能強度）點
強化爆破傷害：50 +（20% 技能強度）點
強化爆破的點燃：75% 機率，200% 傷害

冷卻：14 秒
```

每級變動：
  - 第 3 行：30 / 45 / 60 / 75 / 90
  - 第 4 行：50 / 75 / 100 / 125 / 150

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acdn = 14.0`, `alev = 5`, `amcs = [100, 115, 130, 145, 160]`, `aran = 800.0`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`HeroE25_Dmg`　war3map.j:54172
```jass
if count==1 then
call DestroyEffect(AddSpecialEffect("war3mapImported\\NewDirtEXNofire.mdx",x,y))
set dmg=30+30*I2R(GetUnitAbilityLevel(hero,'A03F'))+udg_ItemBonusDMG[n]*0.25
call GroupEnumUnitsInRange(ug,x,y,240,null)
set check=1
else
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Other\\Incinerate\\FireLordDeathExplode.mdl",x,y))
set dmg=15+15*I2R(GetUnitAbilityLevel(hero,'A03F'))+udg_ItemBonusDMG[n]*0.12
call GroupEnumUnitsInRange(ug,x,y,160,null)
endif
```

`Trig_HeroSkills25_Actions`　war3map.j:54302
```jass
elseif Skill=='A03F' then
set x=GetUnitX(u)
set y=GetUnitY(u)
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set t=CreateTimer()
set Id=GetHandleId(t)
set x2=bj_RADTODEG*Atan2(y2-y,x2-x)
call SaveReal(hash,Id,3,x2)
set x=x+50*Cos(x2*bj_DEGTORAD)
set y=y+50*Sin(x2*bj_DEGTORAD)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,10)
call TimerStart(t,0.08,true,function HeroE25_Dmg)
```

## 火柱 `AHfs`　—　吃技能強度

俄文原名：Огненный столб

```
在指定區域引發爆炸，對被波及的敵人造成傷害。爆炸會留下一灘火焰，造成較低的傷害。

爆炸傷害：45 +（20% 技能強度）點/秒
爆炸持續時間：2.6 秒
火焰傷害：10 +（5% 技能強度）點/秒
火焰持續時間：8 秒

冷卻：13 秒
```

每級變動：
  - 第 3 行：45 / 70 / 95 / 120 / 145
  - 第 5 行：10 / 15 / 20 / 25 / 30

物件欄位（原型 `None`）：`Hfs1 = 0.009999999776482582`, `Hfs2 = 20.0`, `Hfs3 = 0.009999999776482582`, `Hfs4 = 20.0`, `Hfs6 = 0.009999999776482582`, `aare = 225.0`, `acas = 0.0`, `acdn = 13.0`, `adur = 11.0`, `alev = 5`, `amcs = [115, None, 155, 175, 195]`, `atar = enemies`

實作：

`HeroQ25_Start`　war3map.j:54125
```jass
if count>8 then
set dmg=(20+25*I2R(GetUnitAbilityLevel(hero,'AHfs'))+udg_ItemBonusDMG[n]*0.20)*0.33
else
set dmg=5+5*I2R(GetUnitAbilityLevel(hero,'AHfs'))+udg_ItemBonusDMG[n]*0.05
endif
```

`Trig_HeroSkills25_Actions`　war3map.j:54280
```jass
if Skill=='AHfs' then
set x=GetSpellTargetX()
set y=GetSpellTargetY()
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,16)
call TimerStart(t,0.33,true,function HeroQ25_Start)
```

## 烈焰洪流 `A02J`　—　吃技能強度

俄文原名：Огненный поток

```
向指定敵人發射一道火焰投射物洪流。每一發投射物在命中時造成傷害，並有少許機率點燃敵人。

投射物傷害：12 +（3% 技能強度）點
投射物的點燃效果：50% 機率，100% 傷害
投射物數量：20 發

冷卻：20 秒
```

每級變動：
  - 第 3 行：12 / 18 / 24 / 30 / 36
  - 第 5 行：20 / 25 / 30 / 35 / 40

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = charm`, `acap = `, `acdn = 20.0`, `alev = 5`, `amcs = [100, 125, 150, 175, 200]`, `aran = 800.0`, `atar = ground,enemy,neutral,organic,air`

實作：

`FireTorrent`　war3map.j:54209
```jass
function FireTorrent takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2=LoadUnitHandle(hash,Id,2)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real angle
local real dist
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2=GetUnitX(u2)
local real y2=GetUnitY(u2)
local real dmg=6.+6.*I2R(GetUnitAbilityLevel(u,'A02J'))+udg_ItemBonusDMG[n]*0.03
local integer count=LoadInteger(hash,Id,1)
set angle=AngleXY(x,y,x2,y2)
if GetUnitAbilityLevel(u,'A03H')==1 then
set angle=angle+GetRandomReal(-5.,5.)
endif
set x2=PolarX(x,30.,angle)
set y2=PolarY(y,30.,angle)
set dist=GetRandomReal(-30.,30.)
set x=PolarX(x2,dist,angle+90.)
set y=PolarY(y2,dist,angle+90.)
call CreateProjectile(u,'o023',50.,1600.,x,y,angle,dmg,50.,50.,"none","war3mapImported\\Fire Spear.mdl")
set count=count-1
if count==0 then
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SaveInteger(hash,Id,1,count)
endif
set u=null
set u2=null
set t=null
set pl=null
endfunction
```

`Trig_HeroSkills25_Actions`　war3map.j:54290
```jass
elseif Skill=='A02J' then
set u3=GetSpellTargetUnit()
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u3)
set count=15+5*GetUnitAbilityLevel(u,Skill)
if GetUnitAbilityLevel(u,'A03H')==1 then
set count=count*2
endif
call SaveInteger(hash,Id,1,count)
call TimerStart(t,0.04,true,function FireTorrent)
```

## 烈焰旋風 `A03O`　—　吃技能強度

俄文原名：Огненный вихрь

```
在指定位置生成一個無規則移動的火焰旋風。旋風會朝周圍區域射出火焰彈，造成小範圍傷害。此外旋風也會對自身附近的敵人造成額外傷害。旋風與火焰彈都可能點燃敵人。

旋風傷害：30 + （15% 技能強度）點/秒
火焰彈傷害：60 + （30% 技能強度）點
旋風與火焰彈的點燃效果：60% 機率，250% 傷害
技能持續時間：12 秒

冷卻：90 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = 0.800000011920929`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 0.800000011920929`, `Ncl5 = 0`, `Ncl6 = coldarrowstarg`, `acap = `, `acdn = 90.0`, `alev = 1`, `amcs = 300`, `aran = 800.0`

呼叫共用引擎函式：`BurnUnit` —— 完整內容見 `_engine.md`。

實作：

`Trig_HeroSkill25R_Conditions`　war3map.j:54348
```jass
function Trig_HeroSkill25R_Conditions takes nothing returns boolean
return GetSpellAbilityId()=='A03O'
endfunction
```

`Trig_HeroSkill25R_Actions`　war3map.j:54509
```jass
function Trig_HeroSkill25R_Actions takes nothing returns nothing
local unit u=GetTriggerUnit()
local real x=GetSpellTargetX()
local real y=GetSpellTargetY()
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,CreateUnit(GetOwningPlayer(u),'o02S',x,y,0))
call SaveInteger(hash,Id,4,40)
call SaveInteger(hash,Id,5,1)
call SaveInteger(hash,Id,1,1)
call TimerStart(t,0.30,true,function FlamingTwister_Create)
set t=null
set u=null
endfunction
```

`Trig_HeroSkill25R_Conditions`　war3map.j:54348
```jass
function Trig_HeroSkill25R_Conditions takes nothing returns boolean
return GetSpellAbilityId()=='A03O'
endfunction
function FlamingTwister_Move_2 takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local real ugol=LoadReal(hash,Id,4)
local unit dummy=LoadUnitHandle(hash,Id,4)
local real x=GetUnitX(dummy)
local real y=GetUnitY(dummy)
local real x1=LoadReal(hash,Id,2)
local real y1=LoadReal(hash,Id,3)
local group g
local unit GE
local real uron
if DistanceNative(x,y,x1,y1)>45 then
set x=PolarX(x,30,ugol)
set y=PolarY(y,30,ugol)
call SetUnitFacing(dummy,ugol)
call SetUnitX(dummy,x)
call SetUnitY(dummy,y)
else
set g=CreateGroup()
call GroupEnumUnitsInRange(g,x1,y1,160,null)
set uron=60+udg_ItemBonusDMG[n]*0.30
loop
set GE=FirstOfGroup(g)
exitwhen GE==null
if UnitAlive(GE)and IsUnitEnemy(GE,GetOwningPlayer(u))then
call UnitDamageTarget(u,GE,uron,true,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call BurnUnit(u,GE,uron*2.50,0.60)
endif
call GroupRemoveUnit(g,GE)
endloop
call DestroyGroup(g)
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Other\\Incinerate\\FireLordDeathExplode.mdl",x1,y1))
call RemoveUnit(dummy)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
endif
set GE=null
set g=null
set dummy=null
set pl=null
set t=null
set u=null
endfunction
function FlamingTwister_Move takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2=LoadUnitHandle(hash,Id,2)
local unit dummy=LoadUnitHandle(hash,Id,4)
local integer j=LoadInteger(hash,Id,5)
local integer kol=LoadInteger(hash,Id,6)
local real x1=GetUnitX(u2)
local real y1=GetUnitY(u2)
local timer t1
local integer h1
local real ugol
local real ugolGT=LoadReal(hash,Id,6)
local real dist
if kol>0 then
set ugol=GetUnitFacing(dummy)
set x1=x1+100*Cos((ugolGT-j*90)*bj_DEGTORAD)
set y1=y1+100*Sin((ugolGT-j*90)*bj_DEGTORAD)
set x1=x1+100*Cos((ugol+j*6-j*90)*bj_DEGTORAD)
set y1=y1+100*Sin((ugol+j*6-j*90)*bj_DEGTORAD)
call SetUnitX(dummy,x1)
call SetUnitY(dummy,y1)
call SetUnitFacing(dummy,ugol+j*6)
call SaveInteger(hash,Id,6,kol-1)
call SaveReal(hash,Id,6,ugolGT+5.)
else
set t1=CreateTimer()
set h1=GetHandleId(t1)
call SaveUnitHandle(hash,h1,1,u)
set dist=GetRandomReal(215,450)
set x1=GetUnitX(dummy)
set y1=GetUnitY(dummy)
set x1=PolarX(x1,dist,ugolGT)
set y1=PolarY(y1,dist,ugolGT)
call SaveReal(hash,h1,2,x1)
call SaveReal(hash,h1,3,y1)
call SaveReal(hash,h1,4,ugolGT)
call SaveUnitHandle(hash,h1,4,dummy)
call TimerStart(t1,0.03,true,function FlamingTwister_Move_2)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
endif
set t=null
set dummy=null
set u=null
set u2=null
set t1=null
endfunction
function FlamingTwister_Create takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local unit u2=LoadUnitHandle(hash,Id,2)
local integer kol=LoadInteger(hash,Id,4)
local timer t2
local integer Id_2
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local real angle=GetRandomReal(0,360)
local real dmg
local group ug
local unit u3
if kol>0 then
set bj_lastCreatedUnit=CreateUnit(pl,'h042',x,y,angle)
set t2=CreateTimer()
set Id_2=GetHandleId(t2)
call SaveUnitHandle(hash,Id_2,1,u)
call SaveUnitHandle(hash,Id_2,2,u2)
call SaveUnitHandle(hash,Id_2,4,bj_lastCreatedUnit)
call SaveInteger(hash,Id_2,5,LoadInteger(hash,Id,5))
call SaveInteger(hash,Id_2,6,40)
call SaveReal(hash,Id_2,6,GetRandomReal(0,360))
call TimerStart(t2,0.03,true,function FlamingTwister_Move)
call SaveInteger(hash,Id,5,-1*LoadInteger(hash,Id,5))
call SaveInteger(hash,Id,4,kol-1)
set dmg=(30+udg_ItemBonusDMG[n]*0.15)*0.30
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,200.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call BurnUnit(u,u3,dmg*2.50,0.60)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
if LoadInteger(hash,Id,1)==1 then
call KnockBackUnit2(u2,GetRandomReal(75,150),0.6,GetRandomReal(0,360),0.03)
call SaveInteger(hash,Id,1,0)
else
call SaveInteger(hash,Id,1,1)
endif
else
call KillUnit(u2)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
endif
set t2=null
set t=null
set u=null
set ug=null
set pl=null
set u3=null
set u2=null
endfunction
function Trig_HeroSkill25R_Actions takes nothing returns nothing
local unit u=GetTriggerUnit()
local real x=GetSpellTargetX()
local real y=GetSpellTargetY()
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,CreateUnit(GetOwningPlayer(u),'o02S',x,y,0))
call SaveInteger(hash,Id,4,40)
call SaveInteger(hash,Id,5,1)
call SaveInteger(hash,Id,1,1)
call TimerStart(t,0.30,true,function FlamingTwister_Create)
set t=null
set u=null
endfunction
```

## 熔面者 `A031`

俄文原名：Лицеплав

```
對敵人造成傷害並施加易燃效果。

傷害：（200% int）點
易燃：120% 機率

冷卻：15 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = 0.5`, `Ncl2 = 2`, `Ncl3 = 3`, `Ncl4 = 0.5`, `Ncl5 = 0`, `Ncl6 = cloudoffog`, `aare = 180.0`, `acap = `, `acdn = 15.0`, `aher = 0`, `alev = 1`, `amcs = 75`, `aran = 700.0`, `atar = hero,friend,self`

呼叫共用引擎函式：`FlammabilityUnit` —— 完整內容見 `_engine.md`。

實作：

`Trig_HeroSkills25_Actions`　war3map.j:54318
```jass
elseif Skill=='A031' then
set x=GetSpellTargetX()
set y=GetSpellTargetY()
call DestroyEffect(AddSpecialEffect("war3mapImported\\Conflagrate.mdl",x,y))
set dmg=I2R(GetHeroInt(u,true))*2.0
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,185.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
if UnitAlive(u3)then
call FlammabilityUnit(u,u3,1.20)
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
```

## 選擇天賦 `A02L`

俄文原名：Выбрать талант

```
當玩家經驗點數足夠時，你可以選擇一項天賦，將英雄大幅強化至新的力量位階。
```

**天賦選項**：
  - `A03G` 火焰浪潮
    強度等級：T3 屬性加成／每級屬性成長加成： +1 / +0 +0 / +0 +3 / +1  「烈焰洪流」發射的投射物數量增加 100%，但會有些微散射。
  - `A03J` 人間煉獄
    強度等級：T3+ 屬性加成／每級屬性成長加成： +3 / +1 +2 / +0 +6 / +2  你無視敵人的點燃抗性。  點燃效果會立即造成全部傷害，而非逐漸燃燒。易燃所帶來的燃燒時間延長效果同樣會被計入。

物件欄位（原型 `Aspb`）：`aite = 0`, `spb1 = A03G,A03J`, `spb2 = 0`, `spb3 = 2`, `spb4 = 2`

實作：

`Trig_HeroSkills25_Actions`　war3map.j:54262
```jass
if Skill=='A03G' then
call SetHeroStr(u,GetHeroStr(u,false)+1,true)
call SetHeroInt(u,GetHeroInt(u,false)+3,true)
call SaveInteger(hash,GetHandleId(u),'aINT',1)
call UnitRemoveAbility(u,'A02L')
call UnitAddAbility(u,'A03H')
call SaveInteger(hash,GetHandleId(pl),15,1)
elseif Skill=='A03J' then
call SetHeroStr(u,GetHeroStr(u,false)+3,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+2,true)
call SetHeroInt(u,GetHeroInt(u,false)+6,true)
call SaveInteger(hash,GetHandleId(u),'aSTR',1)
call SaveInteger(hash,GetHandleId(u),'aINT',2)
call UnitRemoveAbility(u,'A02L')
call UnitAddAbility(u,'A03M')
call SaveInteger(hash,GetHandleId(u),'A03M',1)
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

## 火焰浪潮 `A03G`　—　來自天賦「選擇天賦」

俄文原名：Волны огня

```
強度等級：T3
屬性加成／每級屬性成長加成：
+1 / +0
+0 / +0
+3 / +1

「烈焰洪流」發射的投射物數量增加 100%，但會有些微散射。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [0.5, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['acidbomb', 'channel']`, `acap = `, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `arqa = 24`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills25_Actions`　war3map.j:54262
```jass
if Skill=='A03G' then
call SetHeroStr(u,GetHeroStr(u,false)+1,true)
call SetHeroInt(u,GetHeroInt(u,false)+3,true)
call SaveInteger(hash,GetHandleId(u),'aINT',1)
call UnitRemoveAbility(u,'A02L')
call UnitAddAbility(u,'A03H')
call SaveInteger(hash,GetHandleId(pl),15,1)
```

## 人間煉獄 `A03J`　—　來自天賦「選擇天賦」

俄文原名：Ад на земле

```
強度等級：T3+
屬性加成／每級屬性成長加成：
+3 / +1
+2 / +0
+6 / +2

你無視敵人的點燃抗性。

點燃效果會立即造成全部傷害，而非逐漸燃燒。易燃所帶來的燃燒時間延長效果同樣會被計入。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [0.5, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['acolyteharvest', 'channel']`, `acap = `, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `arqa = 32`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills25_Actions`　war3map.j:54269
```jass
elseif Skill=='A03J' then
call SetHeroStr(u,GetHeroStr(u,false)+3,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+2,true)
call SetHeroInt(u,GetHeroInt(u,false)+6,true)
call SaveInteger(hash,GetHandleId(u),'aSTR',1)
call SaveInteger(hash,GetHandleId(u),'aINT',2)
call UnitRemoveAbility(u,'A02L')
call UnitAddAbility(u,'A03M')
call SaveInteger(hash,GetHandleId(u),'A03M',1)
call SaveInteger(hash,GetHandleId(pl),15,1)
endif
```

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它
  - **5** — 對 0-1 級敵人傷害 +%〔攻擊者〕
  - **6** — 造成傷害 +%〔攻擊者〕；電擊會扣它 → 目標輸出下降

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
