# -*- coding: utf-8 -*-
"""物件資料（w3u/w3t/w3a/w3q）的字串改寫器：只換字串值，其他位元組一概不動。

鍵的規則跟 w3obj.parse 一致：
    有等級的欄位 → 等級（1 起算）
    沒等級、在同一物件只出現一次 → 0
    沒等級、出現多次 → 出現順序（1 起算）
fn(物件鍵, 欄位, 索引, 原字串) 回傳新字串；回傳 None 表示不改。
"""
import struct
import collections


def _walk(data, has_level):
    """產生每一筆改動的 (物件鍵, 欄位, 等級, 值型別, 值起點, 值終點)。"""
    p = 0
    ver = struct.unpack_from('<i', data, p)[0]; p += 4
    for table in (0, 1):
        n = struct.unpack_from('<i', data, p)[0]; p += 4
        for _ in range(n):
            oid = data[p:p + 4].decode('latin-1'); nid = data[p + 4:p + 8].decode('latin-1'); p += 8
            if ver >= 3:
                cnt = struct.unpack_from('<i', data, p)[0]; p += 4
                for _ in range(cnt):
                    m = struct.unpack_from('<i', data, p)[0]; p += 4 + 4 * m
            nmod = struct.unpack_from('<i', data, p)[0]; p += 4
            key = nid.strip('\x00 ') or oid
            for _ in range(nmod):
                mid = data[p:p + 4].decode('latin-1')
                vt = struct.unpack_from('<i', data, p + 4)[0]; p += 8
                lvl = 0
                if has_level:
                    lvl = struct.unpack_from('<i', data, p)[0]; p += 8
                s = p
                if vt in (0, 1, 2):
                    p += 4
                else:
                    p = data.index(b'\x00', p) + 1
                yield key, mid, lvl, vt, s, p
                p += 4
    return


def rewrite(data, has_level, fn):
    recs = list(_walk(data, has_level))
    cnt = collections.Counter((k, m) for k, m, l, vt, s, e in recs if l == 0)
    seen = collections.Counter()
    out, last, changed = [], 0, 0
    for key, mid, lvl, vt, s, e in recs:
        if lvl == 0:
            seen[(key, mid)] += 1
            idx = 0 if cnt[(key, mid)] == 1 else seen[(key, mid)]
        else:
            idx = lvl
        if vt != 3:
            continue
        raw = data[s:e - 1]
        try:
            txt = raw.decode('utf-8')
        except UnicodeDecodeError:
            continue
        new = fn(key, mid, idx, txt)
        if new is None or new == txt:
            continue
        out.append(data[last:s]); out.append(new.encode('utf-8') + b'\x00'); last = e
        changed += 1
    out.append(data[last:])
    return b''.join(out), changed
