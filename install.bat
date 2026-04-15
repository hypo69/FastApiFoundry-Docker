@echo off
chcp 65001 >nul

REM FastApiFoundry-Docker: Единая установка
REM Запускает install.ps1 (venv, зависимости, .env, logs, RAG) и install-foundry.ps1 (AI backend)

REM 1. Основная установка
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '.\install.ps1' }"
if %errorlevel% neq 0 (
    echo Ошибка при выполнении install.ps1
    pause
    exit /b %errorlevel%
)

REM 2. Установка Foundry Local (опционально, если не установлен)
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '.\install-foundry.ps1' }"
if %errorlevel% neq 0 (
    echo Ошибка при выполнении install-foundry.ps1
    echo Можно установить Foundry вручную install-foundry.ps1 или выбрать другой AI backend.
    pause
)

REM 3. Регистрация автозапуска при старте Windows
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '.\install-autostart.ps1' }"
if %errorlevel% neq 0 (
    echo Предупреждение: автозапуск не зарегистрирован. Запустите install-autostart.ps1 от имени администратора вручную.
)

REM 4. Установка HuggingFace CLI
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '.\install-huggingface-cli.ps1' -SkipAuth }"
if %errorlevel% neq 0 (
    echo Предупреждение: HuggingFace CLI не установлен. Запустите install-huggingface-cli.ps1 вручную.
)

echo.
echo Установка завершена!
echo Следуйте инструкциям в INSTALL.md
pause
