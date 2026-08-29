@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [1/4] build_data2.py    - merge data, fix icon colours
python build_data2.py
if errorlevel 1 goto fail
echo [2/4] build_site_data.py - trilingual dataset
python build_site_data.py
if errorlevel 1 goto fail
echo [3/4] build_site.py      - index.html
python build_site.py
if errorlevel 1 goto fail
echo [4/4] build_md2.py       - markdown guide
python build_md2.py
if errorlevel 1 goto fail
echo.
echo Done. Open ..\index.html
pause
exit /b 0
:fail
echo.
echo BUILD FAILED - see the error above.
pause
exit /b 1
