# -*- coding: utf-8 -*-
"""階段 E：中文化。片段化翻譯，對照優先序：手動 > 網站 > 2.3.0 物件 > 2.3.0 腳本。"""
import os, re, json, collections
import zhconv
from ud_seg import split, template, needs, fill, align, norm
import ud_termfix

BASE = os.path.dirname(os.path.abspath(__file__))
# 2.3.0 舊圖的譯文是多人翻的、用詞不一，改為全部重翻；設 True 可退回舊行為
USE_230 = False


def _load(n):
    p = os.path.join(BASE, n)
    d = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
    # 譯文裡還留著俄文的對照（網站或 2.3.0 翻一半）一律不用
    return {k: v for k, v in d.items() if not (isinstance(v, str) and re.search(u'[Ѐ-ӿ]', v))}


# 地圖原文裡用英文縮寫寫的屬性（+250 HP, +3 HP regen…）；沒有俄文所以對照表抓不到
_LAT = [('HP regen', '生命恢復'), ('MP regen', '魔力恢復'), ('atk speed', '攻擊速度'), ('move speed', '移動速度'),
        ('all stats', '全屬性'), ('main stat', '主屬性'), ('HP', '生命值'), ('MP', '魔力值'), ('int', '智力'),
        ('agi', '敏捷'), ('str', '力量'), ('atk', '攻擊力'), ('armor', '防禦力')]
_LATRX = re.compile(r'(?<![\w.])([+-]?\d+(?:\.\d+)?%?)\s+(' + '|'.join(re.escape(a) for a, _ in _LAT) + r')\b')
_LATZH = dict(_LAT)


def latin_stats(v):
    if not _LATRX.search(v):
        return None
    z = _LATRX.sub(lambda m: '%s %s' % (m.group(1), _LATZH[m.group(2)]), v)
    z = re.sub(r'(?<=[\u4e00-\u9fff])\s*,\s*(?=[+-]?\d)', '、', z)
    return z


# 「點」後面直接接中文的是真的點數（每 100 點技能強度、每 500 點當前魔力），不換
_COUNT = re.compile(r'(數量：(?:(?!\|n|\n|\r).){0,30}?\d+(?:\.\d+)?)\s*點(?![一-鿿])')

class Translator(object):
    def __init__(self, J_new=None, J_230=None):
        self.tm = []                                   # [(名稱, dict)] 依優先序
        man = {}
        for f in sorted(os.listdir(BASE)):
            if f.startswith('ud_tm_manual') and f.endswith('.json'):
                man.update(_load(f))
        # 各對照表的鍵本身已經是模板（數字已換成 {0}），只做同形字母還原，不能再模板化一次
        self.tm.append(('手動', {norm(k): v for k, v in man.items()}))
        self.tm.append(('網站', _load('ud_tm_site.json')))
        if USE_230:
            self.tm.append(('2.3.0', {norm(k): v for k, v in _load('ud_tm_230.json').items()}))
        if USE_230 and J_new and J_230:
            self.tm.append(('2.3.0腳本', self._align_jass(J_new, J_230)))
        self.used = collections.Counter()
        self.missing = collections.Counter()
        # 一致性修正：2.3.0 的舊譯名 → 網站譯名（只在俄文原文提到該名稱時才換）
        from ud_gloss import glossary
        t230 = self.tm[2][1] if USE_230 else {}
        self.rename = []
        for ru, (zh, kind) in glossary().items():
            old = t230.get(ru)
            if old and old != zh and len(old) >= 2 and not re.search(r'\{\d+\}', old):
                pat = re.compile(r'(?<!\w)%s(?!\w)' % re.escape(ru.lower()))
                self.rename.append((pat, old, zh))
        self.rename.sort(key=lambda r: -len(r[1]))
        self.renamed = 0

    def _fix_names(self, ru, zh):
        low = norm(ru).lower()
        for pat, old, new in self.rename:
            if old in zh and pat.search(low):
                zh = zh.replace(old, new)
                self.renamed += 1
        return zh

    @staticmethod
    def _align_jass(Jn, Jz):
        """同名函式裡，含俄文／含中文的字串依序配對，結構與數字都對得上才收。"""
        def funcs(J):
            return {m.group(1): m.group(0) for m in
                    re.finditer(r'^function (\w+) takes.*?^endfunction', J, re.M | re.S)}
        Fn, Fz = funcs(Jn), funcs(Jz)
        tm = {}
        for name, body in Fn.items():
            if name not in Fz:
                continue
            a = [s for s in re.findall(r'"((?:[^"\\]|\\.)*)"', body) if needs(s)]
            b = [s for s in re.findall(r'"((?:[^"\\]|\\.)*)"', Fz[name]) if re.search(r'[一-鿿]', s)]
            if not a or len(a) != len(b):
                continue
            for x, y in zip(a, b):
                pr = align(x, zhconv.convert(y, 'zh-tw'))
                for ta, tb in pr or []:
                    tm.setdefault(ta, tb)
        return tm

    def seg(self, t, strict=False):
        lead, tpl, nums, trail = template(t)
        for name, d in self.tm:
            if strict and name.startswith('2.3.0'):
                continue                      # 道具：只用依新版俄文翻的來源
            if tpl in d:
                self.used[name] += 1
                z = fill(d[tpl], nums)
                if name.startswith('2.3.0'):
                    z = self._fix_names(t, z)
                z = latin_stats(z) or z
                z = ud_termfix.fix(t, z)
                return lead + z + trail
        self.missing[tpl] += 1
        return None

    def __call__(self, s, strict=False):
        """整段翻譯；有片段查不到時，那個片段保留原文（其餘照翻）。
        strict=True：不用 2.3.0 的譯法（道具說明，避免沿用舊版效果）。"""
        if not needs(s):
            z = latin_stats(s)
            if z is not None:
                self.used['英文屬性'] += 1
            return z
        out, miss = [], 0
        for k, v in split(s):
            if k == 'txt' and needs(v):
                z = self.seg(v, strict)
                if z is None:
                    miss += 1; out.append(v)
                else:
                    out.append(z)
            elif k == 'txt' and latin_stats(v) is not None:
                self.used['英文屬性'] += 1
                out.append(latin_stats(v))
            else:
                out.append(v)
        # 「X數量：」後面的「N 點」是個數，不是點數（標籤與數值是分開的片段，對照表分不出來）
        return _COUNT.sub(r'\1 個', ''.join(out))


# 這些行裡的字串是程式邏輯（聊天指令、名稱比對、字串運算），翻了會壞
LOGIC = re.compile(r'TriggerRegisterPlayerChatEvent|==|!=|SubString|StringHash|StringCase|'
                   r'GetEventPlayerChatString|StringLength|ExecuteFunc|Preload|SaveStr|LoadStr')


def jass_strings(J, tr):
    """把腳本裡含俄文、給玩家看的字串常值翻掉。JASS 字串裡的 \\" 與 \\\\ 要維持跳脫。"""
    n, skipped = [0], [0]

    def rep(m):
        raw = m.group(1)
        txt = raw.replace('\\\\', '\x00').replace('\\"', '"').replace('\x00', '\\')
        z = tr(txt)
        if z is None:
            return m.group(0)
        n[0] += 1
        # \n \r \t 是原文就寫在字串裡的 JASS 跳脫序列，保持原樣；其他反斜線才加倍
        z = re.sub(r'\\(?![nrt])', r'\\\\', z).replace('"', '\\"')
        return '"' + z + '"'

    out = []
    for line in J.split('\n'):
        if '"' in line and LOGIC.search(line):
            if needs(line):
                skipped[0] += 1
            out.append(line)
        else:
            out.append(re.sub(r'"((?:[^"\\]|\\.)*)"', rep, line))
    return '\n'.join(out), n[0], skipped[0]


def wts_strings(data, tr):
    txt = data.decode('utf-8', 'replace')
    n = [0]

    def rep(m):
        z = tr(m.group(2))
        if z is None:
            return m.group(0)
        n[0] += 1
        return m.group(1) + z + m.group(3)
    out = re.sub(r'(STRING \d+\s*(?://[^\n]*\n\s*)?\{\r?\n)(.*?)(\r?\n\})', rep, txt, flags=re.S)
    return out.encode('utf-8'), n[0]
