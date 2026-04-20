# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Tesseract OCR Installer
# =============================================================================
# Description:
#   Downloads and installs Tesseract OCR 5.x for Windows x64.
#   Adds Tesseract to the system PATH.
#   Writes TESSERACT_CMD to the project .env file.
#   Required for RAG image indexing (OCR of PNG, JPG, TIFF, etc.)
#   and OCR of embedded images inside PDF files.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\install\install-tesseract.ps1
#   powershell -ExecutionPolicy Bypass -File .\install\install-tesseract.ps1 -EnvFile "D:\project\.env"
#
# File: install\install-tesseract.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    # Path to project .env file (default: .env in parent directory)
    [string]$EnvFile = "",
    # Skip download if tesseract.exe already exists at install path
    [switch]$SkipIfExists
)

$ErrorActionPreference = 'Stop'

# --- Constants ----------------------------------------------------------------

$TESSERACT_VERSION  = '5.5.0.20241111'
$TESSERACT_INSTALLER = "tesseract-ocr-w64-setup-$TESSERACT_VERSION.exe"
$TESSERACT_URL      = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.5.0/$TESSERACT_INSTALLER"
$TESSERACT_DIR      = 'C:\Program Files\Tesseract-OCR'
$TESSERACT_EXE      = Join-Path $TESSERACT_DIR 'tesseract.exe'

# Resolve .env path
if (-not $EnvFile) {
    $EnvFile = Join-Path $PSScriptRoot '..\\.env'
}
$EnvFile = [System.IO.Path]::GetFullPath($EnvFile)

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

function Write-TesseractToEnv {
    <#
    .SYNOPSIS
        Writes or updates TESSERACT_CMD in the project .env file.
    .PARAMETER ExePath
        Full path to tesseract.exe.
    #>
    param([string]$ExePath)

    if (-not (Test-Path $EnvFile)) {
        Write-Host "  .env not found at $EnvFile — skipping TESSERACT_CMD write" -ForegroundColor Yellow
        return
    }

    $content = Get-Content $EnvFile -Raw -Encoding UTF8
    $line    = "TESSERACT_CMD=$ExePath"

    if ($content -match 'TESSERACT_CMD=') {
        # Update existing entry
        $content = $content -replace 'TESSERACT_CMD=.*', $line
        Set-Content $EnvFile -Value $content -Encoding UTF8 -NoNewline
        Write-Host "  Updated in .env: $line" -ForegroundColor Green
    } else {
        # Append new entry
        Add-Content $EnvFile -Value "`n$line" -Encoding UTF8
        Write-Host "  Added to .env: $line" -ForegroundColor Green
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
        Write-TesseractToEnv -ExePath $TESSERACT_EXE
        return
    }
    $ver = & $TESSERACT_EXE --version 2>&1 | Select-Object -First 1
    Write-Host "  Already installed: $ver" -ForegroundColor Green
    Add-TesseractToPath
    Write-TesseractToEnv -ExePath $TESSERACT_EXE
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
    Write-TesseractToEnv -ExePath $TESSERACT_EXE

    $ver = & $TESSERACT_EXE --version 2>&1 | Select-Object -First 1
    Write-Host "  OK: $ver" -ForegroundColor Green
    Write-Host "  Restart PowerShell to apply PATH changes" -ForegroundColor Cyan
} else {
    Write-Host "  Tesseract installation failed or exe not found at $TESSERACT_EXE" -ForegroundColor Red
    Write-Host "  Install manually: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
}
