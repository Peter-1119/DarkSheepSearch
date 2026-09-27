# -*- coding: utf-8 -*-
"""入侵（一般難度）對齊 2.1.0，與「軍械庫」戰場設定調整。

1. 第 11 波：U00T → 無序法師 H020；第 12 波：N05L → 大墓地之主 U018
   （2.1.0 用 H03I / U01H；新版 H03I 改成了玩家英雄「遠古九頭蛇」、U01H 已刪除，
    所以改用新版仍保留、同一隻王的 H020 / U018）
2. 第 7 波最後的王 E00U「被褻瀆者」：加回 2.1.0 的惡魔變身 A0EK（變成 E00C）；
   E00C 的資料照 2.1.0 搬回（新版是空的預設惡魔形態），另外保留新版的冰霜齊射 A0FE。
   2.1.0 沒有觸發器下令變身，這裡加一個：E00U 生命值低於 70% 時下令變身。
3. 軍械庫：玩家積分獲取 +50% → +75%（實際加成與所有顯示文字）。
4. 入侵四路（一般＋骨灰級）：只有守右下王座（h000_0592）的那幾波是四路，照 2.1.0。
   入侵每波會在三個王座間輪替；一般難度右下是第 1/4/7/10/13 波（2.1.0 就是這幾波四路），
   骨灰級右下是第 3/6/9/12/15 波（原本沒有四路，比照一般難度加上）。第 4 個出怪點 (13749,-6645)。
"""
import re
import struct
import mpq
import w3a_poke

OLD_MAP = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/000肥羊的聖誕禮物_2.1.0_ty.w3x'
META_HP = 70


def _func(J, name):
    a = J.index('\nfunction %s takes' % name)
    return a, J.index('\nendfunction', a)


def _in_func(J, name, old, new):
    a, b = _func(J, name)
    body = J[a:b]
    assert body.count(old) == 1, (name, old)
    return J[:a] + body.replace(old, new) + J[b:]


def patch_jass(J):
    J = _in_func(J, 'Trig_Wave11_Actions', "set udg_EnemyHeroType[1]='U00T'", "set udg_EnemyHeroType[1]='H020'")
    J = _in_func(J, 'Trig_Wave12_Actions', "set udg_EnemyHeroType[1]='N05L'", "set udg_EnemyHeroType[1]='U018'")
    # 軍械庫 +75%
    for old, new in [('"Арсенал (+50% получение опыта игрока)"', '"Арсенал (+75% получение опыта игрока)"'),
                     ('Настройка \\"Арсенал\\" (+50%)|r")\nset udg_ModReward=udg_ModReward+0.50',
                      'Настройка \\"Арсенал\\" (+75%)|r")\nset udg_ModReward=udg_ModReward+0.75'),
                     ("Модификатор ''Арсенал'' (+50%)", "Модификатор ''Арсенал'' (+75%)")]:
        assert J.count(old) == 1, old
        J = J.replace(old, new)
    # E00U 生命值低於 70% 時下令惡魔變身
    fn = ("function udI_MetaAct takes nothing returns nothing\n"
          "local unit u=GetTriggerUnit()\n"
          "if GetUnitTypeId(u)=='E00U' and GetUnitLifePercent(u)<%d. then\n"
          "call IssueImmediateOrderById(u,Order_metamorphosis)\n"
          "endif\n"
          "set u=null\n"
          "endfunction\n"
          "function udI_MetaInit takes nothing returns nothing\n"
          "local trigger t=CreateTrigger()\n"
          "call AnyUnitDamagedEvent(t)\n"
          "call TriggerAddAction(t,function udI_MetaAct)\n"
          "set t=null\n"
          "endfunction\n") % META_HP
    anchor = 'function InitTrig_Wave7 takes nothing returns nothing'
    assert J.count(anchor) == 1
    J = J.replace(anchor, fn + anchor)
    old = 'call TriggerAddAction(gg_trg_Wave7,function Trig_Wave7_Actions)\n'
    assert J.count(old) == 1
    J = J.replace(old, old + 'call udI_MetaInit()\n')
    for mode in FOUR:
        J = four_lane(J, mode)
    return J


# ---- 右下王座四路 ----
# 入侵每波在三個王座間輪替（右下 h000_0592／右上 0591／左上 0593）。2.1.0 只有守右下的那幾波是四路：
# S8／SS8／SSS8 裡那幾波的發怪區塊 exitwhen L>4、單發隨機點 GetRandomInt(1,4)，其餘波次維持三路。
SP3 = 'set udg_SpawnPoints[3]=Location(9852.00,-9189.00)\n'
SP4 = 'set udg_SpawnPoints[4]=Location(13749.00,-6645.00)\n'
TRON_BR = 'set udg_Tron=gg_unit_h000_0592\n'
FOUR = {
    # 模式: (發怪觸發後綴, 右下波次, 換守點的函式, 第 1 波的開場函式或 None)
    '一般': ('', (1, 4, 7, 10, 13), 'Trig_WavesEnd_Actions', 'Trig_Lvl_8_Actions'),
    '骨灰': ('_Hard', (3, 6, 9, 12, 15), 'Trig_WavesEnd_Hard_Actions', None),
}
N4 = {}


def _lvl_branches(body, waves, fn):
    """把 body 依 `if/elseif udg_Lvl==N then` 分段，N 在 waves 裡的段落逐行套用 fn。"""
    out, cur = [], None
    for line in body.split('\n'):
        m = re.match(r'(?:else)?if udg_Lvl==(\d+) then$', line)
        if m:
            cur = int(m.group(1))
        out.append(fn(line) if cur in waves else line)
    return '\n'.join(out)


def four_lane(J, mode):
    suf, waves, ends, first = FOUR[mode]
    n = N4[mode] = {'points': 0, 'blocks': 0, 'rand': 0}
    # 輪到右下王座時設第 4 個出怪點
    a, b = _func(J, ends)
    parts = J[a:b].split(TRON_BR)
    for k in range(1, len(parts)):
        assert SP3 in parts[k]
        parts[k] = parts[k].replace(SP3, SP3 + SP4, 1)
    n['points'] = len(parts) - 1
    J = J[:a] + TRON_BR.join(parts) + J[b:]
    if first:                                       # 第 1 波就在右下：開場也放 4 個出怪傳送門
        J = _in_func(J, first, SP3, SP3 + SP4)
        J = _in_func(J, first, 'set bj_forLoopAIndexEnd=3\n', 'set bj_forLoopAIndexEnd=4\n')
        n['points'] += 1
    assert n['points'] == len(waves), (mode, n['points'])

    def fn(line):
        if line == 'exitwhen L>3':
            n['blocks'] += 1
            return 'exitwhen L>4'
        if 'udg_SpawnPoints[GetRandomInt(1,3)]' in line:
            n['rand'] += 1
            return line.replace('GetRandomInt(1,3)', 'GetRandomInt(1,4)')
        return line
    for t in ('S8', 'SS8', 'SSS8'):
        a, b = _func(J, 'Trig_%s%s_Actions' % (t, suf))
        J = J[:a] + _lvl_branches(J[a:b], waves, fn) + J[b:]
    return J


def patch_w3u(data):
    """E00C 換成 2.1.0 的整筆資料；E00U 加回 A0EK。"""
    old = mpq.MPQ(OLD_MAP).read('war3map.w3u')
    so, _, _ = w3a_poke._spans(old, False)
    sn, _, _ = w3a_poke._spans(data, False)
    a, b = sn['E00C']
    x, y = so['E00C']
    data = data[:a] + old[x:y] + data[b:]
    data, _ = w3a_poke.poke_str(data, {
        ('E00U', 'uabi', 0): 'A0FE,ACct,A0EK,ACev,AInv',
        ('E00C', 'uabi', 0): 'A0FE,A0EK,ACev,AInv',
        ('E00C', 'unam', 0): 'Оскверненный',
        ('E00C', 'upro', 0): 'Ларостор,Гиглеос,Нарт,Шарц,Мальвос',
    }, has_level=False)
    chk, _, _ = w3a_poke._spans(data, False)
    assert 'E00C' in chk and 'E00U' in chk
    return data


def patch_wts(data):
    old = 'Арсенал (+50% к награде)'.encode('utf-8')
    assert data.count(old) == 1
    return data.replace(old, 'Арсенал (+75% к награде)'.encode('utf-8'))
