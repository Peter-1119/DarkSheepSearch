# -*- coding: utf-8 -*-
"""小地圖（war3mapMap.blp）與預覽圖示（war3map.mmp）的重新排版。

WC3 的小地圖是一張 256×256 的圖，把「可玩區」等比縮放塞進去、置中，
不夠的方向補黑邊。地圖拓寬後可玩區的長寬比變了，舊圖就會錯位，
所以要照新的可玩區重新排一次。

    rect = (minX, minY, maxX, maxY)   可玩區的世界座標
"""
import struct
from PIL import Image


def layout(rect, size=256):
    """回傳 (每像素幾個世界單位, 左邊界像素, 上邊界像素)。"""
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    s = max(w, h) / float(size)
    return s, (size - w / s) / 2.0, (size - h / s) / 2.0


def world_to_px(rect, x, y, size=256):
    s, ox, oy = layout(rect, size)
    return ox + (x - rect[0]) / s, oy + (rect[3] - y) / s


def px_to_world(rect, px, py, size=256):
    s, ox, oy = layout(rect, size)
    return rect[0] + (px - ox) * s, rect[3] - (py - oy) * s


def remap(old_img, old_rect, new_rect, fill, size=256):
    """把舊小地圖搬到新可玩區的排版上。
    fill(x, y) -> (r,g,b) 或 None：舊圖沒涵蓋的世界座標要塗什麼（None = 黑）。"""
    src = old_img.convert('RGB')
    sp = src.load()
    out = Image.new('RGB', (size, size), (0, 0, 0))
    op = out.load()
    for py in range(size):
        for px in range(size):
            wx, wy = px_to_world(new_rect, px + 0.5, py + 0.5, size)
            if not (new_rect[0] <= wx <= new_rect[2] and new_rect[1] <= wy <= new_rect[3]):
                continue
            if old_rect[0] <= wx <= old_rect[2] and old_rect[1] <= wy <= old_rect[3]:
                ox, oy = world_to_px(old_rect, wx, wy, size)
                ix = min(size - 1, max(0, int(ox)))
                iy = min(size - 1, max(0, int(oy)))
                op[px, py] = sp[ix, iy]
            else:
                c = fill(wx, wy)
                if c:
                    op[px, py] = c
    return out


def blp1_palette(img):
    """寫成 BLP1 調色盤格式（compression=1，無 alpha，單一 mipmap —— 跟原圖一樣沒有 mipmap）。"""
    w, h = img.size
    q = img.convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[:768]
    pal += [0] * (768 - len(pal))
    idx = q.tobytes()
    # 版面：magic, compression, alphaBits, w, h, extra, hasMipmaps, offsets[16], sizes[16], palette[256]
    off0 = 4 + 4 * 6 + 64 + 64 + 1024
    parts = [b'BLP1', struct.pack('<6I', 1, 0, w, h, 5, 0)]
    offs = [off0] + [0] * 15
    sizes = [len(idx)] + [0] * 15
    parts.append(struct.pack('<16I', *offs))
    parts.append(struct.pack('<16I', *sizes))
    parts.append(b''.join(struct.pack('<4B', pal[i * 3 + 2], pal[i * 3 + 1], pal[i * 3], 0)
                          for i in range(256)))
    parts.append(idx)
    return b''.join(parts)


def remap_mmp(data, old_rect, new_rect, size=256):
    """war3map.mmp：8 bytes header（0, 筆數），每筆 16 bytes（type, x, y, BGRA）。"""
    d = bytearray(data)
    n, = struct.unpack_from('<i', d, 4)
    for k in range(n):
        o = 8 + k * 16
        t, x, y = struct.unpack_from('<3i', d, o)
        wx, wy = px_to_world(old_rect, x, y, size)
        nx, ny = world_to_px(new_rect, wx, wy, size)
        struct.pack_into('<2i', d, o + 4, int(round(nx)), int(round(ny)))
    return bytes(d)
