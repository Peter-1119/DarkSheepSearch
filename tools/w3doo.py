# -*- coding: utf-8 -*-
"""war3map.doo（裝飾物／可破壞物）讀寫。

格式（version 8, subversion 11）：
    'W3do' int version, int subversion, int count
    每筆：
        char[4] typeId, int variation, float x, y, z, float angle,
        float sx, sy, sz, byte flags, byte life,
        int itemTablePointer, int droppedSetCount,
            每組：int n, n × (char[4] itemId, int chance)
        int editorId
    之後：int specialVersion, int specialCount, 每筆 (char[4] id, int z, int x, int y)
          —— 懸崖／地形裝飾，座標是地格索引
"""
import struct


class Doodad(object):
    __slots__ = ('tid', 'var', 'x', 'y', 'z', 'ang', 'sx', 'sy', 'sz',
                 'flags', 'life', 'itab', 'sets', 'eid')

    def pack(s):
        out = [s.tid, struct.pack('<i3f f 3f BB i i', s.var, s.x, s.y, s.z, s.ang,
                                  s.sx, s.sy, s.sz, s.flags, s.life, s.itab, len(s.sets))]
        for items in s.sets:
            out.append(struct.pack('<i', len(items)))
            for iid, ch in items:
                out.append(iid + struct.pack('<i', ch))
        out.append(struct.pack('<i', s.eid))
        return b''.join(out)

    def copy(s):
        d = Doodad()
        for k in s.__slots__:
            setattr(d, k, getattr(s, k))
        d.sets = [list(x) for x in s.sets]
        return d


class Special(object):
    __slots__ = ('tid', 'z', 'x', 'y')

    def pack(s):
        return s.tid + struct.pack('<3i', s.z, s.x, s.y)


class DOO(object):
    def __init__(s, data):
        assert data[:4] == b'W3do'
        s.ver, s.sub, n = struct.unpack_from('<3i', data, 4)
        assert s.ver == 8 and s.sub == 11, (s.ver, s.sub)
        p = 16
        s.items = []
        for _ in range(n):
            d = Doodad()
            d.tid = data[p:p + 4]
            (d.var, d.x, d.y, d.z, d.ang, d.sx, d.sy, d.sz,
             d.flags, d.life, d.itab, nsets) = struct.unpack_from('<i3f f 3f BB i i', data, p + 4)
            p += 4 + struct.calcsize('<i3f f 3f BB i i')
            d.sets = []
            for _ in range(nsets):
                k, = struct.unpack_from('<i', data, p); p += 4
                items = []
                for _ in range(k):
                    items.append((data[p:p + 4], struct.unpack_from('<i', data, p + 4)[0])); p += 8
                d.sets.append(items)
            d.eid, = struct.unpack_from('<i', data, p); p += 4
            s.items.append(d)
        s.sp_ver, ns = struct.unpack_from('<2i', data, p); p += 8
        s.special = []
        for _ in range(ns):
            o = Special()
            o.tid = data[p:p + 4]
            o.z, o.x, o.y = struct.unpack_from('<3i', data, p + 4)
            p += 16
            s.special.append(o)
        s.tail = data[p:]

    def pack(s):
        out = [b'W3do', struct.pack('<3i', s.ver, s.sub, len(s.items))]
        out += [d.pack() for d in s.items]
        out.append(struct.pack('<2i', s.sp_ver, len(s.special)))
        out += [o.pack() for o in s.special]
        out.append(s.tail)
        return b''.join(out)
