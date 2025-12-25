@echo off
REM =============================================================================
REM Название процесса: Быстрый запуск FastAPI Foundry через Docker
REM =============================================================================
REM Описание:
REM   Batch скрипт для быстрого запуска FastAPI Foundry в Docker контейнере
REM   Использует Python из Docker, избегая конфликтов с локальным окружением
REM
REM File: start-docker.bat
REM Project: FastApiFoundry (Docker)
REM Version: 0.2.1
REM Author: hypo69
REM License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
REM Copyright: © 2025 AiStros
REM Date: 9 декабря 2025
REM =============================================================================

echo 🐳 FastAPI Foundry - Docker Launcher
echo.

REM Проверка Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker не найден! Установите Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker найден
echo.

REM Запуск через Docker лончер
echo 🚀 Запуск FastAPI Foundry через Docker...
python docker-launcher.py fastapi

pause