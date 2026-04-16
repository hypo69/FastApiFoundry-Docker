@echo off
chcp 65001 >nul

REM FastApiFoundry-Docker: Unified Installation
REM Runs install.ps1 (venv, dependencies, .env, logs, RAG) and install-foundry.ps1 (AI backend)

REM 1. Core Installation
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '.\install.ps1' }"
if %errorlevel% neq 0 (
    echo Error executing install.ps1
    pause
    exit /b %errorlevel%
)

REM 2. Install Foundry Local (optional, if not installed)
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '.\install\install-foundry.ps1' }"
if %errorlevel% neq 0 (
    echo Error executing install-foundry.ps1
    echo You can install Foundry manually using .\install\install-foundry.ps1 or choose another AI backend.
    pause
)

REM 3. Register autostart with Windows
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '.\install\install-autostart.ps1' }"
if %errorlevel% neq 0 (
    echo Warning: autostart not registered. Run .\install\install-autostart.ps1 as administrator manually.
)

REM 4. Install HuggingFace CLI
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '.\install\install-huggingface-cli.ps1' -SkipAuth }"
if %errorlevel% neq 0 (
    echo Warning: HuggingFace CLI not installed. Run .\install\install-huggingface-cli.ps1 manually.
)

echo.
echo Installation complete!
echo Follow instructions in INSTALL.md
pause
