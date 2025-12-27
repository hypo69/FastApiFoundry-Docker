@echo off
REM Запуск FastAPI Foundry с embedded Python 3.11
echo 🚀 FastAPI Foundry с embedded Python 3.11
echo ==================================================

cd /d "%~dp0"

REM Проверяем Foundry
echo 🔍 Проверяем Foundry...
foundry service status >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Foundry не запущен. Запускаем...
    start /B foundry service start >nul 2>&1
    timeout /t 5 >nul
)

REM Запускаем сервер
echo 🌐 Запуск сервера на http://localhost:8000
echo 📚 Документация: http://localhost:8000/docs
echo 📱 Чат: http://localhost:8000/static/chat.html

python-3.11.0-embed-amd64\python.exe -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

pause