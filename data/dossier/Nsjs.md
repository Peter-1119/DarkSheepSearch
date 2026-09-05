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
- **技能直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且傷害事件數越多，穿透越划算。
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

呼叫共用引擎函式：`BurnUnit` —— 完整內容見 `_engine.md`。

實作：

`Trig_HeroSkills55_Actions`　war3map.j:64501
```jass
if Skill=='A0XO' then
set x2=GetSpellTargetX()
set y2=GetSpellTargetY()
set angle=AngleXY(x,y,x2,y2)
set u3=CreateUnit(pl,'o00J',x,y,angle)
call SetUnitX(u3,x)
call SetUnitY(u3,y)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u3)
call SaveReal(hash,Id,1,x2)
call SaveReal(hash,Id,2,y2)
call SaveReal(hash,Id,3,angle)
call SaveInteger(hash,Id,1,lvl)
call SaveReal(hash,Id,4,235.)
call TimerStart(t,0.03,true,function HeroQ55_Dmg)
```

`RemoveDummy`　war3map.j:2746
```jass
function RemoveDummy takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call RemoveUnit(u)
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set u=null
set t=null
endfunction
function StunUnit takes unit attacker,unit target,integer seconds,real chanse returns nothing
local integer random
local integer chanse_random
local unit u
local player pl=GetOwningPlayer(attacker)
local timer t=CreateTimer()
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random and IsUnitEnemy(target,pl)and UnitAlive(target)then
set u=CreateUnit(pl,'o010',GetUnitX(target),GetUnitY(target),0.)
call UnitAddAbility(u,'A0Y8')
call SetUnitAbilityLevel(u,'A0Y8',seconds)
call IssueTargetOrder(u,"creepthunderbolt",target)
call SaveUnitHandle(hash,GetHandleId(t),1,u)
call TimerStart(t,2.,false,function RemoveDummy)
endif
set u=null
set pl=null
set t=null
endfunction
```

`HeroQ55_Dmg`　war3map.j:64379
```jass
function HeroQ55_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local unit u3=LoadUnitHandle(hash,Id,2)
local real x=GetUnitX(u3)
local real y=GetUnitY(u3)
local real x2=LoadReal(hash,Id,1)
local real y2=LoadReal(hash,Id,2)
local real angle=LoadReal(hash,Id,3)
local group ug
local integer lvl=LoadInteger(hash,Id,1)
local real dmg=40+40*I2R(lvl)+udg_ItemBonusDMG[n]*0.30
local real aoe=LoadReal(hash,Id,4)
set x=PolarX(x,45.,angle)
set y=PolarY(y,45.,angle)
if DistanceNative(x,y,x2,y2)<=22.5 then
call SetUnitX(u3,x2)
call SetUnitY(u3,y2)
call KillUnit(u3)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
if UnitAlive(u3)then
call BurnUnit(u,u3,dmg,0.50)
if IsUnitType(u3,UNIT_TYPE_HERO)then
call StunUnit(u,u3,2,1.00)
else
call StunUnit(u,u3,3,1.00)
endif
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
else
call SetUnitX(u3,x)
call SetUnitY(u3,y)
endif
set t=null
set u=null
set pl=null
set u3=null
set ug=null
endfunction
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

## 燃燒砲塔 `A0XT`

俄文原名：Поджигающие турели

```
砲塔的投射物有機率點燃敵人。

點燃（砲塔投射物）：40% 機率；傷害等於英雄力量的 60%
```

每級變動：
  - 第 3 行：40% шанс; урон равен 60 / 45% шанс; урон равен 70 / 50% шанс; урон равен 80 / 55% шанс; урон равен 90 / 60% шанс; урон равен 100

物件欄位（原型 `Amgl`）：`aher = 1`, `alev = 5`

呼叫共用引擎函式：`BurnUnit` —— 完整內容見 `_engine.md`。

實作：

`ProjectileMove`　war3map.j:2999
```jass
elseif u2_Id=='o02C' then
set i=GetUnitAbilityLevel(u,'A0XT')
if i !=0 then
call BurnUnit(u,u3,I2R(GetHeroStr(u,true))*(0.50+0.10*I2R(i)),0.35+0.05*I2R(i))
endif
endif
```

`ProjectileMove`　war3map.j:3044
```jass
elseif u2_Id=='o02C' then
set i=GetUnitAbilityLevel(u,'A0XT')
if i !=0 then
call BurnUnit(u,u3,I2R(GetHeroStr(u,true))*(0.50+0.10*I2R(i)),0.35+0.05*I2R(i))
endif
endif
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

## 以「單位型號」內聯的實作

這幾段不是靠技能 ID 分派的，而是直接用單位型號 `Nsjs` 寫在共用函式的條件式裡
（常見於寫進傷害管線的被動）。照技能抽取抓不到，所以單獨列出來。

`ResHero`　war3map.j:46352
```jass
if GetUnitTypeId(u)=='Nsjs' then
set unit_global=u
call TriggerExecute(gg_trg_HeroTurretsActivate55)
endif
```

`Trig_DieHero_Actions`　war3map.j:46568
```jass
if GetUnitTypeId(u)=='Nsjs' then
call PauseTimer(LoadTimerHandle(hash,GetHandleId(u),'TUR1'))
call PauseTimer(LoadTimerHandle(hash,GetHandleId(u),'TUR2'))
endif
```

---

## 同一組的其他實作函式

英雄的實作散在同編號的一組函式裡，上面按技能抽取時抓不到的補在這裡
（常見的是決定門檻、結算加成、清理 buff 的那幾支）。

`Trig_HeroTurretsActivate55_Actions`　war3map.j:64600
```jass
function Trig_HeroTurretsActivate55_Actions takes nothing returns nothing
local unit u=unit_global
local timer t
local integer Id
set t=LoadTimerHandle(hash,GetHandleId(u),'TUR1')
if t !=null then
set Id=GetHandleId(t)
call PauseTimer(t)
call FlushChildHashtable(hash,Id)
call DestroyTimer(t)
endif
set t=LoadTimerHandle(hash,GetHandleId(u),'TUR2')
if t !=null then
set Id=GetHandleId(t)
call PauseTimer(t)
call FlushChildHashtable(hash,Id)
call DestroyTimer(t)
endif
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,45.)
call TimerStart(t,GetRandomReal(1.,2.),false,function Turret55)
call SaveTimerHandle(hash,GetHandleId(u),'TUR1',t)
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveReal(hash,Id,1,-45.)
call TimerStart(t,GetRandomReal(1.,2.),false,function Turret55)
call SaveTimerHandle(hash,GetHandleId(u),'TUR2',t)
set t=null
set u=null
endfunction
```

`Trig_HeroKills55_Conditions`　war3map.j:64637
```jass
function Trig_HeroKills55_Conditions takes nothing returns boolean
return GetUnitTypeId(GetKillingUnit())=='Nsjs'
endfunction
```

`Trig_HeroKills55_Actions`　war3map.j:64640
```jass
function Trig_HeroKills55_Actions takes nothing returns nothing
local unit u=GetKillingUnit()
local integer u_Id=GetHandleId(u)
local unit u2=GetDyingUnit()
local player pl=GetOwningPlayer(u)
local integer count
if IsUnitEnemy(u2,pl)then
set count=LoadInteger(hash,u_Id,'TAL1')+1
if count==100 then
set count=0
call SaveReal(hash,u_Id,27,LoadReal(hash,u_Id,27)+0.05)
endif
call SaveInteger(hash,u_Id,'TAL1',count)
endif
set u=null
set u2=null
set pl=null
endfunction
```

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
