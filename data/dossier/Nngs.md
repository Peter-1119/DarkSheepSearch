# 黑暗主教 `Nngs`（Прелат Тьмы）

主屬性 **敏捷** · 背包 **6 格** · 解鎖 500000 · 定位 刺客

| | 初始 | 每級 |
|---|---|---|
| 力量 | 19 | （未覆寫） |
| 敏捷 | 30 | 4 |
| 智力 | 24 | 2.5 |

> 近戰刺客，靠擊殺敵方英雄來增強自己的技能威力。

**縮放**：吃技能強度的技能 ['A0EQ', 'A0F4', 'Amgr'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 ['A0ER']

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且事件數越多穿透越划算。
- **召喚物** —— 召喚物**不繼承**主人的裝備觸發／狀態／傷害 +%，只吃主人技能公式裡明寫的屬性（通常是最大生命與技能強度）與原生光環。

細節見 `data/dossier/_engine.md`。


---

## 衝勁 `A0EQ`　—　吃技能強度

俄文原名：Порыв

```
向前進行一次短距離衝刺，對身旁的敵人造成傷害。傷害會造成 2 次。

傷害：60 + （25% 技能強度）點

冷卻：10 秒
```

每級變動：
  - 第 3 行：60 / 90 / 120 / 150 / 180

物件欄位（原型 `ANcl`）：`Ncl1 = 0.009999999776482582`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 0.009999999776482582`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acdn = 10.0`, `alev = 5`, `amcs = [75, 84, 93, 102, 111]`, `aran = 600.0`, `atar = air,enemies,ground,neutral,organic,item,debris`

實作：

`Hero47Q`　war3map.j:60852
```jass
function Hero47Q takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u3
local group ug
local player pl=GetOwningPlayer(u)
local integer count=LoadInteger(hash,Id,1)
local real dmg=30+30*I2R(GetUnitAbilityLevel(u,'A0EQ'))+udg_ItemBonusDMG[GetPlayerId(pl)+1]*0.20
local real x=LoadReal(hash,Id,1)
local real y=LoadReal(hash,Id,2)
local real angle=LoadReal(hash,Id,3)
local real x2
local real y2
set x2=PolarX(x,150,angle)
set y2=PolarY(y,150,angle)
call SetUnitX(u,x2)
call SetUnitY(u,y2)
call SetUnitFacing(u,angle)
call SetUnitAnimation(u,"attack")
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\NightElf\\Blink\\BlinkTarget.mdl",x2,y2))
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\Culling Slash II Red.mdx",u,"origin"))
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x2,y2,275,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
if GetUnitAbilityLevel(u,'B03H')>0 and IsUnitType(u3,UNIT_TYPE_HERO)then
call UnitDamageTarget(u,u3,dmg*(1.00+0.20+0.20*I2R(GetUnitAbilityLevel(u,'A0ER'))),false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
else
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\Stampede\\StampedeMissileDeath.mdl",u3,"origin"))
endif
call GroupRemoveUnit(ug,u3)
endloop
call SaveReal(hash,Id,1,x2)
call SaveReal(hash,Id,2,y2)
set count=count-1
call SaveInteger(hash,Id,1,count)
if count<=0 then
call PauseTimer(t)
call DestroyTimer(t)
call PauseUnit(u,false)
call SetUnitInvulnerable(u,false)
call SetUnitTimeScale(u,1.00)
call IssueImmediateOrderById(u,Order_stop)
call FlushChildHashtable(hash,Id)
else
call TimerStart(t,0.15,false,function Hero47Q)
endif
set u=null
set u3=null
set pl=null
set t=null
set ug=null
endfunction
```

`Trig_HeroSkills47_Actions`　war3map.j:60958
```jass
if Skill=='A0EQ' then
set x=GetUnitX(u)
set y=GetUnitY(u)
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set angle=AngleXY(x,y,x2,y2)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
set count=2
if LoadReal(hash,GetHandleId(u),'ST03')>=2000.00 then
set count=count+1
endif
if LoadReal(hash,GetHandleId(u),'ST03')>=8000.00 then
set count=count+1
endif
if LoadReal(hash,GetHandleId(u),'ST03')>=27000.00 then
set count=count+1
endif
if LoadReal(hash,GetHandleId(u),'ST03')>=45000.00 then
set count=count+1
endif
if LoadReal(hash,GetHandleId(u),'ST03')>=80000.00 then
set count=count+1
endif
call SaveInteger(hash,Id,1,count)
if LoadReal(hash,GetHandleId(u),'ST03')>=15000.00 then
call SaveReal(hash,GetHandleId(u),4,LoadReal(hash,GetHandleId(u),4)+0.25)
set t2=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t2),1,u)
call TimerStart(t2,5,false,function Hero47Q_Buff)
endif
call PauseUnit(u,true)
call SetUnitInvulnerable(u,true)
call SetUnitTimeScale(u,3.00)
call SaveReal(hash,Id,1,x)
call SaveReal(hash,Id,2,y)
call SaveReal(hash,Id,3,angle)
call TimerStart(t,0.01,false,function Hero47Q)
```

`Hero47Q_Buff`　war3map.j:60929
```jass
function Hero47Q_Buff takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
call SaveReal(hash,GetHandleId(u),4,LoadReal(hash,GetHandleId(u),4)-0.25)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
set t=null
set u=null
endfunction
```

## 黑暗強化 `A0ER`　—　⊕ 給裝備技能威力

俄文原名：Темное усиление

```
英雄的攻擊獲得濺射效果。同時強化「衝勁」技能，使其在「黑暗強化」啟動期間對敵方英雄造成更多傷害。

攻擊加成：對 175 點範圍造成 25% 濺射效果
「衝勁」技能對敵方英雄的傷害：+40%
持續時間：20 秒

冷卻：35 秒
```

每級變動：
  - 第 3 行：25 / 32 / 39 / 46 / 53

物件欄位（原型 `Absk`）：`abuf = B03H`, `acdn = 35.0`, `adur = 20.0`, `ahdu = 20.0`, `aher = 1`, `alev = 5`, `amcs = [100, 115, 130, 145, 160]`, `bsk1 = 0.0`, `bsk2 = 0.0`, `bsk3 = 0.0`

實作：

`Hero47Q`　war3map.j:60880
```jass
if GetUnitAbilityLevel(u,'B03H')>0 and IsUnitType(u3,UNIT_TYPE_HERO)then
call UnitDamageTarget(u,u3,dmg*(1.00+0.20+0.20*I2R(GetUnitAbilityLevel(u,'A0ER'))),false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
```

`Trig_HeroSkills47_Actions`　war3map.j:60997
```jass
elseif Skill=='A0ER' then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call UnitAddAbility(u,'A0F3')
if LoadReal(hash,GetHandleId(u),'ST03')>=60000.00 then
call SaveReal(hash,GetHandleId(u),18,LoadReal(hash,GetHandleId(u),18)+0.50)
call SaveInteger(hash,Id,2,1)
endif
if LoadReal(hash,GetHandleId(u),'ST03')>=11000.00 then
call SetUnitAbilityLevel(u,'A0F3',GetUnitAbilityLevel(u,Skill)+5)
else
call SetUnitAbilityLevel(u,'A0F3',GetUnitAbilityLevel(u,Skill))
endif
if LoadReal(hash,GetHandleId(u),'ST03')>=4000.00 then
set x=(GetUnitState((u),UNIT_STATE_MAX_LIFE))*0.01
call SaveReal(hash,Id,1,x)
call SetUnitLifeRegeneration(u,GetUnitLifeRegeneration(u)+x)
endif
call TimerStart(t,20,false,function Hero47W)
endif
```

`Hero47W`　war3map.j:60910
```jass
function Hero47W takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real x=LoadReal(hash,Id,1)
local integer L=LoadInteger(hash,Id,2)
if x>0 then
call SetUnitLifeRegeneration(u,GetUnitLifeRegeneration(u)-x)
endif
call UnitRemoveAbility(u,'A0F3')
if L==1 then
call SaveReal(hash,GetHandleId(u),18,LoadReal(hash,GetHandleId(u),18)-0.50)
endif
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
set t=null
set u=null
endfunction
```

## 受詛之刃 `Amgr`　—　吃技能強度

俄文原名：Проклятое лезвие

```
英雄的攻擊會削弱敵人，降低其造成的傷害並提高其受到的傷害。此效果可以疊加，但不會刷新持續時間。

造成傷害降低：8%
受到傷害提高：8%
持續時間：6 秒

冷卻：3.5 秒
```

每級變動：
  - 第 3 行：8 / 11 / 14 / 17 / 20
  - 第 4 行：8 / 12 / 16 / 20 / 24
  - 第 5 行：6 / 7.3 / 8.6 / 9.9 / 11.2

物件欄位（原型 `None`）：`aher = 1`, `alev = 5`

實作：

`Trig_HeroAttack47_Actions`　war3map.j:61069
```jass
if(GetUnitTypeId(u2)=='Nngs' or GetUnitTypeId(u2)=='Nplh')and GetUnitAbilityLevel(u2,'Amgr')>=1 and LoadInteger(hash,GetHandleId(u2),20)!=1 then
call SaveInteger(hash,GetHandleId(u2),20,1)
set t=CreateTimer()
set Id=GetHandleId(t)
if LoadReal(hash,GetHandleId(u2),'ST03')>=20000.00 then
call TimerStart(t,3.0,false,function HeroE47_Cd)
else
call TimerStart(t,3.5,false,function HeroE47_Cd)
endif
call SaveUnitHandle(hash,Id,1,u2)
if LoadInteger(hash,GetHandleId(u),'Nngs')==3 then
set u=null
set u2=null
set pl=null
set t=null
set t2=null
return
endif
if GetUnitAbilityLevel(u,'A0E8')==0 then
set t2=CreateTimer()
set Id=GetHandleId(t2)
set time=4.7+1.3*I2R(GetUnitAbilityLevel(u2,'Amgr'))
if LoadReal(hash,GetHandleId(u2),'ST03')>=1000.00 then
set time=time+1.5
endif
call TimerStart(t2,time,false,function HeroE47_EndDebuff)
call SaveUnitHandle(hash,Id,1,u)
call UnitAddAbility(u,'A0E8')
call SaveTimerHandle(hash,GetHandleId(u),'Nngs',t2)
set count=1
call SaveInteger(hash,GetHandleId(u),'Nngs',count)
else
set count=LoadInteger(hash,GetHandleId(u),'Nngs')+1
call SaveInteger(hash,GetHandleId(u),'Nngs',count)
set t2=LoadTimerHandle(hash,GetHandleId(u),'Nngs')
set Id=GetHandleId(t2)
endif
set f=CreateForce()
call ForceAddPlayer(f,pl)
set text=CreateTextTagUnitBJ("|cFFBF68D4X"+I2S(count)+"|r",u,0,12.00,100,100,100,0)
call ShowTextTagForceBJ(false,text,bj_FORCE_ALL_PLAYERS)
call ShowTextTagForceBJ(true,text,f)
call SetTextTagVelocityBJ(text,75.00,90.00)
call SetTextTagSuspended(text,false)
call SetTextTagPermanent(text,false)
call SetTextTagLifespan(text,3.00)
call SetTextTagFadepoint(text,2.00)
set dmg=0.05+0.03*I2R(GetUnitAbilityLevel(u2,'Amgr'))
call SaveReal(hash,GetHandleId(u),6,LoadReal(hash,GetHandleId(u),6)-dmg)
call SaveReal(hash,Id,1,LoadReal(hash,Id,1)+dmg)
set dmg=0.04+0.04*I2R(GetUnitAbilityLevel(u2,'Amgr'))
call SaveReal(hash,GetHandleId(u),4,LoadReal(hash,GetHandleId(u),4)-dmg)
call SaveReal(hash,Id,2,LoadReal(hash,Id,2)+dmg)
if LoadReal(hash,GetHandleId(u2),'ST03')>=6000.00 and count==3 then
set dmg=100+udg_ItemBonusDMG[n]*0.35
call UnitDamageTarget(u2,u,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\SoulRitual.mdx",u,"origin"))
endif
endif
```

`HeroE47_Cd`　war3map.j:61029
```jass
function HeroE47_Cd takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
call SaveInteger(hash,GetHandleId(u),20,0)
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
set t=null
set u=null
endfunction
function HeroE47_EndDebuff takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real r=LoadReal(hash,Id,1)
local real r2=LoadReal(hash,Id,2)
call SaveTimerHandle(hash,GetHandleId(u),'Nngs',null)
call SaveReal(hash,GetHandleId(u),6,LoadReal(hash,GetHandleId(u),6)+r)
call SaveReal(hash,GetHandleId(u),4,LoadReal(hash,GetHandleId(u),4)+r2)
call UnitRemoveAbility(u,'A0E8')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
set t=null
set u=null
endfunction
```

## 靈魂撕裂 `A0F4`　—　吃技能強度

俄文原名：Разрыв души

```
英雄造成的擊殺可能生成 3 團黑暗能量，擊中附近的隨機敵人。

能量團的傷害：50 + （75% 技能強度）點。
冷卻：4 秒。
```

物件欄位（原型 `Amgl`）：`aher = 1`

實作：

`HeroR47`　war3map.j:61144
```jass
function HeroR47 takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
call SaveBoolean(hash,GetHandleId(u),'A0F4',true)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
set t=null
set u=null
endfunction
```

`Trig_HeroKills47_Actions`　war3map.j:61169
```jass
if GetUnitAbilityLevel(u,'A0F4')>0 then
if LoadBoolean(hash,GetHandleId(u),'A0F4')==true then
call SaveBoolean(hash,GetHandleId(u),'A0F4',false)
set r=udg_ItemBonusDMG[n]*0.75+50
set x=GetUnitX(u)
set y=GetUnitY(u)
set u2=CreateUnit(pl,'o02N',x,y,0.00)
if LoadReal(hash,GetHandleId(u2),'ST03')>=35000.00 then
call SetUnitAbilityLevel(u2,'A0F6',2)
endif
call SaveReal(hash,GetHandleId(u2),13,r)
call SaveUnitHandle(hash,GetHandleId(u2),13,u)
call UnitApplyTimedLife(u2,'BTLF',2.5)
call IssuePointOrderById(u2,Order_attack,x,y)
set t=CreateTimer()
call TimerStart(t,4,false,function HeroR47)
call SaveUnitHandle(hash,GetHandleId(t),1,u)
endif
endif
```

## 躍進 `AIbk`

俄文原名：Скачок

```
將英雄傳送一小段距離。

冷卻：30 秒。
```

物件欄位（原型 `None`）：`aite = 0`, `amcs = 30`

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

## 額外技能 `A0FB`

俄文原名：Дополнительные умения

```
開啟英雄的額外技能列表。
```

**天賦選項**：
  - `A0F5` 黑暗信徒 [1/2]
    對敵方英雄造成傷害會給予黑暗主教一系列加成：  每累積 500 點傷害：+1 點攻擊力，+15 HP；下一次強化所需的傷害增加 10 點  1000 點傷害：「受詛之刃」的持續時間 +1.5 秒  2000 點傷害：「衝勁」的傷害段數 +1  4000 點傷害：「黑暗強化」每秒回復 1% HP  6000 點傷害：當敵人身上累積 3 層效果時，「受詛之刃」額外造成 100 +（35% 技能強度）點傷害  8000 點傷害：「衝勁」的傷害段數 +1  11000 點傷害：「黑暗強化」的濺射效果範圍 +25%
  - `A0FZ` 黑暗信徒 [2/2]
    15000 點傷害：「衝勁」在 5 秒內將受到傷害的防護提高 25%  20000 點傷害：「受詛之刃」的冷卻降低 0.5 秒  27000 點傷害：「衝勁」的傷害段數 +1  35000 點傷害：「靈魂撕裂」可命中 5 個目標  45000 點傷害：「衝勁」的傷害段數 +1  60000 點傷害：「黑暗強化」使裝備技能威力提高 50%  80000 點傷害：「衝勁」的傷害段數 +1

物件欄位（原型 `Aspb`）：`aite = 0`, `spb1 = A0F5,A0FZ`, `spb2 = 0`, `spb3 = 2`, `spb4 = 2`

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

## 黑暗信徒 [1/2] `A0F5`　—　來自天賦「額外技能」

俄文原名：Последователь Тьмы [1/2]

```
對敵方英雄造成傷害會給予黑暗主教一系列加成：

每累積 500 點傷害：+1 點攻擊力，+15 HP；下一次強化所需的傷害增加 10 點

1000 點傷害：「受詛之刃」的持續時間 +1.5 秒

2000 點傷害：「衝勁」的傷害段數 +1

4000 點傷害：「黑暗強化」每秒回復 1% HP

6000 點傷害：當敵人身上累積 3 層效果時，「受詛之刃」額外造成 100 +（35% 技能強度）點傷害

8000 點傷害：「衝勁」的傷害段數 +1

11000 點傷害：「黑暗強化」的濺射效果範圍 +25%
```

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

## 黑暗信徒 [2/2] `A0FZ`　—　來自天賦「額外技能」

俄文原名：Последователь Тьмы [2/2]

```
15000 點傷害：「衝勁」在 5 秒內將受到傷害的防護提高 25%

20000 點傷害：「受詛之刃」的冷卻降低 0.5 秒

27000 點傷害：「衝勁」的傷害段數 +1

35000 點傷害：「靈魂撕裂」可命中 5 個目標

45000 點傷害：「衝勁」的傷害段數 +1

60000 點傷害：「黑暗強化」使裝備技能威力提高 50%

80000 點傷害：「衝勁」的傷害段數 +1
```

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

---

## 這隻召喚／製造的單位

（技能程式碼裡的 `CreateUnit` 目標。數值取自 war3map.w3u，
沒列出的欄位代表地圖沒覆寫、沿用原型。）

### `o02N` Разрыв души（原型 `ocat`）
  - 骰面 1 ／ 射程 650 ／ 攻擊範圍 1000 ／ 技能 A0F6,Aloc
  - 技能 `A0F6` Мультишот　`Efk1 = 0.0`, `Efk2 = 0.0`, `Efk3 = [1, 3]`, `aare = 750.0`, `acdn = 0.0`, `adur = 0.0`, `ahdu = 0.0`, `alev = 2`, `amat = war3mapImported\BallistaArcaneMissile.mdx`, `amsp = 1000`, `atar = air,enemies,ward,structure,ground,item,debris`

---

## 皮膚

純外觀：黑暗主教（男）

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它
  - **6** — 造成傷害 +%〔攻擊者〕；電擊會扣它 → 目標輸出下降
  - **18** — 裝備技能威力〔持有者〕道具觸發用 cof = key18 + 1

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
