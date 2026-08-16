@echo off
cd /d "%~dp0..\frontend"
call npm run dev
echo.
echo [Frontend] Process exited.
pause
