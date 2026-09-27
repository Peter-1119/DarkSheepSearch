# -*- coding: utf-8 -*-
"""把一張地圖的某塊地形（連同路徑、陰影、裝飾物）搬到另一張地圖的指定位置。

座標約定：
    tilepoint 矩形 (i0, j0, i1, j1) 兩端都包含，對應地格 i0..i1-1、j0..j1-1。
    目的地用左下角 tilepoint (di, dj) 表示。
    世界座標位移 = (dst.ox + di*128) - (src.ox + i0*128)，Y 同理。
"""
import struct

TP = 7


def world_shift(src_e, dst_e, rect, dest):
    i0, j0 = rect[0], rect[1]
    di, dj = dest
    return ((dst_e.ox + di * 128.0) - (src_e.ox + i0 * 128.0),
            (dst_e.oy + dj * 128.0) - (src_e.oy + j0 * 128.0))


def world_rect(e, rect):
    i0, j0, i1, j1 = rect
    return (e.ox + i0 * 128.0, e.oy + j0 * 128.0, e.ox + i1 * 128.0, e.oy + j1 * 128.0)


def copy_w3e(src_e, dst_buf, dst_body, dst_w, rect, dest, tex_map=None):
    """把 src 的 tilepoint 矩形寫進 dst_buf（bytearray）。tex_map：{舊地表索引: 新地表索引}"""
    i0, j0, i1, j1 = rect
    di, dj = dest
    n = 0
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            t = bytearray(src_e.tile(i, j))
            if tex_map:
                g = t[4] & 0x0F
                if g in tex_map:
                    t[4] = (t[4] & 0xF0) | tex_map[g]
            o = dst_body + ((dj + j - j0) * dst_w + (di + i - i0)) * TP
            dst_buf[o:o + TP] = t
            n += 1
    return n


def copy_cells(src, src_hdr, src_w, dst, dst_hdr, dst_w, rect, dest):
    """wpm / shd：每地格 4×4。rect 是 tilepoint 矩形，實際搬的是地格 i0..i1-1。"""
    i0, j0, i1, j1 = rect
    di, dj = dest
    cols = (i1 - i0) * 4
    for y in range(j0 * 4, j1 * 4):
        so = src_hdr + y * src_w + i0 * 4
        do = dst_hdr + (dj * 4 + y - j0 * 4) * dst_w + di * 4
        dst[do:do + cols] = src[so:so + cols]
    return cols * (j1 - j0) * 4


def pick_doodads(src_doo, wrect):
    x0, y0, x1, y1 = wrect
    return [d for d in src_doo.items if x0 <= d.x < x1 and y0 <= d.y < y1]


def pick_special(src_doo, rect):
    i0, j0, i1, j1 = rect
    return [o for o in src_doo.special if i0 <= o.x < i1 and j0 <= o.y < j1]
