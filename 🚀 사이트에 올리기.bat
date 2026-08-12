@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
where py >nul 2>&1
if %errorlevel% == 0 (
    py -X utf8 "%~dp0scripts\check_columns_sync.py"
) else (
    python -X utf8 "%~dp0scripts\check_columns_sync.py"
)
if errorlevel 1 (
    echo.
    echo 칼럼 동기화 검사에 실패했습니다. 배포를 중단합니다.
    pause
    exit /b 1
)
where py >nul 2>&1
if %errorlevel% == 0 (
    py -X utf8 "%~dp0publish.py"
) else (
    python -X utf8 "%~dp0publish.py"
)
echo.
echo ==============================
pause
