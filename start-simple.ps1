# -*- coding: utf-8 -*-
# Простой запуск FastAPI Foundry без дополнительных проверок
# ============================================================================

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

Write-Host ""
Write-Host "🚀 FastAPI Foundry - Simple Launcher" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Активируем venv если существует
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠️  Using system Python" -ForegroundColor Yellow
}

Write-Host ""

# Если нет аргументов, показываем популярные команды
if ($Args.Count -eq 0) {
    Write-Host "Popular commands:" -ForegroundColor Yellow
    Write-Host "  .\start-simple.ps1 --dev --ssl --mcp --auto-port --browser" -ForegroundColor Green
    Write-Host "  .\start-simple.ps1 --prod --ssl --mcp --auto-port" -ForegroundColor White
    Write-Host "  .\start-simple.ps1 --help" -ForegroundColor White
    Write-Host ""
    exit 0
}

# Запускаем с аргументами
$ArgString = $Args -join " "
Write-Host "▶️  Running: python run.py $ArgString" -ForegroundColor Cyan
Write-Host ""

python run.py @Args