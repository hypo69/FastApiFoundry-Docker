# start_simple.ps1 - Упрощенный запуск FastAPI Foundry
# =============================================================================
# Описание:
#   Простой запуск с отображением всего вывода в консоли
#
# File: start_simple.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

Write-Host "🚀 FastAPI Foundry - Упрощенный запуск" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# 1. Поиск и запуск Foundry
Write-Host "🔍 Проверка Foundry..." -ForegroundColor Yellow

$foundryPort = $null
$foundryProcesses = Get-Process -Name "foundry" -ErrorAction SilentlyContinue

if ($foundryProcesses) {
    Write-Host "✅ Foundry уже запущен" -ForegroundColor Green
    # Попробуем найти порт
    $netstatOutput = netstat -ano | Select-String "LISTENING"
    foreach ($line in $netstatOutput) {
        if ($line -match ":([0-9]+).*LISTENING") {
            $port = $matches[1]
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$port/v1/models" -TimeoutSec 2 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    $foundryPort = $port
                    Write-Host "✅ Foundry работает на порту $port" -ForegroundColor Green
                    break
                }
            } catch { }
        }
    }
} else {
    Write-Host "🚀 Запуск Foundry..." -ForegroundColor Yellow
    $foundryOutput = & foundry service start 2>&1
    
    foreach ($line in $foundryOutput) {
        Write-Host "   $line" -ForegroundColor Gray
        if ($line -match "http://127\.0\.0\.1:(\d+)/") {
            $foundryPort = $matches[1]
        }
    }
    
    if ($foundryPort) {
        Write-Host "✅ Foundry запущен на порту $foundryPort" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Foundry запущен, но порт не определен" -ForegroundColor Yellow
        $foundryPort = "50477"  # Порт по умолчанию
    }
}

# 2. Настройка переменных окружения
if ($foundryPort) {
    $env:FOUNDRY_BASE_URL = "http://localhost:$foundryPort/v1/"
    $env:FOUNDRY_PORT = $foundryPort
    Write-Host "🔗 Foundry URL: $env:FOUNDRY_BASE_URL" -ForegroundColor Green
}

# 3. Определение Python
$pythonExe = $null
if (Test-Path "$PSScriptRoot\venv\Scripts\python.exe") {
    $pythonExe = "$PSScriptRoot\venv\Scripts\python.exe"
    Write-Host "🐍 Используем venv Python" -ForegroundColor Green
} elseif (Test-Path "$PSScriptRoot\python.exe") {
    $pythonExe = "$PSScriptRoot\python.exe"
    Write-Host "🐍 Используем embedded Python" -ForegroundColor Green
} else {
    $pythonExe = "python"
    Write-Host "🐍 Используем системный Python" -ForegroundColor Yellow
}

# 4. Запуск FastAPI сервера
Write-Host "" -ForegroundColor Cyan
Write-Host "🌐 Запуск FastAPI сервера..." -ForegroundColor Cyan
Write-Host "📋 Вывод сервера:" -ForegroundColor Cyan
Write-Host "-" * 50 -ForegroundColor Gray

try {
    & $pythonExe "run.py"
} catch {
    Write-Host "❌ Ошибка запуска: $_" -ForegroundColor Red
    exit 1
}