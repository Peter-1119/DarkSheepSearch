# -*- coding: utf-8 -*-
"""選單文字統一格式（翻譯之後對 war3map.j 套用）：
   需要35000積分 / 需要1 000 000積分 → 需要 35 000 積分
   黑暗墓地 (260% 難度)            → 黑暗墓地（260% 難度）
   熔巖地心 → 熔岩地心；「玩家總積分: 」→「玩家總積分：」"""
import re


def _pts(m):
    n = int(m.group(1).replace(' ', ''))
    return '需要 %s 積分' % '{:,}'.format(n).replace(',', ' ')


def tidy(J):
    c = [0]

    def sub(rx, rep, s):
        s2, k = re.subn(rx, rep, s)
        c[0] += k
        return s2
    J = sub(r'需要\s*(\d[\d ]*\d|\d)\s*積分', _pts, J)
    J = sub(r' \((\d+%(?: > \d+%)? 難度)\)', r'（\1）', J)
    J = sub(r'熔巖地心', '熔岩地心', J)
    J = sub(r'玩家總積分: ', '玩家總積分：', J)
    J = sub(r'"\. 可選戰場：', '"。可選戰場：', J)
    J = sub(r'選擇等級: ', '選擇等級：', J)
    return J, c[0]
