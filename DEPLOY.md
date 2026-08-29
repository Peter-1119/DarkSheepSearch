# 部署到 GitHub Pages

Repo：`Peter-1119/DarkSheepSearch`（已建立）
網址（開好 Pages 之後）：`https://peter-1119.github.io/DarkSheepSearch/`

---

## 步驟 1 — 確認要上傳的內容

`.gitignore` 已排除 `data/gg/`（6.5 MB 的灰階圖示，網站用不到）與各種中間產物。
先檢查一遍：

```bash
cd "D:/Notebook Program Scripts/Python_Scripts/DarkSheep"

git init
git add .
git status --short | wc -l           # 約 900 個檔案
git status --short | grep "data/gg"  # 應該沒有任何輸出
```

想知道實際會上傳多少：

```bash
git count-objects -vH
```

---

## 步驟 2 — 第一次推上去

```bash
git commit -m "裝備圖鑑：474 件裝備、420 張圖示、中英俄三語"
git branch -M main
git remote add origin https://github.com/Peter-1119/DarkSheepSearch.git
git push -u origin main
```

### 認證

GitHub 從 2021 起不接受密碼登入，兩種方式擇一：

**方式 A — GitHub CLI（推薦，設定一次就好）**

1. 安裝 <https://cli.github.com/>
2. 重開終端機，執行 `gh auth login`
3. 依序選：`GitHub.com` → `HTTPS` → `Yes`（用 gh 認證 git）→ `Login with a web browser`
4. 複製畫面上的一次性代碼，按 Enter 開瀏覽器貼上
5. 完成後 `git push` 會自動帶認證

**方式 B — Personal Access Token**

1. GitHub → 右上頭像 → Settings → 最下面 **Developer settings**
2. Personal access tokens → Tokens (classic) → **Generate new token (classic)**
3. Note 隨意、Expiration 自訂、**勾選 `repo`**
4. 產生後複製 token（只會顯示這一次）
5. `git push` 時 Username 填 `Peter-1119`，**Password 貼上 token**

### 如果 push 被拒絕（rejected / non-fast-forward）

表示建 repo 時勾了「Add a README」，遠端已有一個 commit。遠端沒有需要保留的東西，
直接覆蓋：

```bash
git push -u origin main --force
```

---

## 步驟 3 — 開啟 GitHub Pages

1. repo 頁面 → **Settings**
2. 左欄 **Pages**
3. **Source** 選 `Deploy from a branch`
4. **Branch** 選 `main`，資料夾選 `/ (root)`
5. **Save**

等 1–2 分鐘後重新整理，最上方會出現：

> Your site is live at `https://peter-1119.github.io/DarkSheepSearch/`

進入點是 `index.html`，開網址就直接是圖鑑。

---

## 步驟 4 — 補上 repo 描述

回 repo 首頁，右側 **About** 旁的齒輪 ⚙：

**Description**

```
Interactive item codex for the Warcraft III map 肥羊的聖誕禮物 / Underground Defence — 474 items with in-game icons, synthesis recipes and full stats, in 中文 · English · Русский. Single-file static site, no build step.
```

**Website**

```
https://peter-1119.github.io/DarkSheepSearch/
```

**Topics**（逐一輸入，按 Enter 分隔）

```
warcraft-3   warcraft-iii   wc3   underground-defence   wc3-map
item-database   game-wiki   github-pages   game-data   static-site
vanilla-javascript   i18n   multilingual   no-dependencies
```

順手勾選 **Use your GitHub Pages website**，About 區塊就會直接顯示網站連結。

---

## 步驟 5 — 之後更新

```bash
git add .
git commit -m "更新說明"
git push
```

約 1 分鐘後網站自動更新，可在 repo 的 **Actions** 分頁看部署進度。

---

## 大小

| 項目 | 大小 | 進版控 |
|---|---|---|
| `images/` 420 張（已修正色彩） | 4.0 MB | ✅ |
| `data/icons/` 原始匯出圖示 | 3.8 MB | ✅ 重建 `images/` 需要 |
| `data/*.json` | 1.6 MB | ✅ |
| `data/gg/` 854 張灰階圖示 | 6.5 MB | ❌ 已排除 |
| `tools/` | 1.0 MB | ✅（中間產物已排除） |
| `synthesis.xlsx` | 2.7 MB | ✅ 合成路線來源 |
| `index.html` | 354 KB | ✅ |
| **實際上傳** | **約 13 MB** | |

GitHub 限制：單檔 100 MB、repo 建議 1 GB、Pages 1 GB、流量 100 GB／月。
13 MB 約是 Pages 上限的 **1.3%**。

---

## 疑難排解

**Pages 開了卻 404**
等 2–3 分鐘。若仍然 404，確認 Settings → Pages 的 Branch 是 `main`、資料夾是 `/ (root)`。

**網站出現但圖片全裂**
確認 `images/` 有推上去：`git ls-files images | wc -l` 應該是 420。

**中文檔名顯示異常**
push 前設定：`git config core.quotepath false`

**改成 private repo**
免費帳號的 Pages 只支援 public repo，改成 private 網站會停掉。
