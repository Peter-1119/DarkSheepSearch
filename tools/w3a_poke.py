# -*- coding: utf-8 -*-
"""在 .w3a/.w3q/.w3h 的原始位元組上精準改某個欄位的值。

跟 w3obj.py 的差別：那支是「讀出來給人看」，會丟掉欄位順序、結束標記這些
還原時需要的東西。這支不解析成字典，而是**走過一遍建立索引**
（物件ID, 欄位代號, 等級）-> 值在檔案裡的位移與型別，然後就地覆寫。

整數與浮點都是固定 4 bytes，改值不會動到檔案結構，所以最安全。
字串長度會變，目前只支援「同型別、定長」的改動 —— 字串請直接用
bytes.replace（見 patch_archer.py 的掠奪箭矢）。
"""
import struct


def index(data, has_level=True):
    """回傳 {(物件ID, 欄位代號, 等級): (值的位移, 型別)}。型別 0=整數 1/2=浮點 3=字串。"""
    idx, p = {}, 0
    ver = struct.unpack_from('<i', data, p)[0]
    p += 4
    for _table in (0, 1):
        n = struct.unpack_from('<i', data, p)[0]
        p += 4
        for _ in range(n):
            oid = data[p:p + 4].decode('latin-1')
            nid = data[p + 4:p + 8].decode('latin-1')
            p += 8
            if ver >= 3:
                cnt = struct.unpack_from('<i', data, p)[0]
                p += 4
                for _ in range(cnt):
                    m = struct.unpack_from('<i', data, p)[0]
                    p += 4 + 4 * m
            nmod = struct.unpack_from('<i', data, p)[0]
            p += 4
            key = nid.strip('\x00 ') or oid
            for _ in range(nmod):
                mid = data[p:p + 4].decode('latin-1')
                vt = struct.unpack_from('<i', data, p + 4)[0]
                p += 8
                lvl = 0
                if has_level:
                    lvl = struct.unpack_from('<i', data, p)[0]
                    p += 8
                idx[(key, mid, lvl)] = (p, vt)
                if vt == 0 or vt in (1, 2):
                    p += 4
                else:
                    p = data.index(b'\x00', p) + 1
                p += 4                          # 結束標記
    return idx


def poke(data, edits, has_level=True):
    """edits = {(物件ID, 欄位代號, 等級): 新值}。回傳 (新的 bytes, 改動說明清單)。

    只允許整數改整數、浮點改浮點 —— 型別不符會直接中止，免得寫出壞檔案。
    """
    idx = index(data, has_level)
    buf = bytearray(data)
    notes = []
    for key, val in edits.items():
        if key not in idx:
            raise SystemExit('w3a_poke: 找不到 %s' % (key,))
        off, vt = idx[key]
        if vt == 0:
            old, = struct.unpack_from('<i', buf, off)
            struct.pack_into('<i', buf, off, int(val))
        elif vt in (1, 2):
            old, = struct.unpack_from('<f', buf, off)
            struct.pack_into('<f', buf, off, float(val))
        else:
            raise SystemExit('w3a_poke: %s 是字串欄位，這支不改字串' % (key,))
        notes.append('%s.%s[等級%d]  %s -> %s' % (key[0], key[1], key[2], old, val))
    return bytes(buf), notes


def poke_str(data, edits, has_level=True):
    """改字串欄位。edits = {(物件ID, 欄位代號, 等級): 新字串}。

    字串長度會變，所以不能就地覆寫 —— 從檔尾往前依序切接，
    這樣前面那些還沒處理的位移才不會跑掉。
    """
    idx = index(data, has_level)
    plan = []
    for key, val in edits.items():
        if key not in idx:
            raise SystemExit('w3a_poke: 找不到 %s' % (key,))
        off, vt = idx[key]
        if vt in (0, 1, 2):
            raise SystemExit('w3a_poke: %s 是數值欄位，用 poke() 改' % (key,))
        end = data.index(b'\x00', off)
        plan.append((off, end, key, data[off:end].decode('utf-8', 'replace'), val))
    out, notes = data, []
    for off, end, key, old, val in sorted(plan, reverse=True):
        out = out[:off] + val.encode('utf-8') + out[end:]
        notes.append('%s.%s[等級%d]  %r -> %r' % (key[0], key[1], key[2], old, val))
    return out, list(reversed(notes))


def _spans(data, has_level=True):
    """回傳 ({物件ID: (起, 迄)}, 自訂物件表的數量欄位移, 資料結束位移)。"""
    p = 0
    ver = struct.unpack_from('<i', data, p)[0]
    p += 4
    spans, cnt_off = {}, None
    for table in (0, 1):
        if table == 1:
            cnt_off = p
        n = struct.unpack_from('<i', data, p)[0]
        p += 4
        for _ in range(n):
            start = p
            oid = data[p:p + 4].decode('latin-1')
            nid = data[p + 4:p + 8].decode('latin-1')
            p += 8
            if ver >= 3:
                c = struct.unpack_from('<i', data, p)[0]
                p += 4
                for _ in range(c):
                    mm = struct.unpack_from('<i', data, p)[0]
                    p += 4 + 4 * mm
            nmod = struct.unpack_from('<i', data, p)[0]
            p += 4
            for _ in range(nmod):
                vt = struct.unpack_from('<i', data, p + 4)[0]
                p += 8
                if has_level:
                    p += 8
                if vt in (0, 1, 2):
                    p += 4
                else:
                    p = data.index(b'\x00', p) + 1
                p += 4
            spans[nid.strip('\x00 ') or oid] = (start, p)
    return spans, cnt_off, p


def clone(data, src_id, new_ids, has_level=True):
    """把 src_id 這個物件整份複製成 new_ids 裡的每個新 ID，接在自訂物件表後面。

    用途：地圖需要一個「加攻擊距離」的科技，但物件檔裡沒有多的可以用。
    與其自己從零組一個物件（欄位很容易漏），不如整份抄一個現成的再改 ID ——
    抄來的東西每一欄都是合法值，只要改想改的那幾欄就好。
    """
    spans, cnt_off, end = _spans(data, has_level)
    if src_id not in spans:
        raise SystemExit('w3a_poke: 找不到要複製的 %s' % src_id)
    for nid in new_ids:
        if nid in spans:
            raise SystemExit('w3a_poke: %s 已經存在，不能重複' % nid)
    a, b = spans[src_id]
    rec = data[a:b]
    blob = b''.join(rec[:4] + nid.encode('latin-1') + rec[8:] for nid in new_ids)
    n = struct.unpack_from('<i', data, cnt_off)[0]
    out = (data[:cnt_off] + struct.pack('<i', n + len(new_ids))
           + data[cnt_off + 4:end] + blob + data[end:])
    # 走一次確認新結構讀得通、而且新 ID 都在
    chk, _, _ = _spans(out, has_level)
    for nid in new_ids:
        if nid not in chk:
            raise SystemExit('w3a_poke: 複製後找不到 %s，結構壞了' % nid)
    return out, ['%s 複製成 %s（%d bytes）' % (src_id, n2, len(rec)) for n2 in new_ids]
