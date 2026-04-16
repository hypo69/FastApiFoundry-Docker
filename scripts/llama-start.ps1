# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск llama.cpp сервера с GGUF моделью
# =============================================================================
# Описание:
#   Запускает llama-server с OpenAI-совместимым API.
#   FastAPI Foundry подключается к нему как к провайдеру.
#
# Примеры:
#   .\llama-start.ps1 -ModelPath "D:\gemma-2-2b-it-Q6_K.gguf"
#   .\llama-start.ps1 -ModelPath "D:\gemma-2-2b-it-Q6_K.gguf" -Port 8080 -NGL 20
#   .\llama-start.ps1 -Via Api   # через FastAPI Foundry API
#
# File: scripts/llama-start.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    [string]$ModelPath = "",
    [int]$Port         = 8080,
    [string]$Host      = "127.0.0.1",
    [int]$CtxSize      = 4096,
    [int]$Threads      = 0,          # 0 = auto
    [int]$NGL          = 0,          # GPU layers, 0 = CPU only
    [string]$ApiBase   = "http://localhost:9696/api/v1",
    [switch]$ViaApi                  # запустить через FastAPI Foundry API
)

$ErrorActionPreference = 'Continue'

Write-Host "🦙 llama.cpp Server Launcher" -ForegroundColor Cyan

# Автоопределение потоков
if ($Threads -eq 0) { $Threads = [Environment]::ProcessorCount }

# Загрузка пути из .env если не передан
if (-not $ModelPath) {
    $envPath = Join-Path $PSScriptRoot ".." ".env"
    if (Test-Path $envPath) {
        $line = Get-Content $envPath | Where-Object { $_ -match '^LLAMA_MODEL_PATH=' }
        if ($line) { $ModelPath = ($line -split '=', 2)[1].Trim() }
    }
}

if (-not $ModelPath) {
    # Поиск .gguf на диске D:
    Write-Host "🔍 Searching for .gguf files on D:\..." -ForegroundColor Yellow
    $found = Get-ChildItem -Path "D:\" -Filter "*.gguf" -Recurse -Depth 3 -ErrorAction SilentlyContinue
    if ($found) {
        Write-Host "Found models:" -ForegroundColor Green
        $found | ForEach-Object { Write-Host "  $($_.FullName)  ($([math]::Round($_.Length/1GB,2)) GB)" }
        $ModelPath = $found[0].FullName
        Write-Host "Using: $ModelPath" -ForegroundColor Yellow
    } else {
        Write-Host "❌ No .gguf files found. Specify -ModelPath" -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path $ModelPath)) {
    Write-Host "❌ File not found: $ModelPath" -ForegroundColor Red
    exit 1
}

$modelName = Split-Path $ModelPath -Leaf
Write-Host "Model:   $modelName" -ForegroundColor White
Write-Host "Port:    $Port" -ForegroundColor White
Write-Host "Threads: $Threads" -ForegroundColor White
Write-Host "GPU layers: $NGL" -ForegroundColor White

# Запуск через FastAPI API
if ($ViaApi) {
    try {
        $body = @{
            model_path   = $ModelPath
            port         = $Port
            host         = $Host
            ctx_size     = $CtxSize
            threads      = $Threads
            n_gpu_layers = $NGL
        } | ConvertTo-Json

        $result = Invoke-RestMethod -Uri "$ApiBase/llama/start" `
            -Method POST -ContentType "application/json" -Body $body -TimeoutSec 15

        if ($result.success) {
            Write-Host "✅ Started via API (PID: $($result.pid))" -ForegroundColor Green
            Write-Host "   OpenAI URL: $($result.openai_url)" -ForegroundColor Cyan
        } else {
            Write-Host "❌ $($result.error)" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ API error: $_" -ForegroundColor Red
        exit 1
    }
    exit 0
}

# Прямой запуск llama-server
$serverBin = $null
foreach ($name in @("llama-server.exe", "server.exe")) {
    $found = Get-Command $name -ErrorAction SilentlyContinue
    if ($found) { $serverBin = $found.Source; break }
    # Стандартные пути
    foreach ($dir in @("C:\llama.cpp", "C:\Program Files\llama.cpp")) {
        $p = Join-Path $dir $name
        if (Test-Path $p) { $serverBin = $p; break }
    }
    if ($serverBin) { break }
}

if (-not $serverBin) {
    Write-Host "❌ llama-server not found in PATH" -ForegroundColor Red
    Write-Host "   Download: https://github.com/ggerganov/llama.cpp/releases" -ForegroundColor Cyan
    Write-Host "   Or add to PATH and retry" -ForegroundColor Gray
    exit 1
}

Write-Host "🚀 Starting llama-server..." -ForegroundColor Green

$args = @(
    "--model",        $ModelPath,
    "--host",         $Host,
    "--port",         $Port,
    "--ctx-size",     $CtxSize,
    "--threads",      $Threads,
    "--n-gpu-layers", $NGL
)

& $serverBin @args

# Сохранить URL в .env для FastAPI Foundry
$envPath = Join-Path $PSScriptRoot ".." ".env"
if (Test-Path $envPath) {
    $content = Get-Content $envPath
    $newLine = "LLAMA_BASE_URL=http://${Host}:${Port}/v1"
    if ($content -match '^LLAMA_BASE_URL=') {
        $content = $content -replace '^LLAMA_BASE_URL=.*', $newLine
    } else {
        $content += "`n$newLine"
    }
    $content | Set-Content $envPath
    Write-Host "✅ LLAMA_BASE_URL saved to .env" -ForegroundColor Green
}
