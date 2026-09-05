# 皇家守衛 `Hapm`（Королевский страж）

主屬性 **力量** · 背包 **6 格** · 解鎖 0 · 定位 坦克/輔助/戰士

| | 初始 | 每級 |
|---|---|---|
| 力量 | None | None |
| 敏捷 | None | None |
| 智力 | None | None |

> 近戰英雄，可走多種路線。裝備類乘數對他影響特別大。

**縮放**：吃技能強度的技能 ['A01B', 'A01C', 'A01E', 'A07U', 'A0Y5'] ／ ◈ 吃裝備技能威力 無 ／ ⊕ 給裝備技能威力 無

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

物件欄位（原型 `ANcl`）：`Ncl1 = 1.0`, `Ncl2 = 1`, `Ncl3 = 1`, `Ncl4 = 1.0`, `Ncl5 = 0`, `Ncl6 = channel`, `acdn = 15.0`, `alev = 5`, `amcs = [60, 68, 76, 84, 92]`, `aran = 800.0`, `atar = air,ground,friend,neutral,self`

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

物件欄位（原型 `AHtc`）：`Htc1 = 1.0`, `aare = 300.0`, `acdn = 9.0`, `adur = [5.5, 6.0, 6.5, 7.0]`, `ahdu = [3.299999952316284, 3.5999999046325684, 3.8999998569488525, 4.199999809265137]`, `alev = 5`, `amcs = [85, 105, 115, 125, 95]`

實作：

`ClearUnit`　war3map.j:2647
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

`SetUnitAttackSpeed`　war3map.j:3819
```jass
function SetUnitAttackSpeed takes unit u,integer a returns nothing
local integer Id=GetHandleId(u)
local integer p=8
local integer i=0
local integer r=a
if r>400 then
set r=400
endif
loop
call UnitRemoveAbility(u,setAttribute___abilityAddAttackSpeed[i])
exitwhen i==8
set i=i+1
endloop
if r>0 then
loop
exitwhen r<=0
if R2I(Pow(2,p))>r then
set p=p-1
elseif R2I(Pow(2,p))<=r then
call UnitAddAbility(u,setAttribute___abilityAddAttackSpeed[p])
set r=r-R2I(Pow(2,p))
set p=p-1
endif
endloop
call SaveInteger(hash,Id,36,a)
endif
endfunction
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
function SetUnitLife takes unit c,integer hp returns nothing
local integer Id=GetHandleId(c)
set hp=R2I(I2R(hp)-(GetUnitState((c),UNIT_STATE_MAX_LIFE)))
call SaveInteger(hash,Id,37,hp)
loop
exitwhen hp==0
if hp>0 then
if hp>=2000 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',10)
call UnitRemoveAbility(c,'ah00')
set hp=hp-2000
elseif hp>=500 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',9)
call UnitRemoveAbility(c,'ah00')
set hp=hp-500
elseif hp>=200 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',8)
call UnitRemoveAbility(c,'ah00')
set hp=hp-200
elseif hp>=50 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',7)
call UnitRemoveAbility(c,'ah00')
set hp=hp-50
elseif hp>=20 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',6)
call UnitRemoveAbility(c,'ah00')
set hp=hp-20
elseif hp>=10 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',5)
call UnitRemoveAbility(c,'ah00')
set hp=hp-10
elseif hp>=5 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',4)
call UnitRemoveAbility(c,'ah00')
set hp=hp-5
elseif hp>=2 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',3)
call UnitRemoveAbility(c,'ah00')
set hp=hp-2
else
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',2)
call UnitRemoveAbility(c,'ah00')
set hp=hp-1
endif
elseif hp<0 then
if hp<=-2000 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',19)
call UnitRemoveAbility(c,'ah00')
set hp=hp+2000
elseif hp<=-500 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',18)
call UnitRemoveAbility(c,'ah00')
set hp=hp+500
elseif hp<=-200 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',17)
call UnitRemoveAbility(c,'ah00')
set hp=hp+200
elseif hp<=-50 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',16)
call UnitRemoveAbility(c,'ah00')
set hp=hp+50
elseif hp<=-20 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',15)
call UnitRemoveAbility(c,'ah00')
set hp=hp+20
elseif hp<=-10 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',14)
call UnitRemoveAbility(c,'ah00')
set hp=hp+10
elseif hp<=-5 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',13)
call UnitRemoveAbility(c,'ah00')
set hp=hp+5
elseif hp<=-2 then
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',12)
call UnitRemoveAbility(c,'ah00')
set hp=hp+2
else
call UnitAddAbility(c,'ah00')
call SetUnitAbilityLevel(c,'ah00',11)
call UnitRemoveAbility(c,'ah00')
set hp=hp+1
endif
endif
endloop
set c=null
endfunction
function SetUnitMana takes unit c,integer mp returns nothing
local integer Id=GetHandleId(c)
set mp=R2I(I2R(mp)-(GetUnitState((c),UNIT_STATE_MAX_MANA)))
call SaveInteger(hash,Id,38,mp)
loop
exitwhen mp==0
if mp>0 then
if mp>=500 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',9)
call UnitRemoveAbility(c,'am00')
set mp=mp-500
elseif mp>=200 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',8)
call UnitRemoveAbility(c,'am00')
set mp=mp-200
elseif mp>=50 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',7)
call UnitRemoveAbility(c,'am00')
set mp=mp-50
elseif mp>=20 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',6)
call UnitRemoveAbility(c,'am00')
set mp=mp-20
elseif mp>=10 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',5)
call UnitRemoveAbility(c,'am00')
set mp=mp-10
elseif mp>=5 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',4)
call UnitRemoveAbility(c,'am00')
set mp=mp-5
elseif mp>=2 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',3)
call UnitRemoveAbility(c,'am00')
set mp=mp-2
else
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',2)
call UnitRemoveAbility(c,'am00')
set mp=mp-1
endif
elseif mp<0 then
if mp<=-500 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',17)
call UnitRemoveAbility(c,'am00')
set mp=mp+500
elseif mp<=-200 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',16)
call UnitRemoveAbility(c,'am00')
set mp=mp+200
elseif mp<=-50 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',15)
call UnitRemoveAbility(c,'am00')
set mp=mp+50
elseif mp<=-20 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',14)
call UnitRemoveAbility(c,'am00')
set mp=mp+20
elseif mp<=-10 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',13)
call UnitRemoveAbility(c,'am00')
set mp=mp+10
elseif mp<=-5 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',12)
call UnitRemoveAbility(c,'am00')
set mp=mp+5
elseif mp<=-2 then
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',11)
call UnitRemoveAbility(c,'am00')
set mp=mp+2
else
call UnitAddAbility(c,'am00')
call SetUnitAbilityLevel(c,'am00',10)
call UnitRemoveAbility(c,'am00')
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

---

## 這隻碰到的 hash key

  - **1** — 裝備技能冷卻乘數
  - **4** — 受到傷害 −%（被減的）
  - **6** — 造成傷害 +%
  - **19** — 反傷加成
  - **27** — 點燃傷害 +%／（整數槽）抵抗點燃旗標
  - **29** — 流血傷害 +%／（整數槽）抵抗流血旗標
  - **37** — 生命上限增量（GetUnitLife 讀這個）
  - **47** — 點燃抗性
  - **48** — 冰凍抗性
  - **49** — 流血抗性
  - **50** — 疾病抗性

---

*由 `tools/build_dossier.py` 從 UD_v3.81 地圖檔產生。*
*機制通則、配裝規則與輸出格式見 `tools/BUILD_BRIEF.md`；*
*道具數值見 `data/dossier/_items.md`。*
