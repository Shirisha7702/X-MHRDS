@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ================================================================
echo  X-MHRDS Launcher
echo ================================================================
echo.

REM ---------------------------------------------------------------
REM 1. Backend: Python virtual environment
REM ---------------------------------------------------------------
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found on PATH. Install Python 3.10+ and try again.
    pause
    exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
    echo [Backend] No virtual environment found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create the virtual environment.
        pause
        exit /b 1
    )

    echo [Backend] Installing Python dependencies from requirements.txt...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] pip install failed.
        pause
        exit /b 1
    )
    call venv\Scripts\deactivate.bat
) else (
    echo [Backend] Virtual environment already present. Skipping install.
)

REM ---------------------------------------------------------------
REM 2. Frontend: npm dependencies
REM ---------------------------------------------------------------
where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm was not found on PATH. Install Node.js and try again.
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo [Frontend] node_modules not found. Running npm install...
    pushd frontend
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed.
        popd
        pause
        exit /b 1
    )
    popd
) else (
    echo [Frontend] node_modules already present. Skipping install.
)

REM ---------------------------------------------------------------
REM 3. Launch backend and frontend, each in its own window
REM ---------------------------------------------------------------
echo.
echo Starting backend on http://localhost:8000 ...
start "X-MHRDS Backend" "%~dp0scripts\start_backend.bat"

echo Starting frontend on http://localhost:5173 ...
start "X-MHRDS Frontend" "%~dp0scripts\start_frontend.bat"

echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Close the two spawned windows to stop the servers.
echo.
pause
