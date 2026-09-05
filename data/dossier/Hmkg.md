# 血騎士女族長 `Hmkg`（Матриарх рыцарей Крови）

主屬性 **力量** · 背包 **6 格** · 解鎖 500000 · 定位 戰士

| | 初始 | 每級 |
|---|---|---|
| 力量 | 22 | （未覆寫） |
| 敏捷 | 19 | 2.3 |
| 智力 | 21 | 2.3 |

> 機動性高的近戰英雄，能衝進戰場中心並承受大量傷害。

**縮放**：吃技能強度的技能 ['A01U', 'A01W', 'Absk', 'Amgl'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

---

## 猛衝 `A01U`　—　吃技能強度

俄文原名：Рывок

```
朝指定方向衝刺，碰撞時對敵人造成傷害。敵方英雄受到的傷害提高 100%。當「閃耀護盾」技能效果啟動時，碰撞會在英雄兩側產生兩道力量波，造成 75% 的傷害。

傷害：100 + （40% 技能強度）點

冷卻：10 秒
```

每級變動：
  - 第 3 行：100 / 150 / 200 / 250 / 300

物件欄位（原型 `ANcl`）：`Ncl1 = 0.20000000298023224`, `Ncl2 = 2`, `Ncl3 = 1`, `Ncl4 = 0.20000000298023224`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acdn = 10.0`, `alev = 5`, `amcs = [75, 84, 93, 102, 111]`, `aran = 700.0`, `atar = air,enemies,ground,neutral,organic,item,debris`

實作：

`Skill43Q`　war3map.j:59595
```jass
if B==true then
set n=GetPlayerId(pl)+1
set dmg=50+50*I2R(GetUnitAbilityLevel(u,'A01U'))+udg_ItemBonusDMG[n]*0.40
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,230,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
if IsUnitType(u,UNIT_TYPE_HERO)==true then
call UnitDamageTarget(u,u3,dmg*2.00,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
else
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
if LoadInteger(hash,GetHandleId(u),29)==1 then
set x2=PolarX(x,40,GetUnitFacing(u)+45)
set y2=PolarY(y,40,GetUnitFacing(u)+45)
set u3=CreateUnit(pl,'o010',x,y,GetUnitFacing(u)+45)
call SaveReal(hash,GetHandleId(u3),13,dmg*0.75)
call SaveUnitHandle(hash,GetHandleId(u3),13,u)
call UnitAddAbility(u3,'A0FW')
call IssuePointOrderById(u3,Order_carrionswarm,x2,y2)
call UnitApplyTimedLife(u3,'BTLF',2.00)
set x2=PolarX(x,40,GetUnitFacing(u)-45)
set y2=PolarY(y,40,GetUnitFacing(u)-45)
set u3=CreateUnit(pl,'o010',x,y,GetUnitFacing(u)-45)
call SaveReal(hash,GetHandleId(u3),13,dmg*0.75)
call SaveUnitHandle(hash,GetHandleId(u3),13,u)
call UnitAddAbility(u3,'A0FW')
call IssuePointOrderById(u3,Order_carrionswarm,x2,y2)
call UnitApplyTimedLife(u3,'BTLF',2.00)
endif
call PauseTimer(t)
call DestroyTimer(t)
set e=LoadEffectHandle(hash,Id,2)
call DestroyEffect(e)
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x,y))
call PauseUnit(u,false)
call SetUnitAnimation(u,"Stand")
call FlushChildHashtable(hash,Id)
set t=null
set u=null
set u3=null
set e=null
set pl=null
set ug=null
return
endif
```

`Skill43Q`　war3map.j:59649
```jass
if count==0 then
set pl=GetOwningPlayer(u)
set n=GetPlayerId(pl)+1
set dmg=50+50*I2R(GetUnitAbilityLevel(u,'A01U'))+udg_ItemBonusDMG[n]*0.40
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,230,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
if IsUnitType(u,UNIT_TYPE_HERO)==true then
call UnitDamageTarget(u,u3,dmg*2.00,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
else
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
if LoadInteger(hash,GetHandleId(u),29)==1 then
set x2=x+250*Cos((GetUnitFacing(u)+45)*bj_DEGTORAD)
set y2=y+250*Sin((GetUnitFacing(u)+45)*bj_DEGTORAD)
set u3=CreateUnit(pl,'o010',x,y,0.00)
call SaveReal(hash,GetHandleId(u3),13,dmg*0.75)
call SaveUnitHandle(hash,GetHandleId(u3),13,u)
call UnitAddAbility(u3,'A0FW')
call IssuePointOrderById(u3,Order_carrionswarm,x2,y2)
call UnitApplyTimedLife(u3,'BTLF',2.00)
set x2=x+250*Cos((GetUnitFacing(u)-45)*bj_DEGTORAD)
set y2=y+250*Sin((GetUnitFacing(u)-45)*bj_DEGTORAD)
set u3=CreateUnit(pl,'o010',x,y,0.00)
call SaveReal(hash,GetHandleId(u3),13,dmg*0.75)
call SaveUnitHandle(hash,GetHandleId(u3),13,u)
call UnitAddAbility(u3,'A0FW')
call IssuePointOrderById(u3,Order_carrionswarm,x2,y2)
call UnitApplyTimedLife(u3,'BTLF',2.00)
endif
set e=LoadEffectHandle(hash,Id,2)
call DestroyEffect(e)
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl",x,y))
call PauseUnit(u,false)
call SetUnitAnimation(u,"Stand")
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
```

`Trig_HeroSkills43_Actions`　war3map.j:59720
```jass
if Skill=='A01U' then
set x=GetUnitX(u)
set y=GetUnitY(u)
set p=GetSpellTargetLoc()
set x2=GetLocationX(p)
set y2=GetLocationY(p)
set x=bj_RADTODEG*Atan2(y2-y,x2-x)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,0.03,true,function Skill43Q)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,x)
call SaveInteger(hash,Id,2,0)
call SaveInteger(hash,Id,3,20)
set e=AddSpecialEffectTarget("war3mapImported\\Valiant Charge.mdx",u,"origin")
call SaveEffectHandle(hash,Id,2,e)
call PauseUnit(u,true)
call SetUnitAnimation(u,"Stand Defend")
```

## 反攻 `Absk`　—　吃技能強度

俄文原名：Контрнаступление

```
英雄以屏障護體，降低所受的傷害。屏障結束後，英雄附近的隨機敵人會受到傷害，英雄本身則獲得暫時的攻擊力與生命回復加成。

屏障降低所受傷害：20%
屏障持續時間：5 秒
屏障結束後造成的傷害：對英雄附近 7 名隨機敵人造成 70 + （25% 技能強度）點
屏障結束後的加成：攻擊力 +20 + （10% 技能強度），生命回復 +4 + （3% 技能強度）點
加成持續時間：8 秒

冷卻：24 秒
```

每級變動：
  - 第 3 行：20 / 28 / 36 / 44 / 52
  - 第 5 行：70 / 105 / 140 / 175 / 210
  - 第 6 行：20 + (10% сила умений) к силе атаки, +4 / 30 + (10% сила умений) к силе атаки, +6 / 40 + (10% сила умений) к силе атаки, +8 / 50 + (10% сила умений) к силе атаки, +10 / 60 + (10% сила умений) к силе атаки, +12

物件欄位（原型 `None`）：`abuf = B03I`, `acdn = 24.0`, `adur = 5.0`, `ahdu = 5.0`, `aher = 1`, `alev = 5`, `amcs = [80, 90, 100, 110, 120]`, `bsk1 = 0.0`, `bsk2 = 0.0`, `bsk3 = 0.0`

實作：

`SetUnitExtraDamage`　war3map.j:3928
```jass
function SetUnitExtraDamage takes unit u,integer a returns nothing
local integer Id=GetHandleId(u)
local integer p=14
local integer index=0
local integer r
if a>8191 then
set a=8191
endif
loop
call UnitRemoveAbility(u,setAttribute___abilityAddDamage[index])
call UnitRemoveAbility(u,setAttribute___abilityRemoveDamage[index])
exitwhen index==14
set index=index+1
endloop
if a>0 then
set r=a
loop
exitwhen r<=0
if R2I(Pow(2,p))>r then
set p=p-1
elseif R2I(Pow(2,p))<=r then
call UnitAddAbility(u,setAttribute___abilityAddDamage[p])
set r=r-R2I(Pow(2,p))
set p=p-1
endif
endloop
elseif a<0 then
set r=-a
loop
exitwhen r<=0
if R2I(Pow(2,p))>r then
set p=p-1
elseif R2I(Pow(2,p))<=r then
call UnitAddAbility(u,setAttribute___abilityRemoveDamage[p])
set r=r-R2I(Pow(2,p))
set p=p-1
endif
endloop
endif
call SaveInteger(hash,Id,34,a)
endfunction
```

`Trig_HeroTakeDamage_Actions`　war3map.j:19805
```jass
if GetUnitAbilityLevel(d,'B03I')==1 then
set DefCof=DefCof-(0.12+0.08*I2R(GetUnitAbilityLevel(d,'Absk')))
endif
```

`Skill43W2`　war3map.j:59499
```jass
function Skill43W2 takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real regen=LoadReal(hash,Id,1)
local integer atk=LoadInteger(hash,Id,1)
local effect e=LoadEffectHandle(hash,Id,2)
call SetUnitExtraDamage(u,GetUnitExtraDamage(u)-atk)
call SetUnitLifeRegeneration(u,GetUnitLifeRegeneration(u)-regen)
call DestroyEffect(e)
call FlushChildHashtable(hash,Id)
call DestroyTimer(t)
set t=null
set u=null
set e=null
endfunction
function Skill43W takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local integer lvl=GetUnitAbilityLevel(u,'Absk')
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local unit u2
local real dmg=35+35*I2R(lvl)+udg_ItemBonusDMG[n]*0.25
local real regen=2+2*I2R(lvl)+udg_ItemBonusDMG[n]*0.03
local integer atk=10+10*lvl+R2I(udg_ItemBonusDMG[n]*0.10)
local effect e
set u2=CreateUnit(pl,'o02K',x,y,0)
call SaveReal(hash,GetHandleId(u2),13,dmg)
call SaveUnitHandle(hash,GetHandleId(u2),13,u)
call UnitApplyTimedLife(u2,'BTLF',1.5)
call IssuePointOrderById(u2,Order_attack,x,y)
call SaveReal(hash,GetHandleId(u),4,LoadReal(hash,GetHandleId(u),4)-LoadReal(hash,Id,1))
call FlushChildHashtable(hash,Id)
call DestroyTimer(t)
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,8,false,function Skill43W2)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,regen)
call SaveInteger(hash,Id,1,atk)
set e=AddSpecialEffectTarget("war3mapImported\\Ember Sword FX 5.mdx",u,"weapon")
call SaveEffectHandle(hash,Id,2,e)
call SetUnitExtraDamage(u,GetUnitExtraDamage(u)+atk)
call SetUnitLifeRegeneration(u,GetUnitLifeRegeneration(u)+regen)
set t=null
set u=null
set u2=null
set pl=null
set e=null
endfunction
```

`Trig_HeroSkills43_Actions`　war3map.j:59738
```jass
elseif Skill=='Absk' then
set t=CreateTimer()
set Id=GetHandleId(t)
call TimerStart(t,5,false,function Skill43W)
call SaveUnitHandle(hash,Id,1,u)
set dmg=0.12+0.08*I2R(GetUnitAbilityLevel(u,Skill))
call SaveReal(hash,GetHandleId(u),4,LoadReal(hash,GetHandleId(u),4)+dmg)
call SaveReal(hash,Id,1,dmg)
```

## 閃耀護盾 `Amgl`　—　吃技能強度

俄文原名：Искрящийся щит

```
當英雄受到攻擊時，護盾會充滿灼熱之光，週期性對附近的敵人造成傷害。

傷害：16 + （5% 技能強度）點/秒
效果持續時間：10 秒

效果冷卻：效果結束後 10 秒
```

每級變動：
  - 第 3 行：16 / 24 / 32 / 40 / 48

物件欄位（原型 `None`）：`achd = 0`, `aher = 1`, `alev = 5`

實作：

`Hero43E2`　war3map.j:59766
```jass
function Hero43E2 takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
call SaveInteger(hash,GetHandleId(u),28,0)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
set t=null
set u=null
endfunction
function Hero43E takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local integer count=LoadInteger(hash,Id,1)
local group ug
local unit u3
local real dmg=8+8*I2R(GetUnitAbilityLevel(u,'Amgl'))+udg_ItemBonusDMG[n]*0.05
local effect e
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,215,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
endif
call GroupRemoveUnit(ug,u3)
endloop
set count=count-1
call SaveInteger(hash,Id,1,count)
if count==0 then
call SaveInteger(hash,GetHandleId(u),29,0)
set e=LoadEffectHandle(hash,Id,2)
call DestroyEffect(e)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call TimerStart(t,10,false,function Hero43E2)
endif
set t=null
set u=null
set u3=null
set ug=null
set pl=null
set e=null
endfunction
```

`Trig_HeroAttack43_Actions`　war3map.j:59831
```jass
if GetUnitAbilityLevel(u,'Amgl')>0 then
if LoadInteger(hash,GetHandleId(u),28)!=1 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,1,10)
call TimerStart(t,1,true,function Hero43E)
call SaveInteger(hash,GetHandleId(u),28,1)
call SaveInteger(hash,GetHandleId(u),29,1)
set e=AddSpecialEffectTarget("war3mapImported\\Ember Shield II FX 5.mdx",u,"hand, right")
call SaveEffectHandle(hash,Id,2,e)
endif
endif
```

## 向聖光祈願 `A01W`　—　吃技能強度

俄文原名：Обращение к Свету

```
英雄對受到「灼燒印記」影響的敵人造成更多傷害，並在攻擊時有機率引爆敵人身上的印記，觸發生命回復效果並造成範圍傷害。此外，技能持續期間會提高對敵人附加印記的機率。

對帶有印記的敵人造成額外傷害：+25%
攻擊時引爆印記的機率：33%
引爆傷害：50 + （25% 技能強度）點
附加印記機率提升：10% > 25%
技能持續時間：22 秒

冷卻：
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, None, 1.0]`, `Ncl3 = [1, None]`, `Ncl4 = [0.5, None, 1.0]`, `Ncl5 = [0, None]`, `Ncl6 = ['spies', None, 'channel']`, `acdn = [100.0, None, 30.0]`, `alev = 1`, `amcs = [185, None, 70, 80, 90, 100, 110]`, `aran = [800.0, None]`, `atar = ['air,ground,debris,enemy,neutral,organic', None]`

實作：

`RemoveBuff`　war3map.j:2875
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

`Trig_HeroSkills43_Actions`　war3map.j:59746
```jass
elseif Skill=='A01W' then
call UnitAddAbility(u,'A01Y')
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveInteger(hash,Id,2,'A01Y')
call TimerStart(t,22,true,function RemoveBuff)
endif
```

## 灼燒印記 `A01V`

俄文原名：Опаляющая метка

```
攻擊英雄的敵人有 10% 機率獲得灼燒印記效果，持續 8 秒。此效果會提高該敵人受到英雄傷害的量。若敵人在印記效果下死亡，英雄會回復生命值。

敵人受到英雄的傷害提高：+25%
帶印記的敵人死亡時回復生命值：（65% 力量）點
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

## 這隻召喚／製造的單位

（技能程式碼裡的 `CreateUnit` 目標。數值取自 war3map.w3u，
沒列出的欄位代表地圖沒覆寫、沿用原型。）

### `o02K` Контрнаступление（原型 `ocat`）
  - 骰面 1 ／ 射程 750 ／ 攻擊範圍 1200 ／ 技能 A01T,Aloc
  - 技能 `A01T` Мультишот　`Efk1 = 0.0`, `Efk2 = 0.0`, `Efk3 = 5`, `aare = 850.0`, `acdn = 0.0`, `adur = 0.0`, `ahdu = 0.0`, `amac = 0.05000000074505806`, `amat = war3mapImported\Shot II Orange.mdx`, `amsp = 1200`, `atar = air,enemies,ward,structure,ground,item,debris`

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它
  - **28** — 實數＝冰凍傷害 +%〔施加者〕／整數＝抵抗冰凍旗標〔受害者〕
  - **29** — 實數＝流血傷害 +%〔施加者〕／整數＝抵抗流血旗標〔受害者〕（加成寫錯變數，實際無效 —— 見 地圖問題回報 A-4）

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
