# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Оркестратор запуска Windows Sandbox
# =============================================================================
# Описание:
#   Управляет полным жизненным циклом запуска песочницы:
#   1. Опциональный шаг подготовки (sandbox-mapper.ps1)
#   2. Синхронизация проекта в staging-директорию
#   3. Запуск Windows Sandbox через предопределённую .wsb-конфигурацию
#
# Модель выполнения:
#   Файловая система хоста → синхронизация → staging-директория → монтирование в Sandbox
#
# Пример:
#   powershell -ExecutionPolicy Bypass -File .\sandbox-launcher.ps1
#
# File: sandbox-launcher.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Автор: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param (
    # Установка задержки (мс) для предотвращения гонки состояний файловой системы.
    [int]$DelayMs = 2000
)

# Установка политики немедленной остановки при ошибках (fail-fast).
$ErrorActionPreference = 'Stop'

# Определение базовой директории на основе расположения текущего скрипта.
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Пути к зависимым компонентам.
$MapperScript = Join-Path $BaseDir 'sandbox-mapper.ps1'
$WsbPath      = Join-Path $BaseDir 'sandbox.wsb'

<#
.SYNOPSIS
    Запуск внешнего скрипта PowerShell в изолированном процессе.

.DESCRIPTION
    Выполнение скрипта через дочерний процесс PowerShell с обходом политики выполнения.
    Обеспечение чистого контекста и изоляции ошибок.

.PARAMETER Path
    [string] Полный путь к файлу скрипта.

#.RETURNS
    [bool] — Успешность завершения дочернего процесса.
#>
[OutputType([bool])]
function Invoke-SandboxScript {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    # Проверка существования файла
    if (!(Test-Path $Path)) {
        Write-Host "❌ Invoke-SandboxScript: Файл не найден: $Path" -ForegroundColor Red
        return $false
    }

    # Выполнение скрипта в дочернем процессе
    & powershell -ExecutionPolicy Bypass -File $Path
    
    # Анализ кода завершения
    return ($LASTEXITCODE -eq 0)
}

<#
.SYNOPSIS
    Оркестрация конвейера запуска Sandbox.

.DESCRIPTION
    Последовательное выполнение этапов: синхронизация данных через mapper,
    пауза для стабилизации файловых дескрипторов и инициализация процесса WSB.

#.RETURNS
    [bool] — True при успешном прохождении всех стадий Pipeline.
#>
[OutputType([bool])]
function Invoke-SandboxPipeline {
    # Объявление локальных переменных
    [bool]$syncOk = $false

    try {
        # ШАГ 1: Синхронизация (зеркалирование) данных
        # Вызов внешнего маппера для подготовки staging-директории.
        if (Test-Path $MapperScript) {
            Write-Host '🔄 Синхронизация проекта через sandbox-mapper...' -ForegroundColor Cyan
            $syncOk = Invoke-SandboxScript -Path $MapperScript
            
            if (-not $syncOk) {
                throw 'Ошибка при синхронизации файлов'
            }
        } else {
            Write-Host '⚠️ Скрипт синхронизации не найден, пропуск шага.' -ForegroundColor Yellow
        }

        # ШАГ 2: Стабилизация состояния файловой системы
        Write-Host "⏳ Ожидание стабилизации ФС ($DelayMs мс)..." -ForegroundColor Cyan
        Start-Sleep -Milliseconds $DelayMs

        # ШАГ 3: Запуск процесса Windows Sandbox
        if (!(Test-Path $WsbPath)) {
            throw "Файл конфигурации Sandbox (.wsb) не найден по пути: $WsbPath"
        }
        
        Write-Host '🚀 Запуск Windows Sandbox...'
        Start-Process $WsbPath
        
        return $true
    }
    catch {
        Write-Host "❌ Критическая ошибка конвейера: $_" -ForegroundColor Red
        return $false
    }
}


# --- main ---
Write-Host '🔧 Инициализация инфраструктуры Sandbox...' -ForegroundColor Cyan

# Запуск основного конвейера (pipeline)
$result = Invoke-SandboxPipeline

# Финализация процесса
if ($result) {
    Write-Host '✅ Окружение Sandbox готово к работе' -ForegroundColor Green
} else {
    Write-Host '❌ Ошибка при инициализации Sandbox' -ForegroundColor Red
}