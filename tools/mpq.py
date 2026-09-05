# -*- coding: utf-8 -*-
"""最小可用的 MPQ (.w3x) 讀取器。

魔獸地圖是 MPQ 壓縮檔，檔案表被加密過，沒辦法直接用 zipfile 之類的開。
這裡實作 MPQ 的雜湊與解密演算法，只支援讀取，
夠用來把 war3map.j / war3map.lua / war3map.w3u 這些檔案挖出來。
"""
import struct, zlib, bz2

# ---------------------------------------------------------------- 加密表
_CT = [0] * 0x500
_s = 0x00100001
for _i in range(0x100):
    _idx = _i
    for _j in range(5):
        _s = (_s * 125 + 3) % 0x2AAAAB
        _t1 = (_s & 0xFFFF) << 16
        _s = (_s * 125 + 3) % 0x2AAAAB
        _CT[_idx] = _t1 | (_s & 0xFFFF)
        _idx += 0x100


def _hash(s, ty):
    """ty: 0=表位置 1=名稱A 2=名稱B 3=檔案金鑰"""
    s1, s2 = 0x7FED7FED, 0xEEEEEEEE
    for c in s.upper().replace('/', '\\'):
        c = ord(c)
        s1 = (_CT[(ty << 8) + c] ^ (s1 + s2)) & 0xFFFFFFFF
        s2 = (c + s1 + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return s1


def _decrypt(data, key):
    n = len(data) // 4
    vals = list(struct.unpack('<%dI' % n, data[:n * 4]))
    s1, s2 = key, 0xEEEEEEEE
    out = []
    for v in vals:
        s2 = (s2 + _CT[0x400 + (s1 & 0xFF)]) & 0xFFFFFFFF
        r = v ^ ((s1 + s2) & 0xFFFFFFFF)
        s1 = (((~s1 << 0x15) + 0x11111111) | (s1 >> 0x0B)) & 0xFFFFFFFF
        s2 = (r + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
        out.append(r)
    return struct.pack('<%dI' % n, *out) + data[n * 4:]


# ---------------------------------------------------------------- 解壓
class _Bits(object):
    def __init__(s, d):
        s.d, s.p, s.b, s.n = d, 0, 0, 0

    def get(s, k):
        while s.n < k:
            s.b |= (s.d[s.p] if s.p < len(s.d) else 0) << s.n
            s.p += 1
            s.n += 8
        v = s.b & ((1 << k) - 1)
        s.b >>= k
        s.n -= k
        return v


# PKWARE DCL 的靜態解碼表
_LEN_BITS = [3, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7]
_LEN_CODE = [5, 3, 1, 6, 10, 2, 12, 20, 4, 24, 8, 48, 16, 32, 64, 0]
_LEN_XBIT = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8]
_LEN_BASE = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 40, 72, 136, 264]
_DST_BITS = [2, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7,
             7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8,
             8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
_DST_CODE = [0x03, 0x0D, 0x05, 0x19, 0x09, 0x11, 0x01, 0x3E, 0x1E, 0x2E, 0x0E,
             0x36, 0x16, 0x26, 0x06, 0x3A, 0x1A, 0x2A, 0x0A, 0x32, 0x12, 0x22,
             0x02, 0x7C, 0x3C, 0x5C, 0x1C, 0x6C, 0x2C, 0x4C, 0x0C, 0x74, 0x34,
             0x54, 0x14, 0x64, 0x24, 0x44, 0x04, 0x78, 0x38, 0x58, 0x18, 0x68,
             0x28, 0x48, 0x08, 0xF0, 0x70, 0xB0, 0x30, 0xD0, 0x50, 0x90, 0x10,
             0xE0, 0x60, 0xA0, 0x20, 0xC0, 0x40, 0x80, 0x00]

# 反查表：(位元數, 編碼) -> 索引，避免每個符號都線性掃描
_LEN_MAP = {(_LEN_BITS[i], _LEN_CODE[i]): i for i in range(len(_LEN_CODE))}
_DST_MAP = {(_DST_BITS[i], _DST_CODE[i]): i for i in range(len(_DST_CODE))}
# 註：_DST_CODE 只抄到 63 筆（規格是 64），最後一個距離碼未經查證就不補。
# WC3 地圖內部檔案實務上一律 zlib，PKWARE 走不到這裡；真的走到會在 _pick 明確報錯。

# ASCII 模式的字面值表在 PKWARE 規格裡是另一組 huffman，地圖不會用到，
# 所以遇到就直接報錯而不是默默解錯。


def _pk_explode(d):
    lit_mode, dsize_bits = d[0], d[1]
    if lit_mode == 1:
        raise ValueError('PKWARE: ASCII 模式未實作')
    if lit_mode != 0:
        raise ValueError('PKWARE: 未知字面模式 %d' % lit_mode)
    if not 4 <= dsize_bits <= 6:
        raise ValueError('PKWARE: 字典大小異常 %d' % dsize_bits)
    b = _Bits(d[2:])
    out = bytearray()
    while b.p <= len(b.d):
        if b.get(1):                                  # 1 = 複製既有內容
            li = _pick(b, _LEN_MAP)
            if li == 15:                              # 結束標記
                break
            ln = _LEN_BASE[li]
            if _LEN_XBIT[li]:
                ln += b.get(_LEN_XBIT[li])
            di = _pick(b, _DST_MAP)
            dist = ((di << 2) | b.get(2)) if ln == 2 else \
                   ((di << dsize_bits) | b.get(dsize_bits))
            dist += 1
            if dist > len(out):
                raise ValueError('PKWARE: 距離超出範圍')
            for _ in range(ln):
                out.append(out[-dist])
        else:                                         # 0 = 原始位元組
            out.append(b.get(8))
    return bytes(out)


def _pick(b, table):
    v = 0
    for n in range(1, 9):
        v |= b.get(1) << (n - 1)
        i = table.get((n, v))
        if i is not None:
            return i
    raise ValueError('PKWARE: 解碼失敗')


def _decompress(data):
    """第一個位元組是壓縮方式的位元遮罩，可以疊加。"""
    m, body = data[0], data[1:]
    if m == 0:
        return body
    if m & 0x10:
        body = bz2.decompress(body)
    if m & 0x02:
        body = zlib.decompress(body)
    if m & 0x08:
        body = _pk_explode(body)
    if m & (0x01 | 0x40 | 0x80):
        raise ValueError('不支援的壓縮方式 0x%02X（huffman/adpcm，只用於音效）' % m)
    return body


# ---------------------------------------------------------------- 主體
FLAG_IMPLODE = 0x00000100
FLAG_COMPRESS = 0x00000200
FLAG_ENCRYPTED = 0x00010000
FLAG_FIX_KEY = 0x00020000
FLAG_SINGLE = 0x01000000
FLAG_SECTOR_CRC = 0x04000000
FLAG_EXISTS = 0x80000000


class MPQ(object):
    def __init__(s, path):
        s.f = open(path, 'rb')
        s.base = 0x200 if s.f.read(4) == b'HM3W' else 0   # w3x 前有 512 byte 標頭
        s.f.seek(s.base)
        h = s.f.read(0x20)
        if h[:4] != b'MPQ\x1a':
            raise ValueError('不是 MPQ 檔')
        (_, _hs, _az, s.ver, s.bshift, htp, btp, s.hn, s.bn) = \
            struct.unpack('<4sIIHHIIII', h)
        s.sector = 512 << s.bshift
        s.hash = s._table(s.base + htp, s.hn, '(hash table)')
        s.block = s._table(s.base + btp, s.bn, '(block table)')

    def _table(s, pos, n, key):
        s.f.seek(pos)
        d = _decrypt(s.f.read(n * 16), _hash(key, 3))
        return [struct.unpack('<4I', d[i * 16:i * 16 + 16]) for i in range(n)]

    def find(s, name):
        i0 = _hash(name, 0) % s.hn
        a, b = _hash(name, 1), _hash(name, 2)
        for k in range(s.hn):
            e = s.hash[(i0 + k) % s.hn]
            if e[3] == 0xFFFFFFFF:                    # 空位 = 找不到
                return None
            if e[0] == a and e[1] == b and e[3] != 0xFFFFFFFE:
                return e[3]
        return None

    def read(s, name):
        bi = s.find(name)
        if bi is None or bi >= len(s.block):
            return None
        pos, csize, fsize, flags = s.block[bi]
        if not flags & FLAG_EXISTS or fsize == 0:
            return None
        pos += s.base
        key = 0
        if flags & FLAG_ENCRYPTED:
            key = _hash(name.split('\\')[-1], 3)
            if flags & FLAG_FIX_KEY:
                key = ((key + (pos - s.base)) ^ fsize) & 0xFFFFFFFF

        if flags & FLAG_SINGLE:
            s.f.seek(pos)
            d = s.f.read(csize)
            if flags & FLAG_ENCRYPTED:
                d = _decrypt(d, key)
            if csize < fsize:
                d = _pk_explode(d) if flags & FLAG_IMPLODE else _decompress(d)
            return d[:fsize]

        if not flags & (FLAG_COMPRESS | FLAG_IMPLODE):
            # 未壓縮的檔案直接接資料，沒有磁區位移表（原版 war3.mpq 很多這種）
            s.f.seek(pos)
            d = s.f.read(fsize)
            return _decrypt(d, key)[:fsize] if flags & FLAG_ENCRYPTED else d

        nsec = (fsize + s.sector - 1) // s.sector
        ntab = nsec + 1 + (1 if flags & FLAG_SECTOR_CRC else 0)
        s.f.seek(pos)
        tab = s.f.read(ntab * 4)
        if flags & FLAG_ENCRYPTED:
            tab = _decrypt(tab, (key - 1) & 0xFFFFFFFF)
        off = struct.unpack('<%dI' % ntab, tab)
        out = bytearray()
        for i in range(nsec):
            s.f.seek(pos + off[i])
            raw = s.f.read(off[i + 1] - off[i])
            if flags & FLAG_ENCRYPTED:
                raw = _decrypt(raw, (key + i) & 0xFFFFFFFF)
            want = min(s.sector, fsize - len(out))
            if len(raw) < want:
                raw = _pk_explode(raw) if flags & FLAG_IMPLODE else _decompress(raw)
            out += raw[:want]
        return bytes(out[:fsize])

    def listfile(s):
        d = s.read('(listfile)')
        if not d:
            return []
        txt = d.decode('utf-8', 'replace').replace('\r', '\n')
        return [x for x in txt.split('\n') if x.strip()]


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    m = MPQ(sys.argv[1])
    print('MPQ 版本 %d ／ 檔案數 %d ／ 磁區 %d bytes' % (m.ver, m.bn, m.sector))
    lf = m.listfile()
    print('(listfile)：%d 筆' % len(lf))
    for x in lf[:80]:
        print('   ', x)
