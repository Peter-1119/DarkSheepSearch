# -*- coding: utf-8 -*-
"""在修好的地圖上再套一層「只加最大攻擊」的實驗版。

背景：魔獸的傷害是 基礎值 + 骰數 × 隨機(1~骰面)，所以
    最小 = 基礎值 + 骰數      最大 = 基礎值 + 骰數 × 骰面
要「只加最大」就只能動骰數或骰面。1.29.2 在遊戲中兩個都改不了（實測證實），
但**科技**可以：UpgradeEffectMetaData.slk 裡的 ratd ＝ 攻擊骰子加成。

弓箭手的骰面是 1，所以加骰子等於 +1/+1，那個把手是死的。這支工具把英雄的
武器改成「骰數 0、骰面 100、基礎值 2」—— 起始傷害一樣是 2-2（0 顆骰子就不擲），
但從此每加 1 顆骰子就是 最小 +1、最大 +100。於是：

    最大攻擊 +200  ->  加 2 顆骰子  ->  顯示 4 - 202

跟說明幾乎一模一樣（最小會多 2，佔 200 的 1%）。

風險：官方沒有任何單位用「骰數 0」。欄位定義說最小值就是 0（UnitMetaData.slk），
所以規格上合法，但沒有先例。這就是為什麼要獨立成一個檔案讓人先試。

用法：python tools/archer_dice.py 已修好的.w3x 輸出.w3x
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mpq import MPQ
import mpq_patch
import slk
import w3a_poke

B = chr(92)
SIDES = 100                     # 骰面上限就是 100（UnitMetaData）
DICE_UPGRADES = [('R00S', 10.0, 10), ('R00T', 1.0, 9)]   # 最多 109 顆，程式裡夾到 100


def hero_ids(bal):
    rows, _ = slk.loads(bal)
    return [k for k, v in sorted(rows.items())
            if re.fullmatch(r'H0[0-9A-Z]{2}', k)
            and str(v.get('Primary', '_')) in ('STR', 'AGI', 'INT')], rows


def fix_weapon(wep, heroes):
    """英雄武器改成 骰數 0 / 骰面 100 / 基礎值 = 原本的最小傷害。"""
    rows, _ = slk.loads(wep)
    cd = slk.col_index(wep, 'dice1')
    cs = slk.col_index(wep, 'sides1')
    cb = slk.col_index(wep, 'dmgplus1')
    cells, notes = [], []
    for h in heroes:
        r = rows.get(h)
        if not r:
            continue
        lo = int(float(r.get('mindmg1') or 0))
        if lo <= 0:
            continue
        cells += [(r['_row'], cd, 0), (r['_row'], cs, SIDES), (r['_row'], cb, lo)]
        notes.append('%s 起始仍是 %d-%d，但每顆骰子 = 最小+1／最大+%d' % (h, lo, lo, SIDES))
    if not cells:
        raise SystemExit('沒有英雄需要改武器')
    out = slk.set_cells(wep, cells)
    # 讀回來核對，順便確認沒動到別人
    back, _ = slk.loads(out)
    before, _ = slk.loads(wep)
    for h in heroes:
        if int(float(back[h]['dice1'])) != 0 or int(float(back[h]['sides1'])) != SIDES:
            raise SystemExit('%s 的武器沒寫進去' % h)
    for uid, rec in before.items():
        for k, v in rec.items():
            if uid in heroes and k in ('dice1', 'sides1', 'dmgplus1'):
                continue
            if back[uid].get(k) != v:
                raise SystemExit('%s 的 %s 被改到了：%r -> %r' % (uid, k, v, back[uid].get(k)))
    return out, notes


def fix_upgrades(w3q):
    """再複製兩個科技出來當骰子階梯。"""
    ids = [i for i, _, _ in DICE_UPGRADES]
    out, _ = w3a_poke.clone(w3q, 'R002', ids, True)
    edits = {}
    for aid, step, lv in DICE_UPGRADES:
        edits[(aid, 'gba1', 0)] = step
        edits[(aid, 'gmo1', 0)] = step
        edits[(aid, 'glvl', 0)] = lv
    out, _ = w3a_poke.poke(out, edits, True)
    out, _ = w3a_poke.poke_str(out, {(i, 'gef1', 0): 'ratd' for i in ids}, True)
    return out


OLD_APPLY = """set want=dmin+(dmax-dmin)/2
if want<0 then
set want=0
endif
if want>50990 then
set want=50990
endif
if want==cur then
return
endif
call SaveReal(YDHT,id,0x41524313,I2R(want))
set s=want/10
call SetPlayerTechResearched(GetOwningPlayer(u),'R00P',s/100)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00Q',(s/10)-(s/100)*10)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00R',s-(s/10)*10)
endfunction"""

# 骰數 D 讓 最小 +D、最大 +100D，所以 D = 差距/99；剩下的用基礎值補平。
NEW_APPLY = """set s=(dmax-dmin)/99
if s<0 then
set s=0
endif
if s>100 then
set s=100
endif
set want=dmin-s
if want<0 then
set want=0
endif
if want>50990 then
set want=50990
endif
call SetPlayerTechResearched(GetOwningPlayer(u),'R00S',s/10)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00T',s-(s/10)*10)
if want==cur then
return
endif
call SaveReal(YDHT,id,0x41524313,I2R(want))
set s=want/10
call SetPlayerTechResearched(GetOwningPlayer(u),'R00P',s/100)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00Q',(s/10)-(s/100)*10)
call SetPlayerTechResearched(GetOwningPlayer(u),'R00R',s-(s/10)*10)
endfunction"""


def main():
    src = sys.argv[1]
    dst = sys.argv[2]
    m = MPQ(src)

    bal = m.read('Units' + B + 'UnitBalance.slk')
    heroes, rows = hero_ids(bal)
    print('英雄 %d 個：%s' % (len(heroes), ' '.join(heroes)))

    wep, notes = fix_weapon(m.read('Units' + B + 'UnitWeapons.slk'), heroes)
    for n in notes[:3]:
        print('  ' + n)
    print('  （其餘 %d 個同樣處理）' % max(0, len(notes) - 3))

    # 英雄要掛上新的兩個科技
    col = slk.col_index(bal, 'upgrades')
    cells = []
    for h in heroes:
        cur = str(rows[h].get('upgrades') or '')
        if 'R00S' in cur:
            continue
        cells.append((rows[h]['_row'], col, cur + ',R00S,R00T'))
    bal2 = slk.set_cells(bal, cells)
    back, _ = slk.loads(bal2)
    for h in heroes:
        if 'R00S' not in str(back[h].get('upgrades')):
            raise SystemExit('%s 沒掛上骰子科技' % h)
    print('  科技掛載：%d 個英雄加上 R00S,R00T' % len(cells))

    w3q = fix_upgrades(m.read('war3map.w3q'))
    print('  骰子科技：R00S（一級 10 顆，10 級）、R00T（一級 1 顆，9 級）')

    j = m.read('war3map.j').decode('utf-8', 'surrogateescape')
    if j.count(OLD_APPLY) != 1:
        raise SystemExit('攻擊力套用那一段找到 %d 次（要剛好 1 次）' % j.count(OLD_APPLY))
    j = j.replace(OLD_APPLY, NEW_APPLY, 1)
    print('  帳本：差距改用骰子表達（骰數 = 差距÷99）')

    edits = {'Units' + B + 'UnitWeapons.slk': wep,
             'Units' + B + 'UnitBalance.slk': bal2,
             'war3map.w3q': w3q,
             'war3map.j': j.encode('utf-8', 'surrogateescape')}
    mpq_patch.write_files(src, dst, edits)
    ok, msg = mpq_patch.verify(src, dst, edits)
    for line in msg:
        print(line)
    if not ok:
        raise SystemExit('驗證失敗')
    print('  完成：%s' % os.path.basename(dst))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
