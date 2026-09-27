# -*- coding: utf-8 -*-
"""片段化翻譯的核心：拆片段、數字模板化、從平行語料對齊出片段對照。"""
import re

LINE = re.compile(r'(\r\n|\n|\|n|\|N)')
COLOR = re.compile(r'(\|[cC][0-9A-Fa-f]{8}|\|[rR])')
NUM = re.compile(r'[-+]?\d+(?:[.,]\d+)?')
CYR = re.compile(r'[Ѐ-ӿ]')
HAN = re.compile(r'[一-鿿]')


def split(s):
    """字串 → token 清單：換行、顏色碼原樣保留，其餘是要翻的文字片段。"""
    out = []
    for part in LINE.split(s):
        if not part:
            continue
        if LINE.fullmatch(part):
            out.append(('sep', part)); continue
        for q in COLOR.split(part):
            if not q:
                continue
            out.append(('sep', q) if COLOR.fullmatch(q) else ('txt', q))
    return out


# 拉丁字母冒充俄文字母（外觀相同）。只在「含俄文的單字」裡還原，英文單字不動。
HOMO = str.maketrans('aceopxyKCMTHBPAEOXk', 'асеорхуКСМТНВРАЕОХк')
WORD = re.compile(r'[A-Za-zЀ-ӿ]+')


LOOK_LOWER = re.compile(r'^[aceopxyk]+$')


def norm(t):
    """含俄文的單字裡的拉丁同形字母還原；整句含俄文時，全小寫同形字母組成的單字（如 yp、ceк）也還原。"""
    has = bool(CYR.search(t))
    t = t.replace('ё', 'е').replace('Ё', 'Е')

    def rep(m):
        w = m.group(0)
        if CYR.search(w) or (has and LOOK_LOWER.match(w)):
            return w.translate(HOMO)
        return w
    return WORD.sub(rep, t)


def template(t):
    """把數字換成 {0} {1}…；回傳 (模板, 數字清單)。前後空白另存。同形字母先還原。"""
    t = norm(t)
    lead = t[:len(t) - len(t.lstrip())]
    trail = t[len(t.rstrip()):]
    core = t.strip()
    nums = []
    def rep(m):
        nums.append(m.group(0)); return '{%d}' % (len(nums) - 1)
    return lead, NUM.sub(rep, core), nums, trail


def needs(t):
    return bool(CYR.search(t))


def fill(tmpl_zh, nums):
    def rep(m):
        i = int(m.group(1))
        return nums[i] if i < len(nums) else m.group(0)
    return re.sub(r'\{(\d+)\}', rep, tmpl_zh)


def structure(tokens):
    return [v if k == 'sep' else ('T' if needs(v) or HAN.search(v) else v.strip()) for k, v in tokens]


def align(ru, zh):
    """ru、zh 兩段遊戲內原文結構相同（換行、顏色碼、非文字片段都一樣）時，回傳片段對照 [(ru模板, zh模板)]。"""
    a, b = split(ru), split(zh)
    if len(a) != len(b):
        return None
    pairs = []
    for (ka, va), (kb, vb) in zip(a, b):
        if ka != kb:
            return None
        if ka == 'sep':
            if va.lower() != vb.lower():
                return None
            continue
        if needs(va):
            if not HAN.search(vb) and CYR.search(vb):
                return None
            _, ta, na, _ = template(va)
            _, tb, nb, _ = template(vb)
            if sorted(na) != sorted(nb):
                return None
            # zh 模板裡的佔位符改成對應 ru 的編號
            mp = {}
            for i, n in enumerate(nb):
                j = [k for k, x in enumerate(na) if x == n and k not in mp.values()]
                if not j:
                    return None
                mp[i] = j[0]
            tb2 = re.sub(r'\{(\d+)\}', lambda m: '{%d}' % mp[int(m.group(1))], tb)
            pairs.append((ta, tb2))
    return pairs
