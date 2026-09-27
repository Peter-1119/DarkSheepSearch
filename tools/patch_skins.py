# -*- coding: utf-8 -*-
"""把地圖裡「綁定帳號名稱」的英雄皮膚，改成每個玩家都能自己選。

地圖本身已經有一整套皮膚選單 —— 「額外資訊」單位（Hvsh）上的「替代皮膚」按鈕
（技能 A0KJ），按下去是一頁 10 個、可翻頁的皮膚清單，點一下切換開／關，
選英雄時 Trig_HeroPick_Actions 會把英雄換成對應的皮膚單位。

唯一的限制在 Trig_NewInit_Actions：`RegisterSkin(玩家, 皮膚技能, 皮膚單位, "on"/"off")`
只有一小批是無條件註冊給所有人的（預設關閉），其餘全部包在
`if name=="某某帳號" then` 裡面。沒註冊 = 選單裡看不到。

這支工具就是把那些綁名字的皮膚，補進「所有人」那一批（一律 "off"，
讓玩家自己去選單開），其他完全不動：
  - 物件資料（w3a/w3u/w3t…）一個位元組都沒改
  - 名字判斷那幾段留著（對名單上的人只是重複註冊一次，無害）

用法：
    python tools/patch_skins.py                     # 用 version.json 的地圖，輸出 *_allskins.w3x
    python tools/patch_skins.py 來源.w3x 目標.w3x

注意：多人連線時所有人的地圖檔必須完全一樣，這份改過的要發給每個隊友。
"""
import io, json, os, re, shutil, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from mpq import MPQ, _hash, _CT

RS = re.compile(r"""call RegisterSkin\(L,'(\w+)','(\w+)',"(on|off)"\)""")


def encrypt(data, key):
    n = len(data) // 4
    vals = list(struct.unpack('<%dI' % n, data[:n * 4]))
    s1, s2, out = key, 0xEEEEEEEE, []
    for v in vals:
        s2 = (s2 + _CT[0x400 + (s1 & 0xFF)]) & 0xFFFFFFFF
        out.append(v ^ ((s1 + s2) & 0xFFFFFFFF))
        s1 = (((~s1 << 0x15) + 0x11111111) | (s1 >> 0x0B)) & 0xFFFFFFFF
        s2 = (v + s2 + (s2 << 5) + 3) & 0xFFFFFFFF
    return struct.pack('<%dI' % n, *out) + data[n * 4:]


def pack(raw, sector):
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


def skin_names():
    """皮膚單位 ID -> (英雄名, 皮膚名)，從 data/site.json 拿，只是給註解用。"""
    out = {}
    p = os.path.join(ROOT, 'data', 'site.json')
    if not os.path.isfile(p):
        return out
    for h in json.load(io.open(p, encoding='utf-8'))['heroes']:
        for k in h.get('skins', []):
            out[k['id']] = (h['n'][0], k['n'][0])
    return out


# 「額外資訊」單位被放在地圖角落 (13000+玩家編號*150, 13100)，開場鏡頭在 (12122,12000)，
# 剛好在畫面外的右上角，所以幾乎沒人知道有這東西。補一個 -skin 指令：選取它並把鏡頭移過去。
SKIN_CMD = """function SkinMenuCmd takes nothing returns nothing
local player pl=GetTriggerPlayer()
local integer n=GetPlayerId(pl)
if Info[n]!=null then
call SelectUnitForPlayerSingle(Info[n],pl)
if GetLocalPlayer()==pl then
call PanCameraToTimed(GetUnitX(Info[n]),GetUnitY(Info[n]),0)
endif
call DisplayTimedTextToPlayer(pl,0,0,15,"|cFF9ED1D8Skin menu: press W on this unit, click a skin to toggle it, then pick your hero.|r")
endif
set pl=null
endfunction
function SkinMenuInit takes nothing returns nothing
local trigger t=CreateTrigger()
local integer i=0
loop
exitwhen i>5
call TriggerRegisterPlayerChatEvent(t,Player(i),"-skin",true)
set i=i+1
endloop
call TriggerAddAction(t,function SkinMenuCmd)
set t=null
endfunction
"""
CMD_ANCHOR = 'function Trig_NewInit_Actions takes nothing returns nothing\n'
INIT_ANCHOR = ('set L=L+1\nendloop\nset u=null\nset ug=null\nset pl=null\n'
               'call DestroyTrigger(GetTriggeringTrigger())\nendfunction\n')


def gated_blocks(lines, start, stop):
    """找出 start..stop 之間「body 只有 RegisterSkin」的 if name== 區塊。

    RegisterSkin 是「往清單後面加一筆」（SkinsCount+1 才寫進 Skins_n），
    所以同一個皮膚註冊兩次，選單裡就會出現兩個按鈕。補進「所有人」那一批之後，
    這些綁名字的區塊就是純粹的重複來源 —— 名單上的玩家會看到重複的皮膚。
    整段拿掉最乾淨：反正每個皮膚在上面都已經註冊過一次了。

    只動 body 全是 RegisterSkin 的那幾段；同一段迴圈裡還有
    Players_Gifts 與 SetPlayerTechResearched 的名字判斷，那些要留著。
    """
    out, i = [], start
    while i < stop:
        if not lines[i].strip().startswith('if name=='):
            i += 1
            continue
        depth, end = 0, None
        for k in range(i, stop + 1):
            s = lines[k].strip()
            if s.startswith('if '):
                depth += 1
            elif s == 'endif':
                depth -= 1
                if depth == 0:
                    end = k
                    break
        if end is None:
            break
        body = [lines[k].strip() for k in range(i + 1, end)]
        if body and all(RS.match(b) or b.startswith('elseif name==')
                        for b in body):
            out.append((i, end))
        i = end + 1
    return out


def check_duplicates(jass):
    """模擬每一個會被判斷到的帳號名稱，看有沒有皮膚被註冊兩次。

    回傳 {帳號名: [重複的皮膚單位]}，正常應該是空的。
    """
    lines = jass.split('\n')
    start = next(i for i, l in enumerate(lines)
                 if l.strip() == 'set name=GetPlayerName(pl)')
    stop = next(i for i in range(start, len(lines))
                if lines[i].strip() == 'set L=L+1')
    uni, per = [], {}
    cur = None
    for k in range(start, stop):
        s = lines[k].strip()
        m = re.match(r'(?:else)?if (name==.*) then$', s)
        if m:
            cur = re.findall(r'name=="([^"]*)"', m.group(1))
            for n in cur:
                per.setdefault(n, [])
            continue
        if s in ('endif', 'else'):
            cur = None
            continue
        r = RS.match(s)
        if r:
            if cur:
                for n in cur:
                    per[n].append(r.group(2))
            else:
                uni.append(r.group(2))
    out = {}
    for n, v in per.items():
        seen, d = set(uni), []
        for u in v:
            (d.append(u) if u in seen else seen.add(u))
        if d:
            out[n] = d
    if len(set(uni)) != len(uni):
        out['(所有人)'] = [u for u in set(uni) if uni.count(u) > 1]
    return out


def build_patch(jass):
    """回傳 (錨點行, 新內容, 補進去的皮膚清單)。"""
    lines = jass.split('\n')
    try:
        start = next(i for i, l in enumerate(lines)
                     if l.strip() == 'set name=GetPlayerName(pl)')
    except StopIteration:
        raise SystemExit('找不到皮膚註冊迴圈（set name=GetPlayerName(pl)）')

    uni, anchor = [], None          # 無條件註冊的那一批
    for i in range(start + 1, start + 200):
        s = lines[i].strip()
        if s.startswith('if name=='):
            break
        m = RS.match(s)
        if m:
            uni.append(m.group(2))
            anchor = lines[i]
    if not anchor:
        raise SystemExit('找不到無條件註冊的皮膚，地圖結構可能變了')

    have, gated = set(uni), []
    for l in lines:
        m = RS.match(l.strip())
        if m and m.group(2) not in have:
            have.add(m.group(2))
            gated.append((m.group(1), m.group(2)))
    if not gated:
        raise SystemExit('沒有綁名字的皮膚可以補 —— 是不是已經改過了？')

    nm = skin_names()
    out = [anchor,
           '// 本機改動：原本只綁定特定帳號名稱的皮膚，改成每個玩家都註冊（預設關閉）。',
           '// 開啟方式跟原本那 %d 個一樣：選英雄前用「額外資訊」單位 -> 替代皮膚 -> 點一下。' % len(uni)]
    for a, u in gated:
        h, s = nm.get(u, ('', ''))
        out.append("""call RegisterSkin(L,'%s','%s',"off")%s"""
                   % (a, u, (' // %s-%s' % (h, s)) if h else ''))
    edits = [(anchor + '\n', '\n'.join(out) + '\n')]

    # 原本綁名字的那幾段整個拿掉，否則名單上的玩家會被註冊兩次 -> 選單出現重複。
    stop = next(i for i in range(start, len(lines))
                if lines[i].strip() == 'set L=L+1')
    dead = gated_blocks(lines, start, stop)
    if not dead:
        raise SystemExit('找不到只含 RegisterSkin 的綁名字區塊，地圖結構可能變了')
    for a, b in dead:
        old = '\n'.join(lines[a:b + 1]) + '\n'
        edits.append((old, '// 本機改動：原本綁帳號名稱的皮膚註冊（%d 行）已移除，'
                           '改由上面的「所有人」那一批統一註冊，避免重複。\n' % (b - a + 1)))
    return edits, gated, dead


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    if len(args) >= 1:
        src = args[0]
    else:
        src = json.load(io.open(os.path.join(HERE, 'version.json'),
                                encoding='utf-8'))['map_file']
    dst = args[1] if len(args) >= 2 else re.sub(r'\.w3x$', '_allskins.w3x', src)

    m = MPQ(src)
    jass = m.read('war3map.j').decode('utf-8', 'surrogateescape')
    edits, added, removed = build_patch(jass)
    new = edits[0][1]
    if 'function SkinMenuCmd ' not in jass:      # -skin 指令（只加一次）
        edits.append((CMD_ANCHOR, SKIN_CMD + CMD_ANCHOR))
        edits.append((INIT_ANCHOR,
                      INIT_ANCHOR.replace('endloop\n', 'endloop\ncall SkinMenuInit()\n', 1)))
    out = jass
    for a, b in edits:
        if out.count(a) != 1:
            raise SystemExit('錨點在檔案裡出現 %d 次（要剛好 1 次）：%s' % (out.count(a), a[:40]))
        out = out.replace(a, b, 1)
    raw = out.encode('utf-8', 'surrogateescape')

    blob = pack(raw, m.sector)
    bi = m.find('war3map.j')
    pos, csize, fsize, flags = m.block[bi]
    if flags & (0x00010000 | 0x01000000):
        raise SystemExit('war3map.j 有加密／單一單元旗標，這支工具不處理')
    base, blocks = m.base, list(m.block)
    m.f.seek(base)
    (_, _hs, _az, _ver, _bs, _htp, btp, _hn, _bn) = struct.unpack('<4sIIHHIIII',
                                                                  m.f.read(0x20))
    m.f.close()

    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy2(src, dst)
    with open(dst, 'r+b') as f:
        if len(blob) <= csize:                    # 塞得回原位就原地覆寫
            newpos, where = pos, '原地覆寫'
        else:                                     # 否則附加到檔尾，改區塊表指過去
            f.seek(0, 2)
            newpos, where = f.tell() - base, '附加到檔尾'
        f.seek(base + newpos)
        f.write(blob)
        blocks[bi] = (newpos, len(blob), len(raw), flags)
        f.seek(base + btp)
        f.write(encrypt(b''.join(struct.pack('<4I', *b) for b in blocks),
                        _hash('(block table)', 3)))

    # 驗證：改過的讀得回來，其他檔案原封不動
    m2 = MPQ(dst)
    t2 = m2.read('war3map.j').decode('utf-8', 'surrogateescape')
    ok = (t2.count(new) == 1 and t2.count('function SkinMenuCmd ') == 1
          and t2.count('call SkinMenuInit()') == 1
          and len(t2.encode('utf-8', 'surrogateescape')) == len(raw))
    m1 = MPQ(src)
    same = all(m1.read(x) == m2.read(x) for x in
               ('war3map.w3a', 'war3map.w3u', 'war3map.w3t', 'war3map.w3h',
                'war3map.w3q', 'war3mapMisc.txt', 'war3map.w3i'))
    # 註冊的皮膚在選英雄時真的會被套用？
    body = t2[t2.index('function Trig_HeroPick_Actions'):]
    body = body[:body.index('\nfunction ', 10)]
    dead = [u for _, u in added if ("LoadInteger(hash,pl_Id,'%s')" % u) not in body]

    # 沒有任何帳號會被註冊到重複的皮膚？（RegisterSkin 是往清單後面加，重複＝選單多一顆按鈕）
    dup = check_duplicates(t2)

    print('%s -> %s' % (os.path.basename(src), os.path.basename(dst)))
    print('  補上 %d 個皮膚，移除 %d 段綁帳號的重複註冊，war3map.j %s'
          % (len(added), len(removed), where))
    print('  war3map.j 寫回正確：%s｜其他檔案未更動：%s' % (ok, same))
    print('  會看到重複皮膚的帳號：%s' % (dup or '無（所有人都是一個皮膚一顆按鈕）'))
    if dup:
        raise SystemExit('還有重複註冊，請不要用這份檔案')
    print('  選英雄時不會生效的：%s' % (dead or '無'))
    print('  已加入 -skin 指令（選取「額外資訊」單位並把鏡頭移過去）')
    if not (ok and same) or dead:
        raise SystemExit('驗證失敗，請不要用這份檔案')
    print('  完成。多人連線時每個隊友都要換成這一份地圖檔。')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
