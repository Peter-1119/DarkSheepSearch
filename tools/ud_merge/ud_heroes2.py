# -*- coding: utf-8 -*-
"""英雄改動（第二批）。

1. 長工（與其造型）的碉堡：原本英雄進碉堡後 ShowUnit(false) 隱藏，點不到英雄，
   不能學技能、不能轉移據點。改成不隱藏，而是：
     透明＋縮到 0.01（點不到模型）、無敵、不能移動（轉向視窗 0）、不能攻擊（Abun）、
     站在碉堡中心且不佔路徑。
   → 可用 F1／左上頭像選到英雄：學技能、選天賦、使用「轉移／拆除據點」(A03V)。
   其他技能與道具在碉堡內一律在施放前取消（不進冷卻、不耗魔）。
   離開碉堡（主動離開或碉堡被摧毀）時恢復原本的大小與色調（依英雄類型，建置時從 w3u 讀出）。
2. 深淵神諭者的「召喚樹人」改成「召喚娜迦守衛」(A2UN)：
   數量 1 +（每 400 點技能強度 1 隻），持續 40 秒、冷卻 60 秒同原技能；
   娜迦守衛 n2NG 抄地圖裡的米爾米頓（1150 生命、41 攻擊、30% 濺射、格擋 8），
   改用樹人的部隊升級清單（繼承部隊升級），且與可雇用的米爾米頓分開（不吃雇用相關程式）。
"""
import re
import w3a_poke

BUNKER_SKILLS = ('A0C3', 'A0WX', 'A0HE', 'A0ZR')
BUNKER_UNITS = ('o01E', 'nntg', 'o02P', 'uzg2')
ALLOW = ('A03V', 'A0QP', 'A0QV', 'A02V')          # 轉移／拆除據點、天賦選項
NAGA_SKILL, NAGA_UNIT = 'A2UN', 'n2NG'
TREANT_UPGR = 'Rnat,R02T,R00P,R002,Rhac,Rhgb'


# ================================================================ 1. 碉堡
def bunker_heroes(w3u):
    """{英雄類型: (縮放, R, G, B)}：技能表裡有碉堡技能的英雄。"""
    g = lambda r, m, d: (r.get(m) if not isinstance(r.get(m), list) else r.get(m)[0]) if r.get(m) not in (None, '') else d
    out = {}
    for k, r in w3u.items():
        uhab = str(g(r, 'uhab', ''))
        if any(s in uhab for s in BUNKER_SKILLS):
            out[k] = (float(g(r, 'usca', 1.0)), int(g(r, 'uclr', 255)), int(g(r, 'uclg', 255)), int(g(r, 'uclb', 255)))
    return out


def _funcs(heroes):
    look = []
    for k, (s, r, gg, b) in sorted(heroes.items()):
        look.append("%sif t=='%s' then\nset s=%.2f\nset r=%d\nset g=%d\nset b=%d\n" % ('' if not look else 'else', k, s, r, gg, b))
    look = ''.join(look) + 'endif\n' if look else ''
    allow = ' and '.join("a!='%s'" % a for a in ALLOW)
    return ("function udW_Enter takes unit u,unit bk returns nothing\n"
            "call SaveUnitHandle(hash,GetHandleId(u),'udWb',bk)\n"
            "call SetUnitPathing(u,false)\n"
            "call SetUnitX(u,GetUnitX(bk))\n"
            "call SetUnitY(u,GetUnitY(bk))\n"
            "call SetUnitVertexColor(u,255,255,255,0)\n"
            "call SetUnitScale(u,0.01,0.01,0.01)\n"
            "call SetUnitPropWindow(u,0.)\n"
            "call UnitAddAbility(u,'Abun')\n"
            "call IssueImmediateOrder(u,\"stop\")\n"
            "endfunction\n"
            "function udW_Leave takes unit u returns nothing\n"
            "local integer t=GetUnitTypeId(u)\n"
            "local real s=1.\n"
            "local integer r=255\n"
            "local integer g=255\n"
            "local integer b=255\n"
            "call RemoveSavedHandle(hash,GetHandleId(u),'udWb')\n"
            "call UnitRemoveAbility(u,'Abun')\n"
            "call SetUnitPropWindow(u,GetUnitDefaultPropWindow(u)*bj_DEGTORAD)\n"
            "call SetUnitPathing(u,true)\n"
            + look +
            "call SetUnitScale(u,s,s,s)\n"
            "call SetUnitVertexColor(u,r,g,b,255)\n"
            "call ShowUnit(u,true)\n"
            "endfunction\n"
            "function udW_Cast takes nothing returns nothing\n"
            "local unit u=GetTriggerUnit()\n"
            "local integer a=GetSpellAbilityId()\n"
            "if HaveSavedHandle(hash,GetHandleId(u),'udWb') and %s then\n"
            "call PauseUnit(u,true)\n"
            "call IssueImmediateOrder(u,\"stop\")\n"
            "call PauseUnit(u,false)\n"
            "call DisplayTimedTextToPlayer(GetOwningPlayer(u),0,0,5,\"|cFFFFCC00在碉堡裡只能選天賦、學技能、轉移／拆除據點。|r\")\n"
            "endif\n"
            "set u=null\n"
            "endfunction\n"
            "function udW_Init takes nothing returns nothing\n"
            "local trigger t=CreateTrigger()\n"
            "call TriggerRegisterAnyUnitEventBJ(t,EVENT_PLAYER_UNIT_SPELL_CAST)\n"
            "call TriggerAddAction(t,function udW_Cast)\n"
            "set t=null\n"
            "endfunction\n") % allow


def patch_bunker(J, heroes):
    old = "call SetUnitInvulnerable(u,true)\ncall UnitRemoveAbility(u,'A0AE')\ncall ShowUnit(u,false)\n"
    assert J.count(old) == 4, J.count(old)
    J = J.replace(old, "call SetUnitInvulnerable(u,true)\ncall UnitRemoveAbility(u,'A0AE')\n")
    for v in BUNKER_UNITS:
        a = "set u2=CreateUnit(pl,'%s',x,y,GetUnitFacing(u))\n" % v
        assert J.count(a) == 1, v
        J = J.replace(a, a + 'call udW_Enter(u,u2)\n')
    a = "call ShowUnit(hero,true)\ncall UnitAddAbility(hero,'A0AE')\n"
    assert J.count(a) == 1
    J = J.replace(a, "call udW_Leave(hero)\ncall UnitAddAbility(hero,'A0AE')\n")
    # JASS 函式要先定義才能呼叫：放在碉堡技能的函式前面
    first = 'function Trig_HeroSkills28_Actions takes nothing returns nothing\n'
    assert J.count(first) == 1
    J = J.replace(first, _funcs(heroes) + first)
    anchor = 'function InitTrig_HeroKills28 takes nothing returns nothing\n'
    assert J.count(anchor) == 1
    J = J.replace(anchor, anchor + 'call udW_Init()\n')
    return J


# ================================================================ 2. 娜迦守衛
_NAGA = ("elseif Skill=='%s' then\n"
         "set x2=x+128*Cos(GetUnitFacing(u)*bj_DEGTORAD)\n"
         "set y2=y+128*Sin(GetUnitFacing(u)*bj_DEGTORAD)\n"
         "set dmg=400.00+udg_ItemBonusDMG[n]\n"
         "loop\n"
         "exitwhen dmg<400.00\n"
         "set u2=CreateUnit(pl,'%s',x2,y2,GetUnitFacing(u))\n"
         "call DestroyEffect(AddSpecialEffectTarget(\"Abilities\\\\Spells\\\\Other\\\\CrushingWave\\\\CrushingWaveDamage.mdl\",u2,\"origin\"))\n"
         "call UnitApplyTimedLife(u2,'BTLF',40)\n"
         "if UnitHasItemOfType(u,'I089')==true then\n"
         "call SetUnitExtraArmor(u2,GetUnitExtraArmor(u2)+5)\n"
         "endif\n"
         "set dmg=dmg-400.00\n"
         "endloop\n") % (NAGA_SKILL, NAGA_UNIT)


def patch_naga_jass(J):
    a = 'set dmg=dmg-200.00\nendloop\nendif\n'
    assert J.count(a) == 1
    J = J.replace(a, 'set dmg=dmg-200.00\nendloop\n' + _NAGA + 'endif\n')
    # 深淵守衛 A0TG：技能強度 ≥1500 時先對還沒建立的 u2 加技能 → 讀未初始化區域變數，整個施法中斷、召不出來。
    # 改成先建立再加技能。
    a = "call UnitAddAbility(u2,'A11J')\nset u2=CreateUnit(pl,'n06W',x2,y2,GetUnitFacing(u))\n"
    assert J.count(a) == 1
    return J.replace(a, "set u2=CreateUnit(pl,'n06W',x2,y2,GetUnitFacing(u))\ncall UnitAddAbility(u2,'A11J')\n")


def patch_w3a(data):
    data, _ = w3a_poke.clone(data, 'A0MC', [NAGA_SKILL])
    data, _ = w3a_poke.poke_str(data, {(NAGA_SKILL, 'aart', 0): r'ReplaceableTextures\CommandButtons\BTNNagaMyrmidon.blp'})
    return data


def patch_w3u(data):
    data, _ = w3a_poke.clone(data, 'nmyr', [NAGA_UNIT], has_level=False)
    data, _ = w3a_poke.poke_str(data, {(NAGA_UNIT, 'upgr', 0): TREANT_UPGR}, has_level=False)
    idx = w3a_poke.index(data, False)
    off, _ = idx[('Ecen', 'uabi', 0)]
    cur = data[off:data.index(b'\x00', off)].decode('latin-1')
    assert 'A0MC' in cur.split(','), cur
    data, _ = w3a_poke.poke_str(data, {('Ecen', 'uabi', 0): cur.replace('A0MC', NAGA_SKILL)}, has_level=False)
    return data


hits = {'skin': 0}
_TIP = ('召喚娜迦守衛助戰，持續 40 秒。守衛的攻擊有濺射效果（30%），能格擋物理攻擊（8 點），並繼承部隊升級。\r\n\r\n'
        '|cFFA085ED守衛數量： |r|cFF07B4C21 +（每 400 點技能強度 1 隻）|r\r\n\r\n'
        '|cFFA085ED冷卻時間： |r|cFF07B4C260 秒|r')


def text(f, k, m, s):
    """翻譯之後套用。"""
    if f == 'war3map.w3a' and k == NAGA_SKILL:
        return {'anam': '召喚娜迦守衛', 'atp1': '召喚娜迦守衛 (|cffffcc00Z|r)', 'aub1': _TIP}.get(m, s)
    if f == 'war3map.w3a' and k == 'A0SW' and m == 'aub1' and s and '改為「深淵守衛」' in s:
        hits['skin'] += 1
        return re.sub(r'(改為「深淵守衛」[^|]*?。)', r'\1「召喚樹人」改為「召喚娜迦守衛」：數量較少、單隻較強。', s, 1)
    if f == 'war3map.w3u' and k == NAGA_UNIT and m == 'unam':
        return '娜迦守衛'
    return s
