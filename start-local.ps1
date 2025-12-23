# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск FastApiFoundry без Docker
# =============================================================================
# Описание:
#   PowerShell скрипт для запуска FastApiFoundry в обычном режиме
#   Альтернатива Docker Compose для локальной разработки
#
# Примеры:
#   .\start-local.ps1
#   .\start-local.ps1 -Port 8001
#
# File: start-local.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

# Установка политики выполнения для текущего пользователя
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

param(
    [int]$Port = 8000,
    [string]$Host = "0.0.0.0",
    [switch]$Dev = $false
)

Write-Host "🚀 FastApiFoundry Local Starter" -ForegroundColor Cyan
Write-Host "=" * 50

# Проверка Python 3.14
try {
    if (Test-Path "python-314\python.exe") {
        $pythonVersion = & .\python-314\python.exe --version 2>$null
        Write-Host "✅ Python 3.14: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python 3.14 не найден в python-314/" -ForegroundColor Red
        Write-Host "Поместите интерпретатор Python 3.14 в директорию python-314/" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Ошибка проверки Python 3.14" -ForegroundColor Red
    exit 1
}

# Проверка зависимостей
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Файл requirements.txt не найден!" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Проверка зависимостей..." -ForegroundColor Yellow
try {
    & .\python-314\python.exe -m pip install -r requirements.txt --quiet
    Write-Host "✅ Зависимости установлены" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка установки зависимостей" -ForegroundColor Red
    exit 1
}

# Проверка конфигурации
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "📋 Создан .env из примера" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  Файл .env не найден" -ForegroundColor Yellow
    }
}

# Освобождение порта
Write-Host "🔧 Освобождение порта $Port..." -ForegroundColor Yellow
try {
    $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
                 Select-Object -ExpandProperty OwningProcess -Unique
    
    foreach ($pid in $processes) {
        if ($pid -and $pid -ne 0) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "   Остановлен процесс PID: $pid" -ForegroundColor Gray
        }
    }
} catch {
    # Порт свободен
}

# Запуск сервера
Write-Host "🚀 Запуск FastApiFoundry на http://$Host`:$Port" -ForegroundColor Green
Write-Host "   Для остановки нажмите Ctrl+C" -ForegroundColor Gray
Write-Host ""

try {
    if ($Dev) {
        # Режим разработки с автоперезагрузкой
        & .\python-314\python.exe -m uvicorn src.api.main:app --host $Host --port $Port --reload
    } else {
        # Обычный запуск
        & .\python-314\python.exe run.py --host $Host --port $Port
    }
} catch {
    Write-Host "❌ Ошибка запуска: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}