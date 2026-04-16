# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: FastAPI Foundry Smart Launcher (corrected regex version)
# =============================================================================
# Description:
#   Alternative launcher with simplified regex patterns for broader PowerShell
#   compatibility. Loads .env, detects or starts the Foundry service by
#   process name, then launches the FastAPI server.
#   Kept as a reference / fallback for environments where start.ps1 has issues.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\start_corrected.ps1
#   powershell -ExecutionPolicy Bypass -File .\start_corrected.ps1 -Config config.json
#
# File: scripts/start/start_corrected.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    # Path to the JSON config file (relative to project root)
    [string]$Config = 'config.json'
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host '🚀 FastAPI Foundry Smart Launcher' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Step 1: Ensure the Python virtual environment exists
# -----------------------------------------------------------------------------
$venvPath = "$Root\venv\Scripts\python.exe"

if (-not (Test-Path $venvPath)) {
    Write-Host '📦 First run - installing dependencies...' -ForegroundColor Yellow
    Write-Host 'This may take several minutes...' -ForegroundColor Yellow

    if (Test-Path "$Root\install.ps1") {
        try {
            & "$Root\install.ps1"
            Write-Host '✅ Installation complete!' -ForegroundColor Green
        } catch {
            Write-Host "❌ Installation error: $_" -ForegroundColor Red
            Write-Host 'Try running install.ps1 manually' -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host '❌ install.ps1 not found!' -ForegroundColor Red
        Write-Host 'Create venv manually: python -m venv venv' -ForegroundColor Yellow
        exit 1
    }
}

# -----------------------------------------------------------------------------
# Step 2: Load .env variables into the current process environment
# -----------------------------------------------------------------------------
function Load-EnvFile {
    <#
    .SYNOPSIS
        Reads a .env file and exports every KEY=VALUE pair as an environment variable.
    .PARAMETER EnvPath
        Full path to the .env file.
    .NOTES
        Skips blank lines and comment lines.
        Strips surrounding quotes from values.
        Masks sensitive keys in console output.
    #>
    param([string]$EnvPath)

    # Guard: .env must be a file, not a directory
    if (-not (Test-Path $EnvPath -PathType Leaf)) {
        if (Test-Path $EnvPath -PathType Container) {
            Write-Host "⚠️ .env is a directory, not a file: $EnvPath" -ForegroundColor Yellow
            Write-Host "💡 Create .env file from .env.example template" -ForegroundColor Cyan
        } else {
            Write-Host "⚠️ .env file not found: $EnvPath" -ForegroundColor Yellow
            Write-Host "💡 Copy .env.example to .env and configure your settings" -ForegroundColor Cyan
        }
        return
    }

    Write-Host '⚙️ Loading .env variables...' -ForegroundColor Gray

    $envVars = 0
    Get-Content $EnvPath | ForEach-Object {
        $line = $_.Trim()

        # Skip empty lines and comment lines
        if ($line -and -not $line.StartsWith('#')) {
            # Simplified regex: split on the first '=' only
            if ($line -match '^([^=]+)=(.*)$') {
                $key   = $matches[1].Trim()
                $value = $matches[2].Trim()

                # Strip surrounding double quotes
                if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
                # Strip surrounding single quotes
                if ($value.StartsWith("'") -and $value.EndsWith("'")) {
                    $value = $value.Substring(1, $value.Length - 2)
                }

                # Set as process-level environment variable (visible to child processes)
                [System.Environment]::SetEnvironmentVariable($key, $value)
                $envVars++

                # Never print secrets to the console
                if ($key -notmatch '(PASSWORD|SECRET|KEY|TOKEN|PAT)') {
                    Write-Host "  ✓ $key = $value" -ForegroundColor DarkGray
                } else {
                    Write-Host "  ✓ $key = ***" -ForegroundColor DarkGray
                }
            }
        }
    }

    Write-Host "✅ Loaded $envVars environment variables" -ForegroundColor Green
}

# Load .env from the project root
Load-EnvFile "$Root\.env"

# -----------------------------------------------------------------------------
# Step 3: Helper functions for Foundry detection
# -----------------------------------------------------------------------------
function Test-FoundryCli {
    <#
    .SYNOPSIS
        Returns $true if the 'foundry' CLI is available in PATH.
    .OUTPUTS
        bool
    #>
    try {
        Get-Command foundry -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Find-FoundryProcess {
    <#
    .SYNOPSIS
        Finds the running Foundry process by exact name.
    .OUTPUTS
        System.Diagnostics.Process | $null
    #>
    try {
        $process = Get-Process -Name "foundry" -ErrorAction Stop
        Write-Host "✅ Found Foundry process (PID: $($process.Id))" -ForegroundColor Green
        return $process
    } catch {
        Write-Host "🔍 No Foundry process found" -ForegroundColor Gray
        return $null
    }
}

function Get-FoundryPort {
    <#
    .SYNOPSIS
        Finds the TCP port on which the Foundry inference service is listening.
    .PARAMETER Process
        The Foundry process object returned by Find-FoundryProcess.
    .OUTPUTS
        string | $null  — port number as string, or $null if not found.
    #>
    param($Process)

    if (-not $Process) { return $null }

    try {
        # Get all LISTENING ports owned by the Foundry process
        $connections = netstat -ano | Select-String "$($Process.Id)" | Select-String "LISTENING"
        foreach ($conn in $connections) {
            # Simplified regex to extract the port number
            if ($conn -match ':([0-9]+)\s+.*LISTENING') {
                $port = $matches[1]
                # Verify this port actually serves the Foundry OpenAI-compatible API
                try {
                    Invoke-WebRequest -Uri "http://localhost:$port/v1/models" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop | Out-Null
                    Write-Host "✅ Foundry API confirmed on port $port" -ForegroundColor Green
                    return $port
                } catch {
                    # Port exists but doesn't respond to /v1/models — keep searching
                    Write-Host "⚠️ Port $port not responding, trying next..." -ForegroundColor Yellow
                    continue
                }
            }
        }
    } catch {
        Write-Host "⚠️ Could not determine Foundry port: $_" -ForegroundColor Yellow
    }
    return $null
}

# -----------------------------------------------------------------------------
# Step 4: Detect or start the Foundry AI service
# -----------------------------------------------------------------------------
Write-Host '🔍 Checking Local Foundry...' -ForegroundColor Cyan

$foundryProcess = Find-FoundryProcess
$foundryPort    = Get-FoundryPort $foundryProcess

if ($foundryPort) {
    # Foundry is already running — record the port for FastAPI
    Write-Host "✅ Foundry already running on port $foundryPort" -ForegroundColor Green
    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
} else {
    if (-not (Test-FoundryCli)) {
        # Foundry CLI not installed — server will run without AI support
        Write-Host '⚠️ Foundry CLI not found. Skipping AI startup.' -ForegroundColor Yellow
        Write-Host 'Install Foundry: https://github.com/foundry-rs/foundry' -ForegroundColor Gray
    } else {
        Write-Host '🚀 Foundry not running, starting service...' -ForegroundColor Yellow

        try {
            # Start the Foundry service and capture its output to parse the port
            $output = & foundry service start 2>&1
            Write-Host "📋 Foundry output: $output" -ForegroundColor Gray

            # Simplified regex to extract the port from the startup URL
            if ($output -match 'http://127\.0\.0\.1:([0-9]+)/') {
                $foundryPort = $matches[1]
                Write-Host "✅ Foundry started on port $foundryPort" -ForegroundColor Green
                $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
            } else {
                Write-Host '⚠️ Could not parse Foundry port from output. Continuing without AI.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Failed to start Foundry: $_" -ForegroundColor Red
            Write-Host '⚠️ Continuing without AI support.' -ForegroundColor Yellow
        }
    }
}

# -----------------------------------------------------------------------------
# Step 5: Launch the FastAPI server (blocking)
# -----------------------------------------------------------------------------
Write-Host '🐍 Starting FastAPI server...' -ForegroundColor Cyan

if (-not (Test-Path $venvPath)) {
    Write-Host '❌ ERROR: Python venv still not found after installation!' -ForegroundColor Red
    exit 1
}

Write-Host "🔗 FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT" -ForegroundColor Gray

Write-Host '🌐 FastAPI Foundry starting...' -ForegroundColor Green
Write-Host "📱 Web interface will be available at: http://localhost:9696" -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# Run FastAPI; this call blocks until the server is stopped (Ctrl+C)
try {
    & $venvPath run.py --config $Config
} catch {
    Write-Host "❌ Failed to start FastAPI server: $_" -ForegroundColor Red
    Write-Host "💡 Check logs and try running manually: $venvPath run.py" -ForegroundColor Yellow
    exit 1
}
