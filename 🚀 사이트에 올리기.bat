@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
where py >nul 2>&1
if %errorlevel% == 0 (
    py -X utf8 "%~dp0publish.py"
) else (
    python -X utf8 "%~dp0publish.py"
)
echo.
echo ==============================
pause
