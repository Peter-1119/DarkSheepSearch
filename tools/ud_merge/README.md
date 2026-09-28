# UD 合併底圖＋中文化

以 `UD_test_24_09_26_opt.w3x`（新版，俄文）為底，產生 8 人合作、拓寬地形、含經典關卡、全中文的測試地圖。

## 產生地圖

```
python ud_build.py
```

輸出 `0UD_合併底圖_E2.w3x`，並複製到 `Documents/Warcraft III/Maps/Download`。

需要的原始地圖（放在 Maps/Download）：
- `UD_test_24_09_26_opt.w3x`：新版底圖
- `肥羊的聖誕禮物_1.41_ty.w3x`：舊版陵墓上層、寒冰洞窟地形
- `000肥羊的聖誕禮物_2.1.0_ty.w3x`：入侵模式、被褻瀆者的惡魔形態
- `UD_v3_82fix_opt.w3x`：網站依據的版本（神器配方）

`ud_new/`、`ud_old/`、`ud_210/`、`ud_vers/`、`*.j` 是從地圖解出的快取，不進版控；
遺失時跑 `python ud_extract.py` 重建（`ud_new_8p_v5.j` 是 8 人化後的腳本，由 `ud_v5.py` 產生）。

## 建置流程（ud_build.py）

1. 8 人化、關卡改名、難度基準
2. 地形拓寬、舊版陵墓上層／寒冰洞窟移植（階段 B）
3. 經典關卡、分頁選單（`ud_stageC.py`）
4. 修正與改版：詛咒者之弩、相位石、亡者公主 R（`ud_princess.py`）、神器配方對齊網站（`ud_recipefix.py`）、
   入侵對齊 2.1.0、右下王座四路（一般＋骨灰級）與軍械庫 +75%（`ud_invasion.py`）
   陵墓下層、冰霜森林（一般＋骨灰）地形與預放單位換回 2.1.0，出怪只改路數（`ud_levels210.py`）
5. 中文化（`ud_translate.py`）→ 道具說明校正（`ud_itemfix.py`）→ 選單格式（`ud_menutidy.py`）→ 介面與版本號（`ud_skin.py`）

## 翻譯

- 對照表優先序：手動 `ud_tm_manual_*.json`（檔名排序，後者覆蓋前者）＞ 網站 `ud_tm_site.json`
- 2.3.0 舊圖譯文已停用（`ud_translate.USE_230 = False`）
- 統一名詞：`ud_terms.py`（規則）＋ `ud_termfix.py`（自動修正），來源為 `data/translation.txt`
- 檢查：
  - `python ud_termcheck.py`：名詞規則違規
  - `python ud_simpcheck.py`：簡體字
  - `python ud_dialogs.py`：選單文字
- 新增待翻：建置後 `python ud_rbatch.py 0 250 > 批次.txt`，譯好寫成新的 `ud_tm_manual_1xx.json`，用 `python ud_rcheck.py 檔名 0 250` 驗證
