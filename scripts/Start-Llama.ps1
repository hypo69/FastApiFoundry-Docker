# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск llama.cpp сервера с GGUF моделью
# =============================================================================
# Описание:
#   Инициализация сервера llama-server для предоставления OpenAI-совместимого API.
#   Обеспечение связи между локальными GGUF моделями и FastAPI Foundry.
#
# Примеры:
#   .\llama-start.ps1 -ModelPath "D:\gemma-2-2b-it-Q6_K.gguf"
#   .\llama-start.ps1 -ModelPath "D:\gemma-2-2b-it-Q6_K.gguf" -Port 8080 -NGL 20
#   .\llama-start.ps1 -Via Api   # через FastAPI Foundry API
#
# File: scripts/llama-start.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Автор: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    # Путь к файлу модели в формате GGUF
    [string]$ModelPath = "",
    # Порт для прослушивания входящих HTTP запросов
    [int]$Port         = 8080,
    [string]$LlamaHost = "127.0.0.1",
    # Размер контекстного окна (токены)
    [int]$CtxSize      = 4096,
    # Количество потоков CPU. Обоснование: 0 — автоматическое определение всех ядер.
    [int]$Threads      = 0,
    # Количество слоев, переносимых на GPU (NGL). Обоснование: 0 — только CPU.
    [int]$NGL          = 0,
    [string]$ApiBase   = "http://localhost:9696/api/v1",
    # Флаг для делегирования запуска самому серверу FastAPI Foundry
    [switch]$ViaApi
)

$ErrorActionPreference = 'Continue'

Write-Host "🦙 Запуск сервера llama.cpp" -ForegroundColor Cyan

# Определение количества потоков на основе аппаратных ресурсов
if ($Threads -eq 0) { $Threads = [Environment]::ProcessorCount }

# Получение пути к модели из конфигурации .env при отсутствии явного параметра
if (-not $ModelPath) {
    $envPath = Join-Path $PSScriptRoot ".." ".env"
    if (Test-Path $envPath) {
        $line = Get-Content $envPath | Where-Object { $_ -match '^LLAMA_MODEL_PATH=' }
        if ($line) { $ModelPath = ($line -split '=', 2)[1].Trim() }
    }
}

if (-not $ModelPath) {
    # Автоматический поиск файлов .gguf на диске D:
    # Обоснование: Упрощение первого запуска для пользователей Windows, хранящих тяжелые модели на доп. дисках.
    Write-Host "🔍 Поиск моделей .gguf на диске D:\..." -ForegroundColor Yellow
    $found = Get-ChildItem -Path "D:\" -Filter "*.gguf" -Recurse -Depth 3 -ErrorAction SilentlyContinue
    if ($found) {
        Write-Host "Обнаруженные модели:" -ForegroundColor Green
        $found | ForEach-Object { Write-Host "  $($_.FullName)  ($([math]::Round($_.Length/1GB,2)) ГБ)" }
        $ModelPath = $found[0].FullName
        Write-Host "Выбрано автоматически: $ModelPath" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Файлы .gguf не найдены. Укажите -ModelPath" -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path $ModelPath)) {
    Write-Host "❌ Файл не найден: $ModelPath" -ForegroundColor Red
    exit 1
}

# Вывод текущих параметров запуска
$modelName = Split-Path $ModelPath -Leaf
Write-Host "Модель:   $modelName" -ForegroundColor White
Write-Host "Порт:     $Port" -ForegroundColor White
Write-Host "Потоки:   $Threads" -ForegroundColor White
Write-Host "GPU слои: $NGL" -ForegroundColor White

# Инициирование запуска через API FastAPI Foundry
# Обоснование: Позволяет управлять жизненным циклом процесса через веб-интерфейс.
if ($ViaApi) {
    try {
        $body = @{
            model_path   = $ModelPath
            port         = $Port
            host         = $LlamaHost
            ctx_size     = $CtxSize
            threads      = $Threads
            n_gpu_layers = $NGL
        } | ConvertTo-Json

        $result = Invoke-RestMethod -Uri "$ApiBase/llama/start" `
            -Method POST -ContentType "application/json" -Body $body -TimeoutSec 15

        if ($result.success) {
            Write-Host "✅ Запущено через API (PID: $($result.pid))" -ForegroundColor Green
            Write-Host "   URL интерфейса OpenAI: $($result.openai_url)" -ForegroundColor Cyan
        } else {
            Write-Host "❌ $($result.error)" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Ошибка обращения к API: $_" -ForegroundColor Red
        exit 1
    }
    exit 0
}

# Find llama-server binary: bin/ in project root, then PATH, then standard locations
$serverBin = $null
$projectRoot = Join-Path $PSScriptRoot ".."
$binDir = Join-Path $projectRoot "bin"

# 1. Search in project bin/ directory (recursive)
if (Test-Path $binDir) {
    $found = Get-ChildItem -Path $binDir -Filter "llama-server.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $serverBin = $found.FullName }
}

# 2. PATH
if (-not $serverBin) {
    foreach ($name in @("llama-server.exe", "server.exe")) {
        $found = Get-Command $name -ErrorAction SilentlyContinue
        if ($found) { $serverBin = $found.Source; break }
    }
}

# 3. Standard install locations
if (-not $serverBin) {
    foreach ($p in @("C:\llama.cpp\llama-server.exe", "C:\Program Files\llama.cpp\llama-server.exe")) {
        if (Test-Path $p) { $serverBin = $p; break }
    }
}

if (-not $serverBin) {
    Write-Host "❌ llama-server не найден" -ForegroundColor Red
    Write-Host "   Проверено: $binDir" -ForegroundColor Gray
    Write-Host "   Загрузите бинарные файлы: https://github.com/ggerganov/llama.cpp/releases" -ForegroundColor Cyan
    exit 1
}

Write-Host "   Бинарник: $serverBin" -ForegroundColor Gray

Write-Host "🚀 Запуск процесса llama-server..." -ForegroundColor Green

$args = @(
    "--model",        $ModelPath,
    "--host",         $LlamaHost,
    "--port",         $Port,
    "--ctx-size",     $CtxSize,
    "--threads",      $Threads,
    "--n-gpu-layers", $NGL
)

# Вызов внешнего процесса сервера
& $serverBin @args

# Сохранение итогового URL в файл .env для автоматизации последующих запусков
$envPath = Join-Path $PSScriptRoot ".." ".env"
if (Test-Path $envPath) {
    $content = Get-Content $envPath
    $newLine = "LLAMA_BASE_URL=http://${LlamaHost}:${Port}/v1"
    if ($content -match '^LLAMA_BASE_URL=') {
        $content = $content -replace '^LLAMA_BASE_URL=.*', $newLine
    } else {
        $content += "`n$newLine"
    }
    $content | Set-Content $envPath
    Write-Host "✅ Параметр LLAMA_BASE_URL успешно обновлен в .env" -ForegroundColor Green
}
