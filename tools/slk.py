# -*- coding: utf-8 -*-
"""SLK（試算表）讀寫。魔獸的「SLK 最佳化」會把物件資料搬進這種檔。

弓箭手小生存 2.0.8 就是這樣：war3map.w3u / war3map.w3t 整個不在封包裡，
單位與道具的數值都搬到 Units\\UnitBalance.slk 等檔，而且從 (listfile) 裡
被拿掉名字 —— 用檔名直接算雜湊還是找得到，內容完整。

格式：每行 C;Y<列>;X<欄>;K<值>，列／欄省略時沿用上一次，所以要記狀態。
第 1 列是欄位名稱，第 1 欄是物件 ID。
"""


def _cells(data):
    """逐筆吐出 (列, 欄, 值)。列／欄省略時沿用上一次。"""
    if isinstance(data, bytes):
        data = data.decode('utf-8', 'replace')
    y = x = 1
    for line in data.replace('\r\n', '\n').split('\n'):
        if not line.startswith('C;'):
            continue
        val = None
        for f in line.split(';')[1:]:
            if not f:
                continue
            t, rest = f[0], f[1:]
            if t == 'Y':
                y = int(rest)
            elif t == 'X':
                x = int(rest)
            elif t == 'K':
                if rest.startswith('"'):
                    val = rest.strip('"')
                else:
                    try:
                        val = float(rest) if '.' in rest else int(rest)
                    except ValueError:
                        val = rest
        if val is not None:
            yield y, x, val


def loads(data):
    """回傳 ({物件ID: {欄位名: 值}}, [欄位名…])；另存 _row ＝ 這筆在第幾列。"""
    rows = {}
    for y, x, v in _cells(data):
        rows.setdefault(y, {})[x] = v

    cols = {i: str(v) for i, v in rows.get(1, {}).items()}
    names = [cols[i] for i in sorted(cols)]
    out = {}
    for yy, r in rows.items():
        if yy == 1:
            continue
        rec = {cols.get(i, 'X%d' % i): v for i, v in r.items()}
        rec['_row'] = yy
        key = r.get(1)
        if key is not None:
            out[str(key)] = rec
    return out, names


def col_index(data, name):
    """欄位名 -> 真正的欄號。找不到丟例外，不要讓呼叫端拿 None 去寫檔。

    標題列的欄號會跳號（UnitBalance.slk 就沒有第 6 欄），所以不能拿
    「第幾個欄位」當欄號 —— 那樣寫進去的是隔壁那一欄。
    """
    for y, x, v in _cells(data):
        if y == 1 and str(v) == name:
            return x
    raise SystemExit('slk: 找不到欄位 %s' % name)


def set_cells(data, cells):
    """cells = [(列, 欄, 值)]，值是字串就加引號。回傳新的位元組。

    做法是把 C 記錄補在檔尾的 E 之前 —— SLK 的列／欄是寫在記錄裡的，
    不靠順序，所以補在後面等於覆蓋前面同一格。比就地改省事也安全。
    """
    raw = data.decode('utf-8', 'replace') if isinstance(data, bytes) else data
    nl = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.replace('\r\n', '\n').split('\n')
    end = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == 'E':
            end = i
            break
    if end is None:
        raise SystemExit('slk: 找不到結束標記 E')
    add = []
    for y, x, v in cells:
        s = '"%s"' % v if isinstance(v, str) else repr(v)
        add.append('C;Y%d;X%d;K%s' % (y, x, s))
    lines[end:end] = add
    return nl.join(lines).encode('utf-8')
