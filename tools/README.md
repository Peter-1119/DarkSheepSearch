# tools/ — 資料重建腳本

## 資料流

```
data/items_database.json ─┐
data/icons/              ─┤     ┌─→ data/items.json ─→ 裝備合成攻略.md ＋ images/
synthesis.xlsx           ─┼─────┤
udwiki（僅配方關聯）      ─┤     └─→ data/site.json  ─→ index.html（網站）
人工翻譯 names/ab        ─┘
```

**地圖檔匯出的 `data/items_database.json` 是數值的唯一權威來源。**
Wiki 只用來補「配方／用於」的關聯（地圖物件資料不含配方，配方寫在觸發裡），
其數值已過時，不要拿來覆蓋。

## 重跑順序

```bash
python parse_db.py        # data/items_database.json -> db_items.json
python mk_ab.py           # 比對舊譯文，產生 ab_db.json（未譯的列在 ab_need.json）
python build_data2.py     # 合併全部        -> ../data/items.json ＋ ../images/*.png
python build_md2.py       # 產生文件        -> ../裝備合成攻略.md
python build_site_data.py # 三語資料        -> ../data/site.json
python build_site.py      # 產生網站        -> ../index.html
```

網站是單一 HTML（資料已內嵌），直接雙擊 `index.html` 就能開，不需要伺服器。
設計決策的說明在 `../DESIGN.md`。

Wiki 端（只有想更新配方關聯時才需要）：

```bash
python parse_wiki.py      # pages/*.html -> wiki_items.json
```

xlsx 端（只有換合成表時才需要）：

```bash
python parse_xlsx.py      # 圖片錨點＋中文舊名 -> xlsx_entries.json
python match.py           # 俄→中自動配對      -> match_raw.json
python build_map.py       # 加人工修正         -> name_map.json
python parse_recipes.py   # 合成表 40 條       -> recipes.json
```

## 檔案

| 檔案 | 說明 |
|---|---|
| `parse_db.py` | 解析地圖匯出的道具敘述。處理西里爾／拉丁同形字混寫（`Kлacc`→`Класс`），並把 `Бонусы комплекта "-c1"` 拆成獨立欄位 |
| `check_colour.py` | 拿 xlsx 遊戲截圖當基準，逐張檢查圖示是否 R/B 顛倒 |
| `validate_rule.py` | 驗證「顏色數 > 256 即為顛倒」這條判別規則的準確率 |
| `sheet.py` | 產生對照圖（截圖 / 目前 / 交換後），用眼睛確認 |
| `tr_bonus2.py` | 俄文屬性 → 繁中。簡單屬性走對照表；傷害／防禦走文法解析（`урон/защита` × `не от статусов/от атак и умений/от поджога…` × 目標） |
| `mk_ab.py` | 比對新舊俄文敘述，沿用未變動的譯文，把需要新翻的列出來 |
| `names2.json` | **人工翻譯**：474 件道具的中文名 |
| `ab_db.json` | **人工翻譯**：329 件道具的能力敘述（`parts` 為俄文原文，`zh` 為對應譯文，索引一一對應） |
| `build_data2.py` | 合併全部來源 → `data/items.json`；同時把圖示複製成 `images/<道具ID>.png` |
| `build_md2.py` | 由 `data/items.json` 產生 Markdown |
| `tr_stats.py` | 同上但同時輸出中／英兩種屬性字串（網站用） |
| `names_en.json` | **人工翻譯**：474 件道具的英文名 |
| `ab_en.json` | **人工翻譯**：345 段能力敘述的英文，索引對應 `ab_db.json` 的 `parts` 展平順序 |
| `build_site_data.py` | 產生網站用的三語資料 `data/site.json` |
| `site_template.html` | 網站模板，`__DATA__` 是資料佔位符 |
| `build_site.py` | 把資料內嵌進模板 → `index.html` |
| `name_map.json` | 舊 xlsx 中文名 ↔ 道具 ID 的對照（附圖片來源） |
| `recipes.json` | 舊合成表的 40 條合成路線 |


## 圖示色彩修正（重要）

匯出的 BLP 圖示有兩種來源，解碼路徑不同：

| BLP 內部格式 | 顏色 | 判別方式 |
|---|---|---|
| 調色盤（palettised） | ✅ 正確 | PNG 顏色數 ≤ 256 |
| JPEG 壓縮 | ❌ R/B 顛倒 | PNG 顏色數 > 256 |

`build_data2.py` 的 `load_icon()` 會依顏色數自動判斷並修正，
407 張裡有 **357 張** 需要交換 R/B。

這條規則是拿 `synthesis.xlsx` 的遊戲截圖當基準驗證出來的，
129 個可判定樣本 **全部命中、零誤判**。要重新驗證：

```bash
python check_colour.py    # 逐張比對截圖與圖示的色差
python validate_rule.py   # 驗證「顏色數 > 256」這條規則的準確率
python sheet.py hval,spre,ratf sheet.png   # 產生對照圖：截圖 | 目前 | 交換後
```

**`data/icons/` 保持原始匯出狀態不要改**，修正只發生在產生 `images/` 的時候。

## data/gg 是什麼

854 張 `DISBTN*` / `DISPAS*`，是遊戲中「不可用」狀態的灰暗版圖示，
沒有任何一張正常的 `BTN` 圖，補不了缺的 54 張圖示，已在 `.gitignore` 排除。

缺的那 54 張是地圖直接沿用暴雪內建圖示（`ReplaceableTextures/CommandButtons/…`）
而未被匯出，要補得從 War3 本體的 `War3.mpq` 撈，清單在 `../裝備合成攻略.md` 第十節。

## 維護重點

- **屬性翻譯涵蓋率**：執行 `python tr_bonus2.py`，正常應輸出 `UNTRANSLATED: 0`。
  地圖改版加了新詞彙時這裡會報出來。
- **能力翻譯缺漏**：`mk_ab.py` 會把沒有現成譯文的段落寫到 `ab_need.json`，
  補完後照索引寫進 `ab_new.json` 再合併。
- **名稱缺漏**：`build_data2.py` 會對缺名稱的 id 報 KeyError，補進 `names2.json`。
- **配方修正**：`build_data2.py` 裡的 `RECIPE_FIX` 用來覆蓋 Wiki 的錯誤配方
  （目前只有黃道十二宮）。`used_in` 一律由 `recipe` 反推，不會前後矛盾。
- **同名裝備**：舊合成表有 7 組「一個中文名對到兩件裝備」。本文以地圖檔的俄文名
  為準另取中文名，舊名保留在 `別名` 欄，兩個名字都查得到。
