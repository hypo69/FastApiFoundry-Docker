# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker управление для FastAPI Foundry (PowerShell)
# =============================================================================
# Описание:
#   PowerShell скрипт для сборки, запуска и управления Docker контейнером
#   Включает команды для экспорта/импорта образа
#
# File: docker-manager.ps1
# Project: FastAPI Foundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$ImageName = "fastapi-foundry"
$ContainerName = "fastapi-foundry"
$Version = "latest"

function Show-Help {
    Write-Host "FastAPI Foundry Docker Manager (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Использование: .\docker-manager.ps1 [КОМАНДА]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Команды:" -ForegroundColor Green
    Write-Host "  build     - Собрать Docker образ"
    Write-Host "  run       - Запустить контейнер"
    Write-Host "  stop      - Остановить контейнер"
    Write-Host "  restart   - Перезапустить контейнер"
    Write-Host "  logs      - Показать логи контейнера"
    Write-Host "  shell     - Войти в контейнер"
    Write-Host "  clean     - Удалить контейнер и образ"
    Write-Host "  export    - Экспортировать образ в tar файл"
    Write-Host "  import    - Импортировать образ из tar файла"
    Write-Host "  status    - Показать статус контейнера"
    Write-Host "  help      - Показать эту справку"
}

function Build-Image {
    Write-Host "🔨 Сборка Docker образа..." -ForegroundColor Yellow
    docker build -t "${ImageName}:${Version}" .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Образ собран: ${ImageName}:${Version}" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка сборки образа" -ForegroundColor Red
        exit 1
    }
}

function Start-Container {
    Write-Host "🚀 Запуск контейнера..." -ForegroundColor Yellow
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Контейнер запущен" -ForegroundColor Green
        Write-Host "🌐 Веб-интерфейс: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "📚 API документация: http://localhost:8000/docs" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Ошибка запуска контейнера" -ForegroundColor Red
        exit 1
    }
}

function Stop-Container {
    Write-Host "⏹️ Остановка контейнера..." -ForegroundColor Yellow
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Контейнер остановлен" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка остановки контейнера" -ForegroundColor Red
        exit 1
    }
}

function Restart-Container {
    Write-Host "🔄 Перезапуск контейнера..." -ForegroundColor Yellow
    docker-compose restart
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Контейнер перезапущен" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка перезапуска контейнера" -ForegroundColor Red
        exit 1
    }
}

function Show-Logs {
    Write-Host "📋 Логи контейнера:" -ForegroundColor Yellow
    docker-compose logs -f
}

function Enter-Shell {
    Write-Host "🐚 Вход в контейнер..." -ForegroundColor Yellow
    docker exec -it $ContainerName /bin/bash
}

function Remove-All {
    Write-Host "🧹 Очистка контейнера и образа..." -ForegroundColor Yellow
    docker-compose down
    docker rmi "${ImageName}:${Version}" 2>$null
    Write-Host "✅ Очистка завершена" -ForegroundColor Green
}

function Export-Image {
    Write-Host "📦 Экспорт образа в файл..." -ForegroundColor Yellow
    $exportFile = "fastapi-foundry-${Version}.tar"
    docker save -o $exportFile "${ImageName}:${Version}"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Образ экспортирован: $exportFile" -ForegroundColor Green
        $fileSize = (Get-Item $exportFile).Length / 1MB
        Write-Host "📊 Размер файла: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Ошибка экспорта образа" -ForegroundColor Red
        exit 1
    }
}

function Import-Image {
    $importFile = "fastapi-foundry-${Version}.tar"
    if (-not (Test-Path $importFile)) {
        Write-Host "❌ Файл $importFile не найден" -ForegroundColor Red
        exit 1
    }
    Write-Host "📥 Импорт образа из файла..." -ForegroundColor Yellow
    docker load -i $importFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Образ импортирован" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка импорта образа" -ForegroundColor Red
        exit 1
    }
}

function Show-Status {
    Write-Host "📊 Статус контейнера:" -ForegroundColor Yellow
    docker-compose ps
    Write-Host ""
    Write-Host "🖼️ Docker образы:" -ForegroundColor Yellow
    docker images | Select-String $ImageName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Образ не найден" -ForegroundColor Gray
    }
}

# Основная логика
switch ($Command.ToLower()) {
    "build" {
        Build-Image
    }
    "run" {
        Start-Container
    }
    "stop" {
        Stop-Container
    }
    "restart" {
        Restart-Container
    }
    "logs" {
        Show-Logs
    }
    "shell" {
        Enter-Shell
    }
    "clean" {
        Remove-All
    }
    "export" {
        Export-Image
    }
    "import" {
        Import-Image
    }
    "status" {
        Show-Status
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "❌ Неизвестная команда: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}