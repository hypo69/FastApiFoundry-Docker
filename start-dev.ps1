# -*- coding: utf-8 -*-
# Быстрый запуск в режиме разработки с полным набором функций
# ============================================================================

Write-Host ""
Write-Host "🔧 FastAPI Foundry - Development Mode" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

# Проверяем что находимся в правильной директории
if (-not (Test-Path ".\run.py")) {
    Write-Host "❌ Error: run.py not found in current directory" -ForegroundColor Red
    Write-Host "   Please run this script from FastApiFoundry directory" -ForegroundColor Red
    exit 1
}

# Активируем venv если существует
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment not found, using system Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting FastAPI Foundry in Development Mode..." -ForegroundColor Cyan
Write-Host "   - Development mode (--dev)" -ForegroundColor White
Write-Host "   - HTTPS enabled (--ssl)" -ForegroundColor White
Write-Host "   - MCP Console enabled (--mcp)" -ForegroundColor White
Write-Host "   - Auto-port detection (--auto-port)" -ForegroundColor White
Write-Host "   - Browser auto-open (--browser)" -ForegroundColor White
Write-Host ""

# Запускаем с полным набором функций для разработки
python run.py --dev --ssl --mcp --auto-port --browser
