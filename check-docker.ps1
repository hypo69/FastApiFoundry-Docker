# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Диагностика Docker для FastApiFoundry
# =============================================================================
# Описание:
#   PowerShell скрипт для проверки состояния Docker и Docker Compose
#   Часть сценария установки - диагностирует проблемы и предлагает решения
#
# Примеры:
#   .\check-docker.ps1
#
# File: check-docker.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

# Установка политики выполнения для текущего пользователя
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

Write-Host "🔍 Docker Diagnostics для FastApiFoundry" -ForegroundColor Cyan
Write-Host "=" * 50

# Проверка Docker
function Test-Docker {
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Host "✅ Docker Engine: $dockerVersion" -ForegroundColor Green
            return $true
        }
    } catch {}
    
    Write-Host "❌ Docker Engine не найден" -ForegroundColor Red
    return $false
}

# Проверка Docker Compose
function Test-DockerCompose {
    try {
        # Новый синтаксис (Docker Compose V2)
        $composeVersion = docker compose version 2>$null
        if ($composeVersion) {
            Write-Host "✅ Docker Compose V2: $composeVersion" -ForegroundColor Green
            return "v2"
        }
        
        # Старый синтаксис (Docker Compose V1)
        $composeVersion = docker-compose --version 2>$null
        if ($composeVersion) {
            Write-Host "✅ Docker Compose V1: $composeVersion" -ForegroundColor Green
            return "v1"
        }
    } catch {}
    
    Write-Host "❌ Docker Compose не найден" -ForegroundColor Red
    return $false
}

# Основная диагностика
Write-Host "🔍 Диагностика Docker..." -ForegroundColor Yellow

$dockerExists = Test-Docker
$composeVersion = Test-DockerCompose

if (-not $dockerExists) {
    Write-Host ""
    Write-Host "📋 УСТАНОВКА DOCKER:" -ForegroundColor Cyan
    Write-Host "1. Автоустановка: .\install-docker.ps1" -ForegroundColor White
    Write-Host "2. Ручная загрузка: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📋 АЛЬТЕРНАТИВА (без Docker):" -ForegroundColor Cyan
    Write-Host "1. Локальный запуск: .\start-local.ps1" -ForegroundColor White
    Write-Host "2. Прямой запуск: python run.py" -ForegroundColor White
    
} elseif (-not $composeVersion) {
    Write-Host ""
    Write-Host "📋 ОБНОВЛЕНИЕ DOCKER:" -ForegroundColor Cyan
    Write-Host "Docker Compose должен быть включен в современные версии Docker Desktop" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Обновите Docker Desktop до последней версии" -ForegroundColor White
    Write-Host "2. Используйте новый синтаксис: docker compose up -d" -ForegroundColor White
    Write-Host "3. Альтернатива: .\start-local.ps1" -ForegroundColor White
    
} else {
    Write-Host ""
    Write-Host "✅ Docker готов к использованию!" -ForegroundColor Green
    
    if ($composeVersion -eq "v2") {
        Write-Host "🚀 Команда запуска: docker compose up -d" -ForegroundColor Cyan
    } else {
        Write-Host "🚀 Команда запуска: docker-compose up -d" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "🎯 РЕКОМЕНДУЕМЫЕ КОМАНДЫ:" -ForegroundColor Green
Write-Host "   .\start-local.ps1       # Локальный запуск (без Docker)" -ForegroundColor White
Write-Host "   docker compose up -d    # Docker запуск (если установлен)" -ForegroundColor White
Write-Host "   .\install-docker.ps1    # Установка Docker Desktop" -ForegroundColor White