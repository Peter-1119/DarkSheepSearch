# -*- coding: utf-8 -*-
"""把 MPQ 裡的檔案換成新內容（可一次換多個）。

從 patch_skins.py 抽出來的，差別是那支只換 war3map.j 一個檔，
改弓箭手小生存要同時動 war3map.j 與 war3map.w3a，所以獨立成模組。

原理：MPQ 的區塊表記著每個檔案在檔內的位移與大小。新內容塞得回原位就原地覆寫，
塞不下就附加到檔尾、再把區塊表那一格指過去。舊位置的資料留著不管（變成空洞），
反正沒有人會去讀它。改完區塊表要重新加密寫回。
"""
import os, shutil, struct, zlib

from mpq import MPQ, _hash, _CT


def _encrypt(data, key):
    n = len(data) // 4
    vals = list(struct.unpack('<%dI' % n, data[:n * 4]))
    s1, s2, out = key, 0xEEEEEEEE, []
    for v in vals:
        s2 = (s2 + _CT[0x400 + (s1 & 0xFF)]) & 0xFFFFFFFF
        out.append(v ^ ((s1 + s2) & 0xFFFFFFFF))
        s1 = (((~s1 << 0x15) + 0x11111111) | (s1 >> 0x0B)) & 0xFFFFFFFF
        s2 = (v + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return struct.pack('<%dI' % n, *out) + data[n * 4:]


def _pack(raw, sector):
    """照 MPQ 的磁區格式壓回去：每個磁區各自 zlib，壓不小就存原文。"""
    n = (len(raw) + sector - 1) // sector
    parts = []
    for i in range(n):
        c = raw[i * sector:(i + 1) * sector]
        z = zlib.compress(c, 9)
        parts.append(b'\x02' + z if len(z) + 1 < len(c) else c)
    off, cur = [], 4 * (n + 1)
    for p in parts:
        off.append(cur)
        cur += len(p)
    return struct.pack('<%dI' % (n + 1), *(off + [cur])) + b''.join(parts)


def write_files(src, dst, edits):
    """edits = {MPQ 內的檔名: 新的位元組內容}。回傳 {檔名: '原地覆寫'/'附加到檔尾'}。

    只動被指名的檔案，其他一個位元組都不碰 —— 呼叫端應該自己再驗一次。
    """
    m = MPQ(src)
    sector, base, blocks = m.sector, m.base, list(m.block)
    idx = {}
    for name in edits:
        i = m.find(name)
        if i is None:
            raise SystemExit('MPQ 裡沒有這個檔：%s' % name)
        pos, csize, fsize, flags = m.block[i]
        if flags & (0x00010000 | 0x01000000):
            raise SystemExit('%s 有加密／單一單元旗標，這支工具不處理' % name)
        idx[name] = i
    m.f.seek(base)
    (_sig, _hs, _az, _ver, _bs, _htp, btp, _hn, _bn) = struct.unpack(
        '<4sIIHHIIII', m.f.read(0x20))
    m.f.close()

    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy2(src, dst)
    where = {}
    with open(dst, 'r+b') as f:
        for name, raw in edits.items():
            i = idx[name]
            pos, csize, fsize, flags = blocks[i]
            blob = _pack(raw, sector)
            if len(blob) <= csize:
                newpos, w = pos, '原地覆寫'
            else:
                f.seek(0, 2)
                newpos, w = f.tell() - base, '附加到檔尾'
            f.seek(base + newpos)
            f.write(blob)
            blocks[i] = (newpos, len(blob), len(raw), flags)
            where[name] = w
        f.seek(base + btp)
        f.write(_encrypt(b''.join(struct.pack('<4I', *b) for b in blocks),
                         _hash('(block table)', 3)))
    return where


def verify(src, dst, edits, untouched=None):
    """確認改過的讀得回來、沒改的逐位元組沒變。回傳 (是否全過, 訊息清單)。"""
    a, b = MPQ(src), MPQ(dst)
    msg, ok = [], True
    for name, raw in edits.items():
        got = b.read(name)
        good = got == raw
        ok &= good
        msg.append('  %-16s 寫回正確：%s（%d bytes）' % (name, good, len(got)))
    names = untouched
    if names is None:
        lst = a.read('(listfile)').decode('utf-8', 'ignore')
        names = [x.strip() for x in lst.replace('\r\n', '\n').split('\n')
                 if x.strip() and x.strip() not in edits]
    bad = []
    for n in names:
        try:
            if a.read(n) != b.read(n):
                bad.append(n)
        except Exception:
            pass
    ok &= not bad
    msg.append('  其他 %d 個檔案未更動：%s%s'
               % (len(names), not bad, ('（變了：%s）' % bad[:5]) if bad else ''))
    return ok, msg
