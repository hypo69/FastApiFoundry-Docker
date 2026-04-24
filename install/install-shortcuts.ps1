# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Desktop Shortcuts Installer
# =============================================================================
# Description:
#   Creates two Windows desktop shortcuts for launching FastAPI Foundry:
#     1. "AI Assistant"          — console window via start.ps1 (normal window)
#     2. "AI Assistant (Silent)" — hidden window via autostart.ps1 (no console)
#   Icon source: assets\icons\icon128.png (converted to icon.ico automatically).
#
# Examples:
#   .\install-shortcuts.ps1
#
# File: install\install-shortcuts.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
# Changes in 0.6.1:
#   - Icon path changed from install\icon.ico to project root icon.ico
#   - Auto-builds icon.ico from assets\icons\ via make-ico.ps1 if missing
#   - WorkingDirectory corrected to project root (not install\ subfolder)
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param (
    [switch]$Silent
)

$ErrorActionPreference = 'Stop'

# --- paths ---

# Project root is one level above this script (install\ subfolder)
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
$DESKTOP_PATH = [Environment]::GetFolderPath('Desktop')
$ICON_PATH    = Join-Path $PROJECT_ROOT 'icon.ico'
$MAKE_ICO     = Join-Path $PROJECT_ROOT 'install\make-ico.ps1'
$START_PS1    = Join-Path $PROJECT_ROOT 'start.ps1'
$AUTOSTART_PS1 = Join-Path $PROJECT_ROOT 'autostart.ps1'

# --- functions ---

function Ensure-Icon {
    <#
    .SYNOPSIS
        Builds icon.ico from assets\icons\ PNGs if it does not exist yet.
    #>
    if (Test-Path $ICON_PATH) {
        Write-Host "  ✅ icon.ico found: $ICON_PATH"
        return
    }

    if (-not (Test-Path $MAKE_ICO)) {
        Write-Host '  ⚠️  make-ico.ps1 not found — shortcuts will use default PowerShell icon' -ForegroundColor Yellow
        return
    }

    Write-Host '  🔧 Building icon.ico from assets\icons\...'
    & powershell.exe -ExecutionPolicy Bypass -File $MAKE_ICO -ProjectRoot $PROJECT_ROOT
    if (Test-Path $ICON_PATH) {
        Write-Host "  ✅ icon.ico created: $ICON_PATH"
    } else {
        Write-Host '  ⚠️  icon.ico was not created — shortcuts will use default icon' -ForegroundColor Yellow
    }
}

function New-AppShortcut {
    <#
    .SYNOPSIS
        Creates a .lnk shortcut on the Desktop.
    .PARAMETER Name
        Shortcut filename (without .lnk).
    .PARAMETER Arguments
        PowerShell arguments string.
    .PARAMETER WindowStyle
        1 = normal, 7 = minimized/hidden.
    .PARAMETER Description
        Tooltip text shown on hover.
    #>
    param (
        [string]$Name,
        [string]$Arguments,
        [int]$WindowStyle,
        [string]$Description
    )

    $lnkPath  = Join-Path $DESKTOP_PATH "$Name.lnk"
    $wsh      = New-Object -ComObject WScript.Shell
    $shortcut = $wsh.CreateShortcut($lnkPath)

    $shortcut.TargetPath       = 'powershell.exe'
    $shortcut.Arguments        = $Arguments
    $shortcut.WorkingDirectory = $PROJECT_ROOT
    $shortcut.WindowStyle      = $WindowStyle
    $shortcut.Description      = $Description

    if (Test-Path $ICON_PATH) {
        $shortcut.IconLocation = $ICON_PATH
    }

    $shortcut.Save()
    Write-Host "  ✅ $lnkPath" -ForegroundColor Gray
}

# --- main ---

Write-Host '🖼️  Preparing icon...'
Ensure-Icon

Write-Host '🔗 Creating desktop shortcuts...'

New-AppShortcut `
    -Name        'AI Assistant' `
    -Arguments   "-ExecutionPolicy Bypass -File `"$START_PS1`"" `
    -WindowStyle 1 `
    -Description 'FastAPI Foundry — AI Assistant (console mode)'

New-AppShortcut `
    -Name        'AI Assistant (Silent)' `
    -Arguments   "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$AUTOSTART_PS1`"" `
    -WindowStyle 7 `
    -Description 'FastAPI Foundry — AI Assistant (silent mode)'

# Docs shortcut: opens browser directly on the docs port (no server start needed)
$DOCS_PORT = 9697
try {
    $cfg = Get-Content (Join-Path $PROJECT_ROOT 'config.json') -Raw | ConvertFrom-Json
    if ($cfg.docs_server.port) { $DOCS_PORT = [int]$cfg.docs_server.port }
} catch { }

$docsLnk  = Join-Path $DESKTOP_PATH 'AI Assistant Docs.lnk'
$wsh      = New-Object -ComObject WScript.Shell
$docsShortcut = $wsh.CreateShortcut($docsLnk)
$docsShortcut.TargetPath       = "http://localhost:$DOCS_PORT"
$docsShortcut.Description      = "FastAPI Foundry — Documentation (http://localhost:$DOCS_PORT)"
if (Test-Path $ICON_PATH) { $docsShortcut.IconLocation = $ICON_PATH }
$docsShortcut.Save()
Write-Host "  ✅ $docsLnk" -ForegroundColor Gray

Write-Host '✅ Done.' -ForegroundColor Green
