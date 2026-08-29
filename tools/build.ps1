# 重新產生所有輸出：images/ · data/items.json · data/site.json · index.html · 攻略.md
#
#   cd tools
#   .\build.ps1
#
# 若出現「因為這個系統上已停用指令碼執行」，先跑一次：
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

$steps = @(
    @{ f = 'build_data2.py';     d = '合併資料 + 修正圖示色彩 -> data/items.json, images/' }
    @{ f = 'build_site_data.py'; d = '三語資料              -> data/site.json' }
    @{ f = 'build_site.py';      d = '產生網站              -> index.html' }
    @{ f = 'build_md2.py';       d = '產生攻略              -> 裝備合成攻略.md' }
)

$n = 0
foreach ($s in $steps) {
    $n++
    Write-Host ("[{0}/{1}] {2}" -f $n, $steps.Count, $s.d) -ForegroundColor Cyan
    python $s.f
    if ($LASTEXITCODE -ne 0) {
        Write-Host "失敗：$($s.f)（結束碼 $LASTEXITCODE）" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host ''
Write-Host '全部完成。' -ForegroundColor Green
Write-Host '直接開啟 ..\index.html 就能看到結果。'
