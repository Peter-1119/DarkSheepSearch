# -*- coding: utf-8 -*-
"""產生 data/dossier/_items.md：配裝用的道具速查表。

agent 設計配裝時需要「哪些道具給什麼」，以前要自己讀 data/items.json
（474 件、含三語與合成關係，很大）。這裡只留配裝真正會用到的欄位，
並且**先照取得難度篩掉拿不到的**，再依稀有度分組排序。

同時附上「屬性排行榜」—— 每個關鍵屬性的前幾名是誰，
這是挑裝備時最常問的問題。
"""
import io, json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.stdout.reconfigure(encoding='utf-8')

OUT = os.path.join(ROOT, 'data', 'dossier', '_items.md')

# 跟 check_build.py 一致的取得難度篩選
BAN = {'新年', '復活節', '萬聖節', '儀式', '完美', '特殊（lv.5++）'}
# 這些類別對配裝沒有意義，不列
SKIP = {'消耗品／掉落物', '任務物品（2/2）', '任務物品（1/2）', '信使'}

MULTIPLIER = {'ckng', 'tfar', 'oven', 'kysn', 'jpnt', 'moon',
              'I0A8', 'I01P', 'I00B', 'I078'}
EARRING = {'I00E', 'I00F', 'I00O', 'I00P', 'I00Q'}

# 排行榜要列的屬性
RANK = [('sp', '技能強度'), ('atk', '攻擊力'), ('as', '攻擊速度'),
        ('hp', '生命值'), ('mp', '法力值'), ('armor', '護甲'),
        ('str', '力量'), ('agi', '敏捷'), ('int', '智力'), ('all', '全屬性'),
        ('pen', '穿透'), ('thorn', '反傷'), ('vamp', '吸血'),
        ('mod', '裝備技能威力'), ('cdmod', '裝備技能冷卻'),
        ('dburn', '點燃傷害'), ('dstat', '狀態傷害'),
        ('hpreg', '生命回復'), ('mpreg', '法力回復'), ('ms', '移動速度')]


def main():
    D = json.load(io.open(os.path.join(ROOT, 'data', 'items.json'),
                          encoding='utf-8'))['items']
    S = json.load(io.open(os.path.join(ROOT, 'data', 'site.json'),
                          encoding='utf-8'))
    IT = S['items']
    META = {m['k']: m for m in S['stats']}
    groups = [g['zh'] for g in S['groups']]

    ok = {i: v for i, v in D.items()
          if v['group'] not in BAN and v['group'] not in SKIP}

    L = ['# 道具速查（配裝用）', '',
         '只列**取得範圍內**的道具：已排除 新年／復活節／萬聖節／儀式（要盜賊）、',
         '完美（要鐵匠）、特殊 lv.5++（幾乎抽不到），以及消耗品與任務物品。',
         '共 %d 件。完整資料在 `data/items.json`。' % len(ok), '',
         '驗配裝用 `python tools/check_build.py --file <你的檔案>`，',
         '或直接 `python tools/check_build.py 星界耳環 純淨紫水晶 …`（接中文名或 ID）。', '',
         '---', '', '## 屬性排行榜', '',
         '挑裝備最常問的問題：某個屬性最高的是誰。各列前 12 名。', '']

    for k, lab in RANK:
        # 裝備技能冷卻是負值越好，排序要反過來
        rows = sorted(((v['v'][k], i) for i, v in IT.items()
                       if i in ok and (v.get('v') or {}).get(k)),
                      reverse=(k != 'cdmod'))
        if not rows:
            continue
        pct = '%' if META.get(k, {}).get('pct') else ''
        top = ['%s %+g%s（%s%s）' % (D[i]['name'], val, pct, D[i]['group'],
                                    '，%d金' % D[i]['gold'] if D[i].get('gold') else '')
               for val, i in rows[:12]]
        L.append('- **%s**：%s' % (lab, ' ／ '.join(top)))
    L += ['', '---', '', '## 硬性規則', '',
          '- 6 個正常欄位（**幽魂之狼／烈焰領主／機械戰體只有 4 格**），',
          '  另加兩個不佔格的：`s1` 吸收器放一件「特殊（lv.1）」、',
          '  `s2` 祕密寶盒隨機生成一件「特殊（lv.2）」',
          '- 同一件神器最多 1 個（鐵匠可複製其中 1 件 → 最多 1 件能出現兩次）',
          '- **耳環最多 1 件**：%s' % '、'.join(D[i]['name'] for i in EARRING if i in D),
          '- **乘算器最多 1 件**（違反時裝備會被退回地上）：%s'
          % '、'.join(D[i]['name'] for i in MULTIPLIER if i in D),
          '- 每套最多 1 件「特殊（lv.5+）」', '', '---', '', '## 依稀有度分組', '']

    by = collections.defaultdict(list)
    for i, v in ok.items():
        by[v['group']].append(i)
    for g in groups:
        ids = by.get(g)
        if not ids:
            continue
        L += ['', '### %s（%d 件）' % (g, len(ids)), '',
              '| ID | 名稱 | 金幣 | 屬性 | 效果 |', '|---|---|---|---|---|']
        for i in sorted(ids, key=lambda x: -(D[x].get('gold') or 0)):
            v = D[i]
            eff = ' ｜ '.join((e['zh'] or '').replace('\n', ' ')
                             for e in (v.get('effects') or []))
            note = []
            if i in EARRING:
                note.append('耳環欄')
            if i in MULTIPLIER:
                note.append('乘算器欄')
            L.append('| `%s` | %s%s | %s | %s | %s |' % (
                i, v['name'], '（%s）' % '、'.join(note) if note else '',
                v.get('gold') or '-', (v.get('stats') or '-').replace('|', '/'),
                eff.replace('|', '/') or '-'))

    doc = '\n'.join(L) + '\n'
    d = os.path.dirname(OUT)
    if not os.path.isdir(d):
        os.makedirs(d)
    io.open(OUT, 'w', encoding='utf-8').write(doc)
    print('道具速查 -> %s（%d 件，%.0f KB）'
          % (os.path.relpath(OUT, ROOT), len(ok), len(doc.encode('utf-8')) / 1024))


if __name__ == '__main__':
    main()
