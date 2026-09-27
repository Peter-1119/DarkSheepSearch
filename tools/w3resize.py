# -*- coding: utf-8 -*-
"""把一張 WC3 地圖的格網往 +X / +Y 方向長大，不動既有內容的世界座標。

原理：w3e 的 centerOffsetX/Y 是「格點 (0,0) 的世界座標」。只要這兩個值不動，
往東邊、北邊長出來的新格子就不會影響任何既有地形、裝飾物、單位或腳本座標。
需要同步長大的檔案：

    war3map.w3e   地形    header + (w×h) × 7 bytes，row-major，j=0 在南邊
    war3map.wpm   路徑    16-byte header + (4(w-1) × 4(h-1)) bytes
    war3map.shd   陰影    無 header， (4(w-1) × 4(h-1)) bytes
    war3map.w3i   資訊    可玩區格數 + 攝影機邊界

用法：
    from w3resize import Grower
    g = Grower(src_dir)
    g.grow(add_x=0, add_y=80, out_dir=dst_dir)
"""
import os
import struct

TP = 7                       # 每個 tilepoint 的 bytes


class W3E(object):
    def __init__(s, data):
        s.d = data
        p = 0
        s.magic = data[p:p + 4]; p += 4
        s.ver, = struct.unpack_from('<i', data, p); p += 4
        s.tileset = data[p:p + 1]; p += 1
        s.custom, = struct.unpack_from('<i', data, p); p += 4
        ng, = struct.unpack_from('<i', data, p); p += 4
        s.ground = [data[p + i * 4:p + i * 4 + 4] for i in range(ng)]; p += 4 * ng
        nc, = struct.unpack_from('<i', data, p); p += 4
        s.cliff = [data[p + i * 4:p + i * 4 + 4] for i in range(nc)]; p += 4 * nc
        s.w, s.h = struct.unpack_from('<ii', data, p); p += 8
        s.ox, s.oy = struct.unpack_from('<ff', data, p); p += 8
        s.body = p
        want = s.body + s.w * s.h * TP
        if len(data) < want:
            raise ValueError('w3e 太短：需要 %d，只有 %d' % (want, len(data)))
        s.extra = data[want:]          # 有些圖尾巴有額外資料，原樣保留

    def tile(s, i, j):
        o = s.body + (j * s.w + i) * TP
        return s.d[o:o + TP]

    def header_bytes(s, w, h):
        out = [s.magic, struct.pack('<i', s.ver), s.tileset,
               struct.pack('<i', s.custom), struct.pack('<i', len(s.ground))]
        out += s.ground
        out.append(struct.pack('<i', len(s.cliff)))
        out += s.cliff
        out.append(struct.pack('<ii', w, h))
        out.append(struct.pack('<ff', s.ox, s.oy))
        return b''.join(out)

    def grown(s, add_x, add_y, fill):
        """回傳長大後的 w3e bytes。fill 是 7 bytes 的樣板格。"""
        nw, nh = s.w + add_x, s.h + add_y
        parts = [s.header_bytes(nw, nh)]
        pad_row = fill * add_x
        for j in range(s.h):
            o = s.body + j * s.w * TP
            parts.append(s.d[o:o + s.w * TP])
            if add_x:
                parts.append(pad_row)
        if add_y:
            parts.append(fill * (nw * add_y))
        parts.append(s.extra)
        return b''.join(parts)


class WPM(object):
    HDR = 16

    def __init__(s, data):
        s.d = data
        s.magic = data[:4]
        s.ver, s.w, s.h = struct.unpack_from('<iii', data, 4)
        if len(data) != s.HDR + s.w * s.h:
            raise ValueError('wpm 大小不符：宣告 %dx%d 需要 %d，實際 %d'
                             % (s.w, s.h, s.HDR + s.w * s.h, len(data)))

    def cell(s, x, y):
        return s.d[s.HDR + y * s.w + x:s.HDR + y * s.w + x + 1]

    def grown(s, add_x, add_y, fill):
        ax, ay = add_x * 4, add_y * 4
        nw, nh = s.w + ax, s.h + ay
        parts = [s.magic, struct.pack('<iii', s.ver, nw, nh)]
        pad = fill * ax
        for y in range(s.h):
            o = s.HDR + y * s.w
            parts.append(s.d[o:o + s.w])
            if ax:
                parts.append(pad)
        if ay:
            parts.append(fill * (nw * ay))
        return b''.join(parts)


class SHD(object):
    """無 header，逐 byte 對應 4×4/地格。"""

    def __init__(s, data, tiles_w, tiles_h):
        s.d = data
        s.w, s.h = tiles_w * 4, tiles_h * 4
        if len(data) != s.w * s.h:
            raise ValueError('shd 大小不符：需要 %d，實際 %d' % (s.w * s.h, len(data)))

    def grown(s, add_x, add_y, fill):
        ax, ay = add_x * 4, add_y * 4
        nw = s.w + ax
        parts = []
        pad = fill * ax
        for y in range(s.h):
            o = y * s.w
            parts.append(s.d[o:o + s.w])
            if ax:
                parts.append(pad)
        if ay:
            parts.append(fill * (nw * ay))
        return b''.join(parts)


class W3I(object):
    """只動可玩區格數與攝影機邊界，其餘原樣不碰（就地覆寫，長度不變）。"""

    def __init__(s, data):
        s.d = bytearray(data)
        p = 0
        s.ver, = struct.unpack_from('<i', data, p); p += 4
        p += 8                                        # saves + editor version
        if s.ver >= 27:
            p += 16
        for _ in range(4):                            # name / author / desc / players
            p = data.index(b'\x00', p) + 1
        s.cam_off = p
        s.cam = list(struct.unpack_from('<8f', data, p)); p += 32
        s.comp_off = p
        s.comp = list(struct.unpack_from('<4i', data, p)); p += 16   # 上 下 左 右
        s.pw_off = p
        s.pw, s.ph = struct.unpack_from('<2i', data, p)

    def grown(s, add_x, add_y):
        d = bytearray(s.d)
        struct.pack_into('<2i', d, s.pw_off, s.pw + add_x, s.ph + add_y)
        # 攝影機：8 個 float 是四個角 (x,y)。只把「右」推東、「上」推北。
        cam = list(s.cam)
        xs, ys = cam[0::2], cam[1::2]
        maxx, maxy = max(xs), max(ys)
        for k in range(0, 8, 2):
            if cam[k] == maxx:
                cam[k] += add_x * 128.0
            if cam[k + 1] == maxy:
                cam[k + 1] += add_y * 128.0
        struct.pack_into('<8f', d, s.cam_off, *cam)
        return bytes(d), cam


class Grower(object):
    FILES = ('war3map.w3e', 'war3map.wpm', 'war3map.shd', 'war3map.w3i')

    def __init__(s, src_dir):
        s.src = src_dir
        s.raw = {}
        for f in s.FILES:
            p = os.path.join(src_dir, f)
            if not os.path.exists(p):
                raise IOError('缺少 %s' % p)
            s.raw[f] = open(p, 'rb').read()
        s.e = W3E(s.raw['war3map.w3e'])
        s.p = WPM(s.raw['war3map.wpm'])
        s.s = SHD(s.raw['war3map.shd'], s.e.w - 1, s.e.h - 1)
        s.i = W3I(s.raw['war3map.w3i'])

    def template(s, i, j):
        """拿 (i,j) 那一格當新地的樣板，回傳 (w3e 7bytes, wpm byte, shd byte)。"""
        return (s.e.tile(i, j), s.p.cell(i * 4, j * 4), s.s.d[j * 4 * s.s.w + i * 4:j * 4 * s.s.w + i * 4 + 1])

    def grow(s, add_x, add_y, tpl_ij, out_dir):
        tw3e, twpm, tshd = s.template(*tpl_ij)
        os.makedirs(out_dir, exist_ok=True)
        out = {}
        out['war3map.w3e'] = s.e.grown(add_x, add_y, tw3e)
        out['war3map.wpm'] = s.p.grown(add_x, add_y, twpm)
        out['war3map.shd'] = s.s.grown(add_x, add_y, tshd)
        out['war3map.w3i'], cam = s.i.grown(add_x, add_y)
        for f, d in out.items():
            open(os.path.join(out_dir, f), 'wb').write(d)
        return out, cam
