# 惡魔獵手 `Edem`（Охотник на демонов）

主屬性 **敏捷** · 背包 **6 格** · 解鎖 0 · 定位 刺客

| | 初始 | 每級 |
|---|---|---|
| 力量 | （未覆寫） | 2 |
| 敏捷 | （未覆寫） | 2.4 |
| 智力 | （未覆寫） | 1.5 |

> 容易上手的近戰刺客。

**縮放**：吃技能強度的技能 ['A04X'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 ['A04T']

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **狀態** —— 走 `Burn_Dmg` 那條，**外面包了 DisableTrigger** → 不吃 DefCof、不帶穿透、被狀態抗性擋。該買的是「狀態傷害 +%」「易燃」「機率倍率」。
- **直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且事件數越多穿透越划算。
- **治療／增益** —— 直接寫數值，不經傷害事件 —— 全地圖沒有「治療加成」這種屬性，只能靠技能公式裡的係數（多半是技能強度）。

細節見 `data/dossier/_engine.md`。


---

## 燃燒之刃 `A04X`　—　吃技能強度

俄文原名：Горящие клинки

```
獲得強化，期間攻擊會造成額外的範圍傷害，並有小機率點燃敵人。

範圍傷害：20 +（8% 技能強度）點
點燃效果：20% 機率，60% 傷害
持續時間：12 秒

冷卻：20 秒
```

每級變動：
  - 第 3 行：20 / 30 / 40 / 50 / 60
  - 第 4 行：60 / 70 / 80 / 90 / 100

物件欄位（原型 `Absk`）：`abuf = B00C`, `acdn = 20.0`, `adur = [None, 12.0]`, `ahdu = [None, 12.0]`, `aher = 1`, `alev = 5`, `amcs = [80, 88, 96, 104, 112]`, `bsk1 = 0.0`, `bsk2 = 0.0`, `bsk3 = 0.0`

呼叫共用引擎函式：`BleedUnit`, `BurnUnit`, `VulnerabilityUnit` —— 完整內容見 `_engine.md`。

實作：

`Trig_HeroQ1_Actions`　war3map.j:46678
```jass
function Trig_HeroQ1_Actions takes nothing returns nothing
local unit u=GetAttacker()
local unit u3
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local integer L
local real dmg=10+(10*I2R(GetUnitAbilityLevel(u,'A04X')))+(udg_ItemBonusDMG[n]*0.08)
local real dmg_cof=0.50+0.10*I2R(GetUnitAbilityLevel(u,'A04X'))
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local group ug
local integer u_Id=GetHandleId(u)
local real aoe=225.+LoadReal(hash,u_Id,'A0RY')
if GetUnitTypeId(u)=='Eevi' then
set L=GetRandomInt(1,100)
if L<=20 then
set dmg=I2R(GetHeroAgi(u,true))
call DestroyEffect(AddSpecialEffect("Culling Slash Silver.mdx",x,y))
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,250.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call BleedUnit(u,u3,dmg,1.00)
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
endif
if LoadInteger(hash,u_Id,'B00C')!=1 then
if GetUnitAbilityLevel(u,'A0YH')==1 then
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\Stampede\\StampedeMissileDeath.mdl",u3,"chest"))
call VulnerabilityUnit(u,u3,0.30)
if GetUnitAbilityLevel(u,'A0RY')!=1 then
call BurnUnit(u,u3,dmg*dmg_cof,0.20)
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
else
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\Stampede\\StampedeMissileDeath.mdl",u3,"chest"))
if GetUnitAbilityLevel(u,'A0RY')!=1 then
call BurnUnit(u,u3,dmg*dmg_cof,0.20)
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
call StartCooldown(u_Id,'B00C',0.25)
endif
set u=null
set u3=null
set pl=null
set ug=null
endfunction
```

## 致命一擊 `A04V`

俄文原名：Смертельный удар

```
英雄的攻擊有機率造成提高的傷害。

機率：20%
傷害：150%
```

每級變動：
  - 第 4 行：150 / 200 / 250 / 300 / 350

物件欄位（原型 `AOcr`）：`Ocr1 = 20.0`, `Ocr2 = [1.5, 2.0, 2.5, 3.0, 3.5]`, `alev = 5`

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

## 著魔 `A04T`　—　⊕ 給裝備技能威力

俄文原名：Одержимость

```
英雄暫時獲得敏捷加成與強力的魔法抗性。

敏捷加成：+100%
魔法抗性：70%
持續時間：20 秒

冷卻：80 秒
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, None, 1.0]`, `Ncl3 = [1, None]`, `Ncl4 = [0.5, None, 1.0]`, `Ncl5 = [0, None]`, `Ncl6 = [None, 'channel']`, `acdn = [80.0, None, 30.0]`, `alev = 1`, `amcs = [115, None, 70, 80, 90, 100, 110]`, `aran = [800.0, None]`, `atar = ['air,ground,debris,enemy,neutral,organic', None]`

實作：

`Trig_HeroSkills1_Actions`　war3map.j:46652
```jass
if Skill=='A04T' then
set i=GetHeroAgi(u,false)
call SetHeroAgi(u,i+i,true)
call SaveInteger(hash,Id,1,i)
call SetUnitVertexColor(u,125,125,125,125)
call UnitAddAbility(u,'A03B')
call UnitAddAbility(u,'A04U')
if GetUnitAbilityLevel(u,'A0YH')==1 then
call SaveReal(hash,GetHandleId(u),1,LoadReal(hash,GetHandleId(u),1)-0.20)
call SaveReal(hash,GetHandleId(u),18,LoadReal(hash,GetHandleId(u),18)+0.40)
call SetUnitAbilityLevel(u,'A0S1',2)
endif
call TimerStart(t,20,true,function HeroR1_EndBuff)
call SaveUnitHandle(hash,Id,1,u)
endif
```

`HeroR1_EndBuff`　war3map.j:46604
```jass
function HeroR1_EndBuff takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local integer bonus=LoadInteger(hash,Id,1)
local real r
call SetHeroAgi(u,GetHeroAgi(u,false)-bonus,true)
call SetUnitVertexColor(u,255,255,255,255)
call UnitRemoveAbility(u,'A03B')
call UnitRemoveAbility(u,'A04U')
if GetUnitAbilityLevel(u,'A0YH')==1 then
call SaveReal(hash,GetHandleId(u),1,LoadReal(hash,GetHandleId(u),1)+0.20)
call SaveReal(hash,GetHandleId(u),18,LoadReal(hash,GetHandleId(u),18)-0.40)
call SetUnitAbilityLevel(u,'A0S1',1)
endif
call FlushChildHashtable(hash,Id)
call DestroyTimer(t)
set t=null
set u=null
endfunction
```

## 幻象 `A04O`

俄文原名：Иллюзия

```
英雄創造 2 個幻象分身。

分身造成傷害：30%
分身受到傷害：180%
持續時間：30 秒

冷卻：30 秒
```

每級變動：
  - 第 3 行：30 / 40 / 50 / 60 / 70
  - 第 4 行：180 / 170 / 160 / 150 / 140

物件欄位（原型 `AOmi`）：`Omi1 = [2, None]`, `Omi2 = [0.5, 0.6000000238418579, 0.7000000476837158, 0.8000000715255737, 0.9000000953674316]`, `Omi3 = [1.7999999523162842, 1.7000000476837158, 1.600000023841858, 1.5, 1.399999976158142]`, `acdn = 30.0`, `adur = 30.0`, `ahdu = 30.0`, `alev = 5`, `amat = Abilities\Weapons\SpiritOfVengeanceMissile\SpiritOfVengeanceMissile.mdl`, `amcs = [90, 100, 110, 120, 130]`, `asat = Abilities\Spells\NightElf\Blink\BlinkCaster.mdl`

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

## 貪得無厭 `A04W`

俄文原名：Ненасытность

```
每次擊殺會為英雄回復 1% 的已失去生命值。
```

*（JASS 裡沒有對應實作 —— 這是原生技能，效果看上面的物件欄位）*

## 選擇天賦 `A0RV`

俄文原名：Выбрать талант

```
當玩家經驗點數足夠時，你可以選擇一項天賦，將英雄大幅強化至新的力量位階。
```

**天賦選項**：
  - `A0RX` 虛空之刃
    強度等級：T2 屬性加成／每級屬性成長加成： +1 / +0 +1 / +1 +1 / +0  技能「燃燒之刃」失去點燃效果。擊殺敵人可使技能「燃燒之刃」的作用範圍提升 1 點。累積 200 次擊殺後，累積效果減弱為 0.5 點。
  - `A0YG` 精湛劍術
    強度等級：T3 屬性加成／每級屬性成長加成： +2 / +1 +3 / +1 +1 / +0  英雄獲得 15% 攻擊閃避與 -20% 裝備技能冷卻。  技能「燃燒之刃」現在會額外以 30% 機率對敵人施加易傷。  技能「著魔」在持續期間會將閃避提升至 30%，額外降低 20% 裝備技能冷卻，並增加 +40% 裝備技能威力。

物件欄位（原型 `Aspb`）：`aite = 0`, `spb1 = A0RX,A0YG`, `spb2 = 0`, `spb3 = 2`, `spb4 = 2`

實作：

`Trig_HeroSkills1_Actions`　war3map.j:46632
```jass
if Skill=='A0RX' then
call SetHeroStr(u,GetHeroStr(u,false)+1,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+1,true)
call SetHeroInt(u,GetHeroInt(u,false)+1,true)
call SaveInteger(hash,GetHandleId(u),'aAGI',1)
call UnitRemoveAbility(u,'A0RV')
call UnitAddAbility(u,'A0RY')
call SaveInteger(hash,GetHandleId(pl),15,1)
elseif Skill=='A0YG' then
call SetHeroStr(u,GetHeroStr(u,false)+2,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+3,true)
call SetHeroInt(u,GetHeroInt(u,false)+1,true)
call SaveInteger(hash,GetHandleId(u),'aSTR',1)
call SaveInteger(hash,GetHandleId(u),'aAGI',1)
call UnitRemoveAbility(u,'A0RV')
call UnitAddAbility(u,'A0YH')
call SaveReal(hash,GetHandleId(u),1,LoadReal(hash,GetHandleId(u),1)-0.20)
call UnitAddAbility(u,'A0S1')
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

## 虛空之刃 `A0RX`　—　來自天賦「選擇天賦」

俄文原名：Пустотные клинки

```
強度等級：T2
屬性加成／每級屬性成長加成：
+1 / +0
+1 / +1
+1 / +0

技能「燃燒之刃」失去點燃效果。擊殺敵人可使技能「燃燒之刃」的作用範圍提升 1 點。累積 200 次擊殺後，累積效果減弱為 0.5 點。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [0.5, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['acidbomb', 'channel']`, `acap = `, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `arqa = 15`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills1_Actions`　war3map.j:46632
```jass
if Skill=='A0RX' then
call SetHeroStr(u,GetHeroStr(u,false)+1,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+1,true)
call SetHeroInt(u,GetHeroInt(u,false)+1,true)
call SaveInteger(hash,GetHandleId(u),'aAGI',1)
call UnitRemoveAbility(u,'A0RV')
call UnitAddAbility(u,'A0RY')
call SaveInteger(hash,GetHandleId(pl),15,1)
```

## 精湛劍術 `A0YG`　—　來自天賦「選擇天賦」

俄文原名：Искусное фехтование

```
強度等級：T3
屬性加成／每級屬性成長加成：
+2 / +1
+3 / +1
+1 / +0

英雄獲得 15% 攻擊閃避與 -20% 裝備技能冷卻。

技能「燃燒之刃」現在會額外以 30% 機率對敵人施加易傷。

技能「著魔」在持續期間會將閃避提升至 30%，額外降低 20% 裝備技能冷卻，並增加 +40% 裝備技能威力。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [0.5, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['faeriefireon', 'channel']`, `acap = `, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `arqa = 24`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills1_Actions`　war3map.j:46640
```jass
elseif Skill=='A0YG' then
call SetHeroStr(u,GetHeroStr(u,false)+2,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+3,true)
call SetHeroInt(u,GetHeroInt(u,false)+1,true)
call SaveInteger(hash,GetHandleId(u),'aSTR',1)
call SaveInteger(hash,GetHandleId(u),'aAGI',1)
call UnitRemoveAbility(u,'A0RV')
call UnitAddAbility(u,'A0YH')
call SaveReal(hash,GetHandleId(u),1,LoadReal(hash,GetHandleId(u),1)-0.20)
call UnitAddAbility(u,'A0S1')
call SaveInteger(hash,GetHandleId(pl),15,1)
endif
```

---

## 皮膚

純外觀：黑曜石獵手、赤紅刺客

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **18** — 裝備技能威力〔持有者〕道具觸發用 cof = key18 + 1

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
