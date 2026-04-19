# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: FastAPI Foundry Launcher Menu
# =============================================================================
# Description:
#   Interactive menu for choosing the FastAPI Foundry launch mode.
#   Can also be driven non-interactively via the -Mode parameter.
#   Delegates actual work to dedicated scripts (start.ps1, setup-env.ps1, etc.)
#
# Examples:
#   .\launcher.ps1                  # show interactive menu
#   .\launcher.ps1 -Mode quick      # quick launch (auto-install + Foundry + FastAPI)
#   .\launcher.ps1 -Mode api        # FastAPI only, no Foundry
#   .\launcher.ps1 -Mode dev        # development mode with verbose output
#   .\launcher.ps1 -Mode docker     # run in Docker container
#   .\launcher.ps1 -Mode setup      # configure .env variables
#   .\launcher.ps1 -Mode diag       # run system diagnostics
#
# File: launcher.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    # Non-interactive mode selector. Leave empty to show the interactive menu.
    [string]$Mode = ""
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

function Show-Menu {
    <#
    .SYNOPSIS
        Clears the screen and renders the main launcher menu.
    #>
    Clear-Host
    Write-Host "🚀 FastAPI Foundry Launcher" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Select launch type:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. 🎯 Quick Launch (Recommended)" -ForegroundColor Green
    Write-Host "   Auto-installation + Foundry + FastAPI"
    Write-Host ""
    Write-Host "2. 🐍 FastAPI Server Only" -ForegroundColor Cyan
    Write-Host "   Web interface without Foundry"
    Write-Host ""
    Write-Host "3. 🔧 Development Mode" -ForegroundColor Magenta
    Write-Host "   With verbose output and debugging"
    Write-Host ""
    Write-Host "4. 🐳 Docker Launch" -ForegroundColor Blue
    Write-Host "   Run in Docker container"
    Write-Host ""
    Write-Host "5. ⚙️ Environment Setup" -ForegroundColor Yellow
    Write-Host "   Configure .env variables"
    Write-Host ""
    Write-Host "6. 🔍 Diagnostics" -ForegroundColor DarkYellow
    Write-Host "   Check system and fix issues"
    Write-Host ""
    Write-Host "0. ❌ Exit" -ForegroundColor Red
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Start-QuickLaunch {
    <#
    .SYNOPSIS
        Runs the full startup sequence: install deps, start Foundry, start FastAPI.
    .NOTES
        Delegates to start.ps1 which handles all steps automatically.
    #>
    Write-Host "🎯 Quick Launch FastAPI Foundry" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    & "$Root\start.ps1"
}

function Start-FastAPIOnly {
    <#
    .SYNOPSIS
        Starts only the FastAPI server without attempting to start Foundry.
    .NOTES
        Useful when Foundry is already running or not needed (e.g. llama.cpp mode).
    #>
    Write-Host "🐍 Running FastAPI Server Only" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan

    # Prefer the venv Python; fall back to system Python if venv is missing
    $pythonExe = "$Root\venv\Scripts\python.exe"
    if (-not (Test-Path $pythonExe)) {
        $pythonExe = "python"
    }

    Write-Host "🌐 Starting without Foundry..." -ForegroundColor Yellow
    & $pythonExe "$Root\run.py"
}

function Start-Development {
    <#
    .SYNOPSIS
        Starts the server in development mode with verbose logging.
    .NOTES
        Delegates to start_simple.ps1 (must exist in the project root).
    #>
    Write-Host "🔧 Development Mode" -ForegroundColor Magenta
    Write-Host "=" * 50 -ForegroundColor Magenta
    & "$Root\start_simple.ps1"
}

function Start-Docker {
    <#
    .SYNOPSIS
        Builds the Docker image and starts the container via docker-compose.
    .NOTES
        Requires Docker Desktop to be installed and running.
    #>
    Write-Host "🐳 Docker Launch" -ForegroundColor Blue
    Write-Host "=" * 50 -ForegroundColor Blue

    # Guard: Docker must be available in PATH
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Docker is not installed!" -ForegroundColor Red
        Write-Host "Install Docker Desktop: https://docker.com/products/docker-desktop" -ForegroundColor Yellow
        Read-Host "Press Enter to continue"
        return
    }

    Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
    docker-compose build

    Write-Host "🚀 Starting Docker container..." -ForegroundColor Yellow
    docker-compose up
}

function Start-Setup {
    <#
    .SYNOPSIS
        Launches the interactive .env configuration wizard.
    .NOTES
        Delegates to setup-env.ps1. Pauses after completion so the user can read output.
    #>
    Write-Host "⚙️ Environment Setup" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Yellow

    if (Test-Path "$Root\setup-env.ps1") {
        & "$Root\setup-env.ps1"
    } else {
        Write-Host "❌ setup-env.ps1 not found!" -ForegroundColor Red
        Write-Host "Create .env file manually from .env.example" -ForegroundColor Yellow
    }

    Read-Host "Press Enter to continue"
}

function Start-Diagnostics {
    <#
    .SYNOPSIS
        Runs a quick system health check: venv, .env, Foundry CLI, and port availability.
    .NOTES
        Checks ports 9696 (FastAPI), 50477 (Foundry default), 8000 (Docker).
        Pauses after completion so the user can read the results.
    #>
    Write-Host "🔍 System Diagnostics" -ForegroundColor DarkYellow
    Write-Host "=" * 50 -ForegroundColor DarkYellow

    # --- Python virtual environment ---
    Write-Host "🐍 Checking Python..." -ForegroundColor Yellow
    if (Test-Path "$Root\venv\Scripts\python.exe") {
        Write-Host "✅ Virtual environment found" -ForegroundColor Green
    } else {
        Write-Host "❌ Virtual environment not found" -ForegroundColor Red
        Write-Host "💡 Run: python -m venv venv" -ForegroundColor Cyan
    }

    # --- .env file ---
    Write-Host "⚙️ Checking .env..." -ForegroundColor Yellow
    if (Test-Path "$Root\.env") {
        Write-Host "✅ .env file found" -ForegroundColor Green
        # Run the Python validator if available
        if (Test-Path "$Root\check_env.py") {
            $pythonExe = if (Test-Path "$Root\venv\Scripts\python.exe") { "$Root\venv\Scripts\python.exe" } else { "python" }
            & $pythonExe "$Root\check_env.py"
        }
    } else {
        Write-Host "❌ .env file not found" -ForegroundColor Red
        Write-Host "💡 Copy .env.example to .env" -ForegroundColor Cyan
    }

    # --- Foundry CLI ---
    Write-Host "🤖 Checking Foundry..." -ForegroundColor Yellow
    try {
        Get-Command foundry -ErrorAction Stop | Out-Null
        Write-Host "✅ Foundry CLI found" -ForegroundColor Green
    } catch {
        Write-Host "❌ Foundry CLI not found" -ForegroundColor Red
        Write-Host "💡 Install: https://github.com/microsoft/foundry" -ForegroundColor Cyan
    }

    # --- Port availability ---
    Write-Host "🔌 Checking ports..." -ForegroundColor Yellow
    $ports = @(9696, 50477, 8000)
    foreach ($port in $ports) {
        try {
            $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
            if ($connection.TcpTestSucceeded) {
                Write-Host "⚠️ Port $port is in use" -ForegroundColor Yellow
            } else {
                Write-Host "✅ Port $port is available" -ForegroundColor Green
            }
        } catch {
            Write-Host "✅ Port $port is available" -ForegroundColor Green
        }
    }

    Read-Host "Press Enter to continue"
}

# --- main ---

# Non-interactive mode: execute the requested action and exit immediately
if ($Mode) {
    switch ($Mode.ToLower()) {
        "quick"  { Start-QuickLaunch;  exit }
        "api"    { Start-FastAPIOnly;  exit }
        "dev"    { Start-Development;  exit }
        "docker" { Start-Docker;       exit }
        "setup"  { Start-Setup;        exit }
        "diag"   { Start-Diagnostics;  exit }
        default  {
            Write-Host "❌ Unknown mode: $Mode" -ForegroundColor Red
            Write-Host "Available modes: quick, api, dev, docker, setup, diag" -ForegroundColor Yellow
            exit 1
        }
    }
}

# Interactive menu loop — runs until the user chooses 0 (Exit)
while ($true) {
    Show-Menu
    $choice = Read-Host "Enter number (0-6)"

    switch ($choice) {
        "1" { Start-QuickLaunch;  break }
        "2" { Start-FastAPIOnly;  break }
        "3" { Start-Development;  break }
        "4" { Start-Docker;       break }
        "5" { Start-Setup;        continue }
        "6" { Start-Diagnostics;  continue }
        "0" {
            Write-Host "👋 Goodbye!" -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host "❌ Invalid choice. Try again." -ForegroundColor Red
            Start-Sleep 2
        }
    }
}
