# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Проверка и запуск Docker для FastApiFoundry
# =============================================================================
# Описание:
#   Проверяет Docker Desktop, собирает образ и запускает контейнер
#
# Примеры:
#   .\docker-check.ps1
#
# File: docker-check.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

Write-Host "🐳 FastAPI Foundry Docker Setup" -ForegroundColor Cyan
Write-Host "=" * 50

# Проверка Docker Desktop
Write-Host "Проверяем Docker Desktop..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker найден: $dockerVersion" -ForegroundColor Green
    } else {
        throw "Docker не найден"
    }
} catch {
    Write-Host "❌ Docker Desktop не запущен или не установлен" -ForegroundColor Red
    Write-Host "Запустите Docker Desktop и повторите попытку" -ForegroundColor Yellow
    exit 1
}

# Проверка docker-compose
Write-Host "Проверяем docker-compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Compose найден: $composeVersion" -ForegroundColor Green
    } else {
        throw "Docker Compose не найден"
    }
} catch {
    Write-Host "❌ Docker Compose не найден" -ForegroundColor Red
    exit 1
}

# Проверка образа
Write-Host "Проверяем образ fastapi-foundry:0.2.1..." -ForegroundColor Yellow
$imageExists = docker images -q fastapi-foundry:0.2.1 2>$null
if ([string]::IsNullOrEmpty($imageExists)) {
    Write-Host "⚠️  Образ не найден, собираем..." -ForegroundColor Yellow
    
    Write-Host "Сборка Docker образа..." -ForegroundColor Cyan
    docker-compose build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Образ успешно собран" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка сборки образа" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Образ найден" -ForegroundColor Green
}

# Запуск контейнера
Write-Host "Запускаем контейнер..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Контейнер запущен успешно!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Веб-интерфейс: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📚 API документация: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "❤️  Health check: http://localhost:8000/api/v1/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Для просмотра логов: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "Для остановки: docker-compose down" -ForegroundColor Yellow
} else {
    Write-Host "❌ Ошибка запуска контейнера" -ForegroundColor Red
    Write-Host "Проверьте логи: docker-compose logs" -ForegroundColor Yellow
}