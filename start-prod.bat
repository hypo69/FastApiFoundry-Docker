@echo off
REM FastAPI Foundry Production Launcher
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo 🚀 FastAPI Foundry - Production Mode
echo ===================================================
echo.

REM Check if run.py exists
if not exist "run.py" (
    echo ❌ Error: run.py not found in current directory
    echo    Please run this script from FastApiFoundry directory
    pause
    exit /b 1
)

REM Activate venv if exists
if exist "venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Virtual environment not found, using system Python
)

echo.
echo 🚀 Starting FastAPI Foundry in Production Mode...
echo    - Production mode (--prod)
echo    - HTTPS enabled (--ssl)
echo    - MCP Console enabled (--mcp)
echo    - Auto-port detection (--auto-port)
echo.

REM Run with production settings
python run.py --prod --ssl --mcp --auto-port

pause
