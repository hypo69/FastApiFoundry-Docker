# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Create requirements.txt
# =============================================================================
# Description:
#   Generates requirements.txt using one of three strategies:
#     freeze   — full pip freeze snapshot of the active venv
#     pipreqs  — only packages actually imported in source code (auto-installs pipreqs)
#     clean    — wipe venv, recreate it, then prompt to install deps manually
#
# Examples:
#   .\create_requirements.ps1 -Mode pipreqs
#   .\create_requirements.ps1 -Mode freeze -ProjectPath . -VenvPath venv
#   .\create_requirements.ps1 -Mode clean
#
# File: scripts/create_requirements.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param (
    [ValidateSet('freeze', 'pipreqs', 'clean')]
    [string]$Mode = 'pipreqs',

    [string]$ProjectPath = (Split-Path $PSScriptRoot -Parent),

    [string]$VenvPath = (Join-Path (Split-Path $PSScriptRoot -Parent) 'venv')
)

$ErrorActionPreference = 'Stop'

# --- main ---

function Write-Log {
    param ([string]$Message, [string]$Level = 'INFO')
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $color = switch ($Level) {
        'WARN'  { 'Yellow' }
        'ERROR' { 'Red' }
        default { 'Cyan' }
    }
    Write-Host "[$ts][$Level] $Message" -ForegroundColor $color
}

function Test-CommandExists {
    param ([string]$Command)
    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Invoke-ActivateVenv {
    param ([string]$Path)
    $activate = Join-Path $Path 'Scripts\Activate.ps1'
    if (-not (Test-Path $activate)) { throw "venv not found at: $Path" }
    Write-Log "Activating venv: $Path"
    . $activate
}

function Invoke-Freeze {
    param ([string]$ProjectPath)
    Write-Log 'Running pip freeze...'
    $out = Join-Path $ProjectPath 'requirements.txt'
    pip freeze | Out-File $out -Encoding utf8
    Write-Log "requirements.txt written (freeze): $out"
}

function Invoke-Pipreqs {
    param ([string]$ProjectPath)
    if (-not (Test-CommandExists 'pipreqs')) {
        Write-Log 'pipreqs not found — installing...' 'WARN'
        pip install pipreqs | Out-Null
    }
    Write-Log 'Running pipreqs...'
    pipreqs $ProjectPath --force
    Write-Log "requirements.txt written (pipreqs): $ProjectPath"
}

function Invoke-CleanVenv {
    param ([string]$ProjectPath, [string]$VenvPath)
    if (Test-Path $VenvPath) {
        Write-Log "Removing existing venv: $VenvPath" 'WARN'
        Remove-Item -Recurse -Force $VenvPath
    }
    Write-Log 'Creating new venv...'
    python -m venv $VenvPath
    Invoke-ActivateVenv -Path $VenvPath
    Write-Log 'Venv ready. Install your packages, then re-run with -Mode freeze.' 'WARN'
}

# --- main ---

try {
    Write-Log "Mode: $Mode | Project: $ProjectPath | Venv: $VenvPath"

    if ($Mode -ne 'clean') {
        Invoke-ActivateVenv -Path $VenvPath
    }

    switch ($Mode) {
        'freeze'  { Invoke-Freeze   -ProjectPath $ProjectPath }
        'pipreqs' { Invoke-Pipreqs  -ProjectPath $ProjectPath }
        'clean'   { Invoke-CleanVenv -ProjectPath $ProjectPath -VenvPath $VenvPath }
    }

    Write-Host '✅ Done' -ForegroundColor Green
}
catch {
    Write-Log $_.Exception.Message 'ERROR'
    exit 1
}
