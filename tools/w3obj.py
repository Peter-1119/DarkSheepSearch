# -*- coding: utf-8 -*-
"""魔獸物件資料（.w3u/.w3t/.w3a/.w3h…）解析器。

格式很單純：一個版本號，接兩張表（原始物件的改動 / 自訂物件），
每張表是 [原始ID, 新ID, 改動數量, 改動…]。
改動的欄位代號（modId）是 4 個字元，例如 'unam' = 名稱、'utub' = 詳細說明。

w3a/w3q/w3d 的每筆改動多了「等級 + 欄位指標」兩個欄位，w3u/w3t 沒有，
所以要用 has_level 區分。
"""
import struct, io


def _cstr(b, p):
    e = b.index(b'\x00', p)
    return b[p:e], e + 1


def _txt(raw):
    """地圖字串多半是 UTF-8，舊資料偶爾是 cp1251，兩個都試。"""
    for enc in ('utf-8', 'cp1251'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode('utf-8', 'replace')


def parse(data, has_level=False):
    """回傳 {物件ID: {欄位代號: 值}}；自訂物件另存 _base = 衍生自哪個原始物件。"""
    out = {}
    p = 0
    ver = struct.unpack_from('<i', data, p)[0]
    p += 4
    for table in (0, 1):                       # 0 = 改原始物件，1 = 自訂物件
        n = struct.unpack_from('<i', data, p)[0]
        p += 4
        for _ in range(n):
            oid = data[p:p + 4].decode('latin-1')
            nid = data[p + 4:p + 8].decode('latin-1')
            p += 8
            if ver >= 3:                       # Reforged 多了一組可選集合
                cnt = struct.unpack_from('<i', data, p)[0]
                p += 4
                for _ in range(cnt):
                    m = struct.unpack_from('<i', data, p)[0]
                    p += 4 + 4 * m
            nmod = struct.unpack_from('<i', data, p)[0]
            p += 4
            key = nid.strip('\x00 ') or oid
            rec = out.setdefault(key, {})
            if nid.strip('\x00 '):
                rec['_base'] = oid
            for _ in range(nmod):
                mid = data[p:p + 4].decode('latin-1')
                vt = struct.unpack_from('<i', data, p + 4)[0]
                p += 8
                if has_level:
                    p += 8                     # 等級 + 欄位指標，這裡用不到
                if vt == 0:
                    v = struct.unpack_from('<i', data, p)[0]; p += 4
                elif vt in (1, 2):
                    v = struct.unpack_from('<f', data, p)[0]; p += 4
                else:
                    raw, p = _cstr(data, p)
                    v = _txt(raw)
                p += 4                         # 結束標記
                # 同一個代號可能出現多次（例如多個技能欄位），存成清單
                if mid in rec:
                    if isinstance(rec[mid], list):
                        rec[mid].append(v)
                    else:
                        rec[mid] = [rec[mid], v]
                else:
                    rec[mid] = v
    return out


if __name__ == '__main__':
    import sys, os, collections
    sys.stdout.reconfigure(encoding='utf-8')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from mpq import MPQ
    m = MPQ(sys.argv[1])
    for name, lvl in (('war3map.w3t', False), ('war3map.w3u', False),
                      ('war3map.w3a', True), ('war3map.w3h', False)):
        d = m.read(name)
        if not d:
            print('%-14s 不存在' % name); continue
        try:
            o = parse(d, lvl)
        except Exception as e:
            print('%-14s 解析失敗：%s' % (name, e)); continue
        fields = collections.Counter()
        for r in o.values():
            fields.update(r.keys())
        print('%-14s %5d 個物件，最常見欄位：%s' %
              (name, len(o), ' '.join('%s(%d)' % (k, v)
                                      for k, v in fields.most_common(14))))
