# scripts/run-qa.ps1
# -*- coding: utf-8 -*-

# =============================================================================
# Название процесса: Запуск полного цикла QA (Linting, Types, Tests, Coverage)
# =============================================================================
# Описание:
#   Автоматизирует запуск статического анализа (ruff, mypy) и тестов (pytest)
#   с генерацией отчета о покрытии кода в формате HTML.
#
# File: scripts/run-qa.ps1
# Project: AiStros
# Author: Gemini Code Assist
# Copyright: © 2026 AiStros
# Version: 1.0.0
# =============================================================================

<#
.SYNOPSIS
    Запускает полный цикл контроля качества (QA) для проекта AiStros.
.DESCRIPTION
    Этот скрипт выполняет следующие шаги:
    1. Активирует виртуальное окружение Python.
    2. Запускает линтер Ruff для проверки стиля кода.
    3. Запускает статический анализатор Mypy для проверки типов.
    4. Запускает Pytest для выполнения всех тестов.
    5. Генерирует отчет о покрытии кода в формате HTML.
    6. Открывает сгенерированный HTML отчет в браузере.
.EXAMPLE
    .\run-qa.ps1
    Запускает полный цикл QA.
.EXAMPLE
    .\run-qa.ps1 -SkipCoverageReport
    Запускает QA, но не открывает отчет о покрытии.
.PARAMETER SkipCoverageReport
    Если указан, HTML отчет о покрытии не будет открыт автоматически.
#>
[CmdletBinding()]
param(
    [switch]$SkipCoverageReport
)

$script:RootPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$script:VenvPath = Join-Path $script:RootPath "..\venv"
$script:SourcePath = Join-Path $script:RootPath "..\src"
$script:CoverageReportDir = Join-Path $script:RootPath "..\tests\reports\coverage"
$script:CoverageReportPath = Join-Path $script:CoverageReportDir "index.html"

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = 'INFO',
        [string]$Color = 'White'
    )
    $timestamp = Get-Date -Format 'HH:mm:ss'
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $Color
}

function Activate-Venv {
    Write-Log "Активация виртуального окружения..." -Color Cyan
    if (Test-Path (Join-Path $script:VenvPath "Scripts\Activate.ps1")) {
        . (Join-Path $script:VenvPath "Scripts\Activate.ps1")
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Ошибка активации виртуального окружения." -Level ERROR -Color Red
            exit 1
        }
        Write-Log "Виртуальное окружение активировано." -Color Green
    } else {
        Write-Log "Виртуальное окружение не найдено по пути: $script:VenvPath. Убедитесь, что оно создано." -Level ERROR -Color Red
        exit 1
    }
}

function Run-Command {
    param(
        [string]$Command,
        [string]$Description,
        [string]$SuccessMessage,
        [string]$ErrorMessage
    )
    Write-Log "Запуск: $Description" -Color Cyan
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Log $ErrorMessage -Level ERROR -Color Red
        exit 1
    }
    Write-Log $SuccessMessage -Color Green
}

# --- Main Script Logic ---
try {
    Write-Log "Начало полного цикла QA для AiStros..." -Color Yellow

    # Очистка предыдущих отчетов
    Write-Log "Подготовка: Очистка старых отчетов..." -Color Cyan
    & powershell -ExecutionPolicy Bypass -File (Join-Path $script:RootPath "clear-reports.ps1")

    # Создание директории для отчетов, если она отсутствует
    if (!(Test-Path $script:CoverageReportDir)) {
        New-Item -Path $script:CoverageReportDir -ItemType Directory -Force | Out-Null
    }
    Activate-Venv
    Run-Command "ruff check $script:SourcePath" "Ruff (линтер)" "Ruff завершен успешно." "Ruff обнаружил ошибки."
    Run-Command "mypy $script:SourcePath" "Mypy (проверка типов)" "Mypy завершен успешно." "Mypy обнаружил ошибки типов."
    $script:JUnitReport = Join-Path $script:RootPath "..\tests\reports\junit.xml"
    Run-Command "pytest --cov=$script:SourcePath --cov-report=html:$script:CoverageReportDir --junitxml=$script:JUnitReport" "Pytest (тесты и покрытие)" "Все тесты пройдены успешно, отчет о покрытии сгенерирован." "Тесты завершились с ошибками."
    if (-not $SkipCoverageReport) {
        if (Test-Path $script:CoverageReportPath) {
            Write-Log "Открытие HTML отчета о покрытии: $script:CoverageReportPath" -Color Green
            Start-Process $script:CoverageReportPath
        } else {
            Write-Log "HTML отчет о покрытии не найден по пути: $script:CoverageReportPath" -Level WARNING -Color Yellow
        }
    }
    Write-Log "Полный цикл QA завершен успешно!" -Color Green
} catch {
    Write-Log "Критическая ошибка в скрипте QA: $($_.Exception.Message)" -Level ERROR -Color Red
    exit 1
}