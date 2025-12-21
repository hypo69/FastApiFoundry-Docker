# -*- coding: utf-8 -*-
# FastAPI Foundry Launcher Script
# Автоматически активирует venv и запускает сервер

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

Write-Host ""
Write-Host "🚀 FastAPI Foundry Launcher" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Проверяем что находимся в правильной директории
if (-not (Test-Path ".\run.py")) {
    Write-Host "❌ Error: run.py not found in current directory" -ForegroundColor Red
    Write-Host "   Please run this script from FastApiFoundry directory" -ForegroundColor Red
    exit 1
}

# Проверяем venv и автоматически устанавливаем если нужно
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found" -ForegroundColor Yellow
    Write-Host ""

    if (Test-Path ".\install.ps1") {
        Write-Host "📦 Running automatic installation..." -ForegroundColor Cyan
        Write-Host ""

        & .\install.ps1

        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Installation failed" -ForegroundColor Red
            exit 1
        }

        Write-Host ""
        Write-Host "✅ Installation complete! Continuing..." -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "❌ install.ps1 not found" -ForegroundColor Red
        Write-Host "   Please create venv first:" -ForegroundColor Yellow
        Write-Host "   python -m venv venv" -ForegroundColor Yellow
        exit 1
    }
}

# Активируем venv
Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Если нет аргументов, показываем справку и предлагаем популярные команды
if ($Args.Count -eq 0) {
    Write-Host "Usage: .\start.ps1 [arguments]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Most popular commands:" -ForegroundColor Cyan
    Write-Host "  .\start.ps1 --help                                    # Show help" -ForegroundColor White
    Write-Host "  .\start.ps1 --dev --ssl --mcp --auto-port --browser  # Full setup" -ForegroundColor Green
    Write-Host "  .\start.ps1 --prod --ssl --mcp --auto-port           # Production" -ForegroundColor White
    Write-Host "  .\start.ps1 --dev --ssl --mcp --auto-port --log-level debug  # Debug" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\start.ps1 --help                    # Show all options" -ForegroundColor White
    Write-Host "  .\start.ps1 --dev --ssl --mcp         # Quick start" -ForegroundColor Green
    Write-Host ""
    exit 0
}

# Запускаем с аргументами
$ArgString = $Args -join " "
Write-Host "▶️  Running: python run.py $ArgString" -ForegroundColor Cyan
Write-Host ""

python run.py @Args
