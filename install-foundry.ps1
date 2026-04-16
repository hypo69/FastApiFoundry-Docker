# -*- coding: utf-8 -*-
# =============================================================================
# Process name: Microsoft Foundry Local - Installer
# =============================================================================
# Description:
#   Installs Microsoft Foundry Local CLI via winget.
#   After installation, starts the service and suggests downloading a model.
#
# Usage:
#   .\install-foundry.ps1
#   .\install-foundry.ps1 -Model "qwen2.5-0.5b-instruct-generic-cpu"
#
# File: install-foundry.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: December 9, 2025
# =============================================================================

param(
    [string]$Model = "qwen2.5-0.5b-instruct-generic-cpu"
)

$ErrorActionPreference = "Stop"

Write-Host "Microsoft Foundry Local - Installer" -ForegroundColor Cyan
Write-Host ("=" * 50)

# --- winget Check ---
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget not found." -ForegroundColor Red
    Write-Host "Install App Installer from the Microsoft Store:" -ForegroundColor Cyan
    Write-Host "  https://apps.microsoft.com/detail/9NBLGGH4NNS1" -ForegroundColor Gray
    exit 1
}

# --- Checking existing installation ---
if (Get-Command foundry -ErrorAction SilentlyContinue) {
    $ver = & foundry --version 2>&1
    Write-Host "Foundry is already installed: $ver" -ForegroundColor Green
} else {
    # --- Installation via winget ---
    Write-Host "`nInstalling Microsoft Foundry Local..." -ForegroundColor Yellow
    try {
        winget install Microsoft.FoundryLocal --accept-source-agreements --accept-package-agreements
        Write-Host "Foundry Local installed" -ForegroundColor Green
    } catch {
        Write-Host "Error installing via winget: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Install manually:" -ForegroundColor Cyan
        Write-Host "  winget install Microsoft.FoundryLocal" -ForegroundColor Gray
        Write-Host "  or download from: https://aka.ms/foundry-local" -ForegroundColor Gray
        exit 1
    }

    # Update PATH in the current session
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# --- Service Startup ---
Write-Host "`nStarting Foundry service..." -ForegroundColor Yellow
try {
    & foundry service start
    Start-Sleep 3
    Write-Host "Service started" -ForegroundColor Green
} catch {
    Write-Host "Failed to start service: $_" -ForegroundColor Yellow
    Write-Host "Start manually: foundry service start" -ForegroundColor Cyan
}

# --- Downloading Model ---
Write-Host "`nDownloading model: $Model" -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
try {
    & foundry model download $Model
    Write-Host "Model downloaded: $Model" -ForegroundColor Green
} catch {
    Write-Host "Failed to download model: $_" -ForegroundColor Yellow
    Write-Host "Download manually: foundry model download $Model" -ForegroundColor Cyan
}

# --- Check ---
Write-Host "`nChecking API..." -ForegroundColor Yellow
Start-Sleep 2
try {
    $response = Invoke-RestMethod "http://localhost:50477/v1/models" -TimeoutSec 5
    Write-Host "Foundry API available on port 50477" -ForegroundColor Green
    Write-Host "Models loaded: $($response.data.Count)" -ForegroundColor Gray
} catch {
    Write-Host "API not yet available — Foundry may be using a different port." -ForegroundColor Yellow
    Write-Host "The server will find it automatically upon startup." -ForegroundColor Cyan
}

Write-Host "`n$("=" * 50)" -ForegroundColor Green
Write-Host "Foundry Local is ready to use!" -ForegroundColor Green
Write-Host ""
Write-Host "Start the FastAPI server:"
Write-Host "  venv\Scripts\python.exe run.py"
