# -*- coding: utf-8 -*-
# =============================================================================
# Process name: Registering FastAPI Foundry autostart in Task Scheduler
# =============================================================================
# Description:
#   Creates a Windows Task Scheduler task that launches autostart.ps1
#   upon user login (hidden window, output to log).
#   Requires running as administrator.
#
# Examples:
#   # Install autostart:
#   .\install-autostart.ps1
#
#   # Remove autostart:
#   .\install-autostart.ps1 -Uninstall
#
# File: install-autostart.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: December 9, 2025
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

# Administrator rights check
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
        ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '❌ Administrator rights required. Run as Admin.' -ForegroundColor Red
    exit 1
}

# Task removal
if ($Uninstall) {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ Task '$TaskName' deleted." -ForegroundColor Green
    } else {
        Write-Host "⚠️ Task '$TaskName' not found." -ForegroundColor Yellow
    }
    exit 0
}

# Checking autostart.ps1
if (-not (Test-Path $Script)) {
    Write-Host "❌ autostart.ps1 not found: $Script" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Arguments for powershell.exe (hidden launch, output to log)
$PsArgs = "-NonInteractive -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Script`""

$Action  = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $PsArgs -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

# Remove old task if it exists
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action   $Action `
    -Trigger  $Trigger `
    -Settings $Settings `
    -RunLevel Highest `
    -Description 'FastAPI Foundry autostart upon login' | Out-Null

Write-Host "✅ Task '$TaskName' registered." -ForegroundColor Green
Write-Host "📋 Launch log: $LogFile" -ForegroundColor Cyan
Write-Host "💡 To remove: .\install-autostart.ps1 -Uninstall" -ForegroundColor Gray
