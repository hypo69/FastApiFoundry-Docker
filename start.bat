@echo off
REM start.bat - Запуск FastAPI Foundry с Deepseek R1
REM =============================================================================
REM Описание:
REM   Полный запуск системы: Foundry + модель Deepseek R1 + FastAPI сервер
REM
REM Использование:
REM   start.bat [порт] [модель]
REM
REM File: start.bat
REM Project: FastApiFoundry-Docker
REM Version: 1.0.0
REM Author: hypo69
REM Date: 27 декабря 2025
REM =============================================================================

setlocal enabledelayedexpansion

set PORT=%1
if "%PORT%"=="" set PORT=8000

set MODEL=%2
if "%MODEL%"=="" set MODEL=qwen2.5-0.5b-instruct-generic-cpu:4

echo 🚀 FastAPI Foundry с Deepseek R1
echo ==================================================

REM Освобождаем порт
echo 🔍 Проверяем порт %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%"') do (
    echo ⚠️  Порт %PORT% занят процессом PID: %%a
    echo 🛑 Убиваем процесс...
    taskkill /PID %%a /F >nul 2>&1
    timeout /t 2 >nul
)
echo ✅ Порт %PORT% свободен

REM Проверяем Foundry
echo 🔍 Проверяем Foundry...
curl -s http://localhost:50477/v1/models >nul 2>&1
if %errorlevel% neq 0 (
    echo 🚀 Запускаем Foundry service...
    start /B foundry service start >nul 2>&1
    echo ⏳ Ждем запуска Foundry (15 сек)...
    timeout /t 15 >nul
)

REM Проверяем Foundry еще раз
curl -s http://localhost:50477/v1/models >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Foundry не запустился
    pause
    exit /b 1
)
echo ✅ Foundry работает

REM Запускаем модель
echo 🤖 Запускаем модель: %MODEL%
foundry model run %MODEL%
if %errorlevel% neq 0 (
    echo ❌ Ошибка запуска модели
    pause
    exit /b 1
)
echo ✅ Модель запущена

REM Запускаем FastAPI сервер
echo 🌐 Запуск FastAPI сервера на порту %PORT%...
echo 📚 Документация: http://localhost:%PORT%/docs
echo 💬 Чат: http://localhost:%PORT%/static/chat.html
echo.

REM Активируем venv и запускаем
call venv\Scripts\activate.bat
python -c "from src.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=%PORT%, reload=False)"

pause