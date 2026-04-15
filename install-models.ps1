# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry - Скачивание моделей по умолчанию
# =============================================================================
# Описание:
#   Скачивает модели по умолчанию для Foundry Local и HuggingFace.
#   Запускается автоматически из install.ps1 при первой установке,
#   или вручную в любой момент.
#
# Использование:
#   .\install-models.ps1
#   .\install-models.ps1 -SkipFoundry
#   .\install-models.ps1 -SkipHuggingFace
#
# File: install-models.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

param(
    [switch]$SkipFoundry,
    [switch]$SkipHuggingFace
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$python = Join-Path $Root "venv\Scripts\python.exe"

Write-Host "FastAPI Foundry - Загрузка моделей" -ForegroundColor Green
Write-Host ("=" * 50)

# --- Foundry ---
if (-not $SkipFoundry) {
    Write-Host "`nFoundry модель..." -ForegroundColor Yellow

    $foundryReady = $null -ne (Get-Command foundry -ErrorAction SilentlyContinue)
    if (-not $foundryReady) {
        Write-Host "  Foundry не установлен, пропускаем" -ForegroundColor Gray
    } else {
        $foundryModel = "qwen2.5-0.5b-instruct-generic-cpu"
        $answer = Read-Host "  Скачать '$foundryModel' (~300 MB)? (y/N)"
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            Write-Host "  Запуск Foundry сервиса..." -ForegroundColor Gray
            & foundry service start 2>&1 | Out-Null
            Write-Host "  Скачивание $foundryModel ..." -ForegroundColor Yellow
            & foundry model download $foundryModel
            Write-Host "  Готово" -ForegroundColor Green
        }
    }
}

# --- HuggingFace ---
if (-not $SkipHuggingFace) {
    Write-Host "`nHuggingFace модель (для RAG)..." -ForegroundColor Yellow

    if (-not (Test-Path $python)) {
        Write-Host "  venv не найден, пропускаем" -ForegroundColor Gray
    } else {
        $hfModel = "sentence-transformers/all-MiniLM-L6-v2"
        $answer = Read-Host "  Скачать '$hfModel' (~90 MB)? (y/N)"
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            Write-Host "  Скачивание $hfModel ..." -ForegroundColor Yellow
            & $python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('$hfModel')"
            Write-Host "  Готово" -ForegroundColor Green
        }
    }
}

Write-Host "`n$("=" * 50)" -ForegroundColor Green
Write-Host "Готово!" -ForegroundColor Green
