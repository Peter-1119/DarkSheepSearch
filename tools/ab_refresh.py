# -*- coding: utf-8 -*-
"""依目前地圖（version.json 的 map_file）更新 ab_db.json 的道具效果文字。

- 原文沒變的條目：保留原本的中文
- 新增／原文有變的條目：用地圖中文化的同一套對照表（tools/ud_merge）翻譯，再套統一名詞
- SITE_FIX：說明與實際程式不符的地方，改成實際效果（與地圖 ud_itemfix 一致）

    python ab_refresh.py        之後跑 build.ps1
"""
import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'ud_merge'))
sys.stdout.reconfigure(encoding='utf-8')
import map_items
import ud_translate
from site_terms import with_ru

LAB = [('Способности', '能力'), ('Способность', '能力'), ('Споссобности', '能力'),
       ('Модификатор', '觸發效果'), ('Множитель', '倍增'),
       ('Задание', '任務'), ('Особенность', '特性'), ('Аура', '光環'),
       ('Уникальная способность', '獨特能力'), ('Уникальный модификатор', '獨特觸發效果'),
       ('Уникальная особенность', '獨特特性'), ('Негативные эффекты', '負面'),
       ('Шанс получения', '機率'), ('Шанс создания', '機率')]

_RUNE = ('在{c}旁（{c}周圍約 190×190 的範圍內）使用：敵人的成長等級 −1。僅限黑暗墓地；敵人約每 80 秒成長 1 級。'
         '每成長 1 級，之後出現的等級 0-4 敵方單位生命值 +10%、魔力 +5%、攻擊力 +（該單位的成長攻擊值）；敵方建築生命值 +10%。'
         '等級 5 以上的敵人另外按「成長等級 ÷ 2」計算，符文不會降低這部分；已在場上的敵人也不受影響。在其他地點使用沒有效果，符文會留著。')
# (道具 ID, 標籤) → 改成的中文；('+', 標籤, 中文) 表示另外加一條
SITE_FIX = {
    'axas': [('能力', '獲得等同穿透值 75% 的反彈傷害（每 0.5 秒更新）。'),
             ('+', '觸發效果', '每 4 秒，英雄被攻擊時對攻擊者造成（300% 敏捷）點傷害，並有 50% 機率使其暈眩 4 秒。')],
    'whwd': [('能力', '使用時完全恢復生命值與魔力值，並移除英雄身上的所有負面效果。冷卻時間 90 秒。')],
    'I01D': [('能力', _RUNE.format(c='金色水晶'))],
    'I01E': [('能力', _RUNE.format(c='紅色水晶'))],
    'I01F': [('能力', _RUNE.format(c='藍色水晶'))],
    'I01G': [('能力', _RUNE.format(c='綠色水晶'))],
}


def norm(s):
    s = re.sub(r'\s+', ' ', s or '').strip().rstrip('.')
    return s.replace('НР', 'HP').replace('МР', 'MP').lower()


def main():
    mapf = json.load(open(os.path.join(HERE, 'version.json'), encoding='utf-8'))['map_file']
    DB = map_items.load(mapf)
    p = os.path.join(HERE, 'ab_db.json')
    old = json.load(open(p, encoding='utf-8'))
    TR = ud_translate.Translator()
    out, kept, tr, miss = {}, 0, 0, []
    for iid in sorted(DB):
        r = DB[iid]
        parts = []
        for key, lab in LAB:
            v = r['fields'].get(key)
            if isinstance(v, str) and v.strip() and v.strip() != '-':
                parts.append([lab, v.strip()])
        for e in r.get('extra') or ([r['fields']['_']] if isinstance(r['fields'].get('_'), str) else []):
            if e and e.strip():
                parts.append(['說明', e.strip()])
        if not parts:
            continue
        prev = {norm(ru): zh for (lab, ru), zh in zip(old.get(iid, {}).get('parts', []), old.get(iid, {}).get('zh', []))}
        zh = []
        for lab, ru in parts:
            if norm(ru) in prev and prev[norm(ru)]:
                zh.append(prev[norm(ru)]); kept += 1
            else:
                z = TR(ru, strict=True)
                if z is None or re.search(r'[Ѐ-ӿ]', z):
                    miss.append((iid, ru))
                    z = None
                else:
                    z = with_ru(ru, z); tr += 1
                zh.append(z)
        for fx in SITE_FIX.get(iid, []):
            if fx[0] == '+':
                parts.append([fx[1], '']); zh.append(fx[2])
            else:
                hit = [k for k, (lab, _) in enumerate(parts) if lab == fx[0]]
                assert hit, (iid, fx[0])
                zh[hit[0]] = fx[1]
        out[iid] = {'parts': parts, 'zh': zh}
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    open(p, 'w', encoding='utf-8').write(txt + '\n')
    print('道具效果 %d 件；沿用舊譯 %d 條、新翻 %d 條、未譯 %d 條' % (len(out), kept, tr, len(miss)))
    for m in miss:
        print('  未譯', m[0], m[1][:80])


if __name__ == '__main__':
    main()
