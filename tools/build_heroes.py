# -*- coding: utf-8 -*-
"""產生 data/heroes.json：英雄資料 + 與裝備的連結。

資料全部來自 UD_v3.81 地圖本體：
  單位/技能定義 -> war3map.w3u / war3map.w3a
  可選名單、主屬性、解鎖門檻 -> war3map.j 的 Random* 函式
  「這個英雄的技能吃不吃裝備技能威力」-> 直接看該技能的 JASS 有沒有讀 real key 18

連結的作法：從技能文字掃出機制關鍵字，對應到網站既有的屬性代碼，
讓英雄頁可以直接跳到「這個英雄該找的裝備」。
"""
import os, re, sys, json, io

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import map_heroes
from mpq import MPQ

MAP = sys.argv[1] if len(sys.argv) > 1 else json.load(
    io.open(os.path.join(HERE, 'version.json'), encoding='utf-8')).get('map_file')

# 技能文字裡的機制關鍵字 -> (網站屬性代碼, 狀態代碼)
# 屬性代碼取自 stat_values.META，狀態代碼取自 status.json。
MECH = [
    ('sp',     None,     r'сил[аыу] умений'),
    ('mod',    None,     r'сил[аыу] модификатор'),
    ('as',     None,     r'скорост[ьи] атаки'),
    ('armor',  None,     r'\bброн|защит[аыу]\b'),
    ('hp',     None,     r'запас[а]? здоровья|ед\. здоровья'),
    ('mp',     None,     r'\bман[аыу]\b|ед\. маны'),
    ('pen',    None,     r'пробити'),
    ('thorn',  None,     r'ответн\w+ урон'),
    ('vamp',   None,     r'вампириз'),
    ('dburn',  'burn',   r'поджог|подожж'),
    ('dbleed', 'bleed',  r'кровотеч'),
    ('ddise',  'disease', r'болезн|заболе'),
    (None,     'flam',   r'горюч'),
    (None,     'freeze', r'заморозк|заморож'),
    (None,     'shock',  r'\bшок\b|шоком|шока'),
    (None,     'curse',  r'проклят'),
    (None,     'weak',   r'слабост'),
    (None,     'vuln',   r'уязвим'),
]


def mechanics(hero):
    """回傳 (屬性代碼集合, 狀態代碼集合)。"""
    txt = ' '.join(a['name_ru'] + ' ' + a['text_ru']
                   for a in hero['abilities']).lower()
    stats, sts = [], []
    for code, st, pat in MECH:
        if re.search(pat, txt):
            if code and code not in stats:
                stats.append(code)
            if st and st not in sts:
                sts.append(st)
    return stats, sts


def scaling(heroes, jass):
    """哪些英雄的技能真的吃裝備技能威力 / 技能強度（讀原始碼判斷）。"""
    lines = jass.split('\n')
    fn, cur = [], '?'
    for l in lines:
        m = re.match(r'function ([A-Za-z0-9_]+) ', l)
        if m:
            cur = m.group(1)
        fn.append(cur)
    use_mod, use_sp = set(), set()
    where = {}
    for i, l in enumerate(lines):
        if re.search(r'LoadReal\(hash,[A-Za-z_0-9()]+,18\)', l):
            use_mod.add(fn[i])
        if 'udg_ItemBonusDMG' in l:
            use_sp.add(fn[i])
        for a in re.findall(r"'(A[A-Za-z0-9]{3})'", l):
            where.setdefault(a, set()).add(fn[i])
    out = {}
    for uid, h in heroes.items():
        mod = [a['id'] for a in h['abilities'] if where.get(a['id'], set()) & use_mod]
        sp = [a['id'] for a in h['abilities'] if where.get(a['id'], set()) & use_sp]
        out[uid] = {'mod': mod, 'sp': sp}
    return out


def main():
    tr = json.load(io.open(os.path.join(HERE, 'heroes_zh.json'), encoding='utf-8'))
    AB = json.load(io.open(os.path.join(HERE, 'abilities_zh.json'),
                           encoding='utf-8'))['names']
    # 技能說明的翻譯（技能ID -> [中文, 英文]）；沒翻到的就三語都放俄文原文
    _tp = os.path.join(HERE, 'abilities_text_zh.json')
    TXT = json.load(io.open(_tp, encoding='utf-8'))['text']           if os.path.isfile(_tp) else {}
    # 天賦／技能書選項的翻譯（技能ID -> {n:[zh,en], t:[zh,en]}）
    _lp = os.path.join(HERE, 'talents_zh.json')
    TAL = json.load(io.open(_lp, encoding='utf-8'))['talents']           if os.path.isfile(_lp) else {}

    def tri_name(a):
        """技能名稱三語。天賦另有自己的翻譯表，優先採用。"""
        if a['id'] in TAL:
            return TAL[a['id']]['n'] + [a['name_ru']]
        if a['name_ru'] in AB:
            return AB[a['name_ru']] + [a['name_ru']]
        return [a['name_ru']] * 3

    def tri_text(a):
        if a['id'] in TAL:
            return TAL[a['id']]['t'] + [a['text_ru']]
        if a['id'] in TXT:
            return TXT[a['id']] + [a['text_ru']]
        return [a['text_ru']] * 3
    H = map_heroes.load(MAP)
    jass = MPQ(MAP).read('war3map.j').decode('utf-8', 'replace')
    scale = scaling(H, jass)

    V = tr['vocab']
    names, descs = tr['names'], tr['desc']
    out = []
    for uid in sorted(H, key=lambda k: (H[k]['attr'] or 'zz', H[k]['unlock'] or 0,
                                        names.get(k, [''])[0])):
        h = H[uid]
        p = h['profile_ru']
        stats, sts = mechanics(h)
        nm = names.get(uid)
        if not nm:
            nm = [h['name_ru'], h['name_ru']]
        roles = [r.strip() for r in (p.get('role') or '').split(',') if r.strip()]

        def tri(table, key, fallback=None):
            v = table.get(key)
            return [v[0], v[1], key] if v else [fallback or key] * 3

        rec = {
            'id': uid,
            'n': [nm[0], nm[1], h['name_ru']],
            'attr': h['attr'] or 'int',      # 只有樹人長者沒被列進三個屬性池
            'unlock': h['unlock'] or 0,
            'random': h['random'],           # False = 不在隨機池，只能手動挑
            'author': p.get('author'),       # 玩家投稿英雄的作者
            'icon': 'images/heroes/h_%s.png' % uid,
            'proper': h['proper_ru'],
            'st': h['stats'],
            'roles': [tri(V['role'], r) for r in roles],
            'sc': [stats, sts],              # 連到裝備用的
            'mod': scale[uid]['mod'],        # 吃裝備技能威力的技能
            'sp': scale[uid]['sp'],          # 吃技能強度的技能
            # kind: 'hero' = QWER 可升級技能；'innate' = 固有技能（被動／專屬機制／天賦入口）
            'ab': [{
                'id': a['id'],
                'kind': a['kind'],
                'n': tri_name(a),
                'k': a['hotkey'],
                'lv': a['levels'],
                # 說明三語；未翻譯的用俄文原文墊著
                't': tri_text(a),
                'icon': 'images/heroes/a_%s.png' % a['id'],
                # 技能書的選項（每個英雄可選的天賦都不一樣）
                **({'opts': [{
                    'id': o['id'],
                    'n': tri_name(o),
                    't': tri_text(o),
                    'icon': 'images/heroes/a_%s.png' % o['id'],
                } for o in a['opts']]} if a.get('opts') else {}),
            } for a in h['abilities'] if a['name_ru']],
        }
        if p.get('tier'):
            rec['tier'] = tri(V['tier'], p['tier'])
        if p.get('late'):
            rec['late'] = tri(V['late'], p['late'])
        d = descs.get(uid)
        rec['d'] = [d[0], d[1], p.get('desc') or p.get('trait') or ''] if d else \
                   [p.get('desc') or '', p.get('desc') or '', p.get('desc') or '']
        out.append(rec)

    have = sum(1 for r in out
               if os.path.isfile(os.path.join(ROOT, r['icon'])))
    path = os.path.join(ROOT, 'data', 'heroes.json')
    json.dump({'heroes': out}, io.open(path, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print('英雄 %d 個 -> %s (%d KB)' % (len(out), path,
                                        os.path.getsize(path) // 1024))
    print('  有圖示 %d ／ 有強度等級 %d ／ 有中文名 %d' % (
        have, sum(1 for r in out if 'tier' in r),
        sum(1 for r in out if r['id'] in names)))
    untr = sorted({a['n'][2] for r in out for a in r['ab'] if a['n'][0] == a['n'][2]})
    if untr:
        print('  技能名稱未翻譯：%d 個 %s' % (len(untr), untr[:6]))
    ab = [a for r in out for a in r['ab']]
    print('  技能 %d 個（英雄技能 %d ／ 固有 %d），吃裝備技能威力的英雄 %d 個' % (
        len(ab), sum(1 for a in ab if a['kind'] == 'hero'),
        sum(1 for a in ab if a['kind'] == 'innate'),
        sum(1 for r in out if r['mod'])))
    print('  只能手動挑的英雄 %d 個；玩家投稿 %d 個' % (
        sum(1 for r in out if not r['random']),
        sum(1 for r in out if r.get('author'))))
    notxt = sum(1 for a in ab if not a['t'][2])
    opts = [o for a in ab for o in a.get('opts', [])]
    print('  技能書 %d 個，內含天賦／選項 %d 個（不重複 %d 個）' % (
        sum(1 for a in ab if a.get('opts')), len(opts), len({o['id'] for o in opts})))
    untr = sum(1 for a in ab if a['t'][2] and a['t'][0] == a['t'][2])
    print('  技能說明：%d 個有原文（%d 個沒有）；其中 %d 個尚未翻譯' % (
        len(ab) - notxt, notxt, untr))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
