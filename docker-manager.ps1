# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker управление для FastAPI Foundry (PowerShell)
# =============================================================================
# Описание:
#   PowerShell скрипт для сборки, запуска и управления Docker контейнером
#   Использует docker-compose как основной механизм
#   Поддерживает экспорт и импорт Docker образов
#
# File: docker-manager.ps1
# Project: FastAPI Foundry
# Author: hypo69
# License: CC BY-NC-SA 4.0
# Copyright: © 2025 AiStros
# =============================================================================

param(
    [Parameter(Position = 0)]
    [string]$Command = 'help'
)

$ImageName  = 'fastapi-foundry'
$Version    = 'latest'
$Service    = 'fastapi-foundry'
$ComposeCmd = 'docker-compose'

# -----------------------------------------------------------------------------
# Проверки окружения
# -----------------------------------------------------------------------------
function Test-Requirements {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host 'Docker не установлен' -ForegroundColor Red
        exit 1
    }

    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Host 'docker-compose не установлен' -ForegroundColor Red
        exit 1
    }
}

# -----------------------------------------------------------------------------
# Справка
# -----------------------------------------------------------------------------
function Show-Help {
    Write-Host 'FastAPI Foundry Docker Manager (PowerShell)' -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Использование:' -ForegroundColor Yellow
    Write-Host '  .\docker-manager.ps1 <команда>'
    Write-Host ''
    Write-Host 'Команды:' -ForegroundColor Green
    Write-Host '  build     Собрать Docker образ'
    Write-Host '  run       Запустить контейнер'
    Write-Host '  stop      Остановить контейнер'
    Write-Host '  restart   Перезапустить контейнер'
    Write-Host '  logs      Показать логи'
    Write-Host '  shell     Войти в контейнер'
    Write-Host '  clean     Удалить контейнер и образ'
    Write-Host '  export    Экспортировать Docker образ'
    Write-Host '  import    Импортировать Docker образ'
    Write-Host '  status    Показать статус'
    Write-Host '  help      Показать справку'
}

# -----------------------------------------------------------------------------
# Docker operations
# -----------------------------------------------------------------------------
function Build-Image {
    Test-Requirements
    & $ComposeCmd build
}

function Start-Container {
    Test-Requirements
    & $ComposeCmd up -d
    Write-Host 'Контейнер запущен' -ForegroundColor Green
    Write-Host 'http://localhost:8000' -ForegroundColor Cyan
    Write-Host 'http://localhost:8000/docs' -ForegroundColor Cyan
}

function Stop-Container {
    Test-Requirements
    & $ComposeCmd down
}

function Restart-Container {
    Test-Requirements
    & $ComposeCmd restart
}

function Show-Logs {
    Test-Requirements
    & $ComposeCmd logs -f
}

function Enter-Shell {
    Test-Requirements
    & $ComposeCmd exec $Service /bin/bash
}

function Remove-All {
    Test-Requirements
    & $ComposeCmd down --remove-orphans
    docker rmi "$ImageName:$Version" 2>$null | Out-Null
}

function Export-Image {
    Test-Requirements
    $file = "$ImageName-$Version.tar"
    docker save -o $file "$ImageName:$Version"
    Write-Host "Образ экспортирован: $file" -ForegroundColor Green
}

function Import-Image {
    Test-Requirements
    $file = "$ImageName-$Version.tar"

    if (-not (Test-Path $file)) {
        Write-Host "Файл $file не найден" -ForegroundColor Red
        exit 1
    }

    docker load -i $file
}

function Show-Status {
    Test-Requirements
    & $ComposeCmd ps
    docker images | Select-String $ImageName | Out-Null
}

# -----------------------------------------------------------------------------
# Router
# -----------------------------------------------------------------------------
switch ($Command.ToLower()) {
    'build'   { Build-Image }
    'run'     { Start-Container }
    'stop'    { Stop-Container }
    'restart' { Restart-Container }
    'logs'    { Show-Logs }
    'shell'   { Enter-Shell }
    'clean'   { Remove-All }
    'export'  { Export-Image }
    'import'  { Import-Image }
    'status'  { Show-Status }
    'help'    { Show-Help }
    default {
        Write-Host "Неизвестная команда: $Command" -ForegroundColor Red
        Write-Host ''
        Show-Help
        exit 1
    }
}
