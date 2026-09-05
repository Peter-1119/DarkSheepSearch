# 引擎附錄：共用函式與全域常數

英雄卷宗只放各自的技能。這一份放**所有英雄共用**的東西：
狀態怎麼被施加與結算、投射物命中時附帶什麼、傷害管線怎麼組成、
以及算裸屬性必備的全域常數。

搭配 `data/dossier/<英雄ID>.md` 與 `tools/BUILD_BRIEF.md` 一起看。

---

## 全域常數（war3mapMisc.txt）

| 常數 | 值 | 意義 |
|---|---|---|
| `MaxHeroLevel` | `25` | 英雄等級上限 |
| `AgiDefenseBonus` | `0.25` | 每點敏捷的護甲 |
| `AgiAttackSpeedBonus` | `0.01` | 每點敏捷的攻擊速度 |
| `DamageBonusNormal` | `1.00,1.50,1.00,0.25,1.00,1.00,0.60,1.00` | 普通攻擊 vs 各護甲類型 |
| `DamageBonusPierce` | `2.00,0.75,1.00,0.35,1.00,0.60,0.60,1.50` | 穿刺攻擊 vs 各護甲類型 |
| `DamageBonusSiege` | `1.00,0.50,1.00,1.25,1.00,0.50,1.15,2.00` | 攻城攻擊 vs 各護甲類型 |
| `DamageBonusMagic` | `1.25,0.75,1.50,0.35,1.00,0.60,1.00,0.90` | 魔法攻擊 vs 各護甲類型 |
| `DamageBonusChaos` | `1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00` | 混亂攻擊 vs 各護甲類型 |
| `DamageBonusHero` | `1.00,1.00,1.00,0.50,1.00,1.00,0.60,1.00` | 英雄攻擊 vs 各護甲類型 |

護甲類型倍率的順序：無甲 / 輕甲 / 中甲 / 重甲 / 城牆 / 英雄 / 神聖 / 其他。

> 這些是**地圖有覆寫**的值。沒列出來的走魔獸預設，
> 例如 `IntManaBonus` 若不在表上就是預設的 15 法力／點智力。

---

## hash key 對照表

同一個數字在「施加者」與「受害者」身上是完全不同的東西，
而且實數槽與整數槽是**兩張不同的表**。

| key | 意義 |
|---|---|
| **1** | 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20 |
| **3** | 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof |
| **4** | 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它 |
| **5** | 對 0-1 級敵人傷害 +%〔攻擊者〕 |
| **6** | 造成傷害 +%〔攻擊者〕；電擊會扣它 → 目標輸出下降 |
| **8** | 對英雄減傷〔受害者〕 |
| **9** | 對亡靈傷害 +%〔攻擊者〕 |
| **10** | 金幣加成〔擊殺者〕Trig_gold_Actions 讀擊殺者 handle |
| **16** | 穿透〔攻擊者〕每次傷害事件後**另外**打一段 CHAOS/UNIVERSAL，不吃減傷 |
| **17** | 反傷〔被攻擊者〕整數槽 ≥1 則免疫反傷 |
| **18** | 裝備技能威力〔持有者〕道具觸發用 cof = key18 + 1 |
| **19** | 反傷加成〔被攻擊者〕 |
| **27** | 實數＝點燃傷害 +%〔施加者〕／整數＝抵抗點燃旗標〔受害者〕**兩者不同表** |
| **28** | 實數＝冰凍傷害 +%〔施加者〕／整數＝抵抗冰凍旗標〔受害者〕 |
| **29** | 實數＝流血傷害 +%〔施加者〕／整數＝抵抗流血旗標〔受害者〕（加成寫錯變數，實際無效 —— 見 地圖問題回報 A-4） |
| **35** | 額外護甲〔單位〕SetUnitExtraArmor 的儲存槽，可為負 |
| **37** | 生命上限增量〔單位〕只存「最後一次呼叫的差值」，不是總量 |
| **44** | 狀態免疫旗標〔受害者〕>0 則所有狀態函式開頭直接 return，完全不判定 |
| **45** | 實數＝疾病傷害 +%〔施加者〕／整數＝抵抗疾病旗標〔受害者〕（加成同樣寫錯變數） |
| **46** | 易燃效果強化〔施加者〕影響易燃的機率倍率與跳數加成 |
| **47** | 點燃抗性〔受害者〕係數減去它；電擊讓它 −1.00 |
| **48** | 冰凍抗性〔受害者〕；電擊 −1.00 |
| **49** | 流血抗性〔受害者〕；電擊 −1.00 |
| **50** | 疾病抗性〔受害者〕；電擊 −1.00 |
| **52** | （全腳本沒有任何地方讀它 —— 死碼） |

---

## 狀態的「施加」—— 機率修正鏈都在這裡

### `BurnUnit`　war3map.j:1837（153 行）

```jass
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
call SaveUnitHandle(hash,Id,1,damager)
call SaveInteger(hash,Id,1,count)
call SaveReal(hash,Id,1,dmg)
call UnitAddAbility(target,'A0Y6')
call SaveInteger(hash,t_Id,'burn',1)
call SaveTimerHandle(hash,t_Id,'burt',t)
call TimerStart(t,0.25,true,function Burn_Dmg)
else
set t=LoadTimerHandle(hash,t_Id,'burt')
set Id=GetHandleId(t)
set i2=0
set i=0
loop
set i=i+1
if LoadInteger(hash,Id,i)==0 then
call SaveUnitHandle(hash,Id,i,damager)
call SaveInteger(hash,Id,i,count)
call SaveReal(hash,Id,i,dmg)
call SaveInteger(hash,t_Id,'burn',i)
set i=count2
set i2=1
endif
exitwhen i==count2
endloop
if i2==0 then
set count2=count2+1
call SaveUnitHandle(hash,Id,count2,damager)
call SaveInteger(hash,Id,count2,count)
call SaveReal(hash,Id,count2,dmg)
call SaveInteger(hash,t_Id,'burn',count2)
endif
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
else
if LoadInteger(hash,GetHandleId(damager),'silk')>=1 then
call FlammabilityUnit(damager,target,0.35)
endif
endif
set t=null
set e=null
endfunction
```

### `FlammabilityUnit`　war3map.j:1693（42 行）

```jass
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
```

### `FrostUnit`　war3map.j:1539（142 行）

```jass
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
```

### `ShockUnit`　war3map.j:2585（62 行）

```jass
function ShockUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
local real time=4.
local real cof=1.
local integer u_Id=GetHandleId(target)
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(damager),'I0AL')>=1 then
set chanse=chanse+0.25
endif
if IsUnitType(target,UNIT_TYPE_HERO)then
set chanse=chanse*0.50
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if LoadInteger(hash,GetHandleId(damager),'I01Q')>=1 then
set time=time+1.
endif
if GetUnitAbilityLevel(target,'B046')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B046')
call TimerStart(t,time,false,function RemoveShock)
else
call UnitAddAbility(target,'S015')
if LoadInteger(hash,GetHandleId(damager),'I09A')>=1 then
set cof=0.50
endif
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)-0.20*cof)
call SaveReal(hash,u_Id,6,LoadReal(hash,u_Id,6)-0.30*cof)
call SaveReal(hash,GetHandleId(target),47,LoadReal(hash,GetHandleId(target),47)-1.00*cof)
call SaveReal(hash,GetHandleId(target),48,LoadReal(hash,GetHandleId(target),48)-1.00*cof)
call SaveReal(hash,GetHandleId(target),49,LoadReal(hash,GetHandleId(target),49)-1.00*cof)
call SaveReal(hash,GetHandleId(target),50,LoadReal(hash,GetHandleId(target),50)-1.00*cof)
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B046',t)
call TimerStart(t,time,false,function RemoveShock)
endif
if LoadInteger(hash,GetHandleId(damager),'rej3')>=1 then
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Other\\Monsoon\\MonsoonBoltTarget.mdl",target,"origin"))
call UnitDamageTarget(damager,target,I2R(GetHeroStr(damager,true))*1.25,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

### `BleedUnit`　war3map.j:2104（91 行）

```jass
function BleedUnit takes unit damager,unit target,real dmg,real chanse returns nothing
local timer t
local integer Id
local integer count
local integer count2
local integer i
local integer i2
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local effect e
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(target),29)>0 then
if LoadInteger(hash,GetHandleId(target),29)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'shdt')>=1 then
if IsUnitType(target,UNIT_TYPE_HERO)then
set count=GetHeroLevel(target)
else
set count=GetUnitLevel(target)
endif
set chanse=chanse*(1.0+0.05*I2R(count))
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
set dmg=dmg/16.
if GetUnitAbilityLevel(target,'A064')==1 then
set count=8
else
set count=16
endif
set count2=LoadInteger(hash,t_Id,'bled')
if count2==0 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,0,target)
call SaveUnitHandle(hash,Id,1,damager)
call SaveInteger(hash,Id,1,count)
call SaveReal(hash,Id,1,dmg)
call UnitAddAbility(target,'A0Y7')
call SaveInteger(hash,t_Id,'bled',1)
call SaveTimerHandle(hash,t_Id,'blud',t)
call TimerStart(t,0.5,true,function Bleed_Dmg)
else
set t=LoadTimerHandle(hash,t_Id,'blud')
set Id=GetHandleId(t)
set i2=0
set i=0
loop
set i=i+1
if LoadInteger(hash,Id,i)==0 then
call SaveUnitHandle(hash,Id,i,damager)
call SaveInteger(hash,Id,i,count)
call SaveReal(hash,Id,i,dmg)
call SaveInteger(hash,t_Id,'bled',i)
set i=count2
set i2=1
endif
exitwhen i==count2
endloop
if i2==0 then
set count2=count2+1
call SaveUnitHandle(hash,Id,count2,damager)
call SaveInteger(hash,Id,count2,count)
call SaveReal(hash,Id,count2,dmg)
call SaveInteger(hash,t_Id,'bled',count2)
endif
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
set e=null
endfunction
```

### `DiseaseUnit`　war3map.j:2299（85 行）

```jass
function DiseaseUnit takes unit damager,unit target,real dmg,real chanse returns nothing
local timer t
local integer Id
local integer count
local integer count2
local integer i
local integer i2
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local effect e
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
elseif LoadInteger(hash,GetHandleId(target),'tkno')>=1 then
call BleedUnit(damager,target,dmg,chanse)
set chanse=0.
elseif LoadInteger(hash,GetHandleId(target),45)>0 then
if LoadInteger(hash,GetHandleId(damager),'dtsb')>=1 then
else
set chanse=0.
endif
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
set dmg=dmg/16.
if GetUnitAbilityLevel(target,'A064')==1 then
set count=8
else
set count=16
endif
set count2=LoadInteger(hash,t_Id,'dise')
if count2==0 then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,0,target)
call SaveUnitHandle(hash,Id,1,damager)
call SaveInteger(hash,Id,1,count)
call SaveReal(hash,Id,1,dmg)
call UnitAddAbility(target,'A0FQ')
call SaveInteger(hash,t_Id,'dise',1)
call SaveTimerHandle(hash,t_Id,'disa',t)
call TimerStart(t,0.75,true,function Disease_Dmg)
else
set t=LoadTimerHandle(hash,t_Id,'disa')
set Id=GetHandleId(t)
set i2=0
set i=0
loop
set i=i+1
if LoadInteger(hash,Id,i)==0 then
call SaveUnitHandle(hash,Id,i,damager)
call SaveInteger(hash,Id,i,count)
call SaveReal(hash,Id,i,dmg)
call SaveInteger(hash,t_Id,'dise',i)
set i=count2
set i2=1
endif
exitwhen i==count2
endloop
if i2==0 then
set count2=count2+1
call SaveUnitHandle(hash,Id,count2,damager)
call SaveInteger(hash,Id,count2,count)
call SaveReal(hash,Id,count2,dmg)
call SaveInteger(hash,t_Id,'dise',count2)
endif
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
set e=null
endfunction
```

### `CurseUnit`　war3map.j:2461（46 行）

```jass
function CurseUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
local integer u_Id=GetHandleId(target)
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(target),30)>0 then
if LoadInteger(hash,GetHandleId(target),30)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B044')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B044')
call TimerStart(t,8.,false,function RemoveCurse)
else
call UnitAddAbility(target,'A0Y9')
call SaveReal(hash,GetHandleId(target),50,LoadReal(hash,GetHandleId(target),50)-0.50)
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)-0.20)
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B044',t)
call TimerStart(t,8.,false,function RemoveCurse)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

### `WeakUnit`　war3map.j:2398（48 行）

```jass
function WeakUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(target),30)>0 then
if LoadInteger(hash,GetHandleId(target),30)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B043')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B043')
call TimerStart(t,8.,false,function RemoveWeak)
else
call UnitAddAbility(target,'S00N')
call SaveReal(hash,GetHandleId(target),49,LoadReal(hash,GetHandleId(target),49)-0.50)
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B043',t)
call TimerStart(t,8.,false,function RemoveWeak)
endif
if UnitHasItemOfType(damager,'I044')then
call UnitDamageTarget(damager,target,I2R(GetHeroAgi(damager,true)),false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
call DestroyEffect(AddSpecialEffectTarget("war3mapImported\\SoulRitual.mdx",target,"origin"))
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

### `VulnerabilityUnit`　war3map.j:2519（43 行）

```jass
function VulnerabilityUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer t_Id=GetHandleId(target)
local integer d_Id=GetHandleId(damager)
local integer random
local integer chanse_random
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(target),30)>0 then
if LoadInteger(hash,GetHandleId(target),30)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,d_Id,'I09G')>=1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B045')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B045')
call TimerStart(t,8.,false,function RemoveVulnerability)
else
call UnitAddAbility(target,'S014')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B045',t)
call TimerStart(t,8.,false,function RemoveVulnerability)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

### `CharmUnit`　war3map.j:49826（42 行）

```jass
function CharmUnit takes unit damager,unit target,real chanse returns nothing
local timer t
local integer random
local integer chanse_random
local integer u_Id=GetHandleId(target)
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if LoadInteger(hash,GetHandleId(target),30)>0 then
if LoadInteger(hash,GetHandleId(target),30)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if LoadInteger(hash,GetHandleId(damager),'I09G')>=1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B016')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B016')
call TimerStart(t,5.,false,function RemoveCharm)
else
call UnitAddAbility(target,'S016')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B016',t)
call TimerStart(t,5.,false,function RemoveCharm)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

### `SliceUnit`　war3map.j:52250（30 行）

```jass
function SliceUnit takes unit target,real chanse returns nothing
local timer t
local integer random
local integer chanse_random
local integer u_Id=GetHandleId(target)
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,GetHandleId(target),44)>0 then
set chanse=0.
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B038')==1 then
set t=LoadTimerHandle(hash,GetHandleId(target),'B038')
call TimerStart(t,10.,false,function RemoveSlice)
else
call UnitAddAbility(target,'S017')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,GetHandleId(target),'B038',t)
call TimerStart(t,10.,false,function RemoveSlice)
endif
endif
set t=null
endfunction
```

### `AnathemaUnit`　war3map.j:55567（50 行）

```jass
function AnathemaUnit takes unit damager,unit target,real debuff,real chanse returns nothing
local timer t
local real r
local integer random
local integer chanse_random
local integer u_Id=GetHandleId(target)
if IsUnitType(target,UNIT_TYPE_STRUCTURE)or IsUnitType(target,UNIT_TYPE_MECHANICAL)or not UnitAlive(target)or LoadInteger(hash,u_Id,44)>0 then
set chanse=0.
endif
if LoadInteger(hash,u_Id,30)>0 then
if LoadInteger(hash,u_Id,30)>50 then
set chanse=0.
endif
set chanse=chanse*0.25
endif
if GetUnitAbilityLevel(target,'B045')==1 then
set chanse=chanse*1.50
endif
if GetUnitAbilityLevel(target,'B00W')>0 then
set chanse=chanse*0.70
endif
if LoadInteger(hash,GetHandleId(damager),'I09G')>=1 then
set chanse=chanse*1.50
endif
set chanse_random=R2I(chanse*100)
set random=GetRandomInt(1,100)
if random<=chanse_random then
if GetUnitAbilityLevel(target,'B047')==1 then
set r=LoadReal(hash,u_Id,'B047')
if debuff>r then
call SaveReal(hash,u_Id,'B047',debuff)
endif
set t=LoadTimerHandle(hash,u_Id,'B047')
call TimerStart(t,8.,false,function RemoveAnathema)
else
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)-0.15)
call SaveReal(hash,u_Id,6,LoadReal(hash,u_Id,6)-0.15)
call SaveReal(hash,u_Id,'B047',debuff)
call UnitAddAbility(target,'S01C')
set t=CreateTimer()
call SaveUnitHandle(hash,GetHandleId(t),1,target)
call SaveTimerHandle(hash,u_Id,'B047',t)
call TimerStart(t,8.,false,function RemoveAnathema)
endif
if LoadInteger(hash,GetHandleId(damager),'I00Y')>=1 then
call FrostUnit(damager,target,0.50)
endif
endif
set t=null
endfunction
```

---

## 狀態的「結算」—— 每跳傷害怎麼算

### `Burn_Dmg`　war3map.j:1735（102 行）

```jass
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
```

### `Bleed_Dmg`　war3map.j:1990（114 行）

```jass
function Bleed_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local integer u_Id
local unit u2=LoadUnitHandle(hash,Id,0)
local integer u2_Id=GetHandleId(u2)
local integer count=LoadInteger(hash,u2_Id,'bled')
local integer i=0
local integer check=0
local integer L
local real dmg
local real dmg_cof=1.0
local real cof
local string str
if not UnitAlive(u2)then
call SaveInteger(hash,u2_Id,'bled',0)
call UnitRemoveAbility(u2,'A0Y7')
call UnitRemoveAbility(u2,'B041')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'blud')
set u=null
set u2=null
set t=null
return
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
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
set dmg_cof=dmg_cof-LoadReal(hash,u2_Id,49)
loop
set i=i+1
set L=LoadInteger(hash,Id,i)
if L>0 then
set u=LoadUnitHandle(hash,Id,i)
set u_Id=GetHandleId(u)
set dmg=LoadReal(hash,Id,i)
set dmg=dmg*(1.-((100.-UnitLifePercent(u2))*0.0075))
set cof=dmg_cof
if LoadInteger(hash,u_Id,'shdt')>=1 then
if IsUnitType(u2,UNIT_TYPE_HERO)then
set cof=cof+(0.05*I2R(GetHeroLevel(u2)))
else
set cof=cof+(0.05*I2R(GetUnitLevel(u2)))
endif
endif
if LoadInteger(hash,u_Id,'gvsm')>=1 or LoadInteger(hash,u_Id,'I00S')>=1 then
if GetUnitAbilityLevel(u2,'B02V')==1 then
set cof=cof+0.35
endif
endif
if LoadInteger(hash,u_Id,'I086')>=1 then
if LoadInteger(hash,u_Id,29)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(u,'B01H')==1 then
set cof=cof+0.50
endif
set dmg_cof=dmg_cof+LoadReal(hash,u_Id,29)
if cof<0.20 then
set cof=0.20
endif
call UnitDamageTarget(u,u2,dmg*cof,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
if LoadInteger(hash,u2_Id,'I068')>=1 then
call UnitDamageTarget(u2,u,dmg*cof*0.20,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_NORMAL,null)
endif
if LoadInteger(hash,GetHandleId(u),'VAMP')==1 then
call SetWidgetLife(u,GetWidgetLife(u)+dmg*LoadReal(hash,GetHandleId(u),'A0P9'))
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
call SaveInteger(hash,u2_Id,'bled',0)
call UnitRemoveAbility(u2,'A0Y7')
call UnitRemoveAbility(u2,'B041')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'blud')
endif
set u=null
set u2=null
set t=null
endfunction
```

### `Disease_Dmg`　war3map.j:2195（104 行）

```jass
function Disease_Dmg takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local integer u_Id
local unit u2=LoadUnitHandle(hash,Id,0)
local integer u2_Id=GetHandleId(u2)
local integer count=LoadInteger(hash,u2_Id,'dise')
local integer i=0
local integer check=0
local integer L
local real dmg
local real dmg_cof=1.00
local real cof
local string str
if not UnitAlive(u2)then
call SaveInteger(hash,u2_Id,'dise',0)
call UnitRemoveAbility(u2,'A0FQ')
call UnitRemoveAbility(u2,'B006')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'disa')
set u=null
set u2=null
set t=null
return
endif
call DisableTrigger(gg_trg_HeroTakeDamage)
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
set dmg_cof=dmg_cof-LoadReal(hash,u2_Id,50)
loop
set i=i+1
set L=LoadInteger(hash,Id,i)
if L>0 then
set u=LoadUnitHandle(hash,Id,i)
set u_Id=GetHandleId(u)
set dmg=LoadReal(hash,Id,i)
set dmg=dmg*(1.+((100.-UnitLifePercent(u2))*0.0075))
set cof=dmg_cof
if LoadInteger(hash,u_Id,'gvsm')>=1 or LoadInteger(hash,u_Id,'I00S')>=1 then
if GetUnitAbilityLevel(u2,'B02V')==1 then
set cof=cof+0.35
endif
endif
if LoadInteger(hash,u_Id,'I086')>=1 then
if LoadInteger(hash,u_Id,45)>=1 then
set cof=cof+0.50
endif
endif
if GetUnitAbilityLevel(u,'B01H')==1 then
set cof=cof+0.50
endif
set dmg_cof=dmg_cof+LoadReal(hash,u_Id,45)
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
call SaveInteger(hash,u2_Id,'dise',0)
call UnitRemoveAbility(u2,'A0FQ')
call UnitRemoveAbility(u2,'B006')
call FlushChildHashtable(hash,Id)
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u2_Id,'disa')
endif
set u=null
set u2=null
set t=null
endfunction
```

### `RemoveShock`　war3map.j:2562（23 行）

```jass
function RemoveShock takes nothing returns nothing
local timer t=GetExpiredTimer()
local unit u=LoadUnitHandle(hash,GetHandleId(t),1)
local real cof=1.
local integer u_Id=GetHandleId(u)
call UnitRemoveAbility(u,'S015')
call UnitRemoveAbility(u,'B046')
if LoadInteger(hash,GetHandleId(u),'I09A')>=1 then
set cof=0.50
endif
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)+0.20*cof)
call SaveReal(hash,u_Id,6,LoadReal(hash,u_Id,6)+0.30*cof)
call SaveReal(hash,u_Id,47,LoadReal(hash,u_Id,47)+1.00*cof)
call SaveReal(hash,u_Id,48,LoadReal(hash,u_Id,48)+1.00*cof)
call SaveReal(hash,u_Id,49,LoadReal(hash,u_Id,49)+1.00*cof)
call SaveReal(hash,u_Id,50,LoadReal(hash,u_Id,50)+1.00*cof)
call RemoveSavedHandle(hash,GetHandleId(u),'B046')
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
set t=null
set u=null
endfunction
```

### `RemoveFlammability`　war3map.j:1681（12 行）

```jass
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
```

### `ClearUnit`　war3map.j:2647（99 行）

```jass
function ClearUnit takes unit u returns nothing
local timer t
local integer u_Id=GetHandleId(u)
call UnitRemoveBuffs(u,false,true)
if GetUnitAbilityLevel(u,'B040')==1 then
call SaveInteger(hash,u_Id,'burn',0)
call UnitRemoveAbility(u,'A0Y6')
call UnitRemoveAbility(u,'B040')
set t=LoadTimerHandle(hash,u_Id,'burt')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'burt')
endif
if GetUnitAbilityLevel(u,'B041')==1 then
call SaveInteger(hash,u_Id,'bled',0)
call UnitRemoveAbility(u,'A0Y7')
call UnitRemoveAbility(u,'B041')
set t=LoadTimerHandle(hash,u_Id,'blud')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'blud')
endif
if GetUnitAbilityLevel(u,'B006')==1 then
call SaveInteger(hash,u_Id,'dise',0)
call UnitRemoveAbility(u,'A0FQ')
call UnitRemoveAbility(u,'B006')
set t=LoadTimerHandle(hash,u_Id,'disa')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'blud')
endif
if GetUnitAbilityLevel(u,'B02V')==1 then
call UnitRemoveAbility(u,'S00G')
call UnitRemoveAbility(u,'B042')
set t=LoadTimerHandle(hash,u_Id,'B02V')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'B02V')
endif
if GetUnitAbilityLevel(u,'B042')==1 then
call UnitRemoveAbility(u,'S00M')
call UnitRemoveAbility(u,'B042')
set t=LoadTimerHandle(hash,u_Id,'B042')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'B042')
endif
if GetUnitAbilityLevel(u,'B043')==1 then
call UnitRemoveAbility(u,'S00N')
call UnitRemoveAbility(u,'B043')
call SaveReal(hash,u_Id,49,LoadReal(hash,u_Id,49)+0.50)
set t=LoadTimerHandle(hash,u_Id,'B043')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'B043')
endif
if GetUnitAbilityLevel(u,'B044')==1 then
call UnitRemoveAbility(u,'A0Y9')
call UnitRemoveAbility(u,'B044')
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)+0.20)
call SaveReal(hash,u_Id,50,LoadReal(hash,u_Id,50)+0.50)
set t=LoadTimerHandle(hash,u_Id,'B044')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'B044')
endif
if GetUnitAbilityLevel(u,'B045')==1 then
call UnitRemoveAbility(u,'S014')
call UnitRemoveAbility(u,'B045')
set t=LoadTimerHandle(hash,u_Id,'B045')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'B045')
endif
if GetUnitAbilityLevel(u,'B046')==1 then
call UnitRemoveAbility(u,'S015')
call UnitRemoveAbility(u,'B046')
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)+0.20)
call SaveReal(hash,u_Id,6,LoadReal(hash,u_Id,6)+0.30)
call SaveReal(hash,u_Id,47,LoadReal(hash,u_Id,47)+1.00)
call SaveReal(hash,u_Id,48,LoadReal(hash,u_Id,48)+1.00)
call SaveReal(hash,u_Id,49,LoadReal(hash,u_Id,49)+1.00)
call SaveReal(hash,u_Id,50,LoadReal(hash,u_Id,50)+1.00)
set t=LoadTimerHandle(hash,u_Id,'B046')
call FlushChildHashtable(hash,GetHandleId(t))
call PauseTimer(t)
call DestroyTimer(t)
call RemoveSavedHandle(hash,u_Id,'B046')
endif
set t=null
endfunction
```

---

## 投射物 —— 命中時會附帶狀態，技能只呼叫 CreateProjectile 是看不出來的

### `CreateProjectile`　war3map.j:3071（27 行）

```jass
function CreateProjectile takes unit u,integer dummy_Id,real speed,real dist,real x,real y,real angle,real dmg,real aoe,real size,string eff,string eff2 returns nothing
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
local unit u2
local player pl=GetOwningPlayer(u)
if eff !="none" then
call DestroyEffect(AddSpecialEffect(eff,x,y))
endif
set u2=CreateUnit(pl,dummy_Id,x,y,angle)
call SetUnitX(u2,x)
call SetUnitY(u2,y)
call SaveUnitHandle(hash,Id,1,u)
call SaveUnitHandle(hash,Id,2,u2)
call SaveReal(hash,Id,1,dmg)
call SaveReal(hash,Id,2,aoe)
call SaveInteger(hash,Id,2,-3)
call SaveReal(hash,Id,3,speed)
call SaveReal(hash,Id,4,dist)
call SaveReal(hash,Id,5,angle)
call SaveReal(hash,Id,6,0.)
call SaveReal(hash,Id,7,size)
call SaveStr(hash,Id,1,eff2)
call TimerStart(t,0.03,true,function ProjectileMove)
set t=null
set u2=null
set pl=null
endfunction
```

### `ProjectileMove`　war3map.j:2937（134 行）

```jass
function ProjectileMove takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u
local unit u2=LoadUnitHandle(hash,Id,2)
local integer u2_Id=GetUnitTypeId(u2)
local unit u3
local real x=GetUnitX(u2)
local real y=GetUnitY(u2)
local player pl
local real dmg=LoadReal(hash,Id,1)
local real aoe=LoadReal(hash,Id,2)
local real speed=LoadReal(hash,Id,3)
local real dist=LoadReal(hash,Id,4)
local real angle=LoadReal(hash,Id,5)
local real way=LoadReal(hash,Id,6)
local real size=LoadReal(hash,Id,7)
local string eff2=LoadStr(hash,Id,1)
local integer check=LoadInteger(hash,Id,2)
local group ug
local boolean B=false
local real r
local integer i
call SetUnitX(u2,PolarX(x,speed,angle))
call SetUnitY(u2,PolarY(y,speed,angle))
set check=check+1
set way=way+speed
if check==2 then
set check=0
set u=LoadUnitHandle(hash,Id,1)
set pl=GetOwningPlayer(u)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,size,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
set B=true
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
if IsTerrainPathable(x,y,PATHING_TYPE_WALKABILITY)then
set B=true
endif
if B==true then
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
if u2_Id=='o02G' or u2_Id=='o023' then
call BurnUnit(u,u3,dmg,0.50)
elseif u2_Id=='o002' then
if GetUnitAbilityLevel(u,'A0A2')==1 then
call BleedUnit(u,u3,dmg*1.50,1.00)
endif
call FrostUnit(u,u3,0.50)
elseif u2_Id=='o02Y' then
call FrostUnit(u,u3,1.00)
elseif u2_Id=='o02C' then
set i=GetUnitAbilityLevel(u,'A0XT')
if i !=0 then
call BurnUnit(u,u3,I2R(GetHeroStr(u,true))*(0.50+0.10*I2R(i)),0.35+0.05*I2R(i))
endif
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveUnit(u2)
if eff2 !="none" then
call DestroyEffect(AddSpecialEffect(eff2,x,y))
endif
set t=null
set u=null
set u2=null
set u3=null
set pl=null
return
endif
endif
call SaveInteger(hash,Id,2,check)
if way>=dist then
set u=LoadUnitHandle(hash,Id,1)
set pl=GetOwningPlayer(u)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,aoe,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)then
call UnitDamageTarget(u,u3,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,null)
if u2_Id=='o02G' or u2_Id=='o023' then
call BurnUnit(u,u3,dmg,0.50)
elseif u2_Id=='o002' then
if GetUnitAbilityLevel(u,'A0A2')==1 then
call BleedUnit(u,u3,dmg*1.50,1.00)
endif
call FrostUnit(u,u3,0.50)
elseif u2_Id=='o02Y' then
call FrostUnit(u,u3,1.00)
elseif u2_Id=='o02C' then
set i=GetUnitAbilityLevel(u,'A0XT')
if i !=0 then
call BurnUnit(u,u3,I2R(GetHeroStr(u,true))*(0.50+0.10*I2R(i)),0.35+0.05*I2R(i))
endif
endif
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
call PauseTimer(t)
call DestroyTimer(t)
call FlushChildHashtable(hash,Id)
call RemoveUnit(u2)
if eff2 !="none" then
call DestroyEffect(AddSpecialEffect(eff2,x,y))
endif
else
call SaveReal(hash,Id,6,way)
endif
set t=null
set u=null
set u2=null
set u3=null
set pl=null
set ug=null
endfunction
```

---

## 傷害管線 —— DefCof、穿透、反傷、苦難面具都在這一支

### `Trig_HeroTakeDamage_Actions`　war3map.j:19501（697 行）

```jass
function Trig_HeroTakeDamage_Actions takes nothing returns nothing
local real dmg=GetEventDamage()
local unit a=GetEventDamageSource()
local unit d=GetTriggerUnit()
local integer a_type=GetUnitTypeId(a)
local integer d_type=GetUnitTypeId(d)
local real life=GetWidgetLife(d)
local real life2=GetWidgetLife(a)
local real mana=GetUnitState(d,UNIT_STATE_MANA)
local real mana2=GetUnitState(a,UNIT_STATE_MANA)
local real DefLifePercent=UnitLifePercent(d)
local real DefCof=1.00
local real x
local real y
local real x2
local real y2
local real dist
local real angle
local integer L
local item Item
local integer ItemID
local integer Id
local timer t
local real r
local real r2
local real mask_dmg=0
local integer check=0
if d_type=='N02K' then
if GetUnitAbilityLevel(d,'A0B9')==1 then
call SetWidgetLife(d,life+dmg)
set r=LoadReal(hash,GetHandleId(d),'N02K')+dmg
call SaveReal(hash,GetHandleId(d),'N02K',r)
set a=null
set d=null
set Item=null
set t=null
return
else
call SaveInteger(hash,GetHandleId(d),'A0B7',8)
endif
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
if LoadReal(hash,GetHandleId(a),13)!=0 then
set Id=GetHandleId(a)
set r=LoadReal(hash,Id,13)
if r>0 then
set a=LoadUnitHandle(hash,Id,13)
call UnitDamageTarget(a,d,r,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
if a_type=='o02O' then
call BurnUnit(a,d,r*0.50,0.50)
elseif a_type=='o03I' then
call DiseaseUnit(a,d,r*2.00,0.50)
elseif a_type=='o03J' then
call DiseaseUnit(a,d,r*1.00,1.00)
endif
if LoadInteger(hash,Id,'A08Y')==1 then
if UnitAlive(d)then
call BurnUnit(a,d,r*1.00,1.00)
endif
endif
set a=null
set d=null
set Item=null
set t=null
return
endif
endif
if a_type=='n00O' then
call BurnUnit(a,d,dmg*1.50,0.20)
elseif a_type=='h01L' then
call FlammabilityUnit(a,d,0.30)
call BurnUnit(a,d,dmg*1.25,0.40)
elseif a_type=='n043' then
if GetPlayerTechCount(GetOwningPlayer(a),'Rhfc',true)==1 then
call FlammabilityUnit(a,d,0.30)
else
call FlammabilityUnit(a,d,0.20)
endif
call BurnUnit(a,d,dmg*0.50,0.60)
elseif a_type=='o00S' or a_type=='o00T' or a_type=='o00U' then
call FlammabilityUnit(a,d,0.15)
elseif a_type=='h01A' or a_type=='h01B' or a_type=='h029' then
call BurnUnit(a,d,dmg*1.00,0.15)
elseif a_type=='o029' then
if GetPlayerTechCount(GetOwningPlayer(a),'Rosp',true)==1 then
call FlammabilityUnit(a,d,1.00)
else
call FlammabilityUnit(a,d,0.35)
endif
call BurnUnit(a,d,dmg*1.50,1.00)
elseif a_type=='h02B' then
call FlammabilityUnit(a,d,0.15)
call BurnUnit(a,d,dmg*1.00,0.30)
elseif a_type=='n03V' then
call BurnUnit(a,d,dmg*1.00,0.60)
elseif a_type=='o01R' then
call BurnUnit(a,d,dmg*1.25,0.10)
elseif a_type=='nlv1' then
call FlammabilityUnit(a,d,0.30)
call BurnUnit(a,d,dmg*1.50,0.60)
elseif a_type=='nbdw' then
call BurnUnit(a,d,dmg*0.75,0.20)
elseif a_type=='uobs' then
call BurnUnit(a,d,dmg*0.75,0.30)
elseif a_type=='ndqt' then
call BurnUnit(a,d,dmg*1.00,0.25)
call BleedUnit(a,d,dmg*1.00,0.25)
elseif a_type=='ninf' then
call BurnUnit(a,d,dmg*0.50,0.50)
elseif a_type=='h02I' then
if GetUnitAbilityLevel(a,'A0GY')==1 then
call BurnUnit(a,d,dmg*1.25,0.40)
endif
elseif a_type=='hmtt' then
if GetUnitAbilityLevel(a,'A0XZ')==1 then
call BurnUnit(a,d,dmg*1.75,0.50)
endif
elseif a_type=='H00M' then
call BurnUnit(a,d,dmg*1.0,0.20)
endif
if a_type=='o00B' then
call BleedUnit(a,d,dmg*1.5,0.10)
elseif a_type=='e00E' or a_type=='e00L' then
call BleedUnit(a,d,dmg*1.25,0.20)
elseif a_type=='e006' then
call BleedUnit(a,d,dmg*1.0,0.10)
elseif a_type=='h00K' then
call BleedUnit(a,d,dmg*1.50,0.30)
elseif a_type=='n03U' then
call BleedUnit(a,d,dmg*0.5,0.50)
elseif a_type=='ugar' then
call BleedUnit(a,d,dmg*1.00,0.50)
elseif a_type=='h03H' then
call BleedUnit(a,d,dmg*1.50,0.30)
elseif a_type=='n05S' then
call BleedUnit(a,d,dmg*1.00,1.00)
elseif a_type=='uske' then
call BleedUnit(a,d,dmg*1.50,0.10)
elseif a_type=='u00L' then
call BleedUnit(a,d,dmg*1.00,0.30)
elseif a_type=='u01G' then
call BleedUnit(a,d,dmg*1.25,0.40)
elseif a_type=='ugho' then
call BleedUnit(a,d,dmg*0.75,0.15)
elseif a_type=='n00X' then
call BleedUnit(a,d,dmg*1.25,0.25)
elseif a_type=='n058' then
call BleedUnit(a,d,dmg*2.00,0.25)
elseif a_type=='n057' then
call BleedUnit(a,d,dmg*1.00,0.75)
elseif a_type=='U00N' then
call BleedUnit(a,d,dmg*1.00,0.33)
elseif a_type=='h011' then
if GetUnitAbilityLevel(a,'A0Y0')==1 then
call BleedUnit(a,d,dmg*1.50,0.40)
endif
endif
if a_type=='n055' or a_type=='n03K' or a_type=='n01Z' then
call FrostUnit(a,d,0.30)
elseif a_type=='n053' then
call FrostUnit(a,d,0.50)
elseif a_type=='n041' or a_type=='n06L' or a_type=='n06S' or a_type=='n06U' or a_type=='n06V' then
if GetPlayerTechCount(GetOwningPlayer(a),'Rufb',true)==1 then
call FrostUnit(a,d,10.00)
else
call FrostUnit(a,d,0.50)
endif
elseif a_type=='nntg' then
if GetUnitAbilityLevel(a,'A0YB')==1 then
call FrostUnit(a,d,0.20)
call ShockUnit(a,d,0.20)
endif
endif
if LoadInteger(hash,GetHandleId(a),45)>0 then
call DiseaseUnit(a,d,dmg*1.75,0.20)
endif
if a_type=='u00C' then
call DiseaseUnit(a,d,dmg*1.5,0.40)
elseif a_type=='umtw' then
call DiseaseUnit(a,d,dmg*1.5,0.40)
elseif a_type=='n01Y' then
call DiseaseUnit(a,d,dmg*2.0,0.30)
elseif a_type=='ucry' then
call BleedUnit(a,d,dmg*2.0,0.30)
call DiseaseUnit(a,d,dmg*2.0,0.30)
elseif a_type=='ndqv' then
call DiseaseUnit(a,d,dmg*2.0,1.00)
elseif a_type=='e00K' or a_type=='e00Y' or a_type=='e015' then
if GetUnitAbilityLevel(d,'B006')==1 then
set life2=life2+dmg*0.50
call SetWidgetLife(a,life2)
endif
if a_type=='e015' then
call DiseaseUnit(a,d,dmg*2.50,0.60)
elseif a_type=='e00Y' then
call DiseaseUnit(a,d,dmg*2.00,0.60)
else
call DiseaseUnit(a,d,dmg*1.50,0.60)
endif
if UpgradeCheck_Rupc[GetPlayerId(GetOwningPlayer(a))]==1 then
call CurseUnit(a,d,0.40)
endif
endif
if a_type=='ngrk' then
call WeakUnit(a,d,0.12)
elseif a_type=='Othr' then
call ShockUnit(a,d,0.20)
elseif a_type=='n04L' then
call ShockUnit(a,d,0.25)
elseif a_type=='n06F' then
if GetUnitAbilityLevel(a,'A0Y1')==1 then
call ShockUnit(a,d,0.20)
endif
elseif a_type=='o01E' then
if GetUnitAbilityLevel(a,'A0YA')==1 then
call FlammabilityUnit(a,d,0.50)
endif
elseif a_type=='uzg2' then
if GetUnitAbilityLevel(a,'A0ZT')==1 then
call CurseUnit(a,d,0.50)
endif
if GetUnitAbilityLevel(a,'A0ZU')==1 then
call FrostUnit(a,d,0.50)
endif
endif
if a_type=='nbt2' then
if not IsUnitType(d,UNIT_TYPE_STRUCTURE)then
if IsUnitType(d,UNIT_TYPE_HERO)then
call StunUnit(a,d,2,0.20)
else
call StunUnit(a,d,3,0.20)
endif
endif
endif
if a_type=='opeo' then
if IsUnitType(d,UNIT_TYPE_STRUCTURE)and GetUnitLevel(d)==0 then
set DefCof=DefCof+4.00
endif
endif
if GetUnitAbilityLevel(a,'A0JO')==1 then
if mana2>(GetUnitState((a),UNIT_STATE_MAX_MANA))*0.1 then
if UpgradeCheck_Rhpt[GetPlayerId(GetOwningPlayer(a))]==1 and(a_type=='h022' or a_type=='h030' or a_type=='h02D')then
set DefCof=DefCof+0.60
else
set DefCof=DefCof+0.30
endif
endif
endif
if GetUnitAbilityLevel(d,'A0JO')==1 then
if mana>(GetUnitState((d),UNIT_STATE_MAX_MANA))*0.1 then
if UpgradeCheck_Rhpt[GetPlayerId(GetOwningPlayer(d))]==1 and(d_type=='h022' or d_type=='h030' or d_type=='h02D')then
set DefCof=DefCof-0.60
call SetUnitState(d,UNIT_STATE_MANA,mana-dmg)
else
set DefCof=DefCof-0.30
if d_type=='h00K' and IsUnitType(a,UNIT_TYPE_HERO)==true then
call SetUnitState(d,UNIT_STATE_MANA,mana-(dmg*0.25))
else
call SetUnitState(d,UNIT_STATE_MANA,mana-(dmg*0.50))
endif
endif
endif
endif
if d_type=='h01T' then
if UpgradeCheck_Reeb[GetPlayerId(GetOwningPlayer(d))]==1 then
if GetUnitAbilityLevel(a,'B045')==1 then
set DefCof=DefCof-0.25
endif
endif
endif
if GetUnitAbilityLevel(d,'B03B')==1 then
set DefCof=DefCof+0.10
endif
if GetUnitAbilityLevel(d,'B01G')==1 then
set life=life+4.0
set DefCof=DefCof-0.20
endif
if GetUnitAbilityLevel(a,'A0ZK')==1 then
call FlammabilityUnit(a,d,0.10)
endif
if GetUnitAbilityLevel(d,'A0RI')==1 then
set life=life+1.0
call SetWidgetLife(d,life)
endif
if GetUnitAbilityLevel(d,'B03I')==1 then
set DefCof=DefCof-(0.12+0.08*I2R(GetUnitAbilityLevel(d,'Absk')))
endif
if GetUnitAbilityLevel(d,'A01X')==1 then
if a_type=='Hmkg' then
if GetUnitAbilityLevel(a,'A01Y')==1 then
set DefCof=DefCof+0.50
else
set DefCof=DefCof+0.25
endif
endif
endif
if GetUnitAbilityLevel(d,'B033')==1 and a_type=='N05T' then
set DefCof=DefCof+0.25
endif
if a_type=='o02P' then
if GetUnitAbilityLevel(a,'A0YC')==1 and GetUnitAbilityLevel(d,'B045')==1 then
set DefCof=DefCof+1.00
endif
endif
if GetUnitAbilityLevel(a,'A089')==1 then
if DefLifePercent<UnitLifePercent(a)then
set DefCof=DefCof+0.20
endif
endif
if GetUnitAbilityLevel(a,'A02E')==1 then
if GetUnitAbilityLevel(d,'BPSE')==1 or GetUnitAbilityLevel(d,'BSTN')==1 then
set DefCof=DefCof+0.20
endif
endif
if GetUnitAbilityLevel(a,'A0MQ')==1 and IsUnitType(d,UNIT_TYPE_HERO)then
set DefCof=DefCof+0.75
endif
if GetUnitAbilityLevel(d,'A0MQ')==1 and IsUnitType(a,UNIT_TYPE_HERO)then
set DefCof=DefCof-0.25
endif
if udg_Modifiers[12]!=true then
if GetUnitAbilityLevel(d,'B01T')>0 and d !=RuneDefender then
set DefCof=DefCof-0.30
call UnitDamageTarget(a,RuneDefender,(dmg*0.15),true,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
endif
else
if GetUnitAbilityLevel(d,'B01T')>0 then
set DefCof=DefCof-0.15
endif
endif
if GetUnitAbilityLevel(a,'B048')>=1 then
set L=GetPlayerId(GetOwningPlayer(a))+1
set DefCof=DefCof+(0.02+0.02*I2R(GetUnitAbilityLevel(udg_Hero[L],'A10E'))+udg_ItemBonusDMG[L]*0.01)
endif
if GetUnitAbilityLevel(d,'B048')>=1 then
set L=GetPlayerId(GetOwningPlayer(d))+1
set DefCof=DefCof-(0.02+0.02*I2R(GetUnitAbilityLevel(udg_Hero[L],'A10E'))+udg_ItemBonusDMG[L]*0.01)
endif
if LoadInteger(hash,GetHandleId(d),6)>=6 and GetUnitLevel(a)<=4 then
set DefCof=DefCof-0.40
endif
if LoadInteger(hash,GetHandleId(d),9)>=5 then
call SetUnitState(d,UNIT_STATE_MANA,(mana+1.00))
endif
if IsUnitType(d,UNIT_TYPE_HERO)then
set DefCof=DefCof+LoadReal(hash,GetHandleId(a),3)
endif
if GetUnitLevel(d)<=1 then
set DefCof=DefCof+LoadReal(hash,GetHandleId(a),5)
endif
if IsUnitType(d,UNIT_TYPE_MELEE_ATTACKER)then
set DefCof=DefCof+LoadReal(hash,GetHandleId(a),40)
endif
if IsUnitType(d,UNIT_TYPE_RANGED_ATTACKER)then
set DefCof=DefCof+LoadReal(hash,GetHandleId(a),41)
endif
set DefCof=DefCof+LoadReal(hash,GetHandleId(a),6)
if IsUnitType(d,UNIT_TYPE_UNDEAD)then
set DefCof=DefCof+LoadReal(hash,GetHandleId(a),9)
endif
set DefCof=DefCof-LoadReal(hash,GetHandleId(d),4)
if IsUnitType(a,UNIT_TYPE_HERO)then
set DefCof=DefCof-LoadReal(hash,GetHandleId(d),8)
endif
if IsUnitType(a,UNIT_TYPE_MELEE_ATTACKER)then
set DefCof=DefCof-LoadReal(hash,GetHandleId(d),42)
endif
if IsUnitType(a,UNIT_TYPE_RANGED_ATTACKER)then
set DefCof=DefCof-LoadReal(hash,GetHandleId(d),43)
endif
if GetUnitLevel(a)<2 then
set DefCof=DefCof-LoadReal(hash,GetHandleId(d),12)
endif
if IsUnitType(a,UNIT_TYPE_UNDEAD)then
set DefCof=DefCof-LoadReal(hash,GetHandleId(d),15)
endif
set Id=GetHandleId(d)
if LoadInteger(hash,Id,'I07A')>=1 then
if DefLifePercent<=25.00 then
set life=life+5.0
call SetWidgetLife(d,life)
endif
endif
if LoadInteger(hash,Id,'I048')>=1 then
if DefLifePercent<=30.00 then
set DefCof=DefCof-0.25
endif
endif
if LoadInteger(hash,Id,'pman')>=1 then
if UnitLifePercent(a)>=75.00 then
set DefCof=DefCof-0.18
endif
endif
if LoadInteger(hash,Id,'tbak')>=1 then
if UnitLifePercent(a)>=75.00 then
set DefCof=DefCof-0.25
endif
endif
if LoadInteger(hash,Id,'tkno')>=1 then
set life=life+2.0
call SetWidgetLife(d,life)
endif
if LoadInteger(hash,Id,'will')>=1 then
set DefCof=DefCof-0.10
call SetUnitState(d,UNIT_STATE_MANA,(mana+dmg*0.10))
endif
if LoadInteger(hash,Id,'I0AB')>=1 then
set DefCof=DefCof-(((100-DefLifePercent)/2.5)*0.01)
endif
if LoadInteger(hash,Id,'I0AY')>=1 then
if GetUnitAbilityLevel(d,'B00Z')==1 then
set DefCof=DefCof-0.20
endif
endif
if LoadInteger(hash,Id,'I053')>=1 then
if DefLifePercent>=50.00 then
set DefCof=DefCof+0.50
endif
endif
if LoadInteger(hash,Id,'rre2')>=1 then
if DefLifePercent>=75.00 then
set DefCof=DefCof+1.00
endif
endif
set Id=GetHandleId(a)
if LoadInteger(hash,Id,'hlst')>=1 then
if DefLifePercent>=75.00 then
set DefCof=DefCof+1.00
elseif GetUnitAbilityLevel(d,'B02V')==1 and DefLifePercent>=50.00 then
set DefCof=DefCof+1.00
endif
endif
if LoadInteger(hash,Id,'I06V')>=1 then
if DefLifePercent<50.00 then
set DefCof=DefCof+0.40
endif
endif
if LoadInteger(hash,Id,'I099')>=1 then
if mana2>=1000.00 then
set DefCof=DefCof+0.20
endif
endif
if LoadInteger(hash,Id,'I0AY')>=1 then
if GetUnitAbilityLevel(d,'B00Z')==1 and GetUnitLevel(d)<=1 then
set DefCof=DefCof+0.50
endif
endif
if LoadInteger(hash,Id,'I07P')>=1 then
if life2<(GetUnitState((a),UNIT_STATE_MAX_LIFE))*0.5 then
set DefCof=DefCof-0.35
endif
endif
if LoadInteger(hash,Id,'I016')>=1 or LoadInteger(hash,Id,'I09Y')>=1 then
if GetUnitAbilityLevel(d,'B006')==1 then
set DefCof=DefCof+0.30
endif
endif
if LoadInteger(hash,Id,'ktrm')>=1 then
if GetUnitAbilityLevel(d,'BPSE')==1 or GetUnitAbilityLevel(d,'BSTN')==1 then
set DefCof=DefCof+0.35
endif
if GetUnitAbilityLevel(d,'B02V')==1 then
set DefCof=DefCof+0.35
endif
endif
if LoadInteger(hash,Id,'I07G')>=1 then
if GetUnitAbilityLevel(d,'B02V')==1 then
set DefCof=DefCof+0.20
endif
endif
if LoadInteger(hash,Id,'arsc')>=1 then
if life>life2 then
set DefCof=DefCof+0.50
endif
endif
if LoadInteger(hash,Id,'fgfh')>=1 then
set check=1
endif
if d_type=='njga' then
set Id=GetHandleId(d)
if DefCof<0.20 then
set r=LoadReal(hash,Id,'njga')+dmg*0.20
else
set r=LoadReal(hash,Id,'njga')+dmg*DefCof
endif
if r>=175.00 then
set r=r-175.00
set t=CreateTimer()
call SetUnitAttackSpeed(d,GetUnitAttackSpeed(d)+10)
call SetUnitLifeRegeneration(d,GetUnitLifeRegeneration(d)+4.0)
call SaveUnitHandle(hash,GetHandleId(t),1,d)
call TimerStart(t,15.,false,function TakeDmg_Buff)
if UpgradeCheck_Robf[GetPlayerId(GetOwningPlayer(d))]==1 then
call SaveInteger(hash,GetHandleId(t),1,1)
call SetUnitExtraArmor(d,GetUnitExtraArmor(d)+2)
call SetUnitExtraDamage(d,GetUnitExtraDamage(d)+3)
endif
endif
call SaveReal(hash,Id,'njga',r)
endif
if LoadInteger(hash,GetHandleId(a),'Rows')==1 then
if IsUnitType(d,UNIT_TYPE_STRUCTURE)then
if DefCof<0.20 then
set life2=life2+dmg*0.20
call SetWidgetLife(a,life2)
else
set life2=life2+dmg*(DefCof-1.00)
call SetWidgetLife(a,life2)
endif
endif
endif
call DisableTrigger(GetTriggeringTrigger())
if LoadInteger(hash,GetHandleId(d),'I070')>=1 then
set L=GetRandomInt(1,100)
if L<=20 then
if DefCof<0.20 then
set DefCof=0.20
endif
call BurnUnit(a,d,(dmg*DefCof)+LoadReal(hash,GetHandleId(a),16),1.00)
call SetWidgetLife(d,life+dmg)
endif
set a=null
set d=null
set Item=null
set t=null
return
endif
if DefCof<1.00 then
if DefCof<0.20 then
set DefCof=0.20
endif
set life=life+dmg*(1.00-DefCof)
call SetWidgetLife(d,life)
elseif DefCof>1.00 then
call UnitDamageTarget(a,d,dmg*(DefCof-1.00),false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
endif
set life=LoadReal(hash,GetHandleId(a),16)
if life>0.00 then
if IsUnitType(d,UNIT_TYPE_STRUCTURE)!=true then
if GetUnitAbilityLevel(d,'B02V')==1 then
if check==1 and IsUnitType(d,UNIT_TYPE_HERO)then
set life=life*2.00
else
set life=life*1.50
endif
else
if check==1 and IsUnitType(d,UNIT_TYPE_HERO)then
set life=life*1.50
endif
endif
if GetUnitAbilityLevel(d,'B01S')>0 then
set life=life*(0.90-0.10*I2R(GetUnitAbilityLevel(d,'A0G0')))
endif
call UnitDamageTarget(a,d,life,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
endif
endif
if LoadInteger(hash,GetHandleId(d),'I068')>=1 then
if IsUnitType(a,UNIT_TYPE_HERO)then
call UnitDamageTarget(d,a,(dmg+life)*0.20,false,false,ATTACK_TYPE_CHAOS,DAMAGE_TYPE_UNIVERSAL,WEAPON_TYPE_WHOKNOWS)
endif
endif
if a_type=='Nngs' or a_type=='Nplh' then
if IsUnitType(d,UNIT_TYPE_HERO)and IsUnitEnemy(d,GetOwningPlayer(a))then
set r=dmg*DefCof+life
call SaveReal(hash,GetHandleId(a),'ST03',LoadReal(hash,GetHandleId(a),'ST03')+r)
set r=r+LoadReal(hash,GetHandleId(a),'ST01')
set r2=LoadReal(hash,GetHandleId(a),'ST02')
if r>=r2 then
loop
exitwhen r<r2
call SetUnitBaseDamage(a,GetUnitBaseDamage(a)+1)
call SetUnitLife(a,R2I((GetUnitState((a),UNIT_STATE_MAX_LIFE)))+15)
set r=r-r2
set r2=r2+10.
call SaveReal(hash,GetHandleId(a),'ST02',r2)
endloop
endif
call SaveReal(hash,GetHandleId(a),'ST01',r)
endif
endif
if a_type=='E00J' then
if IsUnitEnemy(d,GetOwningPlayer(a))then
set r=dmg*DefCof+life
set r=r+LoadReal(hash,GetHandleId(a),'ST01')
set r2=LoadReal(hash,GetHandleId(a),'ST02')
if r>=r2 then
loop
exitwhen r<r2
call SaveReal(hash,GetHandleId(a),16,LoadReal(hash,GetHandleId(a),16)+0.5)
set r=r-r2
set r2=r2+35.
call SaveReal(hash,GetHandleId(a),'ST02',r2)
endloop
endif
call SaveReal(hash,GetHandleId(a),'ST01',r)
endif
endif
if a_type=='Etyr' then
if IsUnitEnemy(d,GetOwningPlayer(a))then
set r=dmg*DefCof+life
set r=r+LoadReal(hash,GetHandleId(a),'ST01')
set r2=LoadReal(hash,GetHandleId(a),'ST02')
if r>=r2 then
loop
exitwhen r<r2
call SetHeroAgi(a,GetHeroAgi(a,false)+1,true)
set r=r-r2
set r2=r2+250.
call SaveReal(hash,GetHandleId(a),'ST02',r2)
endloop
endif
call SaveReal(hash,GetHandleId(a),'ST01',r)
endif
endif
if a_type=='Hmgd' then
if IsUnitEnemy(d,GetOwningPlayer(a))then
set r=dmg*DefCof+life
set r=r+LoadReal(hash,GetHandleId(a),'ST01')
set r2=LoadReal(hash,GetHandleId(a),'ST02')
if r>=r2 then
loop
exitwhen r<r2
call SetUnitBaseDamage(a,GetUnitBaseDamage(a)+1)
call SaveReal(hash,GetHandleId(a),16,LoadReal(hash,GetHandleId(a),16)+0.35)
set r=r-r2
set r2=r2+35.
call SaveReal(hash,GetHandleId(a),'ST02',r2)
endloop
endif
call SaveReal(hash,GetHandleId(a),'ST01',r)
endif
elseif d_type=='Hmgd' then
if IsUnitEnemy(a,GetOwningPlayer(d))then
set r=dmg*DefCof
set r=r+LoadReal(hash,GetHandleId(d),'ST03')
set r2=LoadReal(hash,GetHandleId(d),'ST04')
if r>=r2 then
loop
exitwhen r<r2
call SetUnitLife(d,R2I((GetUnitState((d),UNIT_STATE_MAX_LIFE)))+15)
call SetUnitLifeRegeneration(d,GetUnitLifeRegeneration(d)+0.50)
set r=r-r2
set r2=r2+30.
call SaveReal(hash,GetHandleId(d),'ST04',r2)
endloop
endif
call SaveReal(hash,GetHandleId(d),'ST03',r)
endif
endif
if d_type=='Uclc' then
set r=dmg*DefCof+life
set r=r+LoadReal(hash,GetHandleId(d),'Uclc')
if r>=1000.00 then
loop
exitwhen r<1000.00
set x=GetUnitX(d)
set y=GetUnitY(d)
set dist=GetRandomReal(100.,200.)
set angle=GetRandomReal(0.,360.)
set x2=PolarX(x,dist,angle)
set y2=PolarY(y,dist,angle)
call DestroyEffect(AddSpecialEffect("Objects\\Spawnmodels\\Demon\\DemonSmallDeathExplode\\DemonSmallDeathExplode.mdl",x2,y2))
call SpawnEnemy('nhyd',Location(x2,y2),udg_AttackGroup,0)
set r=r-1000.00
endloop
endif
if r<0.00 then
set r=0.00-r
endif
call SaveReal(hash,GetHandleId(d),'Uclc',r)
endif
call EnableTrigger(GetTriggeringTrigger())
set a=null
set d=null
set Item=null
set t=null
endfunction
```

---

## 道具觸發的入口 —— 注意它們各自的過濾條件

### `Trig_ItemAttacksFromHero_Conditions`　war3map.j:27470（3 行）

```jass
function Trig_ItemAttacksFromHero_Conditions takes nothing returns boolean
return IsUnitEnemy(GetTriggerUnit(),GetOwningPlayer(GetAttacker()))and IsUnitType(GetAttacker(),UNIT_TYPE_HERO)
endfunction
```

### `Trig_ItemKills_Conditions`　war3map.j:29434（3 行）

```jass
function Trig_ItemKills_Conditions takes nothing returns boolean
return IsUnitEnemy(GetDyingUnit(),GetOwningPlayer(GetKillingUnit()))and GetUnitLevel(GetDyingUnit())!=0
endfunction
```

### `Trig_UseSkillsEndcast_Conditions`　war3map.j:28632（3 行）

```jass
function Trig_UseSkillsEndcast_Conditions takes nothing returns boolean
return IsUnitType(GetSpellAbilityUnit(),UNIT_TYPE_HERO)and GetSpellAbilityId()!='A03V' and GetSpellAbilityId()!='A0OX' and GetSpellAbilityId()!='A0JY' and GetSpellAbilityId()!='A0AE' and GetSpellAbilityId()!='A06Q' and GetSpellAbilityId()!='A01Z' and GetSpellAbilityId()!='A020' and GetSpellAbilityId()!='A0FX' and GetSpellAbilityId()!='A0BH' and GetSpellAbilityId()!='A021' and GetSpellAbilityId()!='A074' and GetSpellAbilityId()!='A0BG' and GetSpellAbilityId()!='A0BF' and GetSpellAbilityId()!='A04E'
endfunction
```

### `StartModCooldown`　war3map.j:2914（14 行）

```jass
function StartModCooldown takes integer u_Id,integer i_Id,real CD returns nothing
local real CDCof=LoadReal(hash,u_Id,1)
local timer t=CreateTimer()
if CDCof<0.20 then
set CDCof=0.20
endif
set CD=CD*CDCof
call SaveReal(hash,u_Id,i_Id,1.)
set t=CreateTimer()
call SaveInteger(hash,GetHandleId(t),1,u_Id)
call SaveInteger(hash,GetHandleId(t),2,i_Id)
call TimerStart(t,CD,false,function EndModCooldown)
set t=null
endfunction
```

---

*由 `tools/build_engineref.py` 從 UD_v3.81 地圖檔產生。*
