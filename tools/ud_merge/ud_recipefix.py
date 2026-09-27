# -*- coding: utf-8 -*-
"""神器合成對齊網站（3.82fix）：新版把三件 lv.5 神器改成 3 件合成，這裡換回 4 件的版本，
價值也換回 5400（= 組件總價）。道具本身的屬性仍用新版。"""
import os, re
import w3a_poke, mpq
OLD_MAP = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/UD_v3_82fix_opt.w3x'

BASE = os.path.dirname(os.path.abspath(__file__))
FUNCS = ('T5Necklace', 'T5Shield', 'TitanGloves')      # 水晶項鍊 mnsf、鋼鐵奉獻 axas、泰坦神拳 spre
GOLD = {'mnsf': 5400, 'axas': 5400, 'spre': 5400}


def _func(J, name):
    m = re.search(r'\nfunction %s takes.*?\nendfunction' % name, J, re.S)
    assert m, name
    return m.group(0)


def patch_jass(J):
    old = mpq.MPQ(OLD_MAP).read('war3map.j').decode('utf-8', 'surrogateescape')
    for f in FUNCS:
        J = J.replace(_func(J, f), _func(old, f))
    return J


def patch_w3t(data):
    data, notes = w3a_poke.poke(data, {(k, 'igol', 0): v for k, v in GOLD.items()}, has_level=False)
    return data
