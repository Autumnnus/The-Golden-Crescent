@echo off
where py >nul 2>&1
if %errorlevel% equ 0 (
  py -3 "%~dp0tools.py" %*
) else (
  python "%~dp0tools.py" %*
)
set "tool_exit=%errorlevel%"
if not "%tool_exit%"=="0" pause
exit /b %tool_exit%
