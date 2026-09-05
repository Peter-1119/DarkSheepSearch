# 惡魔獵手 `Edem`（Охотник на демонов）

主屬性 **敏捷** · 背包 **6 格** · 解鎖 0 · 定位 刺客

| | 初始 | 每級 |
|---|---|---|
| 力量 | （未覆寫） | 2 |
| 敏捷 | （未覆寫） | 2.4 |
| 智力 | （未覆寫） | 1.5 |

> 容易上手的近戰刺客。

**縮放**：吃技能強度的技能 ['A04X'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 ['A04T']

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

實作：

`RemoveFrost`　war3map.j:1527
```jass
function RemoveFrost takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call UnitRemoveAbility(u,'S00G')
call UnitRemoveAbility(u,'B02V')
call RemoveSavedHandle(hash,GetHandleId(u),'B02V')
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set t=null
set u=null
endfunction
function FrostUnit takes unit damager,unit target,real chanse returns nothing
local real dmg
local real cof=1.0
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,t_Id,44)>0 then
set t=null
return
endif
if LoadInteger(hash,t_Id,28)>0 and LoadInteger(hash,GetHandleId(damager),'I07G')==0 then
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(damager,'A0AQ')==1 and GetUnitAbilityLevel(target,'B046')==1 then
if IsUnitType(target,UNIT_TYPE_HERO)then
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.25
else
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.05
endif
if LoadInteger(hash,d_Id,'I00R')>=1 then
set dmg=dmg+150.
endif
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\CrushingWave\\CrushingWaveDamage.mdl",target,"chest"))
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,48)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
if LoadInteger(hash,t_Id,'I07A')>=1 then
if UnitLifePercent(target)<=25.0 then
set cof=cof-0.50
endif
endif
if LoadInteger(hash,t_Id,'I048')>=1 then
if UnitLifePercent(target)<=30.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'tbak')>=1 then
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.18
endif
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
set cof=cof-LoadReal(hash,t_Id,48)+LoadReal(hash,d_Id,28)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call EnableTrigger(gg_trg_HeroTakeDamage)
endif
if GetUnitAbilityLevel(target,'B02V')==1 then
set cof=1.00
if IsUnitType(target,UNIT_TYPE_HERO)then
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.25
else
set dmg=GetUnitState(target,UNIT_STATE_MAX_LIFE)*0.05
endif
if LoadInteger(hash,d_Id,'I00R')>=1 then
set dmg=dmg+150.
endif
if GetPlayerTechCount(GetOwningPlayer(damager),'Rufb',true)==1 then
if GetUnitTypeId(damager)=='n041' or GetUnitTypeId(damager)=='n06L' or GetUnitTypeId(damager)=='n06S' or GetUnitTypeId(damager)=='n06U' or GetUnitTypeId(damager)=='n06V' then
set dmg=dmg+100.
endif
endif
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\CrushingWave\\CrushingWaveDamage.mdl",target,"chest"))
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,48)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
if LoadInteger(hash,t_Id,'I07A')>=1 then
if UnitLifePercent(target)<=25.0 then
set cof=cof-0.50
endif
endif
if LoadInteger(hash,t_Id,'I048')>=1 then
if UnitLifePercent(target)<=30.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'tbak')>=1 then
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(damager)>=75.0 then
set cof=cof-0.18
endif
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
set cof=cof-LoadReal(hash,t_Id,48)+LoadReal(hash,d_Id,28)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call EnableTrigger(gg_trg_HeroTakeDamage)
set t=LoadTimerHandle(hash,t_Id,'B02V')
call TimerStart(t,0.,false,function RemoveFrost)
else
call UnitAddAbility(target,'S00G')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,t_Id,'B02V',t)
call TimerStart(t,6.,false,function RemoveFrost)
endif
endif
set t=null
endfunction
function RemoveFlammability takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
call UnitRemoveAbility(u,'S00M')
call UnitRemoveAbility(u,'B042')
call RemoveSavedHandle(hash,GetHandleId(u),'B042')
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set t=null
set u=null
endfunction
function FlammabilityUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)then
set chanse=chanse*0.50
elseif LoadInteger(hash,GetHandleId(target),'tkno')>=1 then
elseif LoadInteger(hash,GetHandleId(target),27)>0 then
set chanse=chanse*0.25
elseif not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B042')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B042')
call TimerStart(t,6.,false,function RemoveFlammability)
else
call UnitAddAbility(target,'S00M')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B042',t)
call TimerStart(t,6.,false,function RemoveFlammability)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
function Burn_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local integer u_Id
local unit u2=LoadUnitHandle(hash,Id,0)
local integer u2_Id=GetHandleId(u2)
local integer count=LoadInteger(hash,u2_Id,'burn')
local integer i=0
local integer check=0
local integer L
local real dmg
local real dmg_cof=1.0
local real cof
if not UnitAlive(u2)then
call SaveInteger(hash,u2_Id,'burn',0)
call UnitRemoveAbility(u2,'A0Y6')
call UnitRemoveAbility(u2,'B040')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'burt')
set u=null
set u2=null
set t=null
return
endif
if LoadInteger(hash,u2_Id,'I07A')>=1 then
if UnitLifePercent(u2)<=25.0 then
set dmg_cof=dmg_cof-0.50
endif
endif
if LoadInteger(hash,u2_Id,'I048')>=1 then
if UnitLifePercent(u2)<=30.0 then
set dmg_cof=dmg_cof-0.25
endif
endif
if LoadInteger(hash,u2_Id,'tbak')>=1 then
if UnitLifePercent(u2)>=75.0 then
set dmg_cof=dmg_cof-0.25
endif
endif
if LoadInteger(hash,u2_Id,'pman')>=1 then
if UnitLifePercent(u2)>=75.0 then
set dmg_cof=dmg_cof-0.18
endif
endif
set dmg_cof=dmg_cof-LoadReal(hash,u2_Id,47)
call DisableTrigger(gg_trg_HeroTakeDamage)
loop
set i=i+1
set L=LoadInteger(hash,Id,i)
if L>0 then
set u=LoadUnitHandle(hash,Id,i)
set u_Id=GetHandleId(u)
set dmg=LoadReal(hash,Id,i)
set cof=dmg_cof
if LoadInteger(hash,u_Id,'gvsm')>=1 or LoadInteger(hash,u_Id,'I00S')>=1 then
if GetUnitAbilityLevel(u2,'B02V')==1 then
set cof=cof+0.35
endif
endif
if LoadInteger(hash,u_Id,'I086')>=1 then
if LoadInteger(hash,u_Id,27)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(u,'B01H')==1 then
set cof=cof+0.50
endif
set cof=cof+LoadReal(hash,u_Id,27)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(u,u2,dmg*cof,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
if LoadInteger(hash,u2_Id,'I068')>=1 then
call UnitDamageTarget(u2,u,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
set L=L-1
if L>0 then
set check=1
else
call RemoveSavedHandle(hash,Id,i)
endif
call SaveInteger(hash,Id,i,L)
endif
exitwhen i==count
endloop
call EnableTrigger(gg_trg_HeroTakeDamage)
if check==0 then
call SaveInteger(hash,u2_Id,'burn',0)
call UnitRemoveAbility(u2,'A0Y6')
call UnitRemoveAbility(u2,'B040')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'burt')
endif
set u=null
set u2=null
set t=null
endfunction
function BurnUnit takes unit damager,unit target,real dmg,real chanse returns nothing
local timer t
local integer Id
local integer count
local integer count2
local integer i
local integer i2
local real cof
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local effect e
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)then
set chanse=chanse*0.50
elseif LoadInteger(hash,GetHandleId(target),'tkno')>=1 then
elseif LoadInteger(hash,GetHandleId(target),27)>0 and LoadInteger(hash,GetHandleId(damager),'A03M')!=1 then
if LoadInteger(hash,GetHandleId(target),27)>50 then
set chanse=0.
endif
if GetUnitTypeId(damager)=='h01A' or GetUnitTypeId(damager)=='h01B' then
if GetPlayerTechCount(GetOwningPlayer(damager),'Ropm',true)==1 then
set chanse=chanse*1.75
else
set chanse=chanse*1.00
endif
else
set chanse=chanse*0.25
endif
elseif not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 and LoadInteger(hash,GetHandleId(damager),'A03M')!=1 then
set chanse=0.
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if GetUnitAbilityLevel(target,'B042')==1 then
set chanse=chanse*(1.00+(0.50*(1.00+LoadReal(hash,GetHandleId(damager),46))))
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if LoadInteger(hash,GetHandleId(damager),'A03M')==1 then
set cof=1.0*(1.00+(0.50*(1.00+LoadReal(hash,GetHandleId(damager),46))))
if LoadInteger(hash,t_Id,'I07A')>=1 then
if UnitLifePercent(target)<=25.0 then
set cof=cof-0.50
endif
endif
if LoadInteger(hash,t_Id,'I048')>=1 then
if UnitLifePercent(target)<=30.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'tbak')>=1 then
if UnitLifePercent(target)>=75.0 then
set cof=cof-0.25
endif
endif
if LoadInteger(hash,t_Id,'pman')>=1 then
if UnitLifePercent(target)>=75.0 then
set cof=cof-0.18
endif
endif
if LoadInteger(hash,d_Id,'gvsm')>=1 or LoadInteger(hash,d_Id,'I00S')>=1 then
if GetUnitAbilityLevel(target,'B02V')==1 then
set cof=cof+0.35
endif
endif
if LoadInteger(hash,d_Id,'I086')>=1 then
if LoadInteger(hash,d_Id,27)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(damager,'B01H')==1 then
set cof=cof+0.50
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
if cof<0.20 then
set cof=0.20
endif
set cof=cof-LoadReal(hash,t_Id,47)+LoadReal(hash,d_Id,27)
call UnitDamageTarget(damager,target,dmg*cof,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
if LoadInteger(hash,t_Id,'I068')>=1 then
call UnitDamageTarget(target,damager,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\AerialExplosionV3.mdx",target,"origin"))
call EnableTrigger(gg_trg_HeroTakeDamage)
set t=null
set e=null
return
endif
set dmg=dmg/16.
set count=16
if GetUnitAbilityLevel(target,'B042')==1 then
set count=count+R2I(8.0*(1.00+(1.00+LoadReal(hash,GetHandleId(damager),46))))
endif
if GetUnitAbilityLevel(target,'A064')==1 then
set count=count/2
endif
set count2=LoadInteger(hash,t_Id,'burn')
if count2==0 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,0,target)
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
  - **27** — 實數＝點燃傷害 +%〔施加者〕／整數＝抵抗點燃旗標〔受害者〕**兩者不同表**
  - **28** — 實數＝冰凍傷害 +%〔施加者〕／整數＝抵抗冰凍旗標〔受害者〕
  - **44** — 狀態免疫旗標〔受害者〕>0 則所有狀態函式開頭直接 return，完全不判定
  - **46** — 易燃效果強化〔施加者〕影響易燃的機率倍率與跳數加成
  - **47** — 點燃抗性〔受害者〕係數減去它；電擊讓它 −1.00
  - **48** — 冰凍抗性〔受害者〕；電擊 −1.00

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
