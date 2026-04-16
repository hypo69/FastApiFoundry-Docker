# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Desktop Shortcuts Installer
# =============================================================================
# Description:
#   Creates two Windows desktop shortcuts for launching FastAPI Foundry:
#     1. "AI Assistant"         — console window via start.ps1 (normal window)
#     2. "AI Assistant (Silent)" — hidden window via autostart.ps1 (no console)
#   If icon.ico exists in the project root it is applied to both shortcuts.
#
# Examples:
#   .\install-shortcuts.ps1
#
# File: install\install-shortcuts.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

# Resolve the directory that contains this script (install\ subfolder)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Resolve the current user's Desktop path (works for any locale)
$DesktopPath = [Environment]::GetFolderPath('Desktop')

# WScript.Shell COM object is the standard Windows API for creating .lnk shortcuts
$WshShell = New-Object -ComObject WScript.Shell

# Optional icon — used for both shortcuts if present
$IconPath = Join-Path $ScriptDir 'icon.ico'

# -----------------------------------------------------------------------------
# Shortcut 1: Console mode — opens a visible PowerShell window
# Useful for monitoring startup output and debugging
# -----------------------------------------------------------------------------
$ShortcutPath1 = Join-Path $DesktopPath 'AI Assistant.lnk'
$Shortcut1 = $WshShell.CreateShortcut($ShortcutPath1)

$Shortcut1.TargetPath       = 'powershell.exe'
$Shortcut1.Arguments        = "-ExecutionPolicy Bypass -File `"$ScriptDir\start.ps1`""
$Shortcut1.WorkingDirectory = $ScriptDir
$Shortcut1.WindowStyle      = 1          # 1 = normal window
$Shortcut1.Description      = 'AI Assistant (console mode)'

if (Test-Path $IconPath) {
    $Shortcut1.IconLocation = $IconPath
}

$Shortcut1.Save()

# -----------------------------------------------------------------------------
# Shortcut 2: Silent mode — hidden window, no console visible to the user
# Intended for background autostart (e.g. on login via Task Scheduler)
# -----------------------------------------------------------------------------
$ShortcutPath2 = Join-Path $DesktopPath 'AI Assistant (Silent).lnk'
$Shortcut2 = $WshShell.CreateShortcut($ShortcutPath2)

$Shortcut2.TargetPath       = 'powershell.exe'
$Shortcut2.Arguments        = "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptDir\autostart.ps1`""
$Shortcut2.WorkingDirectory = $ScriptDir
$Shortcut2.WindowStyle      = 7          # 7 = minimized/hidden window
$Shortcut2.Description      = 'AI Assistant (silent mode)'

if (Test-Path $IconPath) {
    $Shortcut2.IconLocation = $IconPath
}

$Shortcut2.Save()

Write-Host "✅ Shortcuts created on Desktop:" -ForegroundColor Green
Write-Host "   $ShortcutPath1" -ForegroundColor Gray
Write-Host "   $ShortcutPath2" -ForegroundColor Gray
