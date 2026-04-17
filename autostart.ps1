# -*- coding: utf-8 -*-
# =============================================================================
# Process name: FastAPI Foundry autostart on Windows startup
# =============================================================================
# Description:
#   Launches start.ps1 in silent mode, all output is redirected to the log.
#   Intended for launching via Windows Task Scheduler.
#
# Examples:
#   # Direct launch:
#   .\autostart.ps1
#
#   # Registration in the scheduler:
#   .\install\install-autostart.ps1
#
# File: autostart.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: December 9, 2025
# =============================================================================

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

# Directory and log file
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

# Install PowerShell 7 if not already installed
$pwsh = 'C:\Program Files\PowerShell\7\pwsh.exe'
if (-not (Test-Path $pwsh)) {
    $msi = Join-Path $Root 'bin\PowerShell-7.4.6-win-x64.msi'
    if (Test-Path $msi) {
        Write-Log "Installing PowerShell 7 from $msi"
        Start-Process msiexec.exe -ArgumentList "/i `"$msi`" /quiet /norestart" -Wait
        Write-Log "PowerShell 7 installed"
    } else {
        Write-Log "PowerShell 7 MSI not found: $msi" 'WARNING'
    }
} else {
    Write-Log "PowerShell 7 already installed"
}

# Virtual environment activation
$ActivateScript = Join-Path $Root 'venv\Scripts\Activate.ps1'
if (Test-Path $ActivateScript) {
    . $ActivateScript
    Write-Log "venv activated: $ActivateScript"
} else {
    Write-Log "venv/Scripts/Activate.ps1 not found, skipping" 'WARNING'
}

$StartScript = Join-Path $Root 'start.ps1'

if (-not (Test-Path $StartScript)) {
    Write-Log "start.ps1 not found: $StartScript" 'ERROR'
    exit 1
}

Write-Log "Launching start.ps1..."

# Temporary files for capturing output
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

    # Write stdout to log
    if (Test-Path $StdoutFile) {
        Get-Content $StdoutFile -Encoding UTF8 | ForEach-Object {
            $text = $_ -replace '\x1b\[[0-9;]*m', ''
            if ($text.Trim()) { Write-Log $text }
        }
        Remove-Item $StdoutFile -Force
    }

    # Write stderr to log with ERROR level
    if (Test-Path $StderrFile) {
        Get-Content $StderrFile -Encoding UTF8 | ForEach-Object {
            $text = $_ -replace '\x1b\[[0-9;]*m', ''
            if ($text.Trim()) { Write-Log $text 'ERROR' }
        }
        Remove-Item $StderrFile -Force
    }

    $exitCode = $proc.ExitCode
    if ($exitCode -eq 0) {
        Write-Log "start.ps1 completed successfully (exit 0)"
    } else {
        Write-Log "start.ps1 completed with code $exitCode" 'ERROR'
        exit $exitCode
    }

} catch {
    Write-Log "Error launching start.ps1: $_" 'ERROR'
    exit 1
}
