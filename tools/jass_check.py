# -*- coding: utf-8 -*-
"""簡易 JASS 靜態檢查（沒有 pjass 時用）。只抓會讓地圖開不起來的常見錯誤：
   1. 函式在定義之前被呼叫／被 function 參照（JASS 要求先定義）
   2. 同名函式重複定義
   3. 使用未宣告的 udg_ / gg_ / udB_ / udC_ 變數
   4. local 宣告出現在一般敘述之後
   5. function / endfunction、if / endif、loop / endloop 不成對
   地圖外（common.j / blizzard.j）的函式一律當成原生函式放行。
"""
import re
import sys


def check(J, prefixes=('udg_', 'gg_', 'udB_', 'udC_'), quiet=False):
    errs = []
    head = J[:J.index('endglobals')]
    glob = set(re.findall(r'^\s*(?:constant\s+)?\w+(?:\s+array)?\s+(\w+)', head.split('globals', 1)[1], re.M))
    defs = {}
    for m in re.finditer(r'^function (\w+) takes', J, re.M):
        if m.group(1) in defs:
            errs.append('重複定義函式 %s（第 %d 行）' % (m.group(1), J.count('\n', 0, m.start()) + 1))
        defs.setdefault(m.group(1), m.start())
    body_re = re.compile(r'^function (\w+) takes (.*?) returns \w+\n(.*?)^endfunction', re.M | re.S)
    for m in body_re.finditer(J):
        name, params, body = m.group(1), m.group(2), m.group(3)
        pos = m.start()
        line0 = J.count('\n', 0, pos) + 1
        local = set(re.findall(r'^local\s+\w+(?:\s+array)?\s+(\w+)', body, re.M))
        if params.strip() != 'nothing':
            local |= set(p.split()[-1] for p in params.split(','))
        # local 位置
        seen_stmt = False
        for l in body.split('\n'):
            s = l.strip()
            if not s:
                continue
            if s.startswith('local '):
                if seen_stmt:
                    errs.append('%s（第 %d 行起）：local 出現在敘述之後：%s' % (name, line0, s[:60]))
                    break
            else:
                seen_stmt = True
        # 呼叫順序
        code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', body)
        for c in set(re.findall(r'\b(\w+)\s*\(', code)) | set(re.findall(r'\bfunction\s+(\w+)', code)):
            if c in defs and defs[c] >= pos and c != name:
                errs.append('%s（第 %d 行起）呼叫了之後才定義的 %s' % (name, line0, c))
        # 未宣告變數
        for v in set(re.findall(r'\b((?:%s)\w+)\b' % '|'.join(prefixes), code)):
            if v not in glob and v not in local and v not in defs:
                errs.append('%s（第 %d 行起）：未宣告的 %s' % (name, line0, v))
    for a, b in (('function', 'endfunction'), ('if', 'endif'), ('loop', 'endloop')):
        na = len(re.findall(r'^\s*%s\b' % a, J, re.M)); nb = len(re.findall(r'^\s*%s\b' % b, J, re.M))
        if na != nb:
            errs.append('%s %d 個、%s %d 個，不成對' % (a, na, b, nb))
    return errs


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    J = open(sys.argv[1], 'rb').read().decode('utf-8', 'surrogateescape')
    e = check(J)
    for x in e[:200]:
        print(x)
    print('共 %d 個問題' % len(e))
