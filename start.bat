@echo off
REM FastAPI Foundry Launcher (Batch version for convenience)
REM ============================================================================

setlocal enabledelayedexpansion

cd /d "%~dp0"

cls
echo.
echo 🚀 FastAPI Foundry Launcher
echo ===================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ⚠️  Virtual environment not found
    echo.
    echo Do you want to run the installer? (Y/N)
    set /p INSTALL="Enter Y or N: "

    if /i "!INSTALL!"=="Y" (
        call install.bat
        if errorlevel 1 (
            echo.
            echo ❌ Installation failed
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo ❌ Virtual environment required
        echo Please run: install.bat
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Virtual environment found
echo.

REM Check if PowerShell is available and use start.ps1 instead
where pwsh >nul 2>&1
if %errorlevel% equ 0 (
    REM Use PowerShell 7+
    pwsh -ExecutionPolicy RemoteSigned -File start.ps1 %*
) else (
    REM Use Windows PowerShell (built-in)
    powershell -ExecutionPolicy RemoteSigned -File start.ps1 %*
)

pause
