# -*- coding: utf-8 -*-
"""列出成品地圖裡所有對話框（選單）的標題與按鈕文字，檢查有沒有沒翻到的。"""
import sys, re
sys.path.insert(0, r'D:/Notebook Program Scripts/Python_Scripts/DarkSheep/tools')
sys.stdout.reconfigure(encoding='utf-8')
import mpq
j = mpq.MPQ(r'C:/Users/ccvs0/Documents/Warcraft III/Maps/Download/0UD_合併底圖_E2.w3x').read('war3map.j').decode('utf-8', 'replace')
STR = re.compile(r'"((?:[^"\\]|\\.)*)"')
seen = []
for m in re.finditer(r'(DialogAddButton\w*|DialogSetMessage\w*|DialogAddQuitButton\w*|CreateTimerDialog\w*|TimerDialogSetTitle\w*|MultiboardSetTitleText\w*|CreateQuest\w*|QuestSetTitle\w*)\(([^\n]*)\)', j):
    for s in STR.findall(m.group(2)):
        t = re.sub(r'\|c[0-9A-Fa-f]{8}|\|r', '', s)
        if t and t not in seen:
            seen.append(t)
bad = [t for t in seen if re.search(r'[\u0400-\u04ff]', t) or (re.search(r'[A-Za-z]{3,}', t) and not re.search(r'[\u4e00-\u9fff]', t))]
print('共 %d 種文字；可疑 %d 種' % (len(seen), len(bad)))
for t in (bad if '-a' not in sys.argv else seen):
    print(repr(t))
