# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Tesseract OCR Installer
# =============================================================================
# Description:
#   Downloads and installs Tesseract OCR 5.x for Windows x64.
#   Adds Tesseract to the system PATH.
#   Writes tesseract_cmd to config.json (text_extractor section).
#   Required for RAG image indexing (OCR of PNG, JPG, TIFF, etc.)
#   and OCR of embedded images inside PDF files.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\install\install-tesseract.ps1
#   powershell -ExecutionPolicy Bypass -File .\install\install-tesseract.ps1 -ConfigFile "D:\project\config.json"
#
# File: install\install-tesseract.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    # Path to project config.json (default: config.json in parent directory)
    [string]$ConfigFile = "",

    [switch]$Force,
    # Skip download if tesseract.exe already exists at install path
    [switch]$SkipIfExists, 
    
    [switch]$SkipRag,
    [switch]$SkipTesseract,
    [ValidateSet('prod', 'qa', 'debug')]
    [string]$Mode = 'prod'
)



$ErrorActionPreference = 'Stop'

# --- Constants ----------------------------------------------------------------

$TESSERACT_VERSION  = '5.5.0.20241111'
$TESSERACT_INSTALLER = "tesseract-ocr-w64-setup-$TESSERACT_VERSION.exe"
$TESSERACT_URL      = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.5.0/$TESSERACT_INSTALLER"
$TESSERACT_DIR      = 'C:\Program Files\Tesseract-OCR'
$TESSERACT_EXE      = Join-Path $TESSERACT_DIR 'tesseract.exe'

param(
    [switch]$Force,
    [switch]$SkipRag,
    [switch]$SkipTesseract,

    [ValidateSet('prod', 'qa', 'debug')]
    [string]$Mode = 'prod'
)

# Resolve config.json path
if (-not $ConfigFile) {
    $ConfigFile = Join-Path $PSScriptRoot '..\config.json'
}
$ConfigFile = [System.IO.Path]::GetFullPath($ConfigFile)

# --- Functions ----------------------------------------------------------------

function Test-TesseractInstalled {
    <#
    .SYNOPSIS
        Checks whether tesseract.exe is reachable via PATH or at the default install path.
    .OUTPUTS
        bool — True if found.
    #>
    if (Get-Command tesseract -ErrorAction SilentlyContinue) { return $true }
    return Test-Path $TESSERACT_EXE
}

function Add-TesseractToPath {
    <#
    .SYNOPSIS
        Adds Tesseract install directory to the Machine-level PATH if not already present.
    #>
    $current = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    if ($current -notlike "*$TESSERACT_DIR*") {
        [Environment]::SetEnvironmentVariable('Path', "$current;$TESSERACT_DIR", 'Machine')
        $env:Path += ";$TESSERACT_DIR"
        Write-Host "  PATH updated: $TESSERACT_DIR" -ForegroundColor Green
    } else {
        Write-Host "  PATH already contains Tesseract directory" -ForegroundColor Gray
    }
}

function Write-TesseractToConfig {
    <#
    .SYNOPSIS
        Writes or updates text_extractor.tesseract_cmd in config.json.
    .PARAMETER ExePath
        Full path to tesseract.exe.
    #>
    param([string]$ExePath)

    if (-not (Test-Path $ConfigFile)) {
        Write-Host "  config.json not found at $ConfigFile — skipping tesseract_cmd write" -ForegroundColor Yellow
        return
    }

    try {
        $json = Get-Content $ConfigFile -Raw -Encoding UTF8 | ConvertFrom-Json

        if (-not $json.text_extractor) {
            $json | Add-Member -NotePropertyName 'text_extractor' -NotePropertyValue ([PSCustomObject]@{})
        }

        $json.text_extractor | Add-Member -NotePropertyName 'tesseract_cmd' -NotePropertyValue $ExePath -Force

        $json | ConvertTo-Json -Depth 10 | Set-Content $ConfigFile -Encoding UTF8
        Write-Host "  Updated config.json: text_extractor.tesseract_cmd = $ExePath" -ForegroundColor Green
    } catch {
        Write-Host "  Failed to update config.json: $_" -ForegroundColor Red
    }
}

function Install-Tesseract {
    <#
    .SYNOPSIS
        Downloads the Tesseract installer and runs it silently.
    .OUTPUTS
        bool — True if installation succeeded.
    #>
    $tmpDir       = $env:TEMP
    $installerPath = Join-Path $tmpDir $TESSERACT_INSTALLER

    Write-Host "  Downloading Tesseract $TESSERACT_VERSION ..." -ForegroundColor Yellow
    Write-Host "  URL: $TESSERACT_URL" -ForegroundColor Gray

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $TESSERACT_URL -OutFile $installerPath -UseBasicParsing
        Write-Host "  Downloaded: $installerPath" -ForegroundColor Green
    } catch {
        Write-Host "  Download failed: $_" -ForegroundColor Red
        Write-Host "  Download manually from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
        return $false
    }

    Write-Host "  Running installer (silent)..." -ForegroundColor Yellow
    Write-Host "  Installing Russian + English language packs..." -ForegroundColor Gray

    # /S  — silent mode
    # /D  — install directory (must be last argument, no quotes)
    $proc = Start-Process -FilePath $installerPath `
        -ArgumentList '/S', '/D=C:\Program Files\Tesseract-OCR' `
        -Wait -PassThru

    if ($proc.ExitCode -ne 0) {
        Write-Host "  Installer exited with code $($proc.ExitCode)" -ForegroundColor Red
        return $false
    }

    # Clean up installer
    Remove-Item $installerPath -ErrorAction SilentlyContinue

    Write-Host "  Tesseract installed to: $TESSERACT_DIR" -ForegroundColor Green
    return $true
}

# --- main ---------------------------------------------------------------------

Write-Host "`nTesseract OCR..." -ForegroundColor Yellow

if (Test-TesseractInstalled) {
    if ($SkipIfExists) {
        $ver = & $TESSERACT_EXE --version 2>&1 | Select-Object -First 1
        Write-Host "  Already installed: $ver" -ForegroundColor Green
        Add-TesseractToPath
        Write-TesseractToConfig -ExePath $TESSERACT_EXE
        return
    }
    $ver = & $TESSERACT_EXE --version 2>&1 | Select-Object -First 1
    Write-Host "  Already installed: $ver" -ForegroundColor Green
    Add-TesseractToPath
    Write-TesseractToConfig -ExePath $TESSERACT_EXE
    return
}

# Check internet connectivity before attempting download
$online = Test-Connection -ComputerName 'github.com' -Count 1 -Quiet -ErrorAction SilentlyContinue
if (-not $online) {
    Write-Host "  No internet connection — cannot download Tesseract" -ForegroundColor Yellow
    Write-Host "  Install manually: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
    Write-Host "  Then re-run: .\install\install-tesseract.ps1" -ForegroundColor Cyan
    return
}

$ok = Install-Tesseract

if ($ok -and (Test-Path $TESSERACT_EXE)) {
    Add-TesseractToPath
    Write-TesseractToConfig -ExePath $TESSERACT_EXE

    $ver = & $TESSERACT_EXE --version 2>&1 | Select-Object -First 1
    Write-Host "  OK: $ver" -ForegroundColor Green
    Write-Host "  Restart PowerShell to apply PATH changes" -ForegroundColor Cyan
} else {
    Write-Host "  Tesseract installation failed or exe not found at $TESSERACT_EXE" -ForegroundColor Red
    Write-Host "  Install manually: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
}
