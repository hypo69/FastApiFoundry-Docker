@echo off
REM Простой запуск FastAPI Foundry
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo 🚀 FastAPI Foundry - Simple Launcher
echo ====================================================
echo.

REM Активируем venv если существует
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Using system Python
)

echo.

REM Если нет аргументов, показываем популярные команды
if "%~1"=="" (
    echo Popular commands:
    echo   start-simple.bat --dev --ssl --mcp --auto-port --browser
    echo   start-simple.bat --prod --ssl --mcp --auto-port
    echo   start-simple.bat --help
    echo.
    pause
    exit /b 0
)

REM Запускаем с аргументами
echo ▶️  Running: python run.py %*
echo.

python run.py %*

pause