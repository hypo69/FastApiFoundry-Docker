# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Установка HuggingFace CLI и настройка окружения
# =============================================================================
# Описание:
#   Устанавливает huggingface_hub, transformers, accelerate.
#   Авторизует CLI через HF_TOKEN из .env.
#   Выводит инструкцию по работе с публичными и закрытыми моделями.
#
# Примеры:
#   .\install-huggingface-cli.ps1                  # установка + авторизация
#   .\install-huggingface-cli.ps1 -SkipAuth        # только установка
#   .\install-huggingface-cli.ps1 -Token "hf_..."  # с явным токеном
#
# File: install-huggingface-cli.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

param(
    [string]$Token     = "",
    [switch]$SkipAuth,
    [switch]$SkipInstall
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host ""
Write-Host "🤗 HuggingFace CLI Setup" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# 1. Python / venv
# -----------------------------------------------------------------------------
$python = $null
foreach ($p in @(
    "$Root\venv\Scripts\python.exe",
    "$Root\venv\Scripts\python311.exe",
    "python", "python3", "python311"
)) {
    if (Get-Command $p -ErrorAction SilentlyContinue) { $python = $p; break }
    if (Test-Path $p) { $python = $p; break }
}

if (-not $python) {
    Write-Host "❌ Python not found. Run install.ps1 first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python: $python" -ForegroundColor Green

# -----------------------------------------------------------------------------
# 2. Установка пакетов
# -----------------------------------------------------------------------------
if (-not $SkipInstall) {
    Write-Host "`n📦 Installing HuggingFace packages..." -ForegroundColor Yellow

    $packages = @(
        "huggingface_hub>=0.23.0",
        "transformers>=4.40.0",
        "accelerate>=0.30.0"
    )

    foreach ($pkg in $packages) {
        Write-Host "  Installing $pkg..." -ForegroundColor Gray
        & $python -m pip install $pkg --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $pkg" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Failed: $pkg" -ForegroundColor Red
        }
    }
} else {
    Write-Host "⏭️  Skipping package installation" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# 3. Загрузка токена из .env
# -----------------------------------------------------------------------------
$envPath = Join-Path $Root ".env"

if (-not $Token) {
    if (Test-Path $envPath) {
        $line = Get-Content $envPath | Where-Object { $_ -match '^HF_TOKEN=' }
        if ($line) {
            $Token = ($line -split '=', 2)[1].Trim().Trim('"').Trim("'")
        }
    }
}

# -----------------------------------------------------------------------------
# 4. Авторизация
# -----------------------------------------------------------------------------
if (-not $SkipAuth) {
    Write-Host "`n🔐 HuggingFace Authorization..." -ForegroundColor Yellow

    if (-not $Token) {
        Write-Host "⚠️  HF_TOKEN not found in .env" -ForegroundColor Yellow
        Write-Host "   Get your token at: https://huggingface.co/settings/tokens" -ForegroundColor Cyan
        Write-Host "   Then add to .env:  HF_TOKEN=hf_your_token_here" -ForegroundColor Gray
        Write-Host ""
        $Token = Read-Host "   Enter HF token (or press Enter to skip)"
    }

    if ($Token) {
        # Сохранить в .env если ещё нет
        if (Test-Path $envPath) {
            $content = Get-Content $envPath -Raw
            if ($content -match 'HF_TOKEN=') {
                $content = $content -replace 'HF_TOKEN=.*', "HF_TOKEN=$Token"
            } else {
                $content += "`nHF_TOKEN=$Token"
            }
            Set-Content $envPath $content -NoNewline
            Write-Host "✅ HF_TOKEN saved to .env" -ForegroundColor Green
        }

        # Авторизация через huggingface-cli
        Write-Host "   Logging in to HuggingFace Hub..." -ForegroundColor Gray
        $loginResult = & $python -c "
from huggingface_hub import login, whoami
try:
    login(token='$Token', add_to_git_credential=False)
    info = whoami()
    print(f'OK:{info[\"name\"]}')
except Exception as e:
    print(f'ERR:{e}')
" 2>&1

        if ($loginResult -match '^OK:(.+)') {
            Write-Host "✅ Logged in as: $($Matches[1])" -ForegroundColor Green
        } else {
            Write-Host "❌ Login failed: $loginResult" -ForegroundColor Red
            Write-Host "   Check your token at: https://huggingface.co/settings/tokens" -ForegroundColor Cyan
        }
    } else {
        Write-Host "⏭️  Skipping authorization (no token)" -ForegroundColor Gray
    }
}

# -----------------------------------------------------------------------------
# 5. Проверка установки
# -----------------------------------------------------------------------------
Write-Host "`n🔍 Checking installation..." -ForegroundColor Yellow

$checkResult = & $python -c "
import sys
results = []
try:
    import huggingface_hub; results.append(f'huggingface_hub {huggingface_hub.__version__}')
except: results.append('huggingface_hub MISSING')
try:
    import transformers; results.append(f'transformers {transformers.__version__}')
except: results.append('transformers MISSING')
try:
    import accelerate; results.append(f'accelerate {accelerate.__version__}')
except: results.append('accelerate MISSING')
try:
    import torch; results.append(f'torch {torch.__version__} (CUDA: {torch.cuda.is_available()})')
except: results.append('torch MISSING')
print('\n'.join(results))
" 2>&1

$checkResult | ForEach-Object {
    if ($_ -match 'MISSING') {
        Write-Host "  ❌ $_" -ForegroundColor Red
    } else {
        Write-Host "  ✅ $_" -ForegroundColor Green
    }
}

# -----------------------------------------------------------------------------
# 6. Инструкция
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "📚 HOW TO USE HUGGINGFACE MODELS" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host @"

✅ ПУБЛИЧНЫЕ МОДЕЛИ (без лицензии — скачиваются сразу):
   • microsoft/phi-2
   • microsoft/Phi-3-mini-4k-instruct
   • TinyLlama/TinyLlama-1.1B-Chat-v1.0
   • Qwen/Qwen2.5-0.5B-Instruct
   • Qwen/Qwen2.5-1.5B-Instruct
   • deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B

   Скачать через API:
     POST http://localhost:9696/api/v1/hf/models/download
     {"model_id": "microsoft/phi-2"}

   Или через PowerShell:
     .\scripts\hf-download-model.ps1 -ModelId "microsoft/phi-2"

"@ -ForegroundColor White

Write-Host @"
⚠️  МОДЕЛИ С ЛИЦЕНЗИЕЙ (Gemma, Llama, Mistral):
   Шаг 1: Откройте страницу модели в браузере:
           https://huggingface.co/google/gemma-2-2b-it
           https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
           https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3

   Шаг 2: Нажмите "Agree and access repository"
           (нужен аккаунт на huggingface.co)

   Шаг 3: Убедитесь что HF_TOKEN задан в .env

   Шаг 4: Скачайте:
           .\scripts\hf-download-model.ps1 -ModelId "google/gemma-2-2b-it"

"@ -ForegroundColor Yellow

Write-Host @"
🔑 ТОКЕН:
   Получить: https://huggingface.co/settings/tokens
   Тип:      "Read" достаточно для скачивания
   Сохранить в .env: HF_TOKEN=hf_ваш_токен

📁 МОДЕЛИ СОХРАНЯЮТСЯ В:
   ~/.models/hf
   (настраивается через HF_MODELS_DIR в .env)

🌐 УПРАВЛЕНИЕ ЧЕРЕЗ ВЕБ-ИНТЕРФЕЙС:
   http://localhost:9696 → вкладка HuggingFace

"@ -ForegroundColor Cyan

Write-Host "✅ Setup complete!" -ForegroundColor Green
