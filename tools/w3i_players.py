# -*- coding: utf-8 -*-
"""war3map.w3i 的玩家記錄讀寫 —— 用來把被刪掉的玩家槽補回去。

w3i 玩家記錄格式（每筆）：
    int   playerId
    int   controller   0=使用者 1=電腦 2=中立 3=可救援
    int   race         0=選擇 1=人類 2=獸族 3=不死 4=暗夜
    int   fixedStart   0/1
    str   name         以 \\0 結尾
    float startX, startY
    int   allyLowPrioFlags
    int   allyHighPrioFlags
"""
import struct


def _rdstr(d, p):
    z = d.index(b'\x00', p)
    return d[p:z].decode('utf-8', 'replace'), z + 1


class Player(object):
    __slots__ = ('pid', 'ctrl', 'race', 'fixed', 'name', 'sx', 'sy', 'lo', 'hi')

    def __init__(s, pid, ctrl, race, fixed, name, sx, sy, lo, hi):
        (s.pid, s.ctrl, s.race, s.fixed, s.name,
         s.sx, s.sy, s.lo, s.hi) = pid, ctrl, race, fixed, name, sx, sy, lo, hi

    def pack(s):
        return (struct.pack('<4i', s.pid, s.ctrl, s.race, s.fixed)
                + s.name.encode('utf-8') + b'\x00'
                + struct.pack('<2f2I', s.sx, s.sy, s.lo, s.hi))

    def copy(s, pid, name):
        return Player(pid, s.ctrl, s.race, s.fixed, name, s.sx, s.sy, s.lo, s.hi)

    def __repr__(s):
        return 'P%d(ctrl=%d race=%d %r @%.0f,%.0f)' % (s.pid + 1, s.ctrl, s.race, s.name, s.sx, s.sy)


class W3IPlayers(object):
    def __init__(s, data):
        s.d = data
        p = 0
        s.ver, = struct.unpack_from('<i', data, p); p += 4
        p += 8
        if s.ver >= 27:
            p += 16
        for _ in range(4):                       # name / author / desc / recommended
            p = data.index(b'\x00', p) + 1
        p += 32 + 16 + 8 + 4 + 1                 # camera, complements, playable, flags, tileset
        p += 4                                   # loading screen index
        for _ in range(4):                       # LS path / text / title / subtitle
            p = data.index(b'\x00', p) + 1
        p += 4                                   # data set
        for _ in range(4):                       # prologue path / text / title / subtitle
            p = data.index(b'\x00', p) + 1
        p += 4 + 4 + 4 + 4 + 4 + 4               # fog style, z start, z end, density, colour, weather
        p = data.index(b'\x00', p) + 1           # sound environment
        p += 1 + 4                               # light env, water colour
        s.count_off = p
        n, = struct.unpack_from('<i', data, p); p += 4
        s.players = []
        for _ in range(n):
            pid, ctrl, race, fixed = struct.unpack_from('<4i', data, p); p += 16
            name, p = _rdstr(data, p)
            sx, sy, lo, hi = struct.unpack_from('<2f2I', data, p); p += 16
            s.players.append(Player(pid, ctrl, race, fixed, name, sx, sy, lo, hi))
        s.tail_off = p                           # 玩家陣列之後（隊伍數量開始）

    def rebuild(s, players):
        return (s.d[:s.count_off]
                + struct.pack('<i', len(players))
                + b''.join(p.pack() for p in players)
                + s.d[s.tail_off:])

    def add_slots(s, pids, name_fmt='Игрок %d', template_pid=None):
        """在既有玩家槽之後、中立槽之前插入新的玩家槽。"""
        have = {p.pid for p in s.players}
        tpl = None
        for p in s.players:
            if template_pid is not None and p.pid == template_pid:
                tpl = p; break
            if template_pid is None and p.ctrl in (0, 1) and p.pid < 8:
                tpl = p
        if tpl is None:
            raise ValueError('找不到可當樣板的玩家槽')
        out, added = [], []
        for pid in sorted(pids):
            if pid in have:
                continue
            added.append(tpl.copy(pid, name_fmt % (pid + 1)))
        merged = sorted(s.players + added, key=lambda p: p.pid)
        return s.rebuild(merged), added
