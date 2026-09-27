# -*- coding: utf-8 -*-
"""八人 v5 = v4 + 存讀檔指令 + 3 個倒數迴圈指令 + 皮膚系統（Skins_6 / Skins_7）。"""
import sys, os, re, io, struct, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Notebook Program Scripts\Python_Scripts\DarkSheep\tools')
import mpq, mpq_patch

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/UD_test_24_09_26_opt.w3x'
MAPS = r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download'
j = open(os.path.join(BASE, 'ud_new_8p.j'), 'rb').read().decode('utf-8', 'surrogateescape')


def func_span(src, name):
    m = re.search(r'^function %s takes[^\n]*\n' % re.escape(name), src, re.M)
    assert m, name
    return m.start(), src.index('\nendfunction', m.start()) + len('\nendfunction')


def in_func(src, name, a, b, count=1):
    s, e = func_span(src, name)
    body = src[s:e]
    assert body.count(a) == count, (name, a, body.count(a))
    return src[:s] + body.replace(a, b) + src[e:]


# 1. 倒數迴圈：從 7 開始數
for fn in ('InitTrig_Camera_command', 'InitTrig_clear', 'InitTrig_deleteItems'):
    j = in_func(j, fn, 'local integer i=5\n', 'local integer i=7\n')
    print('倒數迴圈 5→7：%s' % fn)

# 2. -save / -load
for fn, trg, cmd, tail in (('InitTrig_ISOV', 'gg_trg_ISOV', '-save', 'true'),
                           ('InitTrig_ILOD', 'gg_trg_ILOD', '-load', 'false')):
    line = 'call TriggerRegisterPlayerChatEvent(%s,Player(5),"%s",%s)' % (trg, cmd, tail)
    add = '\n'.join(line.replace('Player(5)', 'Player(%d)' % k) for k in (6, 7))
    j = in_func(j, fn, line, line + '\n' + add)
    print('聊天指令 %s 補上 Player(6)、Player(7)' % cmd)

# 3. 皮膚：全域陣列、清空迴圈
assert j.count('integer array Skins_5\n') == 1
j = j.replace('integer array Skins_5\n', 'integer array Skins_5\ninteger array Skins_6\ninteger array Skins_7\n')
assert j.count('set Skins_5[L]=0\n') == 1
j = j.replace('set Skins_5[L]=0\n', 'set Skins_5[L]=0\nset Skins_6[L]=0\nset Skins_7[L]=0\n')

# 4. 皮膚：if 鏈的 n==5 分支複製成 6、7
L = j.split('\n')
fnat, cur = [], '?'
for l in L:
    m = re.match(r'function\s+(\w+)\s+takes', l)
    if m:
        cur = m.group(1)
    fnat.append(cur)
starts = [i for i, l in enumerate(L)
          if l.strip() == 'elseif n==5 then' and fnat[i] in ('RegisterSkin', 'SkinsButtons')]
print('要複製的 n==5 分支：%d 條（RegisterSkin 1 + SkinsButtons 3）' % len(starts))
assert len(starts) == 4
for st in reversed(starts):
    depth, k = 0, st + 1
    while True:
        s = L[k].strip()
        if re.match(r'if\b', s):
            depth += 1
        elif s == 'endif':
            if depth == 0:
                break
            depth -= 1
        k += 1
    body = L[st:k]
    assert all('Skins_' not in x or 'Skins_5' in x for x in body)
    new = []
    for n in (6, 7):
        for x in body:
            y = x.replace('elseif n==5 then', 'elseif n==%d then' % n).replace('Skins_5', 'Skins_%d' % n)
            new.append(y)
    L[k:k] = new
j = '\n'.join(L)

# 驗證：Skins_6 / Skins_7 用到的次數要跟 Skins_5 一樣
for k in (5, 6, 7):
    print('  Skins_%d 出現 %d 次' % (k, len(re.findall(r'\bSkins_%d\b' % k, j))))
for a, b in (('function', 'endfunction'), ('loop', 'endloop'), ('if', 'endif')):
    na = len(re.findall(r'^\s*%s\b' % a, j, re.M))
    nb = len(re.findall(r'^\s*%s\b' % b, j, re.M))
    print('  %-9s %6d / %-12s %6d  %s' % (a, na, b, nb, '✓' if na == nb else '✗'))
    assert na == nb

jb = j.encode('utf-8', 'surrogateescape')
open(os.path.join(BASE, 'ud_new_8p_v5.j'), 'wb').write(jb)
w3i8 = open(os.path.join(BASE, 'ud_new_8p.w3i'), 'rb').read()
out = os.path.join(BASE, '0UD_八人測試v5.w3x')
if os.path.exists(out):
    os.remove(out)
mpq_patch.write_files(SRC, out, {'war3map.j': jb, 'war3map.w3i': w3i8})
with open(out, 'r+b') as f:
    h = bytearray(f.read(512)); z = h.index(b'\x00', 8)
    struct.pack_into('<i', h, z + 5, 8); f.seek(0); f.write(h)
m = mpq.MPQ(out)
assert m.read('war3map.j') == jb and m.read('war3map.w3i') == w3i8
dst = os.path.join(MAPS, os.path.basename(out))
shutil.copy(out, dst)
print('八人 v5 讀回一致 ✓ → %s（%s）' % (dst, '存在' if os.path.exists(dst) else '找不到'))
