# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: FastAPI Foundry - Main Installer
# =============================================================================
# Description:
#   Installs Python venv, pip dependencies, Tesseract OCR, llama.cpp,
#   Foundry Local, creates .env and logs directory.
#
#   For QA reinstall (stop all services + clean install) use:
#     tests\qa-install.ps1
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File .\install.ps1
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -Force
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -SkipRag
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -SkipTesseract
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -Mode debug
#
# File: install.ps1
# Project: AI Assistant (ai_assist)
# Version: 0.7.1
# Changes in 0.7.1:
#   - QA logic moved to tests\qa-install.ps1 and tests\qa-start.ps1
#   - Added Resolve-Mode / Get-ModeFromFile helpers
#   - Mode falls back to MODE file when -Mode not supplied
# Changes in 0.6.1:
#   - Removed GUI installer
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    [switch]$Force,
    [switch]$SkipRag,
    [switch]$SkipTesseract,
    [switch]$NoGui,
    # prod | debug | qa | qa+debug  (empty = read from MODE file, default prod)
    [string]$Mode = ''
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

# =============================================================================
# HELPERS
# =============================================================================

function Resolve-Mode {
    <#
    .SYNOPSIS
        Normalises a raw mode string to one of the canonical values.
    .DESCRIPTION
        Canonical values: prod | qa | debug | qa+debug

        Normalisation rules (case-insensitive):
          debug+qa  ->  qa+debug
          qa+debug  ->  qa+debug
          qa        ->  qa
          debug     ->  debug
          prod      ->  prod
          <empty>   ->  prod

        Args:
            $Raw (string) — raw value from -Mode param or MODE file.

        Returns:
            string — one of: prod | qa | debug | qa+debug

        Exceptions:
            RuntimeException — thrown for unrecognised mode strings.

    .EXAMPLE
        Resolve-Mode 'debug+qa'
        # Returns 'qa+debug'
    .EXAMPLE
        Resolve-Mode ''
        # Returns 'prod'
    #>
    param([string]$Raw)

    $n = $Raw.ToLower().Trim()
    switch ($n) {
        ''         { return 'prod'     }
        'prod'     { return 'prod'     }
        'qa'       { return 'qa'       }
        'debug'    { return 'debug'    }
        'qa+debug' { return 'qa+debug' }
        'debug+qa' { return 'qa+debug' }
        default    { throw "Unknown mode: '$Raw'. Valid: prod | qa | debug | qa+debug | debug+qa" }
    }
}

function Get-ModeFromFile {
    <#
    .SYNOPSIS
        Reads the active mode from the MODE file in the project root.
    .DESCRIPTION
        Looks for a line matching `mode = <value>` (case-insensitive).

        Args:
            $ProjectRoot (string) — path to the directory containing MODE.

        Returns:
            string — raw mode value, or empty string if file absent or no match.

    .EXAMPLE
        $raw  = Get-ModeFromFile -ProjectRoot $PSScriptRoot
        $Mode = Resolve-Mode $raw
        # $Mode is now one of: prod | qa | debug | qa+debug
    #>
    param([string]$ProjectRoot)

    $modeFile = Join-Path $ProjectRoot 'MODE'
    if (-not (Test-Path $modeFile)) { return '' }

    $line = Get-Content $modeFile |
            Where-Object { $_ -match '^\s*mode\s*=' } |
            Select-Object -First 1

    if (-not $line) { return '' }
    return ($line -split '=', 2)[1].Trim()
}

function Stop-VenvProcesses {
    <#
    .SYNOPSIS
        Stops processes that hold locks on venv files.
    .DESCRIPTION
        Kills processes listening on the FastAPI port (9696) and MkDocs port (9697),
        then kills any remaining Python processes whose executable lives inside the venv.
        Waits briefly for OS to release file handles.

        Returns:
            void

    .EXAMPLE
        Stop-VenvProcesses
        # Stops uvicorn on 9696, mkdocs on 9697, and venv-bound python processes
    #>
    Write-Host '  Stopping services on ports 9696 / 9697...' -ForegroundColor Gray

    foreach ($port in @(9696, 9697)) {
        $conn = netstat -ano 2>$null |
                Select-String ":$port\s" |
                Select-Object -First 1
        if ($conn) {
            $pid_ = ($conn -split '\s+')[-1]
            if ($pid_ -match '^\d+$') {
                Stop-Process -Id ([int]$pid_) -Force -ErrorAction SilentlyContinue
                Write-Host "  Killed PID $pid_ (port $port)" -ForegroundColor Gray
            }
        }
    }

    # Also kill any python process running from inside the venv
    Get-Process -Name python, python3, python311 -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -like "$venvPath*" } |
        Stop-Process -Force -ErrorAction SilentlyContinue

    Start-Sleep -Milliseconds 700
}

# Normalise mode — command-line wins, then MODE file, then default 'prod'
if (-not $Mode) { $Mode = Get-ModeFromFile -ProjectRoot $Root }
$Mode = Resolve-Mode $Mode

Write-Host "Mode: $Mode" -ForegroundColor Cyan

# --- 0. PowerShell version check ---
if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Host '[ERROR] PowerShell 7+ required.' -ForegroundColor Red
    Write-Host '        Run install.bat or download PS7: https://aka.ms/powershell' -ForegroundColor Cyan
    exit 1
}

Write-Host 'FastAPI Foundry - Installation' -ForegroundColor Green
Write-Host ('=' * 50)

# --- 1. Python ---
Write-Host "`nChecking Python..." -ForegroundColor Yellow

$pythonCmd = $null
foreach ($cmd in @('python', 'python3', 'python311')) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match 'Python 3\.(1[1-9]|[2-9]\d)') {
            $pythonCmd = $cmd
            Write-Host "  Found: $ver ($cmd)" -ForegroundColor Green
            break
        }
    } catch { }
}

if (-not $pythonCmd) {
    $localZip = Join-Path $Root 'bin\Python-3.11.9.zip'
    if (Test-Path $localZip) {
        Write-Host "  Local archive found: $localZip" -ForegroundColor Cyan
        $answer = Read-Host '  Install Python from local archive? (y/N)'
        if ($answer -ne 'y' -and $answer -ne 'Y') { exit 1 }

        $localPythonDir = Join-Path $Root 'bin\Python-3.11.9'
        if (-not (Test-Path $localPythonDir)) {
            Expand-Archive -Path $localZip -DestinationPath $localPythonDir
        }
        $pythonCmd = Get-ChildItem -Path $localPythonDir -Filter 'python.exe' -Recurse |
                     Select-Object -First 1 -ExpandProperty FullName
        if (-not $pythonCmd) { Write-Host '  python.exe not found in archive' -ForegroundColor Red; exit 1 }
    } else {
        Write-Host '  Python 3.11+ not found. Download: https://www.python.org/downloads/' -ForegroundColor Red
        exit 1
    }
}

# --- 2. venv ---
Write-Host "`nVirtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $Root 'venv'

if ((Test-Path $venvPath) -and $Force) {
    Stop-VenvProcesses
    try {
        Remove-Item $venvPath -Recurse -Force
        Write-Host '  Old venv removed' -ForegroundColor Gray
    } catch {
        Write-Host "  Could not remove venv: $_" -ForegroundColor Red
        Write-Host '  Close all terminals/apps using the venv and retry.' -ForegroundColor Cyan
        exit 1
    }
} elseif (Test-Path $venvPath) {
    Write-Host '  venv already exists.' -ForegroundColor Yellow
    $answer = Read-Host '  Recreate? (y/N)'
    if ($answer -eq 'y' -or $answer -eq 'Y') {
        Stop-VenvProcesses
        try {
            Remove-Item $venvPath -Recurse -Force
            Write-Host '  venv removed' -ForegroundColor Gray
        } catch {
            Write-Host "  Could not remove venv: $_" -ForegroundColor Red
            Write-Host '  Close all terminals/apps using the venv and retry.' -ForegroundColor Cyan
            exit 1
        }
    }
}

if (-not (Test-Path $venvPath)) {
    & $pythonCmd -m venv $venvPath
    Write-Host "  venv created: $venvPath" -ForegroundColor Green
}

$python = Join-Path $venvPath 'Scripts\python.exe'

# --- 2.1. pip upgrade ---
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
& $python -m pip install --upgrade pip | Out-Null
Write-Host '  pip upgraded' -ForegroundColor Green

# --- 3. Core dependencies ---
Write-Host "`nInstalling requirements.txt..." -ForegroundColor Yellow
& $python -m pip install -r (Join-Path $Root 'requirements.txt')
Write-Host '  Core dependencies installed' -ForegroundColor Green

# --- 4. GUI installer (unless -NoGui) ---
if (-not $NoGui) {
    Write-Host "`nLaunching GUI installer..." -ForegroundColor Cyan

    $appPort = 9696
    try {
        $cfg = Get-Content (Join-Path $Root 'config.json') -Raw | ConvertFrom-Json
        if ($cfg.fastapi_server.port) { $appPort = [int]$cfg.fastapi_server.port }
    } catch { }

    # Start FastAPI in background (minimized window, keep running)
    $fastApiProc = Start-Process -FilePath $python `
                                 -ArgumentList 'run.py' `
                                 -WorkingDirectory $Root `
                                 -PassThru `
                                 -WindowStyle Minimized

    # Save PID so stop.ps1 can clean it up later
    $fastApiProc.Id | Out-File (Join-Path $env:TEMP 'fastapi-foundry-installer.pid') -Encoding UTF8

    # Wait for FastAPI to be ready (max 30s)
    Write-Host '  Waiting for FastAPI on port $appPort...' -ForegroundColor Gray
    $deadline = (Get-Date).AddSeconds(30)
    $ready    = $false
    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-WebRequest -Uri "http://localhost:$appPort/api/v1/health" `
                                   -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($r.StatusCode -lt 500) { $ready = $true; break }
        } catch { }
        Start-Sleep -Milliseconds 600
    }

    if ($ready) {
        Write-Host "  Opening http://localhost:$appPort/install" -ForegroundColor Green
        Start-Process "http://localhost:$appPort/install"
        Write-Host '  Complete the remaining steps in the browser.' -ForegroundColor Cyan
        Write-Host '  The server will keep running after this script exits.' -ForegroundColor Gray
    } else {
        Write-Host '  FastAPI did not start in time — falling back to CLI install.' -ForegroundColor Yellow
        $fastApiProc | Stop-Process -Force -ErrorAction SilentlyContinue
    }

    # Do NOT block — fall through to CLI steps so they run regardless
}

# --- 4. RAG ---
if (-not $SkipRag) {
    Write-Host "`nRAG components (sentence-transformers, faiss-cpu)..." -ForegroundColor Yellow
    try {
        & $python -m pip install sentence-transformers faiss-cpu --quiet
        Write-Host '  RAG dependencies installed' -ForegroundColor Green
    } catch {
        Write-Host "  RAG install error: $_" -ForegroundColor Yellow
        Write-Host '  Retry: pip install sentence-transformers faiss-cpu' -ForegroundColor Cyan
    }
} else {
    Write-Host "`nRAG skipped (-SkipRag)" -ForegroundColor Gray
}

# --- 5. Tesseract ---
if (-not $SkipTesseract) {
    $tesseractScript = Join-Path $Root 'install\install-tesseract.ps1'
    if (Test-Path $tesseractScript) {
        try {
            & $tesseractScript -SkipIfExists
        } catch {
            Write-Host "  Tesseract error: $_" -ForegroundColor Yellow
            Write-Host '  Install manually: https://github.com/UB-Mannheim/tesseract/wiki' -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "`nTesseract skipped (-SkipTesseract)" -ForegroundColor Gray
}

# --- 6. .env ---
Write-Host "`n.env configuration..." -ForegroundColor Yellow
$envFile    = Join-Path $Root '.env'
$envExample = Join-Path $Root '.env.example'

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host '  .env created from .env.example' -ForegroundColor Green
    } else {
        "# FastAPI Foundry`nFOUNDRY_BASE_URL=http://localhost:50477/v1" | Out-File $envFile -Encoding UTF8
        Write-Host '  .env created with defaults' -ForegroundColor Green
    }
} else {
    Write-Host '  .env already exists' -ForegroundColor Gray
}

# --- 6.1. config.json ---
Write-Host "`nconfig.json..." -ForegroundColor Yellow
$configFile    = Join-Path $Root 'config.json'
$configExample = Join-Path $Root 'config.json.example'

if (-not (Test-Path $configFile)) {
    if (Test-Path $configExample) {
        Copy-Item $configExample $configFile
        Write-Host '  config.json created from config.json.example' -ForegroundColor Green
    } else {
        Write-Host '  config.json.example not found — skipping' -ForegroundColor Yellow
    }
} else {
    Write-Host '  config.json already exists' -ForegroundColor Gray
}

# --- 7. logs/ ---
Write-Host "`nLogs folder..." -ForegroundColor Yellow
$logsDir = Join-Path $Root 'logs'
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Host '  logs/ created' -ForegroundColor Green
} else {
    Write-Host '  logs/ already exists' -ForegroundColor Gray
}

# --- 8. llama.cpp ---
Write-Host "`nllama.cpp..." -ForegroundColor Yellow
$binDir   = Join-Path $Root 'bin'
$llamaZip = Get-ChildItem -Path $binDir -Filter 'llama-*-bin-win-*.zip' -ErrorAction SilentlyContinue |
            Select-Object -First 1

if (-not $llamaZip) {
    Write-Host '  No llama.cpp archive in bin\ — skipping' -ForegroundColor Gray
} else {
    $llamaDir = Join-Path $binDir $llamaZip.BaseName
    if (-not (Test-Path $llamaDir)) {
        Write-Host "  Extracting $($llamaZip.Name)..." -ForegroundColor Yellow
        Expand-Archive -Path $llamaZip.FullName -DestinationPath $llamaDir
        Write-Host "  Done: $llamaDir" -ForegroundColor Green
    } else {
        Write-Host '  llama.cpp already extracted' -ForegroundColor Gray
    }

    $llamaExe = Get-ChildItem -Path $llamaDir -Filter 'llama-server.exe' -Recurse |
                Select-Object -First 1
    if ($llamaExe) {
        $relPath    = ".\bin\$($llamaZip.BaseName)\llama-server.exe"
        $envContent = if (Test-Path $envFile) { Get-Content $envFile -Raw } else { '' }
        if ($envContent -notmatch 'LLAMA_SERVER_PATH') {
            Add-Content -Path $envFile -Value "`nLLAMA_SERVER_PATH=$relPath"
            Write-Host "  LLAMA_SERVER_PATH=$relPath -> .env" -ForegroundColor Green
        }
    }
}

# --- 9. Foundry ---
Write-Host "`nAI Backend (Foundry Local)..." -ForegroundColor Yellow
$foundryInstalled = $null -ne (Get-Command foundry -ErrorAction SilentlyContinue)

if ($Mode -eq 'debug') {
    # Diagnostics only — no changes
    Write-Host '  Debug mode: diagnostics only' -ForegroundColor Cyan
    if ($foundryInstalled) {
        try { & foundry --version } catch { }
        try { & foundry service status 2>$null } catch { }
    } else {
        Write-Host '  Foundry not installed' -ForegroundColor Yellow
    }
} elseif ($foundryInstalled) {
    $ver = & foundry --version 2>&1
    Write-Host "  Foundry already installed: $ver" -ForegroundColor Green
} else {
    Write-Host '  Foundry not found.' -ForegroundColor Yellow
    $wingetOk = $null -ne (Get-Command winget -ErrorAction SilentlyContinue)
    if (-not $wingetOk) {
        Write-Host '  winget not found — install manually: https://aka.ms/foundry-local' -ForegroundColor Cyan
    } else {
        $answer = Read-Host '  Install Microsoft Foundry Local now? (y/N)'
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            winget install Microsoft.FoundryLocal --accept-source-agreements --accept-package-agreements
        }
    }
}

# --- 10. Default models (first install only) ---
$firstInstallMarker = Join-Path $Root 'venv\.first_install_done'
if (-not (Test-Path $firstInstallMarker)) {
    $answer = Read-Host "`nDownload default models? (y/N)"
    if ($answer -eq 'y' -or $answer -eq 'Y') {
        & (Join-Path $Root 'install\install-models.ps1')
    }
    '' | Out-File $firstInstallMarker -Encoding UTF8
}

# --- 11. Shortcuts ---
Write-Host "`nCreating shortcuts..." -ForegroundColor Yellow
$makeIco = Join-Path $Root 'install\make-ico.ps1'
if (Test-Path $makeIco) {
    try { & $makeIco -ProjectRoot $Root } catch { Write-Host "  icon.ico warning: $_" -ForegroundColor Yellow }
}
$shortcuts = Join-Path $Root 'install\install-shortcuts.ps1'
if (Test-Path $shortcuts) {
    try { & $shortcuts; Write-Host '  Shortcuts created' -ForegroundColor Green }
    catch { Write-Host "  Shortcuts error: $_" -ForegroundColor Yellow }
}

# --- 12. Summary ---
Write-Host "`n$('=' * 50)" -ForegroundColor Green
Write-Host 'Installation complete!' -ForegroundColor Green

$appPort  = 9696
$docsPort = 9697
try {
    $cfg = Get-Content (Join-Path $Root 'config.json') -Raw | ConvertFrom-Json
    if ($cfg.fastapi_server.port) { $appPort  = [int]$cfg.fastapi_server.port }
    if ($cfg.docs_server.port)    { $docsPort = [int]$cfg.docs_server.port }
} catch { }

Write-Host ''
Write-Host "  Web UI:    http://localhost:$appPort" -ForegroundColor Green
Write-Host "  Docs:      http://localhost:$docsPort" -ForegroundColor Green
Write-Host "  Swagger:   http://localhost:$appPort/docs" -ForegroundColor Green
Write-Host ''
Write-Host '  Start: powershell -ExecutionPolicy Bypass -File .\start.ps1' -ForegroundColor Cyan
