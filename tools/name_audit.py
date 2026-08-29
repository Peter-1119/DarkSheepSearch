# -*- coding: utf-8 -*-
"""中文名稱來源稽核：每個名字是哪裡來的、可靠度如何。

輸出 ../data/name_audit.csv，可以用 Excel 開啟逐條校對。
改名字的方法：編輯 names2.json，然後重跑
    python build_data2.py && python build_site_data.py && python build_site.py && python build_md2.py
"""
import json, os, re, sys, csv
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NZH = json.load(open(os.path.join(HERE, 'names2.json'), encoding='utf-8'))
NEN = json.load(open(os.path.join(HERE, 'names_en.json'), encoding='utf-8'))
MAP = json.load(open(os.path.join(HERE, 'name_map.json'), encoding='utf-8'))
SITE = json.load(open(os.path.join(ROOT, 'data/items.json'), encoding='utf-8'))['items']

old = {}
for v in MAP.values():
    old.setdefault(v['url'][:-5], re.sub(r'【.*?】', '', v['zh']))

# 我刻意改掉舊表名字的，以及理由
RENAMED = {
    'I04W': '舊表兩件裝備共用「仪式圣杯」，這件是另一件',
    'I085': '舊表兩件裝備共用「迷雾之矛」，這件是另一件',
    'I06S': '舊表兩件裝備共用「刺客之刺」，這件是另一件',
    'clsd': '舊表兩件裝備共用「骑士手套」，這件其實是鎧甲',
    'brac': '舊表兩件裝備共用「骑士手套」；俄文名已改為 Перчатки чемпиона',
    'bgst': '舊表兩件戒指共用「狩猎女神之戒」；Геракл 是大力神',
    'wild': '舊表兩件裝備共用「魔法金汤」，這件是另一件',
    'tret': '舊表兩件法杖共用「辉煌法杖」，這件是另一件',
    'shea': '俄文名已從 Скипетр Искажения 改為 Скипетр разлома',
    'gvsm': '俄文名已從 Жезл с зачарованным кварцом 改為 Жезл с кварцом',
}

rows, tally = [], {'A': 0, 'B': 0, 'C': 0}
for i, v in sorted(SITE.items(), key=lambda kv: (kv[1]['group'], NZH[kv[0]])):
    o = old.get(i)
    if o is None:
        src, note, rel = 'C 我從俄文翻譯', '', '低 — 沒有官方依據'
        tally['C'] += 1
    elif i in RENAMED:
        src, note, rel = 'B 我改了名字', RENAMED[i], '中 — 有理由，但請確認'
        tally['B'] += 1
    else:
        src, note, rel = 'A 沿用舊合成表', '', '高 — 玩家實際用的名字'
        tally['A'] += 1
    rows.append({
        '道具ID': i, '中文名': NZH[i], '舊合成表': o or '',
        '俄文名': v['name_ru'], '英文名': NEN[i],
        '品質': v['cls'], '來源': src, '可靠度': rel, '備註': note,
    })

out = os.path.join(ROOT, 'data', 'name_audit.csv')
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

print('中文名稱來源統計（共 %d 個）' % len(rows))
print('  A 沿用舊合成表（簡轉繁）: %3d   可靠度高' % tally['A'])
print('  B 我刻意改了名字        : %3d   有理由，附在備註欄' % tally['B'])
print('  C 我從俄文自己翻譯      : %3d   ← 沒有官方依據，錯誤最可能出在這裡' % tally['C'])
print()
print('已輸出 ->', out)
print('用 Excel 開啟即可逐條校對；要修正就編輯 tools/names2.json 後重跑建置。')
