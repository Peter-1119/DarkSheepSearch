# -*- coding: utf-8 -*-
"""直接從 .w3x 地圖檔讀出道具資料。

以前的流程要人工從地圖編輯器匯出，這支改成直接讀地圖，
以後改版只要換一個 .w3x 就好。

地圖的說明文字被混入了拉丁同形字（Kлacc、Ocoбый、ceк…），
純粹是為了讓文字搜尋失效，所以要先正規化回西里爾文再解析。
"""
import re, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpq import MPQ
import w3obj

# 拉丁 -> 西里爾同形字。這 17 對是從地圖文字實際統計出來的，
# 剝掉顏色碼之後沒有其他拉丁字母混在西里爾詞裡。
HOMO_PAIRS = {
    'o': 'о', 'e': 'е', 'a': 'а', 'p': 'р', 'c': 'с', 'y': 'у', 'x': 'х',
    'C': 'С', 'O': 'О', 'M': 'М', 'K': 'К', 'P': 'Р', 'B': 'В', 'A': 'А',
    'H': 'Н', 'T': 'Т', 'X': 'Х',
}
HOMO = str.maketrans(HOMO_PAIRS)
COLOUR = re.compile(r'\|c[0-9A-Fa-f]{8}|\|r', re.I)
NEWLINE = re.compile(r'\|n')
CYR = re.compile(r'[Ѐ-ӿ]')


# 這些是說明裡真正的英文縮寫，剛好整個由同形字母組成，不能換
KEEP = {'HP', 'MP'}
_HOMO_SET = set(HOMO_PAIRS)


def _is_ru_token(w):
    """判斷一個詞該不該做同形字還原。

    含西里爾字母 -> 一定是被污染的俄文詞。
    整個詞都由同形字母組成 -> 也是俄文（例如 'yp.' = 'ур.'、'Oco' = 'Осо'）。
    含任何非同形拉丁字母 -> 真英文（regen / armor / atk…），不能動。
    """
    if CYR.search(w):
        return True
    letters = [c for c in w if c.isascii() and c.isalpha()]
    if not letters or ''.join(letters) in KEEP:   # 'HP,' 也要保護，所以只比字母
        return False
    return all(c in _HOMO_SET for c in letters)


def unmix(t):
    if not isinstance(t, str):
        return t
    return ''.join(w.translate(HOMO) if _is_ru_token(w) else w
                   for w in re.split(r'(\s+)', t))


def clean(t):
    """去色碼、換行統一成 \\n、還原同形字。

    地圖文字同時混用 |n 與真正的 CRLF，兩種都要收斂成 \\n，
    否則後面用 re.S 做多行比對時 \\r 會殘留在擷取結果裡。
    """
    if not isinstance(t, str):
        return ''
    t = COLOUR.sub('', t).replace('\r\n', '\n').replace('\r', '\n')
    return unmix(NEWLINE.sub('\n', t)).strip()


# 說明文字的段落標題（正規化之後）
# 從地圖文字實際掃出來的標題，包含地圖自己的錯字 Споссобности。
# 長的要排在短的前面，否則 'Способность' 會先吃掉 'Уникальная способность'。
SECTIONS = ['Уникальная способность', 'Уникальная особенность',
            'Негативные эффекты', 'Шанс создания', 'Шанс получения',
            'Споссобности', 'Способности', 'Способность', 'Особенность',
            'Модификатор', 'Множитель', 'Задание',
            'Класс', 'Бонусы', 'Умение', 'Рецепт', 'Комплект',
            'Время', 'Требования', 'Продажа', 'Цена']
SEC_RE = re.compile(r'^(%s)\s*:\s*' % '|'.join(SECTIONS), re.M)


# 套裝道具的說明尾巴會多一行『Бонусы комплекта "-сN".』。
# 它同時是唯一標明「這件屬於哪一組套裝」的地方，所以要取出來當 Комплект，
# 不能只是刪掉 —— 刪掉的話套裝歸屬就沒了。
SET_HINT = re.compile(r'\s*Бонусы\s+комплекта\s*"?-?[сcС](\d)"?\s*\.?\s*$', re.I)


def split_sections(txt):
    """把 'Класс: … Бонусы: …' 切成 {標題: 內容}。"""
    out, pos = {}, []
    for m in SEC_RE.finditer(txt):
        pos.append((m.start(), m.end(), m.group(1)))
    if not pos:
        return {'_': txt.strip()} if txt.strip() else {}
    if pos[0][0] > 0:
        head = txt[:pos[0][0]].strip()
        if head:
            out['_'] = head
    for i, (s, e, name) in enumerate(pos):
        end = pos[i + 1][0] if i + 1 < len(pos) else len(txt)
        val = txt[e:end].strip()
        if val in ('-', '—', ''):        # 沒有加成的道具寫成 '-'，視為空
            continue
        if name in out:
            out[name] += '\n' + val
        else:
            out[name] = val
    return out


# 內部輔助道具，不是玩家能拿到的東西
SKIP = re.compile(r'^(id\d\d|gold)$')


def load(path):
    """回傳 {道具ID: {...}}，已正規化、已切段。"""
    m = MPQ(path)
    raw = w3obj.parse(m.read('war3map.w3t'))
    out = {}
    for iid, r in raw.items():
        if SKIP.match(iid):
            continue
        name = clean(r.get('unam', ''))
        if not name:
            continue
        body = clean(r.get('utub') or r.get('ides') or '')
        mset = SET_HINT.search(body)
        if mset:
            body = body[:mset.start()].rstrip()
        fields = split_sections(body)
        if mset:
            fields['Комплект'] = 'c' + mset.group(1)
        out[iid] = {
            'id': iid,
            'name_ru': name,
            'gold': r.get('igol'),
            'level': r.get('ilev'),
            'icon': (r.get('iico') or '').strip(),
            'text': body,
            'fields': fields,
            'abilities': [x for x in str(r.get('iabi') or '').split(',') if x],
        }
    return out


if __name__ == '__main__':
    import json, collections
    sys.stdout.reconfigure(encoding='utf-8')
    it = load(sys.argv[1])
    print('道具 %d 件' % len(it))
    sec = collections.Counter()
    for v in it.values():
        sec.update(v['fields'].keys())
    print('段落標題出現次數：')
    for k, n in sec.most_common():
        print('   %-14s %d' % (k, n))
    print()
    print('=== I01M 範例 ===')
    print(json.dumps(it['I01M'], ensure_ascii=False, indent=1))
