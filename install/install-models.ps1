# -*- coding: utf-8 -*-
# =============================================================================
# Process name: FastAPI Foundry - Default Model Download
# =============================================================================
# Description:
#   Downloads default models for Foundry Local and HuggingFace.
#   Runs automatically from install.ps1 during the first installation,
#   or manually at any time.
#
# Usage:
#   .\install-models.ps1
#   .\install-models.ps1 -SkipFoundry
#   .\install-models.ps1 -SkipHuggingFace
#
# File: install-models.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    [switch]$SkipFoundry,
    [switch]$SkipHuggingFace
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$python = Join-Path $Root "venv\Scripts\python.exe"

Write-Host "FastAPI Foundry - Downloading models" -ForegroundColor Green
Write-Host ("=" * 50)

# --- Foundry ---
if (-not $SkipFoundry) {
    Write-Host "`nFoundry model..." -ForegroundColor Yellow

    $foundryReady = $null -ne (Get-Command foundry -ErrorAction SilentlyContinue)
    if (-not $foundryReady) {
        Write-Host "  Foundry is not installed, skipping" -ForegroundColor Gray
    } else {
        $foundryModel = "qwen2.5-0.5b-instruct-generic-cpu"
        $answer = Read-Host "  Download '$foundryModel' (~300 MB)? (y/N)"
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            Write-Host "  Starting Foundry service..." -ForegroundColor Gray
            & foundry service start 2>&1 | Out-Null
            Write-Host "  Downloading $foundryModel ..." -ForegroundColor Yellow
            & foundry model download $foundryModel
            Write-Host "  Done" -ForegroundColor Green
        }
    }
}

# --- HuggingFace ---
if (-not $SkipHuggingFace) {
    Write-Host "`nHuggingFace model (for RAG)..." -ForegroundColor Yellow

    if (-not (Test-Path $python)) {
        Write-Host "  venv not found, skipping" -ForegroundColor Gray
    } else {
        $hfModel = "sentence-transformers/all-MiniLM-L6-v2"
        $answer = Read-Host "  Download '$hfModel' (~90 MB)? (y/N)"
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            Write-Host "  Downloading $hfModel ..." -ForegroundColor Yellow
            & $python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('$hfModel')"
            Write-Host "  Done" -ForegroundColor Green
        }
    }
}

Write-Host "`n$("=" * 50)" -ForegroundColor Green
Write-Host "Done!" -ForegroundColor Green
