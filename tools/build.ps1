# 重新產生所有輸出：images/ · data/items.json · data/site.json · index.html · 攻略.md
#
#   cd tools
#   .\build.ps1
#
# 若出現「因為這個系統上已停用指令碼執行」，先跑一次：
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

# 前兩步直接讀 version.json 指定的 .w3x 地圖檔。改版時只要換地圖、
# 改 version.json 的 map_file 與 map_version，跑這支就好。
$mapFile = (Get-Content -Raw -Encoding UTF8 'version.json' | ConvertFrom-Json).map_file
if (-not $mapFile) { Write-Host 'version.json 缺 map_file' -ForegroundColor Red; exit 1 }
if (-not (Test-Path $mapFile)) {
    Write-Host "找不到地圖檔：$mapFile" -ForegroundColor Red; exit 1
}

$steps = @(
    @{ f = 'refresh_db.py';      a = $mapFile; d = '讀地圖 -> tools/db_items.json + 缺少的圖示' }
    @{ f = 'build_heroes.py';    a = $mapFile; d = '讀地圖 -> data/heroes.json' }
    @{ f = 'build_data2.py';     d = '合併資料 + 修正圖示色彩 -> data/items.json, images/' }
    @{ f = 'build_site_data.py'; d = '三語資料              -> data/site.json' }
    @{ f = 'build_site.py';      d = '產生網站              -> index.html' }
    @{ f = 'build_md2.py';       d = '產生攻略              -> 裝備合成攻略.md' }
    @{ f = 'build_dossier.py';   d = '英雄卷宗              -> data/dossier/*.md' }
    @{ f = 'build_itemref.py';   d = '道具速查              -> data/dossier/_items.md' }
    @{ f = 'build_engineref.py'; d = '引擎附錄              -> data/dossier/_engine.md' }
)

$n = 0
foreach ($s in $steps) {
    $n++
    Write-Host ("[{0}/{1}] {2}" -f $n, $steps.Count, $s.d) -ForegroundColor Cyan
    if ($s.a) { python $s.f $s.a } else { python $s.f }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "失敗：$($s.f)（結束碼 $LASTEXITCODE）" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host ''
Write-Host '全部完成。' -ForegroundColor Green
Write-Host '直接開啟 ..\index.html 就能看到結果。'
