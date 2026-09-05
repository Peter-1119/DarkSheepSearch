# 皇家守衛 `Hapm`（Королевский страж）

主屬性 **力量** · 背包 **6 格** · 解鎖 0 · 定位 坦克/輔助/戰士

| | 初始 | 每級 |
|---|---|---|
| 力量 | （未覆寫） | （未覆寫） |
| 敏捷 | （未覆寫） | （未覆寫） |
| 智力 | （未覆寫） | （未覆寫） |

> 近戰英雄，可走多種路線。裝備類乘數對他影響特別大。

**縮放**：吃技能強度的技能 ['A01B', 'A01C', 'A01E', 'A07U', 'A0Y5'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

**傷害／效果走哪條管線**（決定哪些裝備對這隻有用）：

- **技能直接傷害** —— 走 `Trig_HeroTakeDamage_Actions` → **吃 DefCof（key 3/5/6/9/40/41）也吃穿透**，而且傷害事件數越多，穿透越划算。
- **屬性增益** —— 直接改屬性。注意有些是**永久**的（死亡不歸零），長局會滾雪球。

細節見 `data/dossier/_engine.md`。


---

## 堅忍 `A07U`　—　吃技能強度

俄文原名：Выдержка

```
生命值低於 50% 時，英雄的攻擊獲得濺射效果，並提升傷害防護。

濺射效果強度：350 點範圍內 35%
傷害防護提升：+20%
技能強度 200 以上：攻擊速度 +25%
```

物件欄位（原型 `Amgl`）：`aher = 1`

實作：

`Trig_HeroR2_Conditions`　war3map.j:46949
```jass
function Trig_HeroR2_Conditions takes nothing returns boolean
return GetLearnedSkill()=='A07U'
endfunction
```

`Trig_HeroR2_Actions`　war3map.j:46978
```jass
function Trig_HeroR2_Actions takes nothing returns nothing
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
local unit u=GetLearningUnit()
call TimerStart(t,1.,true,function HeroR2_check)
call SaveUnitHandle(hash,Id,1,u)
set t=null
set u=null
endfunction
```

`Trig_HeroR2_Conditions`　war3map.j:46949
```jass
function Trig_HeroR2_Conditions takes nothing returns boolean
return GetLearnedSkill()=='A07U'
endfunction
function HeroR2_check takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local integer u_Id=GetHandleId(u)
local integer n=GetPlayerId(GetOwningPlayer(u))+1
if UnitAlive(u)then
if UnitLifePercent(u)<50.00 then
if GetUnitAbilityLevel(u,'A01G')!=1 then
call UnitAddAbility(u,'A01G')
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)+0.20)
if udg_ItemBonusDMG[n]>=200 and GetUnitAbilityLevel(u,'A0R5')!=1 then
call UnitAddAbility(u,'A0R5')
endif
endif
else
if GetUnitAbilityLevel(u,'A01G')==1 then
call UnitRemoveAbility(u,'A01G')
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)-0.20)
call UnitRemoveAbility(u,'A0R5')
endif
endif
endif
set t=null
set u=null
endfunction
function Trig_HeroR2_Actions takes nothing returns nothing
local timer t=CreateTimer()
local integer Id=GetHandleId(t)
local unit u=GetLearningUnit()
call TimerStart(t,1.,true,function HeroR2_check)
call SaveUnitHandle(hash,Id,1,u)
set t=null
set u=null
endfunction
```

## 信仰之盾 `A01E`　—　吃技能強度

俄文原名：Щит веры

```
暫時提升 700 點範圍內友軍的護甲，並少量治療部隊。處於「鼓舞」技能效果下的單位可獲得 600% 的治療量。

護甲加成：4 點
加成持續時間：12 秒。
治療：20 + （10% 技能強度）點

冷卻：24 秒。
```

每級變動：
  - 第 3 行：4 / 8 / 12 / 16 / 20
  - 第 5 行：20 / 30 / 40 / 50 / 60

物件欄位（原型 `AIda`）：`Idef = [4, 8, 12, 16, 20]`, `aare = 700.0`, `abuf = B005`, `acdn = 24.0`, `adur = 12.5`, `ahdu = 12.5`, `aher = 1`, `aite = 0`, `alev = 5`, `amcs = [60, 70, 80, 90, 100]`, `aran = 350.0`, `atar = ground,air,friend,self,invu,vuln`

實作：

`Trig_HeroSkills2_Actions`　war3map.j:46911
```jass
elseif Skill=='A01E' or Skill=='A0RM' then
set x=GetUnitX(u)
set y=GetUnitY(u)
set ug=CreateGroup()
if Skill=='A01E' then
set dmg=10+(10*I2R(GetUnitAbilityLevel(u,Skill)))+udg_ItemBonusDMG[n]*0.10
call GroupEnumUnitsInRange(ug,x,y,700,null)
else
set dmg=20+(20*I2R(GetUnitAbilityLevel(u,Skill)))+udg_ItemBonusDMG[n]*0.20
call GroupEnumUnitsInRange(ug,x,y,350,null)
endif
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if UnitAlive(u2)and IsUnitAlly(u2,pl)and IsUnitType(u2,UNIT_TYPE_STRUCTURE)==false then
set r=GetUnitState(u2,UNIT_STATE_LIFE)
if LoadInteger(hash,GetHandleId(u2),'A01C')>=1 then
call SetUnitState(u2,UNIT_STATE_LIFE,r+(dmg*6))
else
call SetUnitState(u2,UNIT_STATE_LIFE,r+dmg)
endif
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
endif
```

## 鼓舞 `A01C`　—　吃技能強度

俄文原名：Воодушевление

```
提升指定目標的攻擊力。若目標為英雄，則額外降低該目標的裝備技能冷卻。一般部隊獲得 150% 的攻擊力加成。

攻擊力加成：15 + （12% 技能強度）點
裝備技能冷卻（英雄）：-15%
攻擊力加成（部隊）：
持續時間：15 秒。

冷卻：15 秒。
```

每級變動：
  - 第 3 行：15 / 30 / 45 / 60 / 75
  - 第 4 行：15 / 20 / 25 / 30 / 35

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = [None, 'channel']`, `acdn = 15.0`, `alev = 5`, `amcs = [60, 68, 76, 84, 92]`, `aran = 800.0`, `atar = air,ground,friend,neutral,self`

實作：

`Hero2Q`　war3map.j:46808
```jass
if count<=0 or not UnitAlive(u)then
call SaveInteger(hash,GetHandleId(u),'A01C',LoadInteger(hash,GetHandleId(u),'A01C')-1)
call DestroyEffect(LoadEffectHandle(hash,GetHandleId(t),2))
call SetUnitExtraDamage(u,GetUnitExtraDamage(u)-LoadInteger(hash,GetHandleId(t),1))
if IsUnitType(u,UNIT_TYPE_HERO)then
call SaveReal(hash,GetHandleId(u),1,LoadReal(hash,GetHandleId(u),1)+LoadReal(hash,GetHandleId(t),1))
endif
call PauseTimer(t)
call FlushChildHashtable(hash,GetHandleId(t))
call DestroyTimer(t)
endif
```

`Trig_HeroSkills2_Actions`　war3map.j:46859
```jass
if Skill=='A01C' then
set t=CreateTimer()
set Id=GetHandleId(t)
call SaveUnitHandle(hash,Id,1,u2)
call SaveInteger(hash,GetHandleId(u2),'A01C',LoadInteger(hash,GetHandleId(u2),'A01C')+1)
call SaveEffectHandle(hash,Id,2,AddSpecialEffectTarget("Raise_Morale_Buff.mdx",u2,"overhead"))
set count=15*GetUnitAbilityLevel(u,Skill)+R2I(udg_ItemBonusDMG[n]*0.12)
if IsUnitType(u2,UNIT_TYPE_HERO)then
call SaveInteger(hash,Id,1,count)
call SetUnitExtraDamage(u2,GetUnitExtraDamage(u2)+count)
set r=0.10+0.05*I2R(GetUnitAbilityLevel(u,Skill))
call SaveReal(hash,Id,1,r)
call SaveReal(hash,GetHandleId(u2),1,LoadReal(hash,GetHandleId(u2),1)-r)
else
set count=count+count/2
call SaveInteger(hash,Id,1,count)
call SetUnitExtraDamage(u2,GetUnitExtraDamage(u2)+count)
endif
call SaveInteger(hash,Id,2,15)
call TimerStart(t,1.,true,function Hero2Q)
```

`Trig_HeroSkills2_Actions`　war3map.j:46927
```jass
if LoadInteger(hash,GetHandleId(u2),'A01C')>=1 then
call SetUnitState(u2,UNIT_STATE_LIFE,r+(dmg*6))
```

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

## 雷霆一擊 `A01B`　—　吃技能強度

俄文原名：Громовой удар

```
對英雄周圍的敵人造成傷害並使其減速。此技能的傷害會隨著失去的生命值而提高。

傷害：50 + （50% 技能強度）
減速強度：-50% 移動速度，-50% 攻擊速度
減速時間（部隊）：5 秒。
減速時間（英雄）：3 秒。

冷卻：9 秒。
```

每級變動：
  - 第 3 行：50 / 100 / 150 / 200 / 250
  - 第 5 行：5 / 5.5 / 6 / 6.5 / 7
  - 第 6 行：3 / 3.3 / 3.6 / 3.9 / 4.2

物件欄位（原型 `AHtc`）：`Htc1 = 1.0`, `aare = [300.0, None]`, `acdn = 9.0`, `adur = [None, 5.5, 6.0, 6.5, 7.0]`, `ahdu = [None, 3.299999952316284, 3.5999999046325684, 3.8999998569488525, 4.199999809265137]`, `alev = 5`, `amcs = [85, 95, 105, 115, 125]`

實作：

`Trig_HeroSkills2_Actions`　war3map.j:46879
```jass
elseif Skill=='A01B' then
if GetUnitAbilityLevel(u,'A0RI')==1 then
call ClearUnit(u)
endif
set dmg=50.00*I2R(GetUnitAbilityLevel(u,Skill))+udg_ItemBonusDMG[n]*0.50
set dmg=dmg*(1+(100-UnitLifePercent(u))*0.01)
set x=GetUnitX(u)
set y=GetUnitY(u)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,305,null)
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if UnitAlive(u2)and IsUnitEnemy(u2,pl)then
if GetUnitAbilityLevel(u,'A0RI')==1 then
call UnitRemoveBuffs(u2,true,false)
endif
call UnitDamageTarget(u,u2,dmg,false,false,ATTACK_TYPE_NORMAL,DAMAGE_TYPE_MAGIC,WEAPON_TYPE_WHOKNOWS)
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
set f=CreateForce()
call ForceAddPlayer(f,pl)
set text=CreateTextTagUnitBJ(("|cFFFF4B39"+I2S(R2I(dmg))),u,0,14.00,100,100,100,0)
call ShowTextTagForceBJ(false,text,bj_FORCE_ALL_PLAYERS)
call ShowTextTagForceBJ(true,text,f)
call SetTextTagVelocityBJ(text,75.00,90.00)
call SetTextTagSuspended(text,false)
call SetTextTagPermanent(text,false)
call SetTextTagLifespan(text,3.00)
call SetTextTagFadepoint(text,2.00)
```

## 聖物守衛 `A0Y5`　—　吃技能強度

俄文原名：Страж реликвария

```
物品中的倍增效果對此英雄產生雙倍效果。
```

實作：

`PercentStatsRefresh`　war3map.j:21797
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set i=LoadInteger(hash,I_Id,1)
set MainStat=GetHeroStr(u,false)
set i2=(MainStat-i)/2
if i !=i2 then
call SetHeroStr(u,MainStat-i+i2,true)
endif
call SaveInteger(hash,I_Id,1,i2)
set i=LoadInteger(hash,I_Id,2)
set MainStat=GetHeroAgi(u,false)
set i2=(MainStat-i)/2
if i !=i2 then
call SetHeroAgi(u,MainStat-i+i2,true)
endif
call SaveInteger(hash,I_Id,2,i2)
set i=LoadInteger(hash,I_Id,3)
set MainStat=GetHeroInt(u,false)
set i2=(MainStat-i)/2
if i !=i2 then
call SetHeroInt(u,MainStat-i+i2,true)
endif
call SaveInteger(hash,I_Id,3,i2)
```

`PercentStatsRefresh`　war3map.j:21843
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set i=LoadInteger(hash,I_Id,1)
set MainStat=GetHeroStr(u,false)
set i2=(MainStat-i)/3*2
if i !=i2 then
call SetHeroStr(u,MainStat-i+i2,true)
endif
call SaveInteger(hash,I_Id,1,i2)
set i=LoadInteger(hash,I_Id,2)
set MainStat=GetHeroAgi(u,false)
set i2=(MainStat-i)/3*2
if i !=i2 then
call SetHeroAgi(u,MainStat-i+i2,true)
endif
call SaveInteger(hash,I_Id,2,i2)
set i=LoadInteger(hash,I_Id,3)
set MainStat=GetHeroInt(u,false)
set i2=(MainStat-i)/3*2
if i !=i2 then
call SetHeroInt(u,MainStat-i+i2,true)
endif
call SaveInteger(hash,I_Id,3,i2)
```

`PercentStatsRefresh`　war3map.j:21889
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set i=LoadInteger(hash,I_Id,1)
set MainStat=R2I((GetUnitState((u),UNIT_STATE_MAX_LIFE)))
set i2=(MainStat-i)/5*2
if i !=i2 then
call SetUnitLife(u,MainStat-i+i2)
endif
call SaveInteger(hash,I_Id,1,i2)
set i=LoadInteger(hash,I_Id,2)
set MainStat=R2I((GetUnitState((u),UNIT_STATE_MAX_MANA)))
set i2=(MainStat-i)/5*2
if i !=i2 then
call SetUnitMana(u,MainStat-i+i2)
endif
call SaveInteger(hash,I_Id,2,i2)
```

`PercentStatsRefresh`　war3map.j:21921
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set i=LoadInteger(hash,I_Id,1)
set MainStat=R2I((GetUnitState((u),UNIT_STATE_MAX_MANA)))
set i2=(MainStat-i)
if i !=i2 then
call SetUnitMana(u,MainStat-i+i2)
endif
call SaveInteger(hash,I_Id,1,i2)
```

`PercentStatsRefresh`　war3map.j:21939
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set i=LoadInteger(hash,I_Id,1)
set MainStat=GetHeroStr(u,false)
set i2=(MainStat-i)/3*2
if i !=i2 then
call SetHeroStr(u,MainStat-i+i2,true)
endif
call SaveInteger(hash,I_Id,1,i2)
```

`PercentStatsRefresh`　war3map.j:21957
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set i=LoadInteger(hash,I_Id,1)
set MainStat=GetUnitAttackSpeed(u)
set i2=GetHeroStr(u,false)
if i !=i2 then
call SetUnitAttackSpeed(u,MainStat-i+i2)
endif
call SaveInteger(hash,I_Id,1,i2)
```

`PercentStatsRefresh`　war3map.j:21975
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set i=LoadInteger(hash,I_Id,1)
set MainStat=GetHeroStr(u,false)
set i2=GetHeroInt(u,false)*2
if i !=i2 then
call SetHeroStr(u,MainStat-i+i2,true)
endif
call SaveInteger(hash,I_Id,1,i2)
```

`PercentStatsRefresh`　war3map.j:21993
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set r=LoadReal(hash,I_Id,1)
set r2=I2R(GetHeroStr(u,false))*0.30
if r !=r2 then
call SetUnitLifeRegeneration(u,GetUnitLifeRegeneration(u)-r+r2)
endif
call SaveReal(hash,I_Id,1,r2)
```

`PercentStatsRefresh`　war3map.j:22009
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set r=LoadReal(hash,I_Id,1)
set r2=I2R(GetHeroInt(u,false))*0.10
if r !=r2 then
call SetUnitManaRegeneration(u,GetUnitManaRegeneration(u)-r+r2)
endif
call SaveReal(hash,I_Id,1,r2)
```

`PercentStatsRefresh`　war3map.j:22025
```jass
if GetUnitAbilityLevel(u,'A0Y5')==1 then
set i=LoadInteger(hash,I_Id,1)
set n=GetPlayerId(GetOwningPlayer(u))+1
set i2=R2I(udg_ItemBonusDMG[n]*0.4)
if i !=i2 then
call SetUnitExtraDamage(u,GetUnitExtraDamage(u)-i+i2)
endif
call SaveInteger(hash,I_Id,1,i2)
```

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

## 選擇天賦 `A0R6`

俄文原名：Выбрать талант

```
當玩家經驗點數足夠時，你可以選擇一項天賦，將英雄大幅強化至新的力量階級。
```

**天賦選項**：
  - `A0RH` 挑釁者
    強度等級：T2 屬性加成／每級屬性成長加成： +2 / +1 +1 / +0 +0 / +0  使用後迫使附近的敵人攻擊英雄。  被動效果： 「雷霆一擊」會移除敵人身上的正面效果，並移除英雄身上的負面效果與狀態。  英雄每次受到傷害時回復 1 點生命值。
  - `A0Y2` 國王的祝福
    強度等級：T3 屬性加成／每級屬性成長加成： +3 / +1 +1 / +0 +3 / +1  英雄每次提升等級時，生命值上限提高 100 點、攻擊力提高 10 點，但同時復活時間增加 1 秒。  英雄獲得點燃抗性、流血抗性以及 +20% 反傷加成。

物件欄位（原型 `Aspb`）：`aite = 0`, `spb1 = A0RH,A0Y2`, `spb2 = 0`, `spb3 = 2`, `spb4 = 2`

實作：

`Trig_HeroSkills2_Actions`　war3map.j:46838
```jass
if Skill=='A0RH' then
call SetHeroStr(u,GetHeroStr(u,false)+2,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+1,true)
call SaveInteger(hash,GetHandleId(u),'aSTR',1)
call UnitRemoveAbility(u,'A0R6')
call UnitAddAbility(u,'A0RI')
call SaveInteger(hash,GetHandleId(pl),15,1)
elseif Skill=='A0Y2' then
call SetHeroStr(u,GetHeroStr(u,false)+3,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+1,true)
call SetHeroInt(u,GetHeroInt(u,false)+3,true)
call SaveInteger(hash,GetHandleId(u),'aSTR',1)
call SaveInteger(hash,GetHandleId(u),'aINT',1)
call UnitRemoveAbility(u,'A0R6')
call UnitAddAbility(u,'A0Y3')
set Id=GetHandleId(u)
call SaveInteger(hash,Id,27,LoadInteger(hash,Id,27)+1)
call SaveInteger(hash,Id,29,LoadInteger(hash,Id,29)+1)
call SaveReal(hash,Id,19,LoadReal(hash,Id,19)+0.20)
call SaveInteger(hash,GetHandleId(pl),15,1)
endif
```

## 挑釁者 `A0RH`　—　來自天賦「選擇天賦」

俄文原名：Провокатор

```
強度等級：T2
屬性加成／每級屬性成長加成：
+2 / +1
+1 / +0
+0 / +0

使用後迫使附近的敵人攻擊英雄。

被動效果：
「雷霆一擊」會移除敵人身上的正面效果，並移除英雄身上的負面效果與狀態。

英雄每次受到傷害時回復 1 點生命值。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [0.5, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['acidbomb', 'channel']`, `acap = `, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `arqa = 15`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills2_Actions`　war3map.j:46838
```jass
if Skill=='A0RH' then
call SetHeroStr(u,GetHeroStr(u,false)+2,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+1,true)
call SaveInteger(hash,GetHandleId(u),'aSTR',1)
call UnitRemoveAbility(u,'A0R6')
call UnitAddAbility(u,'A0RI')
call SaveInteger(hash,GetHandleId(pl),15,1)
```

## 國王的祝福 `A0Y2`　—　來自天賦「選擇天賦」

俄文原名：Благословение короля

```
強度等級：T3
屬性加成／每級屬性成長加成：
+3 / +1
+1 / +0
+3 / +1

英雄每次提升等級時，生命值上限提高 100 點、攻擊力提高 10 點，但同時復活時間增加 1 秒。

英雄獲得點燃抗性、流血抗性以及 +20% 反傷加成。
```

物件欄位（原型 `ANcl`）：`Ncl1 = [0.5, 0.8999999761581421]`, `Ncl2 = [None, 1]`, `Ncl3 = 1`, `Ncl4 = [0.5, 0.8999999761581421]`, `Ncl5 = 0`, `Ncl6 = ['acolyteharvest', 'channel']`, `acap = `, `acdn = [1.0, 16.0]`, `aher = 0`, `alev = 1`, `amcs = [None, 95, 110, 125, 140, 155, 170]`, `aran = 100.0`, `arqa = 24`, `atar = air,ground,debris,enemy,neutral,organic`

實作：

`Trig_HeroSkills2_Actions`　war3map.j:46845
```jass
elseif Skill=='A0Y2' then
call SetHeroStr(u,GetHeroStr(u,false)+3,true)
call SetHeroAgi(u,GetHeroAgi(u,false)+1,true)
call SetHeroInt(u,GetHeroInt(u,false)+3,true)
call SaveInteger(hash,GetHandleId(u),'aSTR',1)
call SaveInteger(hash,GetHandleId(u),'aINT',1)
call UnitRemoveAbility(u,'A0R6')
call UnitAddAbility(u,'A0Y3')
set Id=GetHandleId(u)
call SaveInteger(hash,Id,27,LoadInteger(hash,Id,27)+1)
call SaveInteger(hash,Id,29,LoadInteger(hash,Id,29)+1)
call SaveReal(hash,Id,19,LoadReal(hash,Id,19)+0.20)
call SaveInteger(hash,GetHandleId(pl),15,1)
endif
```

---

## 以「單位型號」內聯的實作

這幾段不是靠技能 ID 分派的，而是直接用單位型號 `Hapm` 寫在共用函式的條件式裡
（常見於寫進傷害管線的被動）。照技能抽取抓不到，所以單獨列出來。

`Trig_HeroLvlUp_Actions`　war3map.j:45509
```jass
elseif GetUnitTypeId(u)=='Hapm' then
if GetUnitAbilityLevel(u,'A0Y3')==1 then
call SetUnitBaseDamage(u,GetUnitBaseDamage(u)+10)
call SetUnitLife(u,R2I((GetUnitState((u),UNIT_STATE_MAX_LIFE)))+100)
call SaveReal(hash,u_Id,2,LoadReal(hash,u_Id,2)+1.)
endif
```

`Trig_DieHero_Actions`　war3map.j:46501
```jass
if GetUnitTypeId(u)=='Hapm' and GetUnitAbilityLevel(u,'A01H')==1 then
set ug=CreateGroup()
call GroupAddGroup(udg_AllHeroes,ug)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)then
call SetUnitState(u3,UNIT_STATE_LIFE,GetUnitState(u3,UNIT_STATE_LIFE)+(GetUnitState((u3),UNIT_STATE_MAX_LIFE))*0.50)
call SetUnitState(u3,UNIT_STATE_MANA,GetUnitState(u3,UNIT_STATE_MANA)+(GetUnitState((u3),UNIT_STATE_MAX_MANA))*0.50)
call DestroyEffect(AddSpecialEffectTarget("Abilities\\Spells\\Human\\Resurrect\\ResurrectTarget.mdl",u3,"origin"))
set time=time-3.
endif
call GroupRemoveUnit(ug,u3)
endloop
call DestroyGroup(ug)
endif
```

---

## 同一組的其他實作函式

英雄的實作散在同編號的一組函式裡，上面按技能抽取時抓不到的補在這裡
（常見的是決定門檻、結算加成、清理 buff 的那幾支）。

`Trig_EnemyHeroesSkill2_Actions`　war3map.j:32335
```jass
function Trig_EnemyHeroesSkill2_Actions takes nothing returns nothing
local unit u=GetSpellAbilityUnit()
local real cof=1.00+LoadReal(hash,GetHandleId(u),18)*0.33
local integer u_Id=GetUnitTypeId(u)
local unit u2
local unit u3
local unit u4
local player pl=GetOwningPlayer(u)
local integer n=GetPlayerId(pl)+1
local integer Skill=GetSpellAbilityId()
local real x=GetUnitX(u)
local real y=GetUnitY(u)
local real x2
local real y2
local real x3
local real y3
local real r
local real r2
local location p
local location p2
local group ug
local group ug2
local integer L
local integer Id
local timer t
local integer i
local real aoe
local real dmg
if Skill=='A0FF' then
set dmg=325.*cof
set ug=CreateGroup()
set ug2=CreateGroup()
call GroupEnumUnitsInRange(ug,x,y,400.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)and not IsUnitType(u3,UNIT_TYPE_STRUCTURE)then
call GroupAddUnit(ug2,u3)
endif
call GroupRemoveUnit(ug,u3)
endloop
set ug2=GetRandomSubGroup(5,ug2)
loop
set u3=FirstOfGroup(ug2)
exitwhen u3==null
call BleedUnit(u,u3,dmg,1.20)
call DestroyEffect(AddSpecialEffectTarget("Objects\\Spawnmodels\\Orc\\OrcSmallDeathExplode\\OrcSmallDeathExplode.mdl",u3,"origin"))
call GroupRemoveUnit(ug2,u3)
endloop
call DestroyGroup(ug)
call DestroyGroup(ug2)
endif
if Skill=='A0OL' then
set x=GetUnitX(GetSpellTargetUnit())
set y=GetUnitY(GetSpellTargetUnit())
set r=GetRandomReal(0,360)
set L=1
loop
exitwhen L>3
set x2=x+250*Cos((r+I2R(L)*120)*bj_DEGTORAD)
set y2=y+250*Sin((r+I2R(L)*120)*bj_DEGTORAD)
call Spellmarker(u,525*cof,125,2.50,x2,y2,"war3mapImported\\Flamestrike Dark Blood I.mdx")
set L=L+1
endloop
endif
if Skill=='A0FR' then
if n>5 then
set ug=CreateGroup()
call GroupAddGroup(udg_AllHeroes,ug)
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if UnitAlive(u2)then
set x=GetUnitX(u2)
set y=GetUnitY(u2)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
set r=GetRandomReal(0,360)
set x=x+250*Cos(r*bj_DEGTORAD)
set y=y+250*Sin(r*bj_DEGTORAD)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
if udg_Modifiers[5]==true and n>5 then
set r=GetRandomReal(0,360)
set x=x+250*Cos(r*bj_DEGTORAD)
set y=y+250*Sin(r*bj_DEGTORAD)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
endif
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
else
set ug=CreateGroup()
call GroupEnumUnitsOfPlayer(ug,Player(8),null)
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if IsUnitType(u2,UNIT_TYPE_HERO)and UnitAlive(u2)then
set x=GetUnitX(u2)
set y=GetUnitY(u2)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
set r=GetRandomReal(0,360)
set x=x+250*Cos(r*bj_DEGTORAD)
set y=y+250*Sin(r*bj_DEGTORAD)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
set ug=CreateGroup()
call GroupEnumUnitsOfPlayer(ug,Player(10),null)
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if IsUnitType(u2,UNIT_TYPE_HERO)and UnitAlive(u2)then
set x=GetUnitX(u2)
set y=GetUnitY(u2)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
set r=GetRandomReal(0,360)
set x=x+250*Cos(r*bj_DEGTORAD)
set y=y+250*Sin(r*bj_DEGTORAD)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
set ug=CreateGroup()
call GroupEnumUnitsOfPlayer(ug,Player(11),null)
loop
set u2=FirstOfGroup(ug)
exitwhen u2==null
if IsUnitType(u2,UNIT_TYPE_HERO)and UnitAlive(u2)then
set x=GetUnitX(u2)
set y=GetUnitY(u2)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
set r=GetRandomReal(0,360)
set x=x+250*Cos(r*bj_DEGTORAD)
set y=y+250*Sin(r*bj_DEGTORAD)
call Spellmarker(u,650*cof,145,1.60,x,y,"Abilities\\Spells\\Human\\Thunderclap\\ThunderClapCaster.mdl")
endif
call GroupRemoveUnit(ug,u2)
endloop
call DestroyGroup(ug)
endif
endif
if Skill=='A0Z4' then
set u2=GetSpellTargetUnit()
set x3=GetUnitX(u2)
set y3=GetUnitY(u2)
set r=40.
set L=1
loop
if udg_Modifiers[5]==true then
exitwhen L>36
else
exitwhen L>18
endif
set L=L+1
set r=r+40.
set r2=GetRandomReal(0.,360.)
set x2=PolarX(x3,r,r2)
set y2=PolarY(y3,r,r2)
set u2=CreateUnit(pl,'o00O',x,y,0.00)
call SaveReal(hash,GetHandleId(u2),13,350.00*cof)
call SaveUnitHandle(hash,GetHandleId(u2),13,u)
call UnitApplyTimedLife(u2,'BTLF',4.50)
call IssuePointOrderById(u2,Order_attackground,x2,y2)
endloop
if UnitLifePercent(u)<=33.00 then
set L=1
loop
if udg_Modifiers[5]==true then
exitwhen L>20
else
exitwhen L>10
endif
set L=L+1
set r=r+90.00
set r2=GetRandomReal(0.,360.)
set x2=PolarX(x3,r,r2)
set y2=PolarY(y3,r,r2)
set u2=CreateUnit(pl,'o00O',x,y,0.00)
call SaveReal(hash,GetHandleId(u2),13,350.00*cof)
call SaveUnitHandle(hash,GetHandleId(u2),13,u)
call UnitApplyTimedLife(u2,'BTLF',4.50)
call IssuePointOrderById(u2,Order_attackground,x2,y2)
endloop
endif
endif
if Skill=='ACdc' then
set u2=GetSpellTargetUnit()
set x2=GetUnitX(u2)
set y2=GetUnitY(u2)
set ug=CreateGroup()
call GroupEnumUnitsInRange(ug,x2,y2,300.,null)
loop
set u3=FirstOfGroup(ug)
exitwhen u3==null
if UnitAlive(u3)and IsUnitEnemy(u3,pl)and not IsUnitType(u3,UNIT_TYPE_UNDEAD)and u3 !=u2 then
set u4=CreateUnit(pl,'o010',x,y,0.00)
call UnitAddAbility(u4,'A05C')
```

`Trig_CreateHero2_Actions`　war3map.j:35139
```jass
function Trig_CreateHero2_Actions takes nothing returns nothing
local location p
local unit u
local integer i
local group ug
if udg_WaveFase==4 then
set udg_EnemyHeroType[1]='E001'
set udg_EnemyHeroType[2]='H00M'
elseif udg_WaveFase==5 then
set udg_EnemyHeroType[1]='E009'
set udg_EnemyHeroType[2]='H00W'
elseif udg_WaveFase==6 then
set udg_EnemyHeroType[1]='H01Q'
set udg_EnemyHeroType[2]='N02R'
elseif udg_WaveFase==7 then
set udg_EnemyHeroType[1]='N035'
set udg_EnemyHeroType[2]='E00U'
elseif udg_WaveFase==8 then
set udg_EnemyHeroType[1]='U01B'
set udg_EnemyHeroType[2]='H03B'
elseif udg_WaveFase==9 then
set udg_EnemyHeroType[1]='U012'
set udg_EnemyHeroType[2]='H028'
elseif udg_WaveFase==10 then
set udg_EnemyHeroType[1]='Nklj'
set udg_EnemyHeroType[2]='H045'
elseif udg_WaveFase>=11 then
set udg_EnemyHeroType[1]='N020'
set udg_EnemyHeroType[2]='U00K'
endif
set udg_EnemyHeroLvl=udg_EnemyHeroLvl+1
set i=GetRandomInt(1,4)
if i<3 then
set ug=udg_AttackGroup2
else
set ug=udg_AttackGroup3
endif
set p=udg_SpawnPoints[i]
set u=CreateUnitAtLoc(AI[GetRandomInt(1,3)],udg_EnemyHeroType[GetRandomInt(1,2)],p,GetRandomReal(0.,360.))
call SetHeroLevel(u,3+udg_EnemyHeroLvl,false)
call PrepareEnemyHero(u)
call GroupAddUnit(ug,u)
if i<3 then
call IssuePointOrderByIdLoc(u,Order_attack,udg_DefPoint2)
else
call IssuePointOrderByIdLoc(u,Order_attack,udg_DefPoint3)
endif
if udg_WaveFase==1 then
set i=1
loop
exitwhen i>4
call SpawnEnemy('n01D',p,ug,0)
set i=i+1
endloop
elseif udg_WaveFase==2 then
set i=1
loop
exitwhen i>4
call SpawnEnemy('u00L',p,ug,0)
call SpawnEnemy('u00C',p,ug,0)
set i=i+1
endloop
elseif udg_WaveFase==3 then
set i=1
loop
exitwhen i>8
call SpawnEnemy('n01E',p,ug,0)
set i=i+1
endloop
call SpawnEnemy('u00I',p,ug,0)
call SpawnEnemy('u00I',p,ug,0)
elseif udg_WaveFase==4 then
set i=1
loop
exitwhen i>8
call SpawnEnemy('n03I',p,ug,0)
set i=i+1
endloop
call SpawnEnemy('u00I',p,ug,0)
call SpawnEnemy('u00I',p,ug,0)
elseif udg_WaveFase==5 then
set i=1
loop
exitwhen i>8
call SpawnEnemy('n03I',p,ug,0)
set i=i+1
endloop
call SpawnEnemy('u00I',p,ug,0)
call SpawnEnemy('u00I',p,ug,0)
call SpawnEnemy('u00M',p,ug,0)
call SpawnEnemy('u00M',p,ug,0)
elseif udg_WaveFase>=6 then
set i=1
loop
exitwhen i>8
call SpawnEnemy('n03I',p,ug,0)
set i=i+1
endloop
call SpawnEnemy('u00I',p,ug,0)
call SpawnEnemy('u00I',p,ug,0)
call SpawnEnemy('n02U',p,ug,0)
call SpawnEnemy('n02U',p,ug,0)
endif
call DisplayTimedTextToForce(bj_FORCE_ALL_PLAYERS,30.,"|cFFE60000Появился вражеский герой!|r")
set p=null
set u=null
set ug=null
endfunction
```

`Trig_CreateHero2_Hard_Actions`　war3map.j:35565
```jass
function Trig_CreateHero2_Hard_Actions takes nothing returns nothing
local location p
local unit u
local integer i
local group ug
if udg_WaveFase==4 then
set udg_EnemyHeroType[1]='U012'
set udg_EnemyHeroType[2]='H028'
elseif udg_WaveFase==5 then
set udg_EnemyHeroType[1]='U01B'
set udg_EnemyHeroType[2]='H03B'
elseif udg_WaveFase==6 then
set udg_EnemyHeroType[1]='H03P'
set udg_EnemyHeroType[2]='N05A'
elseif udg_WaveFase==7 then
set udg_EnemyHeroType[1]='E00B'
set udg_EnemyHeroType[2]='N05L'
elseif udg_WaveFase==8 then
set udg_EnemyHeroType[1]='Udea'
set udg_EnemyHeroType[2]='Ulic'
elseif udg_WaveFase==9 then
set udg_EnemyHeroType[1]='Uanb'
set udg_EnemyHeroType[2]='N04W'
elseif udg_WaveFase==10 then
set udg_EnemyHeroType[1]='Opgh'
set udg_EnemyHeroType[2]='Uwar'
elseif udg_WaveFase>=11 then
set udg_EnemyHeroType[1]='N06H'
set udg_EnemyHeroType[2]='U00N'
endif
set udg_EnemyHeroLvl=udg_EnemyHeroLvl+1
set i=GetRandomInt(1,4)
if i<3 then
set ug=udg_AttackGroup2
else
set ug=udg_AttackGroup3
endif
set p=udg_SpawnPoints[i]
set u=CreateUnitAtLoc(AI[GetRandomInt(1,3)],udg_EnemyHeroType[GetRandomInt(1,2)],p,GetRandomReal(0.,360.))
call SetHeroLevel(u,3+udg_EnemyHeroLvl,false)
call PrepareEnemyHero(u)
call GroupAddUnit(ug,u)
if i<3 then
call IssuePointOrderByIdLoc(u,Order_attack,udg_DefPoint2)
else
call IssuePointOrderByIdLoc(u,Order_attack,udg_DefPoint3)
endif
if udg_WaveFase==1 then
call SpawnEnemy('u00I',p,ug,0)
call SpawnEnemy('u00I',p,ug,0)
elseif udg_WaveFase==2 then
set i=1
loop
exitwhen i>4
call SpawnEnemy('n02M',p,ug,0)
call SpawnEnemy('u00M',p,ug,0)
set i=i+1
endloop
elseif udg_WaveFase==3 then
set i=1
loop
exitwhen i>4
call SpawnEnemy('n02M',p,ug,0)
call SpawnEnemy('u00M',p,ug,0)
set i=i+1
endloop
call SpawnEnemy('u00I',p,ug,0)
call SpawnEnemy('u00I',p,ug,0)
elseif udg_WaveFase==4 then
set i=1
loop
exitwhen i>4
call SpawnEnemy('n02M',p,ug,0)
call SpawnEnemy('u00M',p,ug,0)
set i=i+1
endloop
call SpawnEnemy('n01F',p,ug,0)
call SpawnEnemy('n01F',p,ug,0)
elseif udg_WaveFase==5 then
set i=1
loop
exitwhen i>4
call SpawnEnemy('n02M',p,ug,0)
call SpawnEnemy('n02U',p,ug,0)
set i=i+1
endloop
call SpawnEnemy('n01F',p,ug,0)
call SpawnEnemy('n01F',p,ug,0)
elseif udg_WaveFase>=6 then
set i=1
loop
exitwhen i>4
call SpawnEnemy('n02M',p,ug,0)
call SpawnEnemy('n02U',p,ug,0)
call SpawnEnemy('n02W',p,ug,0)
set i=i+1
endloop
call SpawnEnemy('n01F',p,ug,0)
call SpawnEnemy('n01F',p,ug,0)
endif
call DisplayTimedTextToForce(bj_FORCE_ALL_PLAYERS,30.,"|cFFE60000Появился вражеский герой!|r")
set p=null
set u=null
set ug=null
endfunction
```

`HeroR2_check`　war3map.j:46952
```jass
function HeroR2_check takes nothing returns nothing
local timer t=GetExpiredTimer()
local integer Id=GetHandleId(t)
local unit u=LoadUnitHandle(hash,Id,1)
local integer u_Id=GetHandleId(u)
local integer n=GetPlayerId(GetOwningPlayer(u))+1
if UnitAlive(u)then
if UnitLifePercent(u)<50.00 then
if GetUnitAbilityLevel(u,'A01G')!=1 then
call UnitAddAbility(u,'A01G')
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)+0.20)
if udg_ItemBonusDMG[n]>=200 and GetUnitAbilityLevel(u,'A0R5')!=1 then
call UnitAddAbility(u,'A0R5')
endif
endif
else
if GetUnitAbilityLevel(u,'A01G')==1 then
call UnitRemoveAbility(u,'A01G')
call SaveReal(hash,u_Id,4,LoadReal(hash,u_Id,4)-0.20)
call UnitRemoveAbility(u,'A0R5')
endif
endif
endif
set t=null
set u=null
endfunction
```

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數〔持有者〕StartModCooldown 讀，CD×它，下限 0.20
  - **3** — 對英雄傷害 +%〔攻擊者〕Trig_HeroTakeDamage_Actions 的 DefCof
  - **4** — 受到傷害 −%〔受害者〕DefCof 減去它 → 值越大越耐打；電擊會扣它
  - **19** — 反傷加成〔被攻擊者〕
  - **27** — 實數＝點燃傷害 +%〔施加者〕／整數＝抵抗點燃旗標〔受害者〕**兩者不同表**
  - **29** — 實數＝流血傷害 +%〔施加者〕／整數＝抵抗流血旗標〔受害者〕（加成寫錯變數，實際無效 —— 見 地圖問題回報 A-4）

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
