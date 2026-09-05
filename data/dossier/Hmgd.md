# 亡者公主 `Hmgd`（Принцесса мёртвых）

主屬性 **敏捷** · 背包 **6 格** · 解鎖 4000000 · 定位 刺客

| | 初始 | 每級 |
|---|---|---|
| 力量 | 17 | 1.5 |
| 敏捷 | 33 | 4 |
| 智力 | 23 | 2.5 |

> 強力的近戰單挑者。沒有輔助道具時對群戰無力，但單體極強。

**縮放**：吃技能強度的技能 ['A0X7', 'ANbl', 'AOwk'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且事件數越多穿透越划算。

細節見 `data/dossier/_engine.md`。


---

## 疾行 `AOwk`　—　吃技能強度

俄文原名：Стремительность

```
英雄進入隱形並獲得移動速度加成。從隱形中發動的攻擊會對敵人造成額外魔法傷害，並為英雄回復生命值。

隱形攻擊傷害：100 +（400% 穿透）+（40% 技能強度）點
魔法吸血：33%
移動速度加成：10%
持續時間：11 秒

冷卻：11 秒
```

每級變動：
  - 第 3 行：100 / 150 / 200 / 250 / 300
  - 第 5 行：10 / 20 / 30 / 40 / 50

物件欄位（原型 `None`）：`Owk1 = 0.20000000298023224`, `Owk2 = [None, 0.20000000298023224, 0.30000001192092896, 0.4000000059604645, 0.5]`, `Owk3 = 0.0`, `Owk4 = 0`, `acdn = 11.0`, `adur = 11.0`, `ahdu = 11.0`, `alev = 5`, `amcs = [60, 70, 80, 90, 100]`

實作：

`Trig_HeroAttack53_Actions`　war3map.j:64298
```jass
if GetUnitAbilityLevel(u,'BOwk')>=1 then
call UnitRemoveAbility(u,'BOwk')
set dmg=50.+50.*GetUnitAbilityLevel(u,'AOwk')+LoadReal(hash,GetHandleId(u),16)*4.+udg_ItemBonusDMG[n]*0.40
call SetUnitState(u,UNIT_STATE_LIFE,GetWidgetLife(u)+dmg*0.33)
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\NightElf\\Blink\\BlinkCaster.mdl",u3,"origin"))
set text=CreateTextTagUnitBJ("|cFFFF4B39"+I2S(R2I(dmg))+"!",u,0,13.00,100,100,100,0)
call SetTextTagVelocityBJ(text,75.00,90.00)
call SetTextTagSuspended(text,false)
call SetTextTagPermanent(text,false)
call SetTextTagLifespan(text,3.00)
call SetTextTagFadepoint(text,2.00)
```

## 躍進 `ANbl`　—　吃技能強度

俄文原名：Скачок

```
將英雄傳送一小段距離。傳送後英雄獲得穿透加成。

施放距離：700 點
穿透加成：20 +（10% 技能強度）點
加成持續時間：10 秒

冷卻：16 秒
```

每級變動：
  - 第 3 行：700 / 800 / 900 / 1000 / 1100
  - 第 4 行：20 / 30 / 40 / 50 / 60

物件欄位（原型 `None`）：`Ebl1 = [700.0, 800.0, 900.0, 1000.0, 1100.0]`, `Ebl2 = 100.0`, `acdn = 16.0`, `alev = 5`, `amcs = [75, 84, 93, 102, 111]`

實作：

`Trig_HeroSkills53_Actions`　war3map.j:64217
```jass
if Skill=='ANbl' then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call TimerStart(t,10.,false,function Hero53W_Buff)
set dmg=10.+10.*I2R(lvl)+udg_ItemBonusDMG[n]*0.10
call SaveReal(hash,GetHandleId(u),16,LoadReal(hash,GetHandleId(u),16)+dmg)
call SaveReal(hash,Id,1,dmg)
call SaveEffectHandle(hash,Id,2,AddSpecialEffectTarget("Radiance Royal.mdx",u,"origin"))
call SetUnitAnimation(u,"stand")
```

`Hero53W_Buff`　war3map.j:64189
```jass
function Hero53W_Buff takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local real dmg=LoadReal(hash,Id,1)
call SaveReal(hash,GetHandleId(u),16,LoadReal(hash,GetHandleId(u),16)-dmg)
call DestroyEffect(LoadEffectHandle(hash,Id,2))
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set u=null
set t=null
endfunction
```

## 亡者詛咒 `A0X6`

俄文原名：Проклятие мёртвых

```
英雄的攻擊會對敵人施加詛咒。被詛咒的目標會受到取決於其生命值的混合傷害。

詛咒傷害（點/秒）：敵人目前生命值的 2%
詛咒持續時間：5 秒
```

每級變動：
  - 第 3 行：2 / 3 / 4 / 5 / 6

物件欄位（原型 `Amgl`）：`aher = 1`, `alev = 5`

實作：

`Hero53E_poison`　war3map.j:64265
```jass
function Hero53E_poison takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local unit u2=LoadUnitHandle(hash,Id,2)
local integer count=LoadInteger(hash,GetHandleId(u2),'A0X6')
local real dmg=GetWidgetLife(u2)*(0.01+0.01*I2R(GetUnitAbilityLevel(u,'A0X6')))
call UnitDamageTarget(u,u2,dmg,true,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,WEAPON_TYPE_WHOKNOWS)
set count=count-1
if count==0 or not UnitAlive(u2)then
call DestroyEffect(LoadEffectHandle(hash,Id,3))
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveSavedHandle(hash,GetHandleId(u2),'A0X6')
endif
call SaveInteger(hash,GetHandleId(u2),'A0X6',count)
set t=null
set u=null
set u2=null
endfunction
```

`Trig_HeroAttack53_Actions`　war3map.j:64310
```jass
elseif GetUnitAbilityLevel(u,'A0X6')>=1 then
set u_Id=GetHandleId(u3)
if LoadInteger(hash,u_Id,'A0X6')==0 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u3)
call SaveEffectHandle(hash,Id,3,AddSpecialEffectTarget("NecroBuff_Origin.mdx",u3,"origin"))
call SaveTimerHandle(hash,u_Id,'A0X6',t)
call TimerStart(t,1.,true,function Hero53E_poison)
endif
call SaveInteger(hash,u_Id,'A0X6',5)
endif
```

## 致命切割 `A0X7`　—　吃技能強度

俄文原名：Смертельный разрез

```
瞬間移動到指定敵人的身後並造成傷害。擊殺目標時會重置技能與裝備的冷卻。

傷害：200 + （900% 穿透）+ （90% 技能強度）點

冷卻：50 秒。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.6000000238418579, None, 1.0]`, `Ncl2 = [1, None]`, `Ncl3 = [1, None]`, `Ncl4 = [0.6000000238418579, None, 1.0]`, `Ncl5 = [0, None]`, `Ncl6 = ['chemicalrage', None, 'channel']`, `acap = `, `acdn = [50.0, None, 17.0]`, `alev = 1`, `amcs = [125, None, 80, 90, 100, 110, 120]`, `aran = [900.0, None, 700.0]`, `atar = ['air,ground,enemy,neutral,organic', None, 'air,ground,friend,neutral,self']`

實作：

`Trig_HeroSkills53_Actions`　war3map.j:64227
```jass
elseif Skill=='A0X7' then
set dmg=200.+udg_ItemBonusDMG[n]*0.90+LoadReal(hash,GetHandleId(u),16)*9.00
call UnitAddAbility(u,'A0X8')
set u2=GetSpellTargetUnit()
set x=GetUnitX(u2)
set y=GetUnitY(u2)
set x2=PolarX(x,100,GetUnitFacing(u2)+180)
set y2=PolarY(y,100,GetUnitFacing(u2)+180)
call SetUnitX(u,x2)
call SetUnitY(u,y2)
call SetUnitFacing(u,GetUnitFacing(u2))
call PauseUnit(u,true)
call SetUnitAnimation(u,"Spell One-c")
call DestroyEffect(AddSpecialEffect("Abilities\\Spells\\NightElf\\Blink\\BlinkTarget.mdl",x2,y2))
call DestroyEffect(AddSpecialEffectTarget("Objects\\Spawnmodels\\Orc\\OrcSmallDeathExplode\\OrcSmallDeathExplode.mdl",u2,"origin"))
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
call TriggerSleepAction(0.1)
if not UnitAlive(u2)then
call UnitResetCooldown(u)
endif
call TriggerSleepAction(0.1)
call UnitRemoveAbility(u,'A0X8')
call PauseUnit(u,false)
call SetUnitAnimation(u,"stand")
endif
```

## 適應 `A0X9`

俄文原名：Адаптация

```
造成傷害可為英雄帶來加成：

對任何敵人每造成 100 點傷害：攻擊力 +1 點，穿透 +0.35；下一次強化所需的傷害 +35 點

受到傷害可為英雄帶來加成：

每受到敵人 200 點傷害：生命值上限 +15 點，生命回復 +0.50；下一次強化所需的傷害 +30 點
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

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **16** — 穿透〔攻擊者〕每次傷害事件後**另外**打一段 CHAOS/UNIVERSAL，不吃減傷

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
