# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry Launcher Menu
# =============================================================================
# Описание:
#   Интуитивный интерфейс для выбора типа запуска FastAPI Foundry
#   Объединяет все варианты запуска в одном меню
#
# File: launcher.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

param(
    [string]$Mode = ""
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

function Show-Menu {
    Clear-Host
    Write-Host "🚀 FastAPI Foundry Launcher" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Выберите тип запуска:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. 🎯 Быстрый запуск (рекомендуется)" -ForegroundColor Green
    Write-Host "   Автоматическая установка + Foundry + FastAPI"
    Write-Host ""
    Write-Host "2. 🐍 Только FastAPI сервер" -ForegroundColor Cyan
    Write-Host "   Без Foundry, только веб-интерфейс"
    Write-Host ""
    Write-Host "3. 🔧 Режим разработки" -ForegroundColor Magenta
    Write-Host "   С подробным выводом и отладкой"
    Write-Host ""
    Write-Host "4. 🐳 Docker запуск" -ForegroundColor Blue
    Write-Host "   Запуск в Docker контейнере"
    Write-Host ""
    Write-Host "5. ⚙️ Настройка окружения" -ForegroundColor Yellow
    Write-Host "   Настройка .env переменных"
    Write-Host ""
    Write-Host "6. 🔍 Диагностика" -ForegroundColor DarkYellow
    Write-Host "   Проверка системы и исправление проблем"
    Write-Host ""
    Write-Host "0. ❌ Выход" -ForegroundColor Red
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Start-QuickLaunch {
    Write-Host "🎯 Быстрый запуск FastAPI Foundry" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    & "$Root\start.ps1"
}

function Start-FastAPIOnly {
    Write-Host "🐍 Запуск только FastAPI сервера" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    $pythonExe = "$Root\venv\Scripts\python.exe"
    if (-not (Test-Path $pythonExe)) {
        $pythonExe = "python"
    }
    
    Write-Host "🌐 Запуск без Foundry..." -ForegroundColor Yellow
    & $pythonExe "$Root\run.py"
}

function Start-Development {
    Write-Host "🔧 Режим разработки" -ForegroundColor Magenta
    Write-Host "=" * 50 -ForegroundColor Magenta
    & "$Root\start_simple.ps1"
}

function Start-Docker {
    Write-Host "🐳 Docker запуск" -ForegroundColor Blue
    Write-Host "=" * 50 -ForegroundColor Blue
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Docker не установлен!" -ForegroundColor Red
        Write-Host "Установите Docker Desktop: https://docker.com/products/docker-desktop" -ForegroundColor Yellow
        Read-Host "Нажмите Enter для продолжения"
        return
    }
    
    Write-Host "🔨 Сборка Docker образа..." -ForegroundColor Yellow
    docker-compose build
    
    Write-Host "🚀 Запуск Docker контейнера..." -ForegroundColor Yellow
    docker-compose up
}

function Start-Setup {
    Write-Host "⚙️ Настройка окружения" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Yellow
    
    if (Test-Path "$Root\setup-env.ps1") {
        & "$Root\setup-env.ps1"
    } else {
        Write-Host "❌ setup-env.ps1 не найден!" -ForegroundColor Red
        Write-Host "Создайте .env файл вручную из .env.example" -ForegroundColor Yellow
    }
    
    Read-Host "Нажмите Enter для продолжения"
}

function Start-Diagnostics {
    Write-Host "🔍 Диагностика системы" -ForegroundColor DarkYellow
    Write-Host "=" * 50 -ForegroundColor DarkYellow
    
    # Проверка Python
    Write-Host "🐍 Проверка Python..." -ForegroundColor Yellow
    if (Test-Path "$Root\venv\Scripts\python.exe") {
        Write-Host "✅ Virtual environment найден" -ForegroundColor Green
    } else {
        Write-Host "❌ Virtual environment не найден" -ForegroundColor Red
        Write-Host "💡 Запустите: python -m venv venv" -ForegroundColor Cyan
    }
    
    # Проверка .env
    Write-Host "⚙️ Проверка .env..." -ForegroundColor Yellow
    if (Test-Path "$Root\.env") {
        Write-Host "✅ .env файл найден" -ForegroundColor Green
        if (Test-Path "$Root\check_env.py") {
            $pythonExe = if (Test-Path "$Root\venv\Scripts\python.exe") { "$Root\venv\Scripts\python.exe" } else { "python" }
            & $pythonExe "$Root\check_env.py"
        }
    } else {
        Write-Host "❌ .env файл не найден" -ForegroundColor Red
        Write-Host "💡 Скопируйте .env.example в .env" -ForegroundColor Cyan
    }
    
    # Проверка Foundry
    Write-Host "🤖 Проверка Foundry..." -ForegroundColor Yellow
    try {
        Get-Command foundry -ErrorAction Stop | Out-Null
        Write-Host "✅ Foundry CLI найден" -ForegroundColor Green
    } catch {
        Write-Host "❌ Foundry CLI не найден" -ForegroundColor Red
        Write-Host "💡 Установите: https://github.com/microsoft/foundry" -ForegroundColor Cyan
    }
    
    # Проверка портов
    Write-Host "🔌 Проверка портов..." -ForegroundColor Yellow
    $ports = @(9696, 50477, 8000)
    foreach ($port in $ports) {
        try {
            $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
            if ($connection.TcpTestSucceeded) {
                Write-Host "⚠️ Порт $port занят" -ForegroundColor Yellow
            } else {
                Write-Host "✅ Порт $port свободен" -ForegroundColor Green
            }
        } catch {
            Write-Host "✅ Порт $port свободен" -ForegroundColor Green
        }
    }
    
    Read-Host "Нажмите Enter для продолжения"
}

# Основная логика
if ($Mode) {
    switch ($Mode.ToLower()) {
        "quick" { Start-QuickLaunch; exit }
        "api" { Start-FastAPIOnly; exit }
        "dev" { Start-Development; exit }
        "docker" { Start-Docker; exit }
        "setup" { Start-Setup; exit }
        "diag" { Start-Diagnostics; exit }
        default { 
            Write-Host "❌ Неизвестный режим: $Mode" -ForegroundColor Red
            Write-Host "Доступные режимы: quick, api, dev, docker, setup, diag" -ForegroundColor Yellow
            exit 1
        }
    }
}

# Интерактивное меню
while ($true) {
    Show-Menu
    $choice = Read-Host "Введите номер (0-6)"
    
    switch ($choice) {
        "1" { Start-QuickLaunch; break }
        "2" { Start-FastAPIOnly; break }
        "3" { Start-Development; break }
        "4" { Start-Docker; break }
        "5" { Start-Setup; continue }
        "6" { Start-Diagnostics; continue }
        "0" { 
            Write-Host "👋 До свидания!" -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host "❌ Неверный выбор. Попробуйте снова." -ForegroundColor Red
            Start-Sleep 2
        }
    }
}