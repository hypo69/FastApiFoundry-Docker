# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: llama.cpp Setup
# =============================================================================
# Description:
#   Extracts the llama.cpp Windows binary from bin\llama-*.zip (if not already
#   extracted), then writes the models directory path to config.json under
#   directories.models and llama_cpp.model_path default.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\install\install-llama.ps1
#   powershell -ExecutionPolicy Bypass -File .\install\install-llama.ps1 -ModelsDir "D:\models"
#
# File: install/install-llama.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    [string]$ModelsDir = ""
)

$ErrorActionPreference = 'Continue'
$Root    = Split-Path -Parent $PSScriptRoot
$BinDir  = Join-Path $Root 'bin'
$CfgPath = Join-Path $Root 'config.json'

Write-Host ''
Write-Host '🦙 llama.cpp Setup' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# --- 1. Read config.json defaults ---

$cfg = $null
$defaultModelsDir = '~/.models'

if (Test-Path $CfgPath) {
    try {
        $cfg = Get-Content $CfgPath -Raw | ConvertFrom-Json
        $fromCfg = $cfg.directories?.models
        if ($fromCfg) { $defaultModelsDir = $fromCfg }
    } catch {
        Write-Host "⚠️  Could not read config.json: $_" -ForegroundColor Yellow
    }
}

if (-not $ModelsDir) { $ModelsDir = $defaultModelsDir }

Write-Host "   Models directory : $ModelsDir" -ForegroundColor Gray

# --- 2. Extract llama.cpp zip ---

$zips = Get-ChildItem -Path $BinDir -Filter 'llama-*-bin-win-*.zip' -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending

if (-not $zips) {
    Write-Host '⚠️  No llama.cpp zip found in bin/ — skipping extraction.' -ForegroundColor Yellow
} else {
    $zip      = $zips[0]
    $stem     = [System.IO.Path]::GetFileNameWithoutExtension($zip.Name)
    $destDir  = Join-Path $BinDir $stem
    $serverExe = Join-Path $destDir 'llama-server.exe'

    if (Test-Path $serverExe) {
        Write-Host "✅ Already extracted: $stem" -ForegroundColor Green
    } else {
        Write-Host "📦 Extracting $($zip.Name) → bin\$stem\ ..." -ForegroundColor Yellow
        try {
            if (Test-Path $destDir) { Remove-Item $destDir -Recurse -Force }
            Expand-Archive -Path $zip.FullName -DestinationPath $destDir -Force
            Write-Host "✅ Extracted: $destDir" -ForegroundColor Green
        } catch {
            Write-Host "❌ Extraction failed: $_" -ForegroundColor Red
            exit 1
        }
    }

    # Update bin_version in config.json
    if ($cfg) {
        try {
            if (-not $cfg.llama_cpp) { $cfg | Add-Member -NotePropertyName 'llama_cpp' -NotePropertyValue ([PSCustomObject]@{}) }
            $cfg.llama_cpp | Add-Member -NotePropertyName 'bin_version' -NotePropertyValue $stem -Force
            $cfg | ConvertTo-Json -Depth 10 | Set-Content $CfgPath -Encoding UTF8
            Write-Host "✅ config.json: llama_cpp.bin_version = $stem" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Could not update bin_version: $_" -ForegroundColor Yellow
        }
    }
}

# --- 3. Write models directory to config.json ---

if ($cfg) {
    try {
        # Expand ~ to real home path for storage
        $resolvedDir = $ModelsDir -replace '^~', $env:USERPROFILE

        if (-not $cfg.directories) {
            $cfg | Add-Member -NotePropertyName 'directories' -NotePropertyValue ([PSCustomObject]@{}) }
        $cfg.directories | Add-Member -NotePropertyName 'models' -NotePropertyValue $ModelsDir -Force

        if (-not $cfg.llama_cpp) {
            $cfg | Add-Member -NotePropertyName 'llama_cpp' -NotePropertyValue ([PSCustomObject]@{}) }
        $cfg.llama_cpp | Add-Member -NotePropertyName 'model_path' -NotePropertyValue $resolvedDir -Force

        $cfg | ConvertTo-Json -Depth 10 | Set-Content $CfgPath -Encoding UTF8
        Write-Host "✅ config.json: directories.models = $ModelsDir" -ForegroundColor Green
        Write-Host "✅ config.json: llama_cpp.model_path = $resolvedDir" -ForegroundColor Green
    } catch {
        Write-Host "❌ Could not update config.json: $_" -ForegroundColor Red
    }
}

# --- 4. Create models directory ---

$resolvedDir = $ModelsDir -replace '^~', $env:USERPROFILE
if (-not (Test-Path $resolvedDir)) {
    try {
        New-Item -ItemType Directory -Path $resolvedDir -Force | Out-Null
        Write-Host "✅ Created models directory: $resolvedDir" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Could not create directory: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Models directory exists: $resolvedDir" -ForegroundColor Green
}

Write-Host ''
Write-Host '✅ llama.cpp setup complete!' -ForegroundColor Green
