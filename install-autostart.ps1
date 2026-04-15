# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Регистрация автозапуска FastAPI Foundry в Task Scheduler
# =============================================================================
# Описание:
#   Создаёт задачу Windows Task Scheduler, которая запускает autostart.ps1
#   при входе пользователя в систему (скрытое окно, вывод в лог).
#   Требует запуска от имени администратора.
#
# Примеры:
#   # Установить автозапуск:
#   .\install-autostart.ps1
#
#   # Удалить автозапуск:
#   .\install-autostart.ps1 -Uninstall
#
# File: install-autostart.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

param(
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'

$TaskName   = 'FastApiFoundry-Autostart'
$Root       = $PSScriptRoot
$Script     = Join-Path $Root 'autostart.ps1'
$LogDir     = Join-Path $Root 'logs'
$LogFile    = Join-Path $LogDir 'autostart.log'

# Проверка прав администратора
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
        ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '❌ Требуются права администратора. Запустите от имени Admin.' -ForegroundColor Red
    exit 1
}

# Удаление задачи
if ($Uninstall) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ Задача '$TaskName' удалена." -ForegroundColor Green
    } else {
        Write-Host "⚠️ Задача '$TaskName' не найдена." -ForegroundColor Yellow
    }
    exit 0
}

# Проверка autostart.ps1
if (-not (Test-Path $Script)) {
    Write-Host "❌ Не найден autostart.ps1: $Script" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Аргументы для powershell.exe (скрытый запуск, вывод в лог)
$PsArgs = "-NonInteractive -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Script`""

$Action  = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $PsArgs -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

# Удалить старую задачу если есть
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action   $Action `
    -Trigger  $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Description 'Автозапуск FastAPI Foundry при входе в систему' | Out-Null

Write-Host "✅ Задача '$TaskName' зарегистрирована." -ForegroundColor Green
Write-Host "📋 Лог запуска: $LogFile" -ForegroundColor Cyan
Write-Host "💡 Для удаления: .\install-autostart.ps1 -Uninstall" -ForegroundColor Gray
