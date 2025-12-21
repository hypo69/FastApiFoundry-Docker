@echo off
REM FastAPI Foundry Installation Script
REM ============================================================================
REM Установщик для FastAPI Foundry с поддержкой virtual environment
REM

setlocal enabledelayedexpansion

cd /d "%~dp0"

cls
echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║         FastAPI Foundry - Installation Wizard                         ║
echo ║                                                                        ║
echo ║  REST API для локальных AI моделей через Foundry с RAG поддержкой   ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
echo 🐍 Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo Пожалуйста, установите Python 3.8+ с https://www.python.org
    echo При установке отметьте "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION% найден
echo.

REM Detect PowerShell version
echo 📋 Поиск PowerShell...
where pwsh >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PowerShell 7+ найден
    set PS_CMD=pwsh
) else (
    echo ✅ Windows PowerShell найден
    set PS_CMD=powershell
)
echo.

REM Run PowerShell installation script
echo ▶️  Запуск установщика...
echo.
%PS_CMD% -ExecutionPolicy RemoteSigned -File install.ps1

if %errorlevel% equ 0 (
    cls
    echo.
    echo ╔════════════════════════════════════════════════════════════════════════╗
    echo ║                    ✅ УСТАНОВКА ЗАВЕРШЕНА!                            ║
    echo ╚════════════════════════════════════════════════════════════════════════╝
    echo.
    echo 🎉 Следующие шаги:
    echo.
    echo 1. Запустить на порту по умолчанию (8000):
    echo    python run.py
    echo.
    echo 2. Запустить с проверкой занятости порта (если порт занят - подключиться к существующему):
    echo    python run.py --fixed-port 8000
    echo.
    echo 3. Запустить с автопоиском свободного порта:
    echo    python run.py --auto-port
    echo.
    echo 4. Запустить с MCP консолью и браузером:
    echo    python run.py --mcp --browser
    echo.
    echo 5. Production режим:
    echo    python run.py --prod
    echo.
    echo 6. Справка:
    echo    python run.py --help
    echo.
) else (
    echo.
    echo ❌ Установка завершена с ошибкой
    echo Пожалуйста, проверьте логи выше
    echo.
)

pause
