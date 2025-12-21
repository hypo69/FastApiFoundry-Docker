# -*- coding: utf-8 -*-
# Быстрый запуск в Production режиме
# ============================================================================

Write-Host ""
Write-Host "🚀 FastAPI Foundry - Production Mode" -ForegroundColor Green
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
Write-Host "🚀 Starting FastAPI Foundry in Production Mode..." -ForegroundColor Cyan
Write-Host "   - Production mode (--prod)" -ForegroundColor White
Write-Host "   - HTTPS enabled (--ssl)" -ForegroundColor White
Write-Host "   - MCP Console enabled (--mcp)" -ForegroundColor White
Write-Host "   - Auto-port detection (--auto-port)" -ForegroundColor White
Write-Host ""

# Запускаем в production режиме
python run.py --prod --ssl --mcp --auto-port
