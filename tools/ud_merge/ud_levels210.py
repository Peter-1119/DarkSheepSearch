# -*- coding: utf-8 -*-
"""陵墓下層、冰霜森林（一般＋骨灰）改回 2.1.0 的地圖；出怪只改「路數」，數量與陣容維持新版。

地圖（terrain / placed_units）
  三塊區域的地格、路徑、陰影、裝飾物照 2.1.0；兩版都有的裝飾物沿用新版那一份（保留腳本綁定的城門）。
  預放單位：
    - 能量圈、水晶、商店等「點位」照 2.1.0 的擺放（跟地形綁在一起）
    - 敵對單位／塔：舊版單位附近（256 內）有新版同位置的，留新版（數值與 ID 用新版）；
      新版多出來、2.1.0 沒有的移除（例：陵墓下層中段入口的野怪營地，會跟恢復的出怪門重疊）；
      2.1.0 有、但該 ID 在新版是別的單位（基底不同）就不加，記在 log
路數（lanes）
  陵墓下層：出怪門 6 → 8（2.1.0 的中段左右入口加回來）、每波 4 路 → 6 路；
            區塊、隨機點、敵方英雄出生點的索引全部照 2.1.0（兩版的出怪序列逐一比對，完全相同才換）
  冰霜森林（骨灰）：加回 2.1.0 的第 3 個出怪點 (16415,-12317)，2 路 → 3 路
  冰霜森林（一般）：兩版本來就是 3 路、出怪點相同，不動
"""
import re
import mpq
import w3obj
import w3transplant as tp
from w3resize import W3E, WPM
from w3doo import DOO

OLD_MAP = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/000肥羊的聖誕禮物_2.1.0_ty.w3x'
# (名稱, 世界矩形)。陵墓下層往下接到冰霜森林頂端（兩區之間的通道也不同）；骨灰冰霜北緣外框另列
AREAS = [
    ('陵墓下層', (-4000.0, -2592.0, 3488.0, 6720.0)),
    ('冰霜森林', (-7072.0, -11296.0, 3936.0, -2592.0)),
    ('冰霜森林（骨灰）', (14176.0, -14336.0, 26624.0, -4960.0)),
    ('冰霜森林（骨灰）北緣', (19200.0, -4960.0, 26624.0, -3584.0)),
]
POINTS = {'n000', 'n001', 'n002', 'n003', 'n01U', 'n068',          # 能量圈
          'n030', 'n031', 'n05V', 'n05X',                          # 水晶
          'o00K', 'o00L', 'h00R', 'n01G', 'h000'}                  # 商店、王座
PAIR_DIST = 256.0


class _Old(object):
    def __init__(s):
        m = mpq.MPQ(OLD_MAP)
        s.e = W3E(m.read('war3map.w3e'))
        s.p = WPM(m.read('war3map.wpm'))
        s.s = m.read('war3map.shd')
        s.doo = DOO(m.read('war3map.doo'))
        s.w3u = w3obj.parse(m.read('war3map.w3u'), False)
        s.blp = m.read('war3mapMap.blp')
        s.w3i = m.read('war3map.w3i')


_OLD = []


def old():
    if not _OLD:
        _OLD.append(_Old())
    return _OLD[0]


def trect(e, w):
    """世界矩形 → tilepoint 矩形（外擴到整格）。"""
    return (int((w[0] - e.ox) // 128), int((w[1] - e.oy) // 128),
            int(-(-(w[2] - e.ox) // 128)), int(-(-(w[3] - e.oy) // 128)))


# ================================================================ 地形
def terrain(W3E_B, E2, WPM_B, SHD_B, DN, log):
    """W3E_B/WPM_B/SHD_B：bytearray（已拓寬）；E2：W3E(W3E_B)；DN：新版 DOO。拓寬只加在北邊，座標不變。"""
    O = old()
    EO = O.e
    assert (EO.ox, EO.oy) == (E2.ox, E2.oy) and EO.w == E2.w
    assert EO.cliff == E2.cliff, '懸崖貼圖不同'
    tex = {}
    for k, g in enumerate(EO.ground):
        if k < len(E2.ground) and E2.ground[k] == g:
            continue
        # 2.1.0 的 Itbk 新圖沒有，改用最接近的 Ibkb（同陵墓上層的做法）
        assert g == b'Itbk' and b'Ibkb' in E2.ground, (k, g)
        tex[k] = E2.ground.index(b'Ibkb')
    next_eid = max(d.eid for d in DN.items) + 1
    key = lambda d: (d.tid, round(d.x), round(d.y))
    for name, w in AREAS:
        r = trect(EO, w)
        tp.copy_w3e(EO, W3E_B, E2.body, E2.w, r, (r[0], r[1]), tex)
        tp.copy_cells(O.p.d, O.p.HDR, O.p.w, WPM_B, 16, (E2.w - 1) * 4, r, (r[0], r[1]))
        tp.copy_cells(O.s, 0, (EO.w - 1) * 4, SHD_B, 0, (E2.w - 1) * 4, r, (r[0], r[1]))
        wr = tp.world_rect(EO, r)
        inw = lambda d: wr[0] <= d.x < wr[2] and wr[1] <= d.y < wr[3]
        ko = {key(d): d for d in O.doo.items if inw(d)}
        kn = {key(d) for d in DN.items if inw(d)}
        n0 = len(DN.items)
        DN.items = [d for d in DN.items if not inw(d) or key(d) in ko]
        removed = n0 - len(DN.items)
        added = 0
        for k, d in ko.items():
            if k not in kn:
                c = d.copy(); c.eid = next_eid; next_eid += 1
                DN.items.append(c); added += 1
        ins = lambda o: r[0] <= o.x < r[2] and r[1] <= o.y < r[3]
        ns = len(DN.special)
        DN.special = [o for o in DN.special if not ins(o)] + tp.pick_special(O.doo, r)
        log('[2.1.0 地圖] %s：地格 %d×%d、路徑、陰影換成 2.1.0；裝飾物 −%d／+%d（相同的 %d 個沿用新版）；地形裝飾 %d→%d'
            % (name, r[2] - r[0], r[3] - r[1], removed, added, len(ko) - added, ns, len(DN.special)))
    return [w for n, w in AREAS]


# ================================================================ 預放單位
_CU = re.compile(r"set (\w+)=CreateUnit\(p,'(\w{4})',(-?[\d.]+),(-?[\d.]+),")


def _blocks(J):
    """Create* 函式裡的每個 CreateUnit：(函式名, 起行, 迄行, 變數, ID, x, y)。迄行不含。"""
    lines = J.split('\n')
    out, owner = [], None
    for k, l in enumerate(lines):
        m = re.match(r'function (Create\w+) takes', l)
        if m:
            owner = m.group(1)
            continue
        if owner and l.startswith('endfunction'):
            owner = None
            continue
        m = _CU.match(l)
        if owner and m:
            j = k + 1
            while j < len(lines) and not (_CU.match(lines[j]) or lines[j].startswith('endfunction')):
                j += 1
            out.append((owner, k, j, m.group(1), m.group(2), float(m.group(3)), float(m.group(4))))
    return lines, out


def placed_units(J, J210, w3u_new, log):
    O = old()
    lines, bn = _blocks(J)
    lo, bo = _blocks(J210)
    fn_new = set(re.findall(r'^function (\w+) takes', J, re.M))
    drop, add, moved = set(), {}, []
    for name, w in AREAS:
        inw = lambda b: w[0] <= b[5] < w[2] and w[1] <= b[6] < w[3]
        N = [b for b in bn if inw(b)]
        Ob = [b for b in bo if inw(b)]
        kn = {(b[4], round(b[5]), round(b[6])) for b in N}
        ko = {(b[4], round(b[5]), round(b[6])) for b in Ob}
        only_n = [b for b in N if (b[4], round(b[5]), round(b[6])) not in ko]
        only_o = [b for b in Ob if (b[4], round(b[5]), round(b[6])) not in kn]
        kept_new, skipped = [], []
        # 有名字的單位（腳本會參照）：沿用新版那一行，只把座標搬到 2.1.0 的位置
        for b in [x for x in only_o if x[3] != 'u']:
            nb = [x for x in N if x[3] == b[3]]
            assert len(nb) == 1 and nb[0][4] == b[4], ('有名字的單位兩版對不上', b)
            k = nb[0][1]
            lines[k] = _CU.sub(lambda m: "set %s=CreateUnit(p,'%s',%.1f,%.1f," % (b[3], b[4], b[5], b[6]), lines[k], 1)
            kept_new.append(nb[0]); moved.append(b[3])
        only_o = [x for x in only_o if x[3] == 'u']
        for b in only_o:
            if b[4] not in POINTS:
                # 敵對單位／塔：附近有新版同功能（同函式）的新單位 → 留新版
                near = [x for x in only_n if x[0] == b[0] and x[4] not in POINTS and x not in kept_new
                        and (x[5] - b[5]) ** 2 + (x[6] - b[6]) ** 2 <= PAIR_DIST ** 2]
                if near:
                    kept_new.append(min(near, key=lambda x: (x[5] - b[5]) ** 2 + (x[6] - b[6]) ** 2))
                    continue
            a, n = O.w3u.get(b[4]), w3u_new.get(b[4])
            if (a or n) and (a is None or n is None or a.get('_base') != n.get('_base')):
                skipped.append(b[4]); continue
            body = lo[b[1]:b[2]]
            ref = set(re.findall(r'function (\w+)', '\n'.join(body)))
            if ref - fn_new:          # 掉寶函式新版沒有：只放單位，不掛掉寶
                body = [x for x in body if not re.search(r'CreateTrigger|TriggerRegister|TriggerAddAction', x)]
            assert b[3] == 'u', b     # 有名字的單位兩版都一樣，不會走到這裡
            add.setdefault(b[0], []).extend(body)
        for b in only_n:
            if b not in kept_new:
                assert b[3] == 'u', ('新版有名字的單位要被移除？', b)
                drop.add(b[1])
        n_pair = len(kept_new) - len(moved)
        log('[2.1.0 地圖] %s 預放單位：共同 %d、照 2.1.0 加 %d、移除新版 %d、敵對單位沿用新版 %d%s%s'
            % (name, len(ko & kn), len(only_o) - n_pair - len(skipped), len(only_n) - len(kept_new),
               n_pair, '；有名字的單位移到 2.1.0 位置：%s' % ','.join(moved) if moved else '',
               '；ID 在新版是別的單位、略過：%s' % ','.join(skipped) if skipped else ''))
        del moved[:]
    # 移除新版多出的區塊
    dead = set()
    for b in bn:
        if b[1] in drop:
            dead.update(range(b[1], b[2]))
    lines = [l for k, l in enumerate(lines) if k not in dead]
    J = '\n'.join(lines)
    # 加到對應函式的結尾
    for fn, body in add.items():
        m = re.search(r'^function %s takes[^\n]*\n' % fn, J, re.M)
        assert m, fn
        e = J.index('\nendfunction', m.start())
        J = J[:e] + '\n' + '\n'.join(body) + J[e:]
    return J


# ================================================================ 路數
def _func(J, name):
    m = re.search(r'^function %s takes[^\n]*\n' % re.escape(name), J, re.M)
    assert m, name
    return m.start(), J.index('\nendfunction', m.start()) + len('\nendfunction')


_TOK = re.compile(r'SpawnPoints\[(GetRandomInt\(\d,\d\)|\d)\]')


def _tokens(body):
    """出怪索引記號，依出現順序：('L', 迴圈起行, 起, 迄, 單位) / ('T', 行, 位置, 文字, 單位)。"""
    lines = body.split('\n')
    out = []
    k = 0
    while k < len(lines):
        m = re.match(r'set L=(\d+)$', lines[k])
        if m and k + 2 < len(lines) and lines[k + 1] == 'loop':
            m2 = re.match(r'exitwhen L>(\d+)$', lines[k + 2])
            if m2:
                j = k + 3; units = []
                while not lines[j].startswith('set L=L+1'):
                    units += re.findall(r"'(\w{4})'", lines[j]); j += 1
                out.append(['L', k, m.group(1), m2.group(1), tuple(units)])
                k = j + 1
                continue
        for mm in _TOK.finditer(lines[k]):
            out.append(['T', k, mm.start(1), mm.group(1), tuple(re.findall(r"'(\w{4})'", lines[k]))])
        k += 1
    return lines, out


def align_lanes(J, J210, name):
    """把新版函式的出怪索引換成 2.1.0 同一個函式的；兩邊的出怪序列（單位）必須完全一樣。"""
    s, e = _func(J, name)
    so, eo = _func(J210, name)
    ln, tn = _tokens(J[s:e])
    lo, to = _tokens(J210[so:eo])
    sig = lambda T: [(t[0], t[4]) for t in T]
    assert sig(tn) == sig(to), '%s：兩版出怪序列不同，不能只換路數' % name
    n = 0
    for a, b in sorted(zip(tn, to), key=lambda ab: (-ab[0][1], -(ab[0][2] if ab[0][0] == 'T' else 0))):
        if a[0] == 'L':
            if (a[2], a[3]) != (b[2], b[3]):
                ln[a[1]] = 'set L=%s' % b[2]; ln[a[1] + 2] = 'exitwhen L>%s' % b[3]; n += 1
        elif a[3] != b[3]:
            l = ln[a[1]]
            ln[a[1]] = l[:a[2]] + b[3] + l[a[2] + len(a[3]):]; n += 1
    return J[:s] + '\n'.join(ln) + J[e:], n


def _sub(J, name, a, b, count=None):
    s, e = _func(J, name)
    body = J[s:e]
    c = body.count(a)
    assert c and (count is None or c == count), (name, a, c)
    return J[:s] + body.replace(a, b) + J[e:], c


def _branch_rand(J, J210, name, lvls):
    """ExtraEnemyHero：`if udg_Lvl==N` 分支裡的 set b=GetRandomInt(..) 照 2.1.0。"""
    def br(body):
        out, cur = {}, None
        for k, l in enumerate(body.split('\n')):
            m = re.match(r'(?:else)?if udg_Lvl==(\d+) then$', l)
            if m:
                cur = int(m.group(1))
            m = re.match(r'set b=GetRandomInt\((\d,\d)\)$', l)
            if m and cur in lvls:
                out[cur] = (k, m.group(1))
        return out
    s, e = _func(J, name)
    so, eo = _func(J210, name)
    ln = J[s:e].split('\n')
    a, b = br(J[s:e]), br(J210[so:eo])
    n = 0
    for lv in lvls:
        if lv in a and lv in b and a[lv][1] != b[lv][1]:
            ln[a[lv][0]] = 'set b=GetRandomInt(%s)' % b[lv][1]; n += 1
    return J[:s] + '\n'.join(ln) + J[e:], n


def lanes(J, J210, log):
    # ---- 陵墓下層（Lvl 5 一般／15 骨灰）----
    for L in (5, 15):
        name = 'Trig_Lvl_%d_Actions' % L
        s, e = _func(J, name)
        so, eo = _func(J210, name)
        new_pts = re.search(r'(set udg_SpawnPoints\[1\]=Location[^\n]*\n(?:set udg_SpawnPoints\[\d\]=Location[^\n]*\n)*)', J[s:e]).group(1)
        old_pts = re.search(r'(set udg_SpawnPoints\[1\]=Location[^\n]*\n(?:set udg_SpawnPoints\[\d\]=Location[^\n]*\n)*)', J210[so:eo]).group(1)
        assert new_pts.count('\n') == 6 and old_pts.count('\n') == 8
        J, _ = _sub(J, name, new_pts, old_pts, 1)
        # 出怪門 6→8、小地圖提示 4→6（2.1.0 也是提示前 6 個）
        J, _ = _sub(J, name, "set bj_forLoopAIndexEnd=6\nloop\nexitwhen bj_forLoopAIndex>bj_forLoopAIndexEnd\ncall CreateNUnitsAtLoc(1,'o010'",
                    "set bj_forLoopAIndexEnd=8\nloop\nexitwhen bj_forLoopAIndex>bj_forLoopAIndexEnd\ncall CreateNUnitsAtLoc(1,'o010'", 1)
        J, _ = _sub(J, name, "set bj_forLoopAIndexEnd=4\nloop\nexitwhen bj_forLoopAIndex>bj_forLoopAIndexEnd\ncall PingMinimapLocForForceEx(GetPlayersAll(),udg_SpawnPoints[",
                    "set bj_forLoopAIndexEnd=6\nloop\nexitwhen bj_forLoopAIndex>bj_forLoopAIndexEnd\ncall PingMinimapLocForForceEx(GetPlayersAll(),udg_SpawnPoints[", 1)
        J, n = align_lanes(J, J210, name)
        log('[2.1.0 路數] 陵墓下層 Lvl %d：出怪門 6→8（加回中段左右入口）、首領出生點 %d 處照 2.1.0' % (L, n))
    tot = 0
    for t in ('S5', 'SS5', 'SSS5', 'Hard_S5', 'Hard_SS5', 'Hard_SSS5', 'CreateHero5', 'CreateHero5_Hard'):
        J, n = align_lanes(J, J210, 'Trig_%s_Actions' % t)
        tot += n
    J, nb = _branch_rand(J, J210, 'Trig_ExtraEnemyHero_Actions', (5, 15))
    log('[2.1.0 路數] 陵墓下層出怪：每波 4 路 → 6 路，改了 %d 處索引（出怪序列兩版逐一比對相同）；額外敵方英雄 %d 處' % (tot, nb))

    # ---- 冰霜森林骨灰（Lvl 16）：加回第 3 個出怪點 ----
    name = 'Trig_Lvl_16_Actions'
    a = 'set udg_SpawnPoints[2]=Location(23767.00,-7637.00)\n'
    J, _ = _sub(J, name, a, a + 'set udg_SpawnPoints[3]=Location(16415.00,-12317.00)\n', 1)
    J, _ = _sub(J, name, "set bj_forLoopAIndexEnd=2\nloop\nexitwhen bj_forLoopAIndex>bj_forLoopAIndexEnd\ncall CreateNUnitsAtLoc(1,'o010'",
                "set bj_forLoopAIndexEnd=3\nloop\nexitwhen bj_forLoopAIndex>bj_forLoopAIndexEnd\ncall CreateNUnitsAtLoc(1,'o010'", 1)
    J, c0 = _sub(J, name, 'SpawnPoints[GetRandomInt(1,2)]', 'SpawnPoints[GetRandomInt(1,3)]')
    tot = c0
    for t in ('Hard_S6', 'Hard_SS6', 'Hard_SSS6'):
        s, e = _func(J, 'Trig_%s_Actions' % t)
        body = J[s:e]
        c = body.count('exitwhen L>2\n') + body.count('SpawnPoints[GetRandomInt(1,2)]')
        body = body.replace('exitwhen L>2\n', 'exitwhen L>3\n').replace('SpawnPoints[GetRandomInt(1,2)]', 'SpawnPoints[GetRandomInt(1,3)]')
        J = J[:s] + body + J[e:]
        tot += c
    J, c = _sub(J, 'Trig_CreateHero6_Hard_Actions', 'SpawnPoints[GetRandomInt(1,2)]', 'SpawnPoints[GetRandomInt(1,3)]')
    tot += c
    J, nb = _branch_rand(J, J210, 'Trig_ExtraEnemyHero_Actions', (16,))
    log('[2.1.0 路數] 冰霜森林骨灰：加回第 3 個出怪點 (16415,-12317)，2 路 → 3 路，改了 %d 處；額外敵方英雄 %d 處' % (tot, nb))
    return J


# ================================================================ 小地圖
def minimap(img, R1, mm, log):
    """把三塊區域在小地圖上的像素換成 2.1.0 小地圖同一點。R1：新小地圖的世界矩形（拓寬後）；mm：w3minimap。"""
    import io
    from PIL import Image
    from w3resize import W3I
    O = old()
    src = Image.open(io.BytesIO(O.blp)).convert('RGB')
    wi = W3I(O.w3i)
    R0 = (O.e.ox + wi.comp[2] * 128, O.e.oy + wi.comp[1] * 128,
          O.e.ox + (wi.comp[2] + wi.pw) * 128, O.e.oy + (wi.comp[1] + wi.ph) * 128)
    sp, dp = src.load(), img.load()
    W, H = img.size
    n = 0
    for v in range(H):
        for u in range(W):
            wx, wy = mm.px_to_world(R1, u + 0.5, v + 0.5, W)
            if not any(w[0] <= wx < w[2] and w[1] <= wy < w[3] for _, w in AREAS):
                continue
            a, b = mm.world_to_px(R0, wx, wy, src.size[0])
            dp[u, v] = sp[min(src.size[0] - 1, max(0, int(a))), min(src.size[1] - 1, max(0, int(b)))]
            n += 1
    log('[2.1.0 地圖] 小地圖：三塊區域 %d 像素改用 2.1.0 小地圖' % n)
    return img
