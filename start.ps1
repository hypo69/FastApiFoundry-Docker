# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: FastAPI Foundry Smart Launcher
# =============================================================================
# Description:
#   Main entry point for starting the FastAPI Foundry server.
#   On first run, automatically installs all Python dependencies via install.ps1.
#   Loads .env variables, detects or starts the Foundry AI service,
#   optionally starts llama.cpp and MkDocs servers, then launches FastAPI.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\start.ps1
#   powershell -ExecutionPolicy Bypass -File .\start.ps1 -Config config.json
#
# File: start.ps1
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
# Step 1: Dependency check and auto-installation
# On first run the venv does not exist yet — trigger install.ps1 to create it.
# -----------------------------------------------------------------------------

# Activate the virtual environment if it already exists (sets PATH for pip/python)
$ActivateScript = "$Root\venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    . $ActivateScript
    Write-Host '✅ venv activated' -ForegroundColor Green
} else {
    Write-Host '⚠️ venv/Scripts/Activate.ps1 not found' -ForegroundColor Yellow
}

# Prefer python.exe; fall back to python311.exe for non-standard installs
$venvPath = "$Root\venv\Scripts\python.exe"
if (-not (Test-Path $venvPath)) {
    $venvPath = "$Root\venv\Scripts\python311.exe"
}

# If neither exists, the venv is missing — run the installer
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
        Write-Host 'Create venv manually: python311 -m venv venv' -ForegroundColor Yellow
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
        - Skips blank lines and lines starting with '#'.
        - Strips surrounding single/double quotes from values.
        - Masks sensitive keys (PASSWORD, SECRET, KEY, TOKEN, PAT) in console output.
    #>
    param([string]$EnvPath)
    
    # Guard: .env must be a file, not a directory (common mistake on Windows)
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
    try {
        Get-Content $EnvPath | ForEach-Object {
            $line = $_.Trim()
            
            # Skip empty lines and comment lines
            if ($line -and -not $line.StartsWith('#')) {
                # Match KEY=VALUE (value may be empty or contain '=')
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
    } catch {
        Write-Host "❌ Error loading .env file: $_" -ForegroundColor Red
    }
}

# Load .env file
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

function Get-FoundryPort {
    <#
    .SYNOPSIS
        Finds the TCP port on which the Foundry inference service is listening.
    .DESCRIPTION
        Locates the 'Inference.Service.Agent' process, then scans its LISTENING
        ports via netstat and probes each one with a GET /v1/models request.
        Returns the first port that responds with HTTP 200.
    .OUTPUTS
        string | $null  — port number as string, or $null if not found.
    #>
    # Find the Foundry inference process by name pattern
    $foundryProcess = Get-Process | Where-Object { $_.ProcessName -like "Inference.Service.Agent*" }
    if (-not $foundryProcess) { return $null }
    
    # Get all LISTENING ports owned by that process
    $netstatOutput = netstat -ano | Select-String "$($foundryProcess.Id)" | Select-String "LISTENING"
    foreach ($line in $netstatOutput) {
        if ($line -match ':(\d+)\s') {
            $port = $matches[1]
            try {
                # Confirm the port actually serves the Foundry OpenAI-compatible API
                $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/v1/models" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ Foundry API found on port $port" -ForegroundColor Green
                    return $port
                }
            } catch { }
        }
    }
    return $null
}

# -----------------------------------------------------------------------------
# Step 4: Detect or start the Foundry AI service
# Foundry uses a dynamic port — we discover it at runtime and pass it to FastAPI.
# -----------------------------------------------------------------------------
Write-Host '🔍 Checking Local Foundry...' -ForegroundColor Cyan

# Check if Foundry is already running (e.g. started manually or by autostart)
$foundryPort = Get-FoundryPort

if ($foundryPort) {
    # Foundry is up — just record the port for FastAPI
    Write-Host "✅ Foundry already running on port $foundryPort" -ForegroundColor Green
    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
} else {
    if (-not (Test-FoundryCli)) {
        # Foundry CLI not installed — skip AI, server will run without it
        Write-Host '⚠️ Foundry CLI not found. Skipping AI startup.' -ForegroundColor Yellow
        Write-Host 'Install Foundry from Microsoft' -ForegroundColor Gray
    } else {
        Write-Host '🚀 Starting Foundry service...' -ForegroundColor Yellow
        
        try {
            # Launch Foundry in a minimized window so it doesn't block this console
            Start-Process -FilePath "foundry" -ArgumentList "service", "start" -WindowStyle Minimized -NoNewWindow:$false
            Write-Host "Foundry service start command executed" -ForegroundColor Gray
            
            # Poll until Foundry is ready (up to 20 seconds)
            for ($i = 1; $i -le 10; $i++) {
                Start-Sleep 2
                $foundryPort = Get-FoundryPort
                if ($foundryPort) {
                    Write-Host "✅ Foundry started on port $foundryPort" -ForegroundColor Green
                    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
                    break
                }
                Write-Host "⏳ Waiting for Foundry to start... ($i/10)" -ForegroundColor Gray
            }
            
            if (-not $foundryPort) {
                Write-Host "❌ Foundry failed to start or port not found" -ForegroundColor Red
                Write-Host '⚠️ Continuing without AI support.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Failed to start Foundry: $_" -ForegroundColor Red
            Write-Host '⚠️ Continuing without AI support.' -ForegroundColor Yellow
        }
    }
}

# Export the full base URL so FastAPI can build requests to Foundry
if ($foundryPort) {
    $env:FOUNDRY_BASE_URL = "http://localhost:$foundryPort/v1/"
    Write-Host "🔗 FOUNDRY_BASE_URL = $env:FOUNDRY_BASE_URL" -ForegroundColor Green
} else {
    Write-Host "⚠️ Foundry not available - AI features disabled" -ForegroundColor Yellow
}

# -----------------------------------------------------------------------------
# Step 5: Optional MkDocs documentation server
# Enabled via docs_server.enabled = true in config.json
# -----------------------------------------------------------------------------
Write-Host '🔍 Checking Docs Server configuration...' -ForegroundColor Cyan

# Read docs_server section from config.json
try {
    $configContent = Get-Content "$Root\$Config" | Out-String
    $parsedConfig = $configContent | ConvertFrom-Json
    $docsServerConfig = $parsedConfig.docs_server
} catch {
    Write-Host "❌ Error reading config.json for docs_server: $_" -ForegroundColor Red
    $docsServerConfig = $null
}

if ($docsServerConfig -and $docsServerConfig.enabled) {
    Write-Host "🚀 Starting MkDocs server on port $($docsServerConfig.port)..." -ForegroundColor Yellow
    try {
        # Run mkdocs in a separate minimized window so it doesn't block this console
        Start-Process powershell.exe -ArgumentList @(
            '-NonInteractive', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-Command', "mkdocs serve -a 0.0.0.0:$($docsServerConfig.port)"
        ) -WindowStyle Minimized -PassThru | Out-Null
        Write-Host "✅ MkDocs server started in background" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to start MkDocs server: $_" -ForegroundColor Red
        Write-Host "⚠️ Continuing without docs server." -ForegroundColor Yellow
    }
} else {
    Write-Host "💡 Docs server is disabled in config.json (skipping)" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# Step 6: Optional llama.cpp local inference server
# Only started when LLAMA_MODEL_PATH and LLAMA_AUTO_START=true are set in .env
# -----------------------------------------------------------------------------
$llamaModelPath = [System.Environment]::GetEnvironmentVariable('LLAMA_MODEL_PATH')
$llamaAutoStart = [System.Environment]::GetEnvironmentVariable('LLAMA_AUTO_START')

if ($llamaModelPath -and $llamaAutoStart -eq 'true') {
    Write-Host '🦙 Starting llama.cpp server...' -ForegroundColor Cyan

    $llamaScript = Join-Path $Root 'scripts\llama-start.ps1'
    if (Test-Path $llamaScript) {
        $llamaPort = [System.Environment]::GetEnvironmentVariable('LLAMA_PORT')
        # Default to port 8080 if not specified in .env
        if (-not $llamaPort) { $llamaPort = 8080 }

        # Start llama.cpp in a separate minimized window; it keeps running in background
        Start-Process powershell.exe -ArgumentList @(
            '-NonInteractive', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', $llamaScript,
            '-ModelPath', $llamaModelPath,
            '-Port', $llamaPort
        ) -WindowStyle Minimized

        # Tell FastAPI where to find the llama.cpp OpenAI-compatible endpoint
        $env:LLAMA_BASE_URL = "http://127.0.0.1:$llamaPort/v1"
        Write-Host "✅ llama.cpp starting (port $llamaPort)" -ForegroundColor Green
        Write-Host "🔗 LLAMA_BASE_URL = $env:LLAMA_BASE_URL" -ForegroundColor Green
    } else {
        Write-Host '⚠️ scripts\llama-start.ps1 not found, skipping llama.cpp' -ForegroundColor Yellow
    }
} elseif ($llamaModelPath) {
    # Model path is configured but auto-start is off — user must start manually
    Write-Host "💡 llama.cpp model configured but LLAMA_AUTO_START != true (skipping)" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# Step 7: Launch the FastAPI server (blocking — keeps this window open)
# -----------------------------------------------------------------------------
Write-Host '🐍 Starting FastAPI server...' -ForegroundColor Cyan

# Final guard: venv must exist at this point (either pre-existing or just installed)
if (-not (Test-Path $venvPath)) {
    Write-Host '❌ ERROR: Python venv still not found after installation!' -ForegroundColor Red
    Write-Host "Expected path: $venvPath" -ForegroundColor Yellow
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
    Write-Host "💡 Or check if all dependencies are installed: $venvPath -m pip list" -ForegroundColor Yellow
    exit 1
}