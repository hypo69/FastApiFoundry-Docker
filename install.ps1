# -*- coding: utf-8 -*-
# =============================================================================
# Process name: FastAPI Foundry - Main Installer
# =============================================================================
# Description:
#   Installs Python venv, dependencies, creates .env and logs folder.
#   Foundry / llama.cpp / Ollama are installed separately (see INSTALL.md).
#
# Usage:
#   .\install.ps1              # standard installation
#   .\install.ps1 -Force       # reinstall venv
#   .\install.ps1 -SkipRag     # without RAG dependencies
#
# File: install.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    [switch]$Force,
    [switch]$SkipRag
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

Write-Host "FastAPI Foundry - Installer" -ForegroundColor Green
Write-Host ("=" * 50)

# --- 1. Python ---
Write-Host "`nChecking Python..." -ForegroundColor Yellow

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "python311")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(1[1-9]|[2-9]\d)") {
            $pythonCmd = $cmd
            Write-Host "  Python found: $ver ($cmd)" -ForegroundColor Green
            break
        }
    } catch { }
}

if (-not $pythonCmd) {
    Write-Host "  Python 3.11+ not found in the system." -ForegroundColor Yellow

    $localZip = Join-Path $Root "bin\Python-3.11.9.zip"
    if (Test-Path $localZip) {
        Write-Host "  Found local interpreter: $localZip" -ForegroundColor Cyan
        $answer = Read-Host "  Install Python from local archive? (y/N)"
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            $localPythonDir = Join-Path $Root "bin\Python-3.11.9"
            if (-not (Test-Path $localPythonDir)) {
                Write-Host "  Extracting $localZip ..." -ForegroundColor Yellow
                Expand-Archive -Path $localZip -DestinationPath $localPythonDir
                Write-Host "  Done" -ForegroundColor Green
            } else {
                Write-Host "  Interpreter already extracted" -ForegroundColor Gray
            }

            # Find python.exe inside the extracted directory
            $localPythonExe = Get-ChildItem -Path $localPythonDir -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue |
                              Select-Object -First 1 -ExpandProperty FullName

            if ($localPythonExe) {
                $ver = & $localPythonExe --version 2>&1
                Write-Host "  Using local Python: $ver" -ForegroundColor Green
                Write-Host "  Path: $localPythonExe" -ForegroundColor Gray
                $pythonCmd = $localPythonExe
            } else {
                Write-Host "  python.exe not found inside the archive. Check bin\Python-3.11.9.zip content" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "  Installation cancelled. Download Python manually: https://www.python.org/downloads/" -ForegroundColor Cyan
            exit 1
        }
    } else {
        Write-Host "  Python 3.11+ not found and local archive bin\Python-3.11.9.zip is missing." -ForegroundColor Red
        Write-Host "  Download Python from https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
}

# --- 2. venv ---
Write-Host "`nVirtual Environment..." -ForegroundColor Yellow
$venvPath = Join-Path $Root "venv"

if ((Test-Path $venvPath) -and $Force) {
    Remove-Item $venvPath -Recurse -Force
    Write-Host "  Old venv removed" -ForegroundColor Gray
}

if (-not (Test-Path $venvPath)) {
    & $pythonCmd -m venv $venvPath
    Write-Host "  venv created: $venvPath" -ForegroundColor Green
} else {
    Write-Host "  venv already exists (use -Force to recreate)" -ForegroundColor Gray
}

$pip = Join-Path $venvPath "Scripts\pip.exe"
$python = Join-Path $venvPath "Scripts\python.exe"

# --- 2.1. Update pip ---
Write-Host "`nUpdating pip..." -ForegroundColor Yellow
& $python -m pip install --upgrade pip
Write-Host "  pip updated" -ForegroundColor Green

# --- 3. Dependencies ---
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
& $python -m pip install -r (Join-Path $Root "requirements.txt")
Write-Host "  Core dependencies installed" -ForegroundColor Green

# --- 4. RAG dependencies ---
if (-not $SkipRag) {
    Write-Host "`nRAG dependencies (sentence-transformers, faiss-cpu)..." -ForegroundColor Yellow
    Write-Host "  This may take a few minutes..." -ForegroundColor Gray
    try {
        & $python -m pip install sentence-transformers faiss-cpu --quiet
        Write-Host "  RAG dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "  Failed to install RAG dependencies: $_" -ForegroundColor Yellow
        Write-Host "  Run later: python install_rag_deps.py" -ForegroundColor Cyan
    }
} else {
    Write-Host "`nRAG dependencies skipped (-SkipRag)" -ForegroundColor Gray
}

# --- 5. .env ---
Write-Host "`nConfiguration .env..." -ForegroundColor Yellow
$envFile = Join-Path $Root ".env"
$envExample = Join-Path $Root ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "  .env created from .env.example" -ForegroundColor Green
    } else {
        "# FastAPI Foundry`nFOUNDRY_BASE_URL=http://localhost:50477/v1" | Out-File $envFile -Encoding UTF8
        Write-Host "  .env created with default settings" -ForegroundColor Green
    }
    Write-Host "  Edit .env if necessary" -ForegroundColor Cyan
} else {
    Write-Host "  .env already exists" -ForegroundColor Gray
}

# --- 6. logs folder ---
Write-Host "`nLogs folder..." -ForegroundColor Yellow
$logsDir = Join-Path $Root "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Host "  logs/ created" -ForegroundColor Green
} else {
    Write-Host "  logs/ already exists" -ForegroundColor Gray
}

# --- 7. llama.cpp ---
Write-Host "`nllama.cpp server..." -ForegroundColor Yellow

$binDir = Join-Path $Root "bin"
$llamaZip = if (Test-Path $binDir) {
    Get-ChildItem -Path $binDir -Filter "llama-*-bin-win-*.zip" -ErrorAction SilentlyContinue | Select-Object -First 1
}

if (-not $llamaZip) {
    Write-Host "  llama.cpp archive not found in bin\ — skipping" -ForegroundColor Gray
} else {
    $llamaDir = Join-Path $binDir $llamaZip.BaseName
    if (-not (Test-Path $llamaDir)) {
        Write-Host "  Extracting $($llamaZip.Name) ..." -ForegroundColor Yellow
        Expand-Archive -Path $llamaZip.FullName -DestinationPath $llamaDir
        Write-Host "  Done: $llamaDir" -ForegroundColor Green
    } else {
        Write-Host "  llama.cpp already extracted" -ForegroundColor Gray
    }

    $llamaExe = Get-ChildItem -Path $llamaDir -Filter "llama-server.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($llamaExe) {
        Write-Host "  llama-server.exe: $($llamaExe.FullName)" -ForegroundColor Green
        $relPath = ".\bin\$($llamaZip.BaseName)\llama-server.exe"
        $envContent = if (Test-Path $envFile) { Get-Content $envFile -Raw } else { "" }
        if ($envContent -notmatch "LLAMA_SERVER_PATH") {
            Add-Content -Path $envFile -Value "`nLLAMA_SERVER_PATH=$relPath"
            Write-Host "  LLAMA_SERVER_PATH=$relPath → .env" -ForegroundColor Green
        } else {
            Write-Host "  LLAMA_SERVER_PATH already exists in .env" -ForegroundColor Gray
        }
    } else {
        Write-Host "  llama-server.exe not found inside the archive" -ForegroundColor Yellow
    }
}

# --- 8. Foundry ---
Write-Host "`nAI Backend (Foundry Local)..." -ForegroundColor Yellow

# Check if foundry is in PATH
$foundryInstalled = $null -ne (Get-Command foundry -ErrorAction SilentlyContinue)

if ($foundryInstalled) {
    $ver = & foundry --version 2>&1
    Write-Host "  Foundry already installed: $ver" -ForegroundColor Green
} else {
    Write-Host "  Foundry not found." -ForegroundColor Yellow
    Write-Host "  Foundry Local is an AI backend for running models (DeepSeek, Qwen, etc.)" -ForegroundColor Gray
    Write-Host ""

    # Check for winget — installation is impossible without it
    $wingetAvailable = $null -ne (Get-Command winget -ErrorAction SilentlyContinue)

    if (-not $wingetAvailable) {
        Write-Host "  winget not found — install Foundry manually:" -ForegroundColor Yellow
        Write-Host "  https://aka.ms/foundry-local" -ForegroundColor Cyan
    } else {
        $answer = Read-Host "  Install Microsoft Foundry Local now? (y/N)"
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            Write-Host "  Installing Foundry Local..." -ForegroundColor Yellow
            try {
                winget install Microsoft.FoundryLocal --accept-source-agreements --accept-package-agreements
                Write-Host "  Foundry Local installed" -ForegroundColor Green
                Write-Host "  Restart PowerShell for foundry to appear in PATH" -ForegroundColor Cyan
            } catch {
                Write-Host "  Installation error: $_" -ForegroundColor Red
                Write-Host "  Install manually: winget install Microsoft.FoundryLocal" -ForegroundColor Cyan
            }
        } else {
            Write-Host "  Skipped. Install later:" -ForegroundColor Gray
            Write-Host "  winget install Microsoft.FoundryLocal" -ForegroundColor Cyan
            Write-Host "  Or use llama.cpp / Ollama — see INSTALL.md" -ForegroundColor Cyan
        }
    }
}

# --- 8. Default Models ---
$isFirstInstall = -not (Test-Path (Join-Path $Root "venv\.first_install_done"))
if ($isFirstInstall) {
    $answer = Read-Host "`nDownload default models? (y/N)"
    if ($answer -eq 'y' -or $answer -eq 'Y') {
        & (Join-Path $Root "install\install-models.ps1")
    }
    "" | Out-File (Join-Path $Root "venv\.first_install_done") -Encoding UTF8
}

# --- 9. Desktop shortcuts ---
Write-Host "`nDesktop shortcuts..." -ForegroundColor Yellow
$shortcutsScript = Join-Path $Root "install\install-shortcuts.ps1"
if (Test-Path $shortcutsScript) {
    try {
        & $shortcutsScript
        Write-Host "  Shortcuts created" -ForegroundColor Green
    } catch {
        Write-Host "  Failed to create shortcuts: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  install-shortcuts.ps1 not found — skipping" -ForegroundColor Gray
}

# --- 10. Summary ---
Write-Host "`n$("=" * 50)" -ForegroundColor Green
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""

# Re-check after possible Foundry installation in step 7
$foundryReady = $null -ne (Get-Command foundry -ErrorAction SilentlyContinue)

Write-Host "Next steps:" -ForegroundColor Cyan
if ($foundryReady) {
    Write-Host "  1. Start Foundry service:"
    Write-Host "     foundry service start"
    Write-Host "  2. Download a model (if not already downloaded):"
    Write-Host "     foundry model download qwen2.5-0.5b-instruct-generic-cpu"
    Write-Host "  3. Start the server:"
    Write-Host "     venv\Scripts\python.exe run.py"
    Write-Host "  4. Open: http://localhost:9696"
} else {
    Write-Host "  1. Install AI backend (choose one):"
    Write-Host "     Foundry Local:  winget install Microsoft.FoundryLocal"
    Write-Host "     llama.cpp:      https://github.com/ggerganov/llama.cpp/releases"
    Write-Host "     Ollama:         https://ollama.com/download"
    Write-Host "     More info:      INSTALL.md"
    Write-Host "  2. (Optional) Fill .env via setup wizard:"
    Write-Host "     .\setup-env.ps1"
    Write-Host "  3. Start the server:"
    Write-Host "     venv\Scripts\python.exe run.py"
    Write-Host "  4. Open: http://localhost:9696"
}
