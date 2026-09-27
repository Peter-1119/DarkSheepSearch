# -*- coding: utf-8 -*-
"""把網站的中文來源檔換成統一名詞（與地圖 tools/ud_merge 用同一套規則）。

    python site_terms.py          實際改寫
    python site_terms.py -n       只統計、不寫檔

有俄文原文的地方用 ud_termfix.fix(俄文, 中文)——依原文判斷，跟地圖完全一致；
沒有俄文的（攻略、配裝說明）只做不需要上下文就一定正確的替換（NO_RU）。
改完跑 build.ps1 重新產生網站。
"""
import sys, os, re, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'ud_merge'))
sys.stdout.reconfigure(encoding='utf-8')
import ud_termfix
from ud_termfix import _C
import mpq, w3obj

DRY = '-n' in sys.argv
MAP = json.load(open(os.path.join(HERE, 'version.json'), encoding='utf-8'))['map_file']

# 不需要上下文的替換：一律成立的用字與專有名詞
NO_RU = [
    (r'回復', '恢復'),
    (r'MOD\s*強度|裝備技能威力|MOD威力|裝備效果強度', '觸發效果強度'),
    (r'MOD\s*冷卻|裝備技能冷卻|裝備效果冷卻', '觸發效果冷卻'),
    (r'(?<![A-Za-z])MOD(?![A-Za-z])|裝備效果|裝備技能', '觸發效果'),
    (r'反擊傷害', '反彈傷害'),
    (r'反傷加成|反傷強化', '反彈傷害提升'),
    (r'免疫反傷|反傷免疫', '免疫反彈傷害'),
    (r'反傷', '反彈傷害'),
    (r'電擊', '震擊'),
    (r'星辰物質', '星塵'),
    (r'法力依存|魔法渴求', '魔力成癮'),
    (r'法力', '魔力'),
    (r'射程', '攻擊距離'),
    (r'存活時間', '持續時間'),
    (r'抵抗點燃', '點燃抗性'),
    (r'抵抗易燃', '易燃抗性'),
    # 英雄、技能、單位名稱（朋友的名詞表）
    (r'黑暗女獵手|黑暗獵手', '黑暗遊俠'),
    (r'聖武士', '聖騎士'),
    (r'劍聖', '刀鋒大師'),
    (r'女獵手', '女獵人'),
    (r'守衛塔', '箭塔'),
    (r'瞭望塔', '箭塔'),
    (r'秘法學者|奧術學者', '奧術師'),
    (r'恩澤|聖恩', '聖光術'),
    (r'統兵官', '戰爭統帥'),
    (r'(?<!萊特林)鼠人', '萊特林人'),
    (r'切口', '割裂'),
    (r'致命切割', '致命割裂'),
    (r'螢火蟲', '小精靈'),
    (r'弩砲手', '弩車'),
    (r'神射手', '火槍先鋒'),
    (r'惡魔獵手', '惡魔獵人'),
    (r'幽魂之狼', '幽魂狼'),
    (r'魅惑', '咒印'),
    (r'巫術之箭', '巫術箭'),
    (r'黑水之刃', '暗水之刃'),
    (r'穢物', '憎惡'),
    (r'機甲兵', '機械戰體'),
    (r'(?<=暗影|灼燒|火焰|風暴|吸收|吸血|治癒)(?:法球|之球)', '球體'),
    (r'預言者寶珠', '預言者球體'),
    (r'五行吊墜', '防禦吊墜'),
    (r'熔岩球(?!體)', '熔岩球體'),
    (r'聖武', '聖騎'),
    (r'護甲類型', '防禦類型'),
    (r'(?<!寒冰|秘銀|骨質|冰霜)護甲(?!類型)', '防禦力'),
    (r'防禦力力', '防禦力'),
    (r'球體體', '球體'),
    (r'冷卻時間時間', '冷卻時間'),
]
NO_RU_C = [(re.compile(a), b) for a, b in NO_RU]


def no_ru(zh):
    for rx, b in NO_RU_C:
        zh = rx.sub(b, zh)
    return zh


def with_ru(ru, zh):
    zh = ud_termfix.fix(ru or '', zh)
    return no_ru(zh)


stat = collections.Counter()


def walk(obj, fn, path=''):
    """把 obj 裡的中文字串都丟給 fn(path, s)。"""
    if isinstance(obj, dict):
        return {k: walk(v, fn, path + '/' + str(k)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk(v, fn, path + '/' + str(i)) for i, v in enumerate(obj)]
    if isinstance(obj, str) and re.search(r'[一-鿿]', obj):
        n = fn(path, obj)
        if n != obj:
            stat[path.split('/')[1] if '/' in path else path] += 1
        return n
    return obj


def _pairs(a, b, out):
    if isinstance(a, dict):
        for k in a:
            _pairs(a[k], b[k], out)
    elif isinstance(a, list):
        for x, y in zip(a, b):
            _pairs(x, y, out)
    elif isinstance(a, str) and a != b:
        out[a] = b


def save(name, data, before):
    """只替換有改動的字串，保留原檔排版，差異才看得清楚。"""
    pairs = {}
    _pairs(json.loads(before), data, pairs)
    print('%-24s %d 個字串改動' % (name, len(pairs)))
    if not pairs or DRY:
        return
    p = os.path.join(HERE, name)
    text = open(p, encoding='utf-8').read()
    for old, new in sorted(pairs.items(), key=lambda kv: -len(kv[0])):
        eo, en = json.dumps(old, ensure_ascii=False), json.dumps(new, ensure_ascii=False)
        assert eo in text, (name, old[:40])
        text = text.replace(eo, en)
    assert json.loads(text) == data, name
    open(p, 'w', encoding='utf-8').write(text)


def load(name):
    t = open(os.path.join(HERE, name), encoding='utf-8').read()
    return json.loads(t), json.dumps(json.loads(t), ensure_ascii=False)


if __name__ == '__main__':
    # 地圖（網站依據的版本）裡的俄文，當作沒有俄文欄位的檔案的上下文
    M = mpq.MPQ(MAP)
    A = w3obj.parse(M.read('war3map.w3a'), True)
    U = w3obj.parse(M.read('war3map.w3u'), False)
    T = w3obj.parse(M.read('war3map.w3t'), False)


    def txt(v):
        if isinstance(v, list):
            return ' '.join(str(x) for x in v if x)
        return str(v or '')


    def ru_of(oid):
        for D, fields in ((A, ('anam', 'atp1', 'aub1', 'arut', 'aret')), (U, ('unam', 'upro', 'utub', 'utip')),
                          (T, ('unam', 'ides', 'utub'))):
            if oid in D:
                return ' '.join(txt(D[oid].get(f)) for f in fields)
        return ''


    # 1. 道具效果（有俄文）
    d, b = load('ab_db.json')
    for k, v in d.items():
        if isinstance(v, dict) and 'zh' in v:
            ru = ' '.join(p[1] for p in v.get('parts', []))
            v['zh'] = [with_ru(ru, z) for z in v['zh']]
    save('ab_db.json', d, b)

    # 2. 技能名稱（鍵是俄文）
    d, b = load('abilities_zh.json')
    for k, v in d.get('names', {}).items():
        v[0] = with_ru(k, v[0])
    save('abilities_zh.json', d, b)

    # 3. 技能說明、天賦（依 ID 取地圖俄文）
    for name, key in (('abilities_text_zh.json', 'text'), ('talents_zh.json', 'talents')):
        d, b = load(name)
        for k, v in d.get(key, {}).items():
            ru = ru_of(k)
            if isinstance(v, list):
                v[0] = with_ru(ru, v[0])
            elif isinstance(v, dict):
                for f in ('n', 't'):
                    if f in v and v[f]:
                        v[f][0] = with_ru(ru, v[f][0])
        save(name, d, b)

    # 4. 英雄與名稱表
    d, b = load('heroes_zh.json')
    d = walk(d, lambda p, s: with_ru(ru_of(p.split('/')[2]) if p.startswith('/names/') else '', s))
    save('heroes_zh.json', d, b)

    # 5. 道具名稱（依 ID 取地圖俄文）
    d, b = load('names2.json')
    d = {k: with_ru(ru_of(k), v) for k, v in d.items()}
    save('names2.json', d, b)

    # 6. 狀態、套裝（有俄文）
    for name in ('status.json', 'set_bonus.json'):
        d, b = load(name)

        def fn(p, s, _d=d):
            node = _d
            parts = [x for x in p.split('/') if x]
            for x in parts[:-1]:
                node = node[int(x)] if isinstance(node, list) else node[x]
            ru = ''
            if isinstance(node, dict) and 'ru' in node:
                ru = node['ru']
            elif isinstance(node, list) and len(node) >= 3 and isinstance(node[2], str):
                ru = node[2]
            return with_ru(ru, s)
        d = walk(d, fn)
        save(name, d, b)

    # 7. 配裝、攻略（沒有俄文）
    for name in ('hero_builds.json', 'builds.json', 'gacha.json'):
        d, b = load(name)
        d = walk(d, lambda p, s: no_ru(s))
        save(name, d, b)

    print('字串改動：', dict(stat))
