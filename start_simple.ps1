# start_simple.ps1 - Простой запуск с одним портом
# =============================================================================
# File: start_simple.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# Date: 9 декабря 2025
# =============================================================================

param(
    [string]$Model = "qwen2.5-0.5b-instruct-generic-cpu:4"
)

Write-Host "🚀 FastAPI Foundry - Простой запуск" -ForegroundColor Cyan

# Киллинг ВСЕХ процессов foundry
Write-Host "🛑 Киллинг всех процессов Foundry..." -ForegroundColor Red
Get-Process -Name "foundry" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Остановка сервиса Foundry
Write-Host "🛑 Остановка сервиса Foundry..." -ForegroundColor Red
& foundry service stop 2>$null
Start-Sleep -Seconds 2

# Киллинг всех процессов на портах 8000 и 50477
Write-Host "🛑 Освобождение портов..." -ForegroundColor Yellow
$ports = @(8000, 50477)
foreach ($port in $ports) {
    $connections = netstat -ano | findstr ":$port"
    if ($connections) {
        Write-Host "⚠️ Порт $port занят, киллинг процессов..." -ForegroundColor Yellow
        foreach ($line in $connections) {
            $parts = $line -split '\s+'
            $processId = $parts[-1]
            if ($processId -and $processId -ne "0") {
                Write-Host "🛑 Киллинг PID: $processId" -ForegroundColor Red
                taskkill /PID $processId /F 2>$null
            }
        }
    }
}

Write-Host "✅ Все процессы убиты" -ForegroundColor Green

# Запуск Foundry и парсинг порта
Write-Host "🚀 Запуск Foundry..." -ForegroundColor Yellow
$foundryOutput = & foundry service start 2>&1
$foundryPort = $null

# Парсинг порта из вывода Foundry
foreach ($line in $foundryOutput) {
    if ($line -match "http://127\.0\.0\.1:(\d+)/") {
        $foundryPort = $matches[1]
        Write-Host "✅ Foundry запущен на порту $foundryPort" -ForegroundColor Green
        break
    }
}

if (-not $foundryPort) {
    Write-Host "❌ Не удалось получить порт Foundry" -ForegroundColor Red
    exit 1
}

# Сохранение порта в глобальную переменную
$script:FoundryPort = $foundryPort

# Запуск модели
Write-Host "🤖 Загрузка модели $Model..." -ForegroundColor Yellow
& foundry model run $Model

# Запуск FastAPI с передачей порта Foundry
Write-Host "🌐 Запуск FastAPI на порту 8000..." -ForegroundColor Green
$env:FOUNDRY_BASE_URL = "http://localhost:$foundryPort/v1/"
python run.py