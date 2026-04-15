# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Автозапуск FastAPI Foundry при старте Windows
# =============================================================================
# Описание:
#   Запускает start.ps1 в silent mode, весь вывод перенаправляется в лог.
#   Предназначен для запуска через Windows Task Scheduler.
#
# Примеры:
#   # Прямой запуск:
#   .\autostart.ps1
#
#   # Регистрация в планировщике:
#   .\install-autostart.ps1
#
# File: autostart.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

# Директория и файл лога
$LogDir  = Join-Path $Root 'logs'
$LogFile = Join-Path $LogDir 'autostart.log'

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $ts   = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "$ts | $($Level.PadRight(8)) | autostart | $Message"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

Write-Log "=== FastAPI Foundry autostart ==="
Write-Log "Root: $Root"
Write-Log "Log:  $LogFile"

$StartScript = Join-Path $Root 'start.ps1'

if (-not (Test-Path $StartScript)) {
    Write-Log "start.ps1 not found: $StartScript" 'ERROR'
    exit 1
}

Write-Log "Запуск start.ps1..."

# Временные файлы для перехвата вывода
$StdoutFile = Join-Path $LogDir 'autostart_stdout.tmp'
$StderrFile = Join-Path $LogDir 'autostart_stderr.tmp'

try {
    $proc = Start-Process -FilePath 'powershell.exe' `
        -ArgumentList @(
            '-NonInteractive', '-NoProfile',
            '-ExecutionPolicy', 'Bypass',
            '-File', $StartScript
        ) `
        -WorkingDirectory $Root `
        -RedirectStandardOutput $StdoutFile `
        -RedirectStandardError  $StderrFile `
        -NoNewWindow `
        -PassThru `
        -Wait

    # Записать stdout в лог
    if (Test-Path $StdoutFile) {
        Get-Content $StdoutFile -Encoding UTF8 | ForEach-Object {
            $text = $_ -replace '\x1b\[[0-9;]*m', ''
            if ($text.Trim()) { Write-Log $text }
        }
        Remove-Item $StdoutFile -Force
    }

    # Записать stderr в лог с уровнем ERROR
    if (Test-Path $StderrFile) {
        Get-Content $StderrFile -Encoding UTF8 | ForEach-Object {
            $text = $_ -replace '\x1b\[[0-9;]*m', ''
            if ($text.Trim()) { Write-Log $text 'ERROR' }
        }
        Remove-Item $StderrFile -Force
    }

    $exitCode = $proc.ExitCode
    if ($exitCode -eq 0) {
        Write-Log "start.ps1 завершён успешно (exit 0)"
    } else {
        Write-Log "start.ps1 завершён с кодом $exitCode" 'ERROR'
        exit $exitCode
    }

} catch {
    Write-Log "Ошибка запуска start.ps1: $_" 'ERROR'
    exit 1
}
