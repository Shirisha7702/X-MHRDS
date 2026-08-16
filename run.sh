#!/usr/bin/env bash
# X-MHRDS Launcher (cross-platform: Git Bash on Windows, Linux, macOS).
# Run with: bash run.sh   (or ./run.sh if the executable bit is set)
#
# Checks for a Python venv and node_modules, creates/installs whichever is missing,
# then runs the backend (uvicorn) and frontend (vite) concurrently in this one terminal.
# Press Ctrl+C to stop both.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================"
echo " X-MHRDS Launcher"
echo "================================================================"

# ---------------------------------------------------------------
# 1. Backend: Python virtual environment
# ---------------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "[ERROR] Python was not found on PATH. Install Python 3.10+ and try again."
    exit 1
fi

if [ -f "venv/Scripts/activate" ]; then
    VENV_ACTIVATE="venv/Scripts/activate"      # Windows venv layout (Git Bash)
elif [ -f "venv/bin/activate" ]; then
    VENV_ACTIVATE="venv/bin/activate"          # Linux/macOS venv layout
else
    VENV_ACTIVATE=""
fi

if [ -z "$VENV_ACTIVATE" ]; then
    echo "[Backend] No virtual environment found. Creating one..."
    "$PYTHON_BIN" -m venv venv

    if [ -f "venv/Scripts/activate" ]; then
        VENV_ACTIVATE="venv/Scripts/activate"
    else
        VENV_ACTIVATE="venv/bin/activate"
    fi

    echo "[Backend] Installing Python dependencies from requirements.txt..."
    # shellcheck disable=SC1090
    source "$VENV_ACTIVATE"
    pip install -r requirements.txt
    deactivate
else
    echo "[Backend] Virtual environment already present. Skipping install."
fi

# ---------------------------------------------------------------
# 2. Frontend: npm dependencies
# ---------------------------------------------------------------
if ! command -v npm >/dev/null 2>&1; then
    echo "[ERROR] npm was not found on PATH. Install Node.js and try again."
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "[Frontend] node_modules not found. Running npm install..."
    (cd frontend && npm install)
else
    echo "[Frontend] node_modules already present. Skipping install."
fi

# ---------------------------------------------------------------
# 3. Launch backend and frontend concurrently in this one terminal
# ---------------------------------------------------------------
cleanup() {
    echo ""
    echo "Stopping backend and frontend..."
    [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" 2>/dev/null || true
    [ -n "${FRONTEND_PID:-}" ] && kill "$FRONTEND_PID" 2>/dev/null || true
    wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo ""
echo "Starting backend on http://localhost:8000 ..."
(
    cd backend/src
    # shellcheck disable=SC1090
    source "../../$VENV_ACTIVATE"
    exec uvicorn main:app --reload --port 8000
) &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173 ..."
(
    cd frontend
    exec npm run dev
) &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both."
echo ""

wait "$BACKEND_PID" "$FRONTEND_PID"
