# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry - Главный установщик
# =============================================================================
# Описание:
#   Устанавливает Python venv, зависимости, создаёт .env и папку logs.
#   Foundry / llama.cpp / Ollama устанавливаются отдельно (см. INSTALL.md).
#
# Использование:
#   .\install.ps1              # стандартная установка
#   .\install.ps1 -Force       # переустановка venv
#   .\install.ps1 -SkipRag     # без RAG зависимостей
#
# File: install.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
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
Write-Host "`nПроверка Python..." -ForegroundColor Yellow

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "python311")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(1[1-9]|[2-9]\d)") {
            $pythonCmd = $cmd
            Write-Host "  Python найден: $ver ($cmd)" -ForegroundColor Green
            break
        }
    } catch { }
}

if (-not $pythonCmd) {
    Write-Host "  Python 3.11+ не найден в системе." -ForegroundColor Yellow

    $localZip = Join-Path $Root "bin\Python-3.11.9.zip"
    if (Test-Path $localZip) {
        Write-Host "  Найден локальный интерпретатор: $localZip" -ForegroundColor Cyan
        $answer = Read-Host "  Установить Python из локального архива? (y/N)"
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            $localPythonDir = Join-Path $Root "bin\Python-3.11.9"
            if (-not (Test-Path $localPythonDir)) {
                Write-Host "  Распаковка $localZip ..." -ForegroundColor Yellow
                Expand-Archive -Path $localZip -DestinationPath $localPythonDir
                Write-Host "  Готово" -ForegroundColor Green
            } else {
                Write-Host "  Интерпретатор уже распакован" -ForegroundColor Gray
            }

            # Ищем python.exe внутри распакованной директории
            $localPythonExe = Get-ChildItem -Path $localPythonDir -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue |
                              Select-Object -First 1 -ExpandProperty FullName

            if ($localPythonExe) {
                $ver = & $localPythonExe --version 2>&1
                Write-Host "  Используется локальный Python: $ver" -ForegroundColor Green
                Write-Host "  Путь: $localPythonExe" -ForegroundColor Gray
                $pythonCmd = $localPythonExe
            } else {
                Write-Host "  python.exe не найден внутри архива. Проверьте содержимое bin\Python-3.11.9.zip" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "  Установка отменена. Скачайте Python вручную: https://www.python.org/downloads/" -ForegroundColor Cyan
            exit 1
        }
    } else {
        Write-Host "  Python 3.11+ не найден и локальный архив bin\Python-3.11.9.zip отсутствует." -ForegroundColor Red
        Write-Host "  Скачайте Python с https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
}

# --- 2. venv ---
Write-Host "`nВиртуальное окружение..." -ForegroundColor Yellow
$venvPath = Join-Path $Root "venv"

if ((Test-Path $venvPath) -and $Force) {
    Remove-Item $venvPath -Recurse -Force
    Write-Host "  Старый venv удалён" -ForegroundColor Gray
}

if (-not (Test-Path $venvPath)) {
    & $pythonCmd -m venv $venvPath
    Write-Host "  venv создан: $venvPath" -ForegroundColor Green
} else {
    Write-Host "  venv уже существует (используйте -Force для пересоздания)" -ForegroundColor Gray
}

$pip = Join-Path $venvPath "Scripts\pip.exe"
$python = Join-Path $venvPath "Scripts\python.exe"

# --- 2.1. Обновление pip ---
Write-Host "`nОбновление pip..." -ForegroundColor Yellow
& $python -m pip install --upgrade pip
Write-Host "  pip обновлён" -ForegroundColor Green

# --- 3. Зависимости ---
Write-Host "`nУстановка зависимостей..." -ForegroundColor Yellow
& $python -m pip install -r (Join-Path $Root "requirements.txt")
Write-Host "  Основные зависимости установлены" -ForegroundColor Green

# --- 4. RAG зависимости ---
if (-not $SkipRag) {
    Write-Host "`nRAG зависимости (sentence-transformers, faiss-cpu)..." -ForegroundColor Yellow
    Write-Host "  Это может занять несколько минут..." -ForegroundColor Gray
    try {
        & $python -m pip install sentence-transformers faiss-cpu --quiet
        Write-Host "  RAG зависимости установлены" -ForegroundColor Green
    } catch {
        Write-Host "  Не удалось установить RAG зависимости: $_" -ForegroundColor Yellow
        Write-Host "  Запустите позже: python install_rag_deps.py" -ForegroundColor Cyan
    }
} else {
    Write-Host "`nRAG зависимости пропущены (-SkipRag)" -ForegroundColor Gray
}

# --- 5. .env ---
Write-Host "`nКонфигурация .env..." -ForegroundColor Yellow
$envFile = Join-Path $Root ".env"
$envExample = Join-Path $Root ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "  .env создан из .env.example" -ForegroundColor Green
    } else {
        "# FastAPI Foundry`nFOUNDRY_BASE_URL=http://localhost:50477/v1" | Out-File $envFile -Encoding UTF8
        Write-Host "  .env создан с настройками по умолчанию" -ForegroundColor Green
    }
    Write-Host "  Отредактируйте .env при необходимости" -ForegroundColor Cyan
} else {
    Write-Host "  .env уже существует" -ForegroundColor Gray
}

# --- 6. Папка logs ---
Write-Host "`nПапка logs..." -ForegroundColor Yellow
$logsDir = Join-Path $Root "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Host "  logs/ создана" -ForegroundColor Green
} else {
    Write-Host "  logs/ уже существует" -ForegroundColor Gray
}

# --- 7. llama.cpp ---
Write-Host "`nllama.cpp сервер..." -ForegroundColor Yellow

$binDir = Join-Path $Root "bin"
$llamaZip = if (Test-Path $binDir) {
    Get-ChildItem -Path $binDir -Filter "llama-*-bin-win-*.zip" -ErrorAction SilentlyContinue | Select-Object -First 1
}

if (-not $llamaZip) {
    Write-Host "  llama.cpp архив не найден в bin\ — пропущено" -ForegroundColor Gray
} else {
    $llamaDir = Join-Path $binDir $llamaZip.BaseName
    if (-not (Test-Path $llamaDir)) {
        Write-Host "  Распаковка $($llamaZip.Name) ..." -ForegroundColor Yellow
        Expand-Archive -Path $llamaZip.FullName -DestinationPath $llamaDir
        Write-Host "  Готово: $llamaDir" -ForegroundColor Green
    } else {
        Write-Host "  llama.cpp уже распакован" -ForegroundColor Gray
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
            Write-Host "  LLAMA_SERVER_PATH уже есть в .env" -ForegroundColor Gray
        }
    } else {
        Write-Host "  llama-server.exe не найден внутри архива" -ForegroundColor Yellow
    }
}

# --- 8. Foundry ---
Write-Host "`nAI бэкенд (Foundry Local)..." -ForegroundColor Yellow

# Проверка наличия foundry в PATH
$foundryInstalled = $null -ne (Get-Command foundry -ErrorAction SilentlyContinue)

if ($foundryInstalled) {
    $ver = & foundry --version 2>&1
    Write-Host "  Foundry уже установлен: $ver" -ForegroundColor Green
} else {
    Write-Host "  Foundry не найден." -ForegroundColor Yellow
    Write-Host "  Foundry Local — AI бэкенд для запуска моделей (DeepSeek, Qwen и др.)" -ForegroundColor Gray
    Write-Host ""

    # Проверка наличия winget — без него установка невозможна
    $wingetAvailable = $null -ne (Get-Command winget -ErrorAction SilentlyContinue)

    if (-not $wingetAvailable) {
        Write-Host "  winget не найден — установите Foundry вручную:" -ForegroundColor Yellow
        Write-Host "  https://aka.ms/foundry-local" -ForegroundColor Cyan
    } else {
        $answer = Read-Host "  Установить Microsoft Foundry Local сейчас? (y/N)"
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            Write-Host "  Установка Foundry Local..." -ForegroundColor Yellow
            try {
                winget install Microsoft.FoundryLocal --accept-source-agreements --accept-package-agreements
                Write-Host "  Foundry Local установлен" -ForegroundColor Green
                Write-Host "  Перезапустите PowerShell чтобы foundry появился в PATH" -ForegroundColor Cyan
            } catch {
                Write-Host "  Ошибка установки: $_" -ForegroundColor Red
                Write-Host "  Установите вручную: winget install Microsoft.FoundryLocal" -ForegroundColor Cyan
            }
        } else {
            Write-Host "  Пропущено. Установите позже:" -ForegroundColor Gray
            Write-Host "  winget install Microsoft.FoundryLocal" -ForegroundColor Cyan
            Write-Host "  Или используйте llama.cpp / Ollama — см. INSTALL.md" -ForegroundColor Cyan
        }
    }
}

# --- 8. Модели по умолчанию ---
$isFirstInstall = -not (Test-Path (Join-Path $Root "venv\.first_install_done"))
if ($isFirstInstall) {
    $answer = Read-Host "`nСкачать модели по умолчанию? (y/N)"
    if ($answer -eq 'y' -or $answer -eq 'Y') {
        & (Join-Path $Root "install-models.ps1")
    }
    "" | Out-File (Join-Path $Root "venv\.first_install_done") -Encoding UTF8
}

# --- 9. Итог ---
Write-Host "`n$("=" * 50)" -ForegroundColor Green
Write-Host "Установка завершена!" -ForegroundColor Green
Write-Host ""

# Повторная проверка после возможной установки Foundry в шаге 7
$foundryReady = $null -ne (Get-Command foundry -ErrorAction SilentlyContinue)

Write-Host "Следующие шаги:" -ForegroundColor Cyan
if ($foundryReady) {
    Write-Host "  1. Запустите Foundry сервис:"
    Write-Host "     foundry service start"
    Write-Host "  2. Скачайте модель (если ещё не скачана):"
    Write-Host "     foundry model download qwen2.5-0.5b-instruct-generic-cpu"
    Write-Host "  3. Запустите сервер:"
    Write-Host "     venv\Scripts\python.exe run.py"
    Write-Host "  4. Откройте: http://localhost:9696"
} else {
    Write-Host "  1. Установите AI бэкенд (выберите один):"
    Write-Host "     Foundry Local:  winget install Microsoft.FoundryLocal"
    Write-Host "     llama.cpp:      https://github.com/ggerganov/llama.cpp/releases"
    Write-Host "     Ollama:         https://ollama.com/download"
    Write-Host "     Подробнее:      INSTALL.md"
    Write-Host "  2. (Опционально) Заполните .env через мастер настройки:"
    Write-Host "     .\setup-env.ps1"
    Write-Host "  3. Запустите сервер:"
    Write-Host "     venv\Scripts\python.exe run.py"
    Write-Host "  4. Откройте: http://localhost:9696"
}
