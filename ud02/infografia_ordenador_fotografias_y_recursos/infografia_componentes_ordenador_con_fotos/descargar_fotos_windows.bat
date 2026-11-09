@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
    py descargar_fotos.py
) else (
    python descargar_fotos.py
)
echo.
pause
