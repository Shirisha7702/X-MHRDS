@echo off
cd /d "%~dp0..\backend\src"
call "%~dp0..\venv\Scripts\activate.bat"
uvicorn main:app --reload --port 8000
echo.
echo [Backend] Process exited.
pause
