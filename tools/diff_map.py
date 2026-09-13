# -*- coding: utf-8 -*-
"""比對兩個版本的地圖，列出改了什麼、影響到哪些技能／英雄／道具。

    python tools/diff_map.py 新地圖.w3x               # 舊版 = version.json 的 map_file
    python tools/diff_map.py 舊地圖.w3x 新地圖.w3x

比對三層：
  1. war3map.j 逐函式 —— 新增／移除／內容變動（附 unified diff，每支最多 60 行）
  2. 物件資料（w3a 技能、w3u 單位、w3t 道具、w3h buff）逐物件逐欄位
  3. war3mapMisc.txt 全域常數

影響分析（這才是重點）：
  - 改到的函式若是共用引擎函式（BurnUnit、FrostUnit、Trig_HeroTakeDamage_Actions…），
    從 data/abilmap.json 反查所有依賴它的技能，按英雄分組。
  - 改到的函式若是某技能的實作，列出那些技能。
  - 改到的函式本文裡提到的 4 字元 ID（英雄／道具／技能）也列出來 ——
    很多機制是按單位型號或道具 ID 內聯在共用函式裡的，技能範圍抓不到。
  - 改到的物件直接對應到技能／英雄／道具名稱。

輸出：地圖版本差異.md（可直接讀）＋ 終端摘要。
"""
import io, json, os, re, sys, difflib, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding='utf-8')
from mpq import MPQ
import w3obj

ID4 = re.compile(r"'([A-Za-z0-9]{4})'")
FN = re.compile(r'^function ([A-Za-z0-9_]+) ', re.M)
MAX_DIFF_LINES = 60


def read_all(path):
    m = MPQ(path)
    def get(n):
        try:
            return m.read(n)
        except Exception:
            return None
    j = (get('war3map.j') or b'').decode('utf-8', 'replace')
    objs = {}
    for name, lvl in (('w3a', True), ('w3u', False), ('w3t', False), ('w3h', False), ('w3q', True), ('w3d', True)):
        d = get('war3map.' + name)
        if not d:
            objs[name] = {}
            continue
        try:
            objs[name] = w3obj.parse(d, lvl)
        except Exception:
            try:
                objs[name] = w3obj.parse(d)
            except Exception:
                objs[name] = {}
    misc = {}
    md = get('war3mapMisc.txt')
    if md:
        for line in md.decode('utf-8-sig', 'replace').replace('\r\n', '\n').split('\n'):
            if '=' in line and not line.strip().startswith('//'):
                k, v = line.split('=', 1)
                misc[k.strip()] = v.strip()
    return j, objs, misc


def split_fns(j):
    """函式名 -> (起行, 本文)。本文去掉尾端空白，方便比對。"""
    lines = j.split('\n')
    out, cur, start = {}, None, 0
    for i, l in enumerate(lines):
        m = re.match(r'function ([A-Za-z0-9_]+) ', l)
        if m:
            if cur:
                out[cur] = (start, lines[start:i])
            cur, start = m.group(1), i
    if cur:
        out[cur] = (start, lines[start:])
    return {k: (s, [x.rstrip() for x in b]) for k, (s, b) in out.items()}


def obj_name(kind, oid, objs, lang_names):
    r = objs.get(kind, {}).get(oid, {})
    f = {'w3a': 'anam', 'w3u': 'unam', 'w3t': 'unam', 'w3h': 'fnam', 'w3q': 'gnam', 'w3d': 'bnam'}.get(kind)
    v = r.get(f)
    v = v[0] if isinstance(v, list) else v
    zh = lang_names.get(oid)
    v = re.sub(r'\|c[0-9A-Fa-f]{8}|\|r', '', str(v or ''))
    return (zh + ' ' if zh else '') + (v or '')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    if len(args) == 1:
        old = json.load(io.open(os.path.join(HERE, 'version.json'), encoding='utf-8'))['map_file']
        new = args[0]
    elif len(args) == 2:
        old, new = args
    else:
        raise SystemExit(__doc__)
    print('舊：%s\n新：%s' % (old, new))
    jo, oo, mo = read_all(old)
    jn, on, mn = read_all(new)

    # 名稱對照（中文），從既有的網站資料撈
    names = {}
    try:
        hs = json.load(io.open(os.path.join(ROOT, 'data', 'heroes.json'), encoding='utf-8'))['heroes']
        for h in hs:
            names[h['id']] = h['n'][0]
            for a in h['ab']:
                names[a['id']] = a['n'][0]
                for o in a.get('opts') or []:
                    names[o['id']] = o['n'][0]
            for s in h.get('skins') or []:
                names[s['id']] = h['n'][0] + u'／皮膚 ' + s['n'][0]
                for a in s.get('add') or []:
                    names[a['id']] = a['n'][0]
        site = json.load(io.open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))
        for iid, it in site['items'].items():
            names[iid] = it['n'][0]
    except Exception as e:
        print('（名稱對照載入失敗：%s）' % e)
    try:
        AM = json.load(io.open(os.path.join(ROOT, 'data', 'abilmap.json'), encoding='utf-8'))
        AB = {a['id']: a for a in AM['abilities']}
    except Exception:
        AM, AB = None, {}

    # ---- 1. 函式 ----
    fo, fnn = split_fns(jo), split_fns(jn)
    added = sorted(set(fnn) - set(fo))
    removed = sorted(set(fo) - set(fnn))
    changed = sorted(k for k in fo if k in fnn and fo[k][1] != fnn[k][1])

    # ---- 2. 物件 ----
    # 魔獸編輯器重新存檔時會回收 ID：3.82fix 把「劍刃召喚」拿掉，它的 A01S 被
    # 拿去給「背包擴充」用。同一個 ID 比欄位會把兩個不相干的東西當成「改了 40 個欄位」。
    # 所以先用「名稱＋原型」當內容簽名：名稱變了的視為「ID 被重新指派」，
    # 舊內容若在新版換了 ID 就標成「搬家」，欄位 diff 只對真正同一個東西做。
    NAMEF = {'w3a': 'anam', 'w3u': 'unam', 'w3t': 'unam', 'w3h': 'fnam', 'w3q': 'gnam', 'w3d': 'bnam'}
    def sig(kind, r):
        n = r.get(NAMEF[kind]); n = n[0] if isinstance(n, list) else n
        return (re.sub(r'\|c[0-9A-Fa-f]{8}|\|r', '', str(n or '')).strip(), r.get('_base'))
    obj_changes = {}   # kind -> {oid: {'state': +/-/~/reassigned/moved, 'fields':..., 'to':...}}
    for kind in ('w3a', 'w3u', 'w3t', 'w3h', 'w3q', 'w3d'):
        a, b = oo.get(kind, {}), on.get(kind, {})
        bsig = {}
        for k, r in b.items():
            bsig.setdefault(sig(kind, r), []).append(k)
        ch = {}
        for oid in sorted(set(a) | set(b)):
            if oid not in a:
                ch[oid] = {'state': '+'}
            elif oid not in b:
                ch[oid] = {'state': '-'}
            elif sig(kind, a[oid]) != sig(kind, b[oid]):
                moved = [k for k in bsig.get(sig(kind, a[oid]), []) if k != oid and k not in a]
                ch[oid] = {'state': 'reassigned', 'old': sig(kind, a[oid]), 'new': sig(kind, b[oid]), 'to': moved}
            else:
                diff = {}
                for f in sorted(set(a[oid]) | set(b[oid])):
                    if a[oid].get(f) != b[oid].get(f):
                        diff[f] = (a[oid].get(f), b[oid].get(f))
                if diff:
                    ch[oid] = {'state': '~', 'fields': diff}
        if ch:
            obj_changes[kind] = ch

    # ---- 3. 常數 ----
    misc_changes = {k: (mo.get(k), mn.get(k)) for k in sorted(set(mo) | set(mn)) if mo.get(k) != mn.get(k)}

    # ---- 影響分析 ----
    engine = set(AM['engine_fns']) if AM else set()
    impact = []   # (函式, 類型, [受影響清單])
    heroes_by_id = {h['id']: h for h in hs} if names else {}
    for f in changed + added + removed:
        body = ' '.join((fo.get(f, (0, []))[1]) + (fnn.get(f, (0, []))[1]))
        ids = set(ID4.findall(body))
        via_ab = sorted(set((AM['by_fn'].get(f, []) if AM else []) + (AM['fn_owner'].get(f, []) if AM else [])))
        hero_ids = sorted(i for i in ids if i in heroes_by_id)
        item_ids = sorted(i for i in ids if i in (site['items'] if names else {}))
        abil_ids = sorted(i for i in ids if i in AB and i not in via_ab)
        impact.append((f, 'engine' if f in engine else 'fn', via_ab, hero_ids, item_ids, abil_ids))

    # ---- 報告 ----
    L = []
    L.append(u'# 地圖版本差異')
    L.append(u'')
    L.append(u'- 舊：`%s`\n- 新：`%s`\n- 產生時間：%s' % (os.path.basename(old), os.path.basename(new),
                                                   datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
    L.append(u'')
    L.append(u'| | 新增 | 移除 | 變動 | ID 重新指派 |')
    L.append(u'|---|---|---|---|---|')
    L.append(u'| 函式 | %d | %d | %d | |' % (len(added), len(removed), len(changed)))
    for kind, lab in (('w3a', u'技能'), ('w3u', u'單位'), ('w3t', u'道具'), ('w3h', u'buff'), ('w3q', u'升級'), ('w3d', u'可破壞物')):
        ch = obj_changes.get(kind, {})
        L.append(u'| %s（%s） | %d | %d | %d | %d |' % (lab, kind, sum(1 for v in ch.values() if v['state'] == '+'),
                                                sum(1 for v in ch.values() if v['state'] == '-'),
                                                sum(1 for v in ch.values() if v['state'] == '~'),
                                                sum(1 for v in ch.values() if v['state'] == 'reassigned')))
    L.append(u'| 全域常數 | | | %d | |' % len(misc_changes))
    L.append(u'')

    # 影響：先列引擎函式，再列技能函式
    eng = [x for x in impact if x[1] == 'engine']
    oth = [x for x in impact if x[1] != 'engine']
    if eng:
        L.append(u'## ⚠ 共用引擎函式有變動 —— 影響範圍最大')
        L.append(u'')
        for f, _, via, hids, iids, aids in eng:
            L.append(u'### `%s`' % f)
            if via:
                by_hero = {}
                for a in via:
                    r = AB.get(a)
                    if r:
                        by_hero.setdefault(r['hero_n'][0], []).append(r['n'][0])
                L.append(u'依賴它的技能（%d 個，%d 隻英雄）：' % (len(via), len(by_hero)))
                for hn, al in sorted(by_hero.items()):
                    L.append(u'- **%s**：%s' % (hn, u'、'.join(al)))
            if f in ('Trig_HeroTakeDamage_Actions',):
                L.append(u'- 傷害管線是所有直接傷害的必經之路，**全部英雄**都受影響；下面是本文裡按 ID 內聯的分支：')
            if hids:
                L.append(u'- 本文裡按單位型號內聯的英雄：%s' % u'、'.join(names.get(i, i) for i in hids))
            if iids:
                L.append(u'- 本文裡按道具 ID 內聯的道具：%s' % u'、'.join(names.get(i, i) for i in iids))
            L.append(u'')
    if oth:
        L.append(u'## 函式變動')
        L.append(u'')
        for f, _, via, hids, iids, aids in oth:
            tag = u'新增' if f in added else u'移除' if f in removed else u'變動'
            who = []
            if via:
                who.append(u'技能：' + u'、'.join('%s（%s）' % (AB[a]['n'][0], AB[a]['hero_n'][0]) for a in via if a in AB))
            if hids:
                who.append(u'英雄：' + u'、'.join(names.get(i, i) for i in hids))
            if iids:
                who.append(u'道具：' + u'、'.join(names.get(i, i) for i in iids[:12]) + (u'…' if len(iids) > 12 else ''))
            if aids:
                who.append(u'提到的技能：' + u'、'.join(names.get(i, i) for i in aids[:12]))
            L.append(u'- `%s`（%s）%s' % (f, tag, (u' — ' + u'；'.join(who)) if who else u' — 沒有對應到任何英雄／技能／道具'))
        L.append(u'')

    # 物件變動明細
    for kind, lab in (('w3a', u'技能'), ('w3u', u'單位'), ('w3t', u'道具'), ('w3h', u'buff'), ('w3q', u'升級'), ('w3d', u'可破壞物')):
        ch = obj_changes.get(kind)
        if not ch:
            continue
        L.append(u'## 物件資料變動：%s（%s）' % (lab, kind))
        L.append(u'')
        for oid, v in ch.items():
            nm = obj_name(kind, oid, on if v['state'] != '-' else oo, names)
            if v['state'] == '+':
                L.append(u'- `%s` %s —— **新增**' % (oid, nm))
            elif v['state'] == '-':
                L.append(u'- `%s` %s —— **移除**' % (oid, nm))
            elif v['state'] == 'reassigned':
                on_, nn = v['old'][0] or '?', v['new'][0] or '?'
                L.append(u'- `%s` **ID 被重新指派**：原本是「%s%s」，現在是「%s」%s' % (
                    oid, (names.get(oid) + ' ') if names.get(oid) else '', on_, nn,
                    (u' —— 舊內容搬到了 `%s`' % u'`、`'.join(v['to'])) if v['to'] else u' —— 舊內容在新版找不到（可能被拿掉）'))
            else:
                L.append(u'- `%s` %s' % (oid, nm))
                for f, (a, b) in v['fields'].items():
                    sa, sb = json.dumps(a, ensure_ascii=False), json.dumps(b, ensure_ascii=False)
                    if len(sa) > 90: sa = sa[:88] + u'…'
                    if len(sb) > 90: sb = sb[:88] + u'…'
                    L.append(u'  - `%s`：%s → %s' % (f, sa, sb))
        L.append(u'')
    if misc_changes:
        L.append(u'## 全域常數變動（war3mapMisc.txt）')
        L.append(u'')
        for k, (a, b) in misc_changes.items():
            L.append(u'- `%s`：%s → %s' % (k, a, b))
        L.append(u'')

    # 函式 diff 原文
    if changed:
        L.append(u'## 函式內容差異')
        L.append(u'')
        for f in changed:
            (so, bo), (sn, bn) = fo[f], fnn[f]
            d = list(difflib.unified_diff(bo, bn, 'old:%d' % (so + 1), 'new:%d' % (sn + 1), n=2, lineterm=''))
            L.append(u'### `%s`（舊 %d 行 → 新 %d 行）' % (f, len(bo), len(bn)))
            L.append(u'```diff')
            L.extend(d[:MAX_DIFF_LINES])
            if len(d) > MAX_DIFF_LINES:
                L.append(u'… 還有 %d 行' % (len(d) - MAX_DIFF_LINES))
            L.append(u'```')
            L.append(u'')

    rp = os.path.join(ROOT, u'地圖版本差異.md')
    io.open(rp, 'w', encoding='utf-8').write(u'\n'.join(L))
    print(u'函式：+%d −%d ~%d｜物件變動：%s｜常數：%d' % (
        len(added), len(removed), len(changed),
        ' '.join('%s:%d' % (k, len(v)) for k, v in obj_changes.items()) or u'無', len(misc_changes)))
    if eng:
        print(u'⚠ 引擎函式變動：%s' % u'、'.join(x[0] for x in eng))
    print(u'報告 -> %s' % os.path.relpath(rp, ROOT))


if __name__ == '__main__':
    main()
