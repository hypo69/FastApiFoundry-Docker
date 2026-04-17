# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry - Главный установщик
# =============================================================================
# Описание:
#   Инсталляция виртуального окружения Python, установка зависимостей,
#   создание файла .env и подготовка директории логов.
#   Установка Foundry / llama.cpp выполняется отдельно (см. INSTALL.md).
#
# Использование:
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
    # Принудительная переустановка виртуального окружения
    [switch]$Force,
    # Пропуск установки библиотек для векторного поиска (RAG)
    [switch]$SkipRag
)

# Обоснование остановки при ошибках: предотвращение некорректной настройки системы при сбое на промежуточном этапе.
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

Write-Host "FastAPI Foundry - Установка системы" -ForegroundColor Green
Write-Host ("=" * 50)

# --- 1. Проверка наличия Python ---
# Поиск подходящей версии Python (3.11+). Обоснование: использование современных фич типизации и асинхронности.
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

    # Попытка использования локального архива. Обоснование: обеспечение автономной установки при отсутствии глобального Python.
    $localZip = Join-Path $Root "bin\Python-3.11.9.zip"
    if (Test-Path $localZip) {
        Write-Host "  Обнаружен локальный архив интерпретатора: $localZip" -ForegroundColor Cyan
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

            # Поиск исполняемого файла во вложенных папках архива
            $localPythonExe = Get-ChildItem -Path $localPythonDir -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue |
                              Select-Object -First 1 -ExpandProperty FullName

            if ($localPythonExe) {
                $ver = & $localPythonExe --version 2>&1
                Write-Host "  Использование локального Python: $ver" -ForegroundColor Green
                Write-Host "  Путь: $localPythonExe" -ForegroundColor Gray
                $pythonCmd = $localPythonExe
            } else {
                Write-Host "  python.exe не найден внутри архива. Проверьте структуру bin\Python-3.11.9.zip" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "  Отмена установки. Требуется ручная загрузка: https://www.python.org/downloads/" -ForegroundColor Cyan
            exit 1
        }
    } else {
        Write-Host "  Python 3.11+ не найден, локальный архив отсутствует." -ForegroundColor Red
        Write-Host "  Загрузите Python с официального сайта: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
}

# --- 2. Инициализация виртуального окружения (venv) ---
# Обоснование: Изоляция библиотек проекта от системного Python предотвращает 
# конфликты версий и упрощает управление зависимостями.
Write-Host "`nСоздание виртуального окружения..." -ForegroundColor Yellow
$venvPath = Join-Path $Root "venv"

if ((Test-Path $venvPath) -and $Force) {
    # Удаление старого окружения при использовании флага Force.
    Remove-Item $venvPath -Recurse -Force
    Write-Host "  Старое окружение venv удалено" -ForegroundColor Gray
}

if (-not (Test-Path $venvPath)) {
    & $pythonCmd -m venv $venvPath
    Write-Host "  venv создан по пути: $venvPath" -ForegroundColor Green
} else {
    Write-Host "  venv уже существует (используйте -Force для пересоздания)" -ForegroundColor Gray
}

$pip = Join-Path $venvPath "Scripts\pip.exe"
$python = Join-Path $venvPath "Scripts\python.exe"

# --- 2.1. Обновление менеджера пакетов pip ---
Write-Host "`nОбновление pip..." -ForegroundColor Yellow
& $python -m pip install --upgrade pip
Write-Host "  pip обновлен до актуальной версии" -ForegroundColor Green

# --- 3. Установка основных зависимостей ---
# Обоснование: инсталляция базового стека для работы FastAPI и AI-функционала.
Write-Host "`nУстановка библиотек из requirements.txt..." -ForegroundColor Yellow
& $python -m pip install -r (Join-Path $Root "requirements.txt")
Write-Host "  Основные зависимости установлены" -ForegroundColor Green

# --- 4. Установка зависимостей системы RAG (Retrieval Augmented Generation) ---
# Обоснование: Библиотеки faiss и sentence-transformers имеют значительный объем
# и вынесены в опциональный блок для ускорения базовой установки.
if (-not $SkipRag) {
    Write-Host "`nУстановка RAG компонентов (transformers, faiss)..." -ForegroundColor Yellow
    Write-Host "  Это может занять некоторое время..." -ForegroundColor Gray
    try {
        & $python -m pip install sentence-transformers faiss-cpu --quiet
        Write-Host "  RAG зависимости успешно установлены" -ForegroundColor Green
    } catch {
        Write-Host "  Ошибка при установке RAG: $_" -ForegroundColor Yellow
        Write-Host "  Попробуйте запустить позже: python install_rag_deps.py" -ForegroundColor Cyan
    }
} else {
    Write-Host "`nУстановка RAG пропущена (флаг -SkipRag)" -ForegroundColor Gray
}

# --- 5. Подготовка конфигурации .env ---
# Обоснование: Хранение ключей доступа и персональных настроек вне системы контроля версий.
Write-Host "`nНастройка .env файла..." -ForegroundColor Yellow
$envFile = Join-Path $Root ".env"
$envExample = Join-Path $Root ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "  Создание .env на основе шаблона .env.example" -ForegroundColor Green
    } else {
        "# FastAPI Foundry`nFOUNDRY_BASE_URL=http://localhost:50477/v1" | Out-File $envFile -Encoding UTF8
        Write-Host "  Создание .env с базовыми настройками" -ForegroundColor Green
    }
    Write-Host "  Отредактируйте .env для настройки API-ключей" -ForegroundColor Cyan
} else {
    Write-Host "  Файл .env уже существует" -ForegroundColor Gray
}

# --- 6. Создание директории логов ---
# Обоснование: Гарантированное наличие папки для работы LOGGING-STANDARD.md.
Write-Host "`nПодготовка папки логов..." -ForegroundColor Yellow
$logsDir = Join-Path $Root "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
    Write-Host "  logs/ создана" -ForegroundColor Green
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
            Write-Host "  Installing Foundry Local via winget..." -ForegroundColor Yellow
            Write-Host "  This may take several minutes. Please wait..." -ForegroundColor Gray
            Write-Host "  (downloading ~200MB installer)" -ForegroundColor Gray
            try {
                $job = Start-Job -ScriptBlock {
                    winget install Microsoft.FoundryLocal `
                        --accept-source-agreements `
                        --accept-package-agreements `
                        --disable-interactivity 2>&1
                }

                # Анимация ожидания (спиннер)
                $spinner = @('|', '/', '-', '\')
                $i = 0
                while ($job.State -eq 'Running') {
                    Write-Host "`r  $($spinner[$i % 4]) Установка..." -NoNewline -ForegroundColor Yellow
                    $i++
                    Start-Sleep -Milliseconds 300
                }
                Write-Host "`r  " -NoNewline  # clear spinner line

                $output = Receive-Job $job
                Remove-Job $job

                $output | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

                if ($LASTEXITCODE -eq 0 -or ($output -match 'Successfully installed')) {
                    Write-Host "  Foundry Local успешно установлен" -ForegroundColor Green
                    Write-Host "  Перезапустите PowerShell для обновления PATH" -ForegroundColor Cyan
                } else {
                    Write-Host "  winget завершил работу (код: $LASTEXITCODE)" -ForegroundColor Yellow
                    Write-Host "  Если Foundry не найден после перезапуска, выполните:" -ForegroundColor Cyan
                    Write-Host "  winget install Microsoft.FoundryLocal" -ForegroundColor Cyan
                }
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

# --- 8. Загрузка моделей по умолчанию ---
$isFirstInstall = -not (Test-Path (Join-Path $Root "venv\.first_install_done"))
if ($isFirstInstall) {
    $answer = Read-Host "`nЗагрузить модели по умолчанию? (y/N)"
    if ($answer -eq 'y' -or $answer -eq 'Y') {
        & (Join-Path $Root "install\install-models.ps1")
    }
    "" | Out-File (Join-Path $Root "venv\.first_install_done") -Encoding UTF8
}

# --- 9. Создание ярлыков на рабочем столе ---
Write-Host "`nСоздание ярлыков..." -ForegroundColor Yellow
$shortcutsScript = Join-Path $Root "install\install-shortcuts.ps1"
if (Test-Path $shortcutsScript) {
    try {
        & $shortcutsScript
        Write-Host "  Ярлыки созданы" -ForegroundColor Green
    } catch {
        Write-Host "  Ошибка создания ярлыков: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "  install-shortcuts.ps1 не найден — пропуск" -ForegroundColor Gray
}

# --- 10. Итоговая сводка ---
Write-Host "`n$("=" * 50)" -ForegroundColor Green
Write-Host "Установка завершена!" -ForegroundColor Green
Write-Host ""

$foundryReady = $null -ne (Get-Command foundry -ErrorAction SilentlyContinue)

Write-Host "Следующие шаги:" -ForegroundColor Cyan
if ($foundryReady) {
    Write-Host "  1. Запуск службы Foundry:"
    Write-Host "     foundry service start"
    Write-Host "  2. Загрузка модели (если еще не сделано):"
    Write-Host "     foundry model download qwen2.5-0.5b-instruct-generic-cpu"
    Write-Host "  3. Запуск сервера:"
    Write-Host "     venv\Scripts\python.exe run.py"
    Write-Host "  4. Переход по адресу: http://localhost:9696"
} else {
    Write-Host "  1. Установка AI бэкенда (выберите один):"
    Write-Host "     Foundry Local:  winget install Microsoft.FoundryLocal"
    Write-Host "     llama.cpp:      https://github.com/ggerganov/llama.cpp/releases"
    Write-Host "     Ollama:         https://ollama.com/download"
    Write-Host "     Доп. информация: INSTALL.md"
    Write-Host "  2. (Опционально) Заполнение .env через мастер настройки:"
    Write-Host "     .\setup-env.ps1"
    Write-Host "  3. Запуск сервера:"
    Write-Host "     venv\Scripts\python.exe run.py"
    Write-Host "  4. Переход по адресу: http://localhost:9696"
}
