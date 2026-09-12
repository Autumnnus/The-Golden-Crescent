@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" tools\atlas_launcher.py %*
    goto finish
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 tools\atlas_launcher.py %*
    goto finish
)
where python >nul 2>nul
if not errorlevel 1 (
    python tools\atlas_launcher.py %*
    goto finish
)
echo Python 3.10+ bulunamadi. Python kurup Atlas.bat dosyasini tekrar acin.
if "%~1"=="" pause
exit /b 1
:finish
set ATLAS_RESULT=%ERRORLEVEL%
if "%~1"=="" pause
exit /b %ATLAS_RESULT%
