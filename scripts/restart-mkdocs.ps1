# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Restart MkDocs Documentation Server
# =============================================================================
# Description:
#   Stops the running MkDocs process (by port from config.json),
#   then starts a new one in a detached window.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\restart-mkdocs.ps1
#
# File: restart-mkdocs.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

$ErrorActionPreference = 'Stop'

# --- config ---

$SCRIPT_DIR  = Split-Path -Parent $MyInvocation.MyCommand.Path
$CONFIG_FILE = Join-Path $SCRIPT_DIR 'config.json'
$MKDOCS_FILE = Join-Path $SCRIPT_DIR 'mkdocs.yml'
$PYTHON      = Join-Path $SCRIPT_DIR 'venv\Scripts\python.exe'

# --- functions ---

function Get-DocsPort {
    <#
    .SYNOPSIS
        Reads docs_server.port from config.json.
    .OUTPUTS
        int — port number (default 9697).
    #>
    if (-not (Test-Path $CONFIG_FILE)) {
        return 9697
    }
    try {
        $cfg = Get-Content $CONFIG_FILE -Raw | ConvertFrom-Json
        return [int]$cfg.docs_server.port
    } catch {
        return 9697
    }
}

function Stop-MkDocs {
    <#
    .SYNOPSIS
        Kills the process listening on the MkDocs port.
    .PARAMETER Port
        TCP port to check.
    .OUTPUTS
        bool — True if a process was killed.
    #>
    param ([int]$Port)

    $connections = netstat -ano | Select-String ":$Port\s"
    if (-not $connections) {
        Write-Host "⚪ No process found on port $Port"
        return $false
    }

    $killed = $false
    foreach ($line in $connections) {
        $parts = ($line -replace '\s+', ' ').Trim().Split(' ')
        $pid   = $parts[-1]
        if ($pid -match '^\d+$' -and [int]$pid -gt 0) {
            try {
                Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
                Write-Host "🛑 Killed PID $pid (port $Port)"
                $killed = $true
            } catch {
                # Process may have already exited
            }
        }
    }
    return $killed
}

function Start-MkDocs {
    <#
    .SYNOPSIS
        Starts mkdocs serve in a new detached window.
    .PARAMETER Port
        TCP port to bind.
    #>
    param ([int]$Port)

    if (-not (Test-Path $PYTHON)) {
        Write-Host "❌ Python not found: $PYTHON"
        Write-Host '   Run install.ps1 first.'
        exit 1
    }
    if (-not (Test-Path $MKDOCS_FILE)) {
        Write-Host "❌ mkdocs.yml not found: $MKDOCS_FILE"
        exit 1
    }

    $args = "-m mkdocs serve -f `"$MKDOCS_FILE`" --dev-addr 0.0.0.0:$Port"
    Start-Process -FilePath $PYTHON `
                  -ArgumentList $args `
                  -WorkingDirectory $SCRIPT_DIR `
                  -WindowStyle Normal

    Write-Host "✅ MkDocs started on http://localhost:$Port"
}

# --- main ---

$port = Get-DocsPort
Write-Host "🔄 Restarting MkDocs on port $port..."

Stop-MkDocs -Port $port
Start-Sleep -Milliseconds 800
Start-MkDocs -Port $port
