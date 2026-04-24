# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry Smart Launcher (Умный запуск)
# =============================================================================
# Описание:
#   Основная точка входа для запуска сервера FastAPI Foundry.
#   При первом запуске — автоматическая установка зависимостей через install.ps1.
#   Загрузка переменных .env, обнаружение или запуск службы Foundry AI,
#   опциональный запуск серверов llama.cpp и MkDocs, финальный запуск FastAPI.
#
# Примеры:
#   powershell -ExecutionPolicy Bypass -File .\start.ps1
#   powershell -ExecutionPolicy Bypass -File .\start.ps1 -Config config.json
#
# File: start.ps1
# Project: AiStros
# Package: FastApiFoundry
# Version: 0.6.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: 2025
# =============================================================================

param(
    # Path to the JSON configuration file (relative to the project root)
    [string]$Config = 'config.json'
)

# Настройка режима обработки некритических ошибок
$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host '🚀 FastAPI Foundry Smart Launcher - Запуск' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Этап 0: Проверка обновлений (git tag-based)
# -----------------------------------------------------------------------------

$UpdateScript = "$Root\scripts\Update-Project.ps1"
if (Test-Path $UpdateScript) {
    try {
        # Execution of the update script
        & $UpdateScript
    } catch {
        Write-Host "⚠️ Проверка обновлений завершилась с ошибкой: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host '💡 scripts/Update-Project.ps1 not found — update check skipped.' -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# Этап 1: Проверка зависимостей и установка
# -----------------------------------------------------------------------------

# Создание директории архива при инсталляции
# Creation of the archive directory during installation
if (-not (Test-Path "$Root\archive")) {
    New-Item -ItemType Directory -Path "$Root\archive" -Force | Out-Null
}

<#
.SYNOPSIS
    Активация виртуального окружения Python.
    Настройка путей для работы с pip и python внутри venv.
#>

# Активация виртуального окружения

$ActivateScript = "$Root\venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    . $ActivateScript
    Write-Host '✅ venv активирован' -ForegroundColor Green
} else {
    Write-Host '⚠️ venv/Scripts/Activate.ps1 не найден' -ForegroundColor Yellow
}

# Определение пути к интерпретатору
$venvPath = "$Root\venv\Scripts\python.exe"
if (-not (Test-Path $venvPath)) {
    $venvPath = "$Root\venv\Scripts\python311.exe"
}

if (-not (Test-Path $venvPath)) {
    Write-Host '📦 First launch - dependency installation...' -ForegroundColor Yellow
    Write-Host 'Это может занять несколько минут...' -ForegroundColor Yellow
    
    if (Test-Path "$Root\install.ps1") {
        try {
            & "$Root\install.ps1"
            Write-Host '✅ Установка завершена!' -ForegroundColor Green
        } catch {
            Write-Host "❌ Ошибка установки: $_" -ForegroundColor Red
            Write-Host 'Попробуйте запустить install.ps1 вручную' -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host '❌ install.ps1 не найден!' -ForegroundColor Red
        Write-Host 'Создайте venv вручную: python311 -m venv venv' -ForegroundColor Yellow
        exit 1
    }
}

<#
.SYNOPSIS
    Загрузка переменных окружения из файла.
    Чтение .env файла и экспорт пар КЛЮЧ=ЗНАЧЕНИЕ.
.PARAMETER EnvPath
    Полный путь к файлу .env.
.NOTES
    - Пропуск пустых строк и комментариев (#).
    - Очистка кавычек вокруг значений.
    - Маскировка секретных данных (PASSWORD, SECRET, KEY, TOKEN, PAT) в выводе.
.OUTPUTS
    Переменные устанавливаются в [System.Environment].
#>
function Load-EnvFile {
    param([string]$EnvPath)
    
    $envVarsCount = 0
    $line = $null
    
    if (-not (Test-Path $EnvPath -PathType Leaf)) {
        if (Test-Path $EnvPath -PathType Container) { 
            Write-Host "⚠️ .env — это папка, а не файл: $EnvPath" -ForegroundColor Yellow
        } else {
            Write-Host "⚠️ Файл .env не найден: $EnvPath" -ForegroundColor Yellow
            Write-Host "💡 Создайте .env на основе .env.example" -ForegroundColor Cyan
        }
        return
    }
    
    Write-Host '⚙️ Loading .env variables...' -ForegroundColor Gray
    
    try {
        Get-Content $EnvPath | ForEach-Object {
            $line = $_.Trim()
            
            if ($line -and -not $line.StartsWith('#')) {
                if ($line -match '^([^=]+)=(.*)$') {
                    $key   = $matches[1].Trim()
                    $value = $matches[2].Trim()
                    
                    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                        $value = $value.Substring(1, $value.Length - 2)
                    }
                    if ($value.StartsWith("'") -and $value.EndsWith("'")) {
                        $value = $value.Substring(1, $value.Length - 2)
                    }
                    
                    [System.Environment]::SetEnvironmentVariable($key, $value)
                    $envVarsCount++
                    
                    if ($key -notmatch '(PASSWORD|SECRET|KEY|TOKEN|PAT)') {
                        Write-Host "  ✓ $key = $value" -ForegroundColor DarkGray
                    } else {
                        Write-Host "  ✓ $key = ***" -ForegroundColor DarkGray
                    }
                }
            }
        }
        Write-Host "✅ Environment variables loaded: $envVarsCount" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ошибка загрузки .env: $_" -ForegroundColor Red
    }
}

Load-EnvFile "$Root\.env"

<#
.SYNOPSIS
    Проверка доступности Foundry CLI.
    Поиск утилиты 'foundry' в системном PATH.
.OUTPUTS
    bool — True если утилита найдена.
#>
function Test-FoundryCli {
    try {
        Get-Command foundry -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

<#
.SYNOPSIS
    Поиск TCP-порта службы инференса Foundry.
    Обнаружение активного порта Foundry AI.
.DESCRIPTION
    Поиск процесса 'Inference.Service.Agent', сканирование портов LISTENING
    и проверка через API запрос к /v1/models.
.OUTPUTS
    string — Номер порта или $null.
#>
function Get-FoundryPort {
    $foundryProcess = Get-Process | Where-Object { $_.ProcessName -like "Inference.Service.Agent*" }
    if (-not $foundryProcess) { 
        return $null 
    }
    
    $netstatOutput = netstat -ano | Select-String "$($foundryProcess.Id)" | Select-String "LISTENING"
    foreach ($line in $netstatOutput) {
        if ($line -match ':(\d+)\s') {
            $port = $matches[1]
            try {
                $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/v1/models" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ API Foundry найден на порту $port" -ForegroundColor Green
                    return $port
                }
            } catch { }
        }
    }
    return $null
}

# -----------------------------------------------------------------------------
# Этап 4: Обнаружение или запуск службы Foundry AI
# -----------------------------------------------------------------------------

Write-Host '🔍 Local Foundry check...' -ForegroundColor Cyan

$foundryPort = Get-FoundryPort

if ($foundryPort) {
    Write-Host "✅ Foundry уже запущен на порту $foundryPort" -ForegroundColor Green
    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
} else {
    if (-not (Test-FoundryCli)) {
        Write-Host '⚠️ Foundry CLI not found. AI features might be limited.' -ForegroundColor Yellow
    } else {
        Write-Host '🚀 Starting Foundry service...' -ForegroundColor Yellow
        
        try {
            # Foundry execution in minimized window
            Start-Process -FilePath "foundry" -ArgumentList "service", "start" -WindowStyle Minimized -NoNewWindow:$false
            Write-Host "Выполнение команды запуска службы Foundry" -ForegroundColor Gray
            
            # Опрос готовности Foundry (таймаут 20 секунд)
            for ($i = 1; $i -le 10; $i++) {
                Start-Sleep 2
                $foundryPort = Get-FoundryPort
                if ($foundryPort) {
                    Write-Host "✅ Foundry запущен на порту $foundryPort" -ForegroundColor Green
                    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
                    break
                }
                Write-Host "⏳ Ожидание запуска Foundry... ($i/10)" -ForegroundColor Gray
            }
            
            if (-not $foundryPort) {
                Write-Host "❌ Ошибка запуска Foundry или порт не найден" -ForegroundColor Red
                Write-Host '⚠️ Продолжение работы без поддержки AI.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Сбой при запуске Foundry: $_" -ForegroundColor Red
            Write-Host '⚠️ Продолжение работы без поддержки AI.' -ForegroundColor Yellow
        }
    }
}

# Экспорт базового URL для FastAPI
if ($foundryPort) {
    $env:FOUNDRY_BASE_URL = "http://localhost:$foundryPort/v1/"
    Write-Host "🔗 FOUNDRY_BASE_URL = $env:FOUNDRY_BASE_URL" -ForegroundColor Green
} else {
    Write-Host "⚠️ Foundry not available - AI features disabled" -ForegroundColor Yellow
}
# -----------------------------------------------------------------------------
# Этап 5: Опциональный сервер документации MkDocs
# Активация через параметр docs_server.enabled = true в config.json
# -----------------------------------------------------------------------------
Write-Host '🔍 Проверка конфигурации сервера документации...' -ForegroundColor Cyan

# Чтение секции docs_server из config.json
$docsServerConfig = $null
try {
    $configContent = Get-Content "$Root\$Config" | Out-String
    $parsedConfig = $configContent | ConvertFrom-Json
    
    if ($parsedConfig) {
        $docsServerConfig = $parsedConfig.docs_server
    }
} catch {
    Write-Host "❌ Ошибка чтения config.json для docs_server: $_" -ForegroundColor Red
    $docsServerConfig = $null
}

if ($docsServerConfig -and $docsServerConfig.enabled) {
    # Stop previous mkdocs serve instance if running on this port
    $docsPort = $docsServerConfig.port
    $oldMkdocs = Get-NetTCPConnection -LocalPort $docsPort -State Listen -ErrorAction SilentlyContinue
    if ($oldMkdocs) {
        $oldMkdocsPid = $oldMkdocs.OwningProcess
        try {
            Stop-Process -Id $oldMkdocsPid -Force -ErrorAction Stop
            Write-Host "✅ Предыдущий MkDocs (PID: $oldMkdocsPid) остановлен" -ForegroundColor Green
        } catch {
            Write-Host "⚠️ Не удалось остановить MkDocs (PID: $oldMkdocsPid): $_" -ForegroundColor Yellow
        }
    }

    Write-Host "📚 Сборка документации MkDocs..." -ForegroundColor Yellow
    try {
        Push-Location $Root
        & $venvPath -m mkdocs build --quiet
        Pop-Location
        Write-Host "✅ Документация собрана" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Сборка документации не удалась: $_" -ForegroundColor Yellow
    } 

    Write-Host "🚀 Запуск сервера MkDocs на порту $docsPort..." -ForegroundColor Yellow
    try {
        # Запуск mkdocs serve в отдельном свернутом окне (hot-reload при изменениях docs/)
        $mkdocsProc = Start-Process powershell.exe -ArgumentList @(
            '-NonInteractive', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-Command', "cd '$Root'; & '$venvPath' -m mkdocs serve -a 0.0.0.0:$docsPort"
        ) -WindowStyle Minimized -PassThru
        $script:MkDocsPid = $mkdocsProc.Id
        Write-Host "✅ Сервер MkDocs запущен на http://localhost:$docsPort (PID: $($mkdocsProc.Id))" -ForegroundColor Green
    } catch {
        Write-Host "❌ Сбой при запуске сервера MkDocs: $_" -ForegroundColor Red
        Write-Host "⚠️ Продолжение работы без сервера документации." -ForegroundColor Yellow
    }
} else {
    Write-Host "💡 Сервер документации отключен в config.json (пропуск)" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# Step 6: Optional llama.cpp local inference server
# Only started when LLAMA_MODEL_PATH and LLAMA_AUTO_START=true are set in .env
# -----------------------------------------------------------------------------
<#
.SYNOPSIS
    Обеспечение актуальности бинарных файлов llama.cpp.
    Распаковка llama-server из zip архива в директории bin/.
.OUTPUTS
    string — Путь к llama-server.exe или $null.
#>
function Ensure-LlamaBin {
    $binDir     = Join-Path $Root 'bin'
    $configPath = Join-Path $Root 'config.json'
    $installedVersion = $null
    $cfg = $null
    
    # Find all llama zips, pick the latest by name (build number is in the name)
    $zips = Get-ChildItem -Path $binDir -Filter 'llama-*-bin-win-*.zip' -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending

    if (-not $zips) {
        Write-Host '⚠️  No llama.cpp zip found in bin/' -ForegroundColor Yellow
        return $null
    }

    $latestZip  = $zips[0]
    $latestStem = [System.IO.Path]::GetFileNameWithoutExtension($latestZip.Name)
    $extractDir = Join-Path $binDir $latestStem
    $serverExe  = Join-Path $extractDir 'llama-server.exe'

    # Read installed version from config.json
    try {
        $cfg = Get-Content $configPath -Raw | ConvertFrom-Json
        $installedVersion = $cfg.llama_cpp.bin_version
    } catch { }

    $isUpToDate = ($installedVersion -eq $latestStem) -and (Test-Path $serverExe)

    if ($isUpToDate) {
        Write-Host "✅ llama.cpp binary up-to-date: $latestStem" -ForegroundColor Green
        return $serverExe
    }

    # Version update prompt
    if ($installedVersion -and $installedVersion -ne $latestStem) {
        Write-Host '' 
        Write-Host '📦 New llama.cpp version available!' -ForegroundColor Cyan
        Write-Host "   Installed : $installedVersion" -ForegroundColor Gray
        Write-Host "   Available : $latestStem" -ForegroundColor Green
        $answer = Read-Host '   Install now? [Y/n]'
        if ($answer -match '^[Nn]') {
            Write-Host '⏭️  Skipping update. Using existing binary.' -ForegroundColor Yellow
            # Return existing exe if it still works
            $oldExe = Join-Path $binDir $installedVersion 'llama-server.exe'
            if (Test-Path $oldExe) { return $oldExe }
            Write-Host '⚠️  Old binary not found, proceeding with extraction.' -ForegroundColor Yellow
        }
    } else {
        Write-Host "📦 Extracting $($latestZip.Name) → bin/$latestStem/ ..." -ForegroundColor Yellow
    }

    # Directory cleanup and extraction
    if (Test-Path $extractDir) {
        Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue
    }

    try {
        # Zip has no root folder — extract directly into the named subdirectory
        Expand-Archive -Path $latestZip.FullName -DestinationPath $extractDir -Force
        Write-Host "✅ Extracted: $extractDir" -ForegroundColor Green
    } catch {
        Write-Host "❌ Extraction failed: $_" -ForegroundColor Red
        return $null
    }

    # Configuration update
    try {
        if (-not $cfg) { $cfg = Get-Content $configPath -Raw | ConvertFrom-Json }
        $cfg.llama_cpp.bin_version = $latestStem
        $cfg | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
        Write-Host "✅ config.json updated: llama_cpp.bin_version = $latestStem" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Could not update config.json: $_" -ForegroundColor Yellow
    }

    if (Test-Path $serverExe) { return $serverExe }
    Write-Host "❌ llama-server.exe not found after extraction in $extractDir" -ForegroundColor Red
    return $null
}

<#
.SYNOPSIS
    Запуск сервера llama.cpp.
    Инициализация процесса инференса локальной модели.
.PARAMETER ServerExe
    Путь к бинарному файлу.
.PARAMETER ModelPath
    Путь к файлу модели GGUF.
.PARAMETER Port
    TCP порт для сервера.
#>
function Start-LlamaServer {
    param(
        [string]$ServerExe,
        [string]$ModelPath,
        [int]$Port
    )

    for ($attempt = 1; $attempt -le 2; $attempt++) {
        if (-not (Test-Path $ServerExe)) {
            Write-Host "🔧 llama-server.exe missing, re-extracting (attempt $attempt)..." -ForegroundColor Yellow
            $ServerExe = Ensure-LlamaBin
            if (-not $ServerExe) {
                Write-Host '❌ Cannot find llama-server.exe after extraction.' -ForegroundColor Red
                return $false
            }
        }

        Write-Host "🦙 Starting llama.cpp (attempt $attempt): $([System.IO.Path]::GetFileName($ServerExe))" -ForegroundColor Cyan

        $proc = Start-Process -FilePath $ServerExe `
            -ArgumentList "--model", $ModelPath, "--port", $Port, "--host", "127.0.0.1", "--log-disable" `
            -PassThru -WindowStyle Minimized -ErrorAction SilentlyContinue 

        if (-not $proc) {
            Write-Host "⚠️  Start-Process returned nothing on attempt $attempt." -ForegroundColor Yellow
            $ServerExe = ''  # force re-extract on next attempt
            continue
        }

        # Health endpoint polling
        for ($i = 1; $i -le 5; $i++) {
            Start-Sleep 2
            try {
                $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                if ($r.StatusCode -eq 200) {
                    Write-Host "✅ llama.cpp running on port $Port (PID: $($proc.Id))" -ForegroundColor Green
                    return $true
                }
            } catch { }
            Write-Host "⏳ Waiting for llama.cpp... ($i/5)" -ForegroundColor Gray
        }

        # Crash handling
        if ($proc.HasExited) {
            Write-Host "⚠️  llama-server.exe exited immediately (code $($proc.ExitCode)). Re-extracting..." -ForegroundColor Yellow
            $ServerExe = Ensure-LlamaBin
            if (-not $ServerExe) { return $false }
        }
    }

    Write-Host '❌ llama.cpp failed to start after 2 attempts.' -ForegroundColor Red
    return $false
}

$llamaModelPath = $null
$llamaAutoStart = $false
$llamaPort      = 9780

# Загрузка настроек llama.cpp из config.json
try {
    $cfg        = Get-Content (Join-Path $Root 'config.json') -Raw | ConvertFrom-Json
    $llamaCfg   = $cfg.llama_cpp
    $llamaModelPath = $llamaCfg.model_path
    $llamaAutoStart = [bool]$llamaCfg.auto_start
    $llamaPort      = if ($llamaCfg.port) { [int]$llamaCfg.port } else { 9780 }
} catch {
    Write-Host "⚠️  Could not read llama_cpp from config.json: $_" -ForegroundColor Yellow
}

# Переопределение пути сервера из .env
$llamaServerPathEnv = [System.Environment]::GetEnvironmentVariable('LLAMA_SERVER_PATH')

# Обновление бинарных файлов
$llamaServerExe = Ensure-LlamaBin

if ($llamaModelPath -and $llamaAutoStart) {
    Write-Host '🦙 Auto-starting llama.cpp server...' -ForegroundColor Cyan
    Write-Host "   Model : $llamaModelPath" -ForegroundColor Gray
    Write-Host "   Port  : $llamaPort" -ForegroundColor Gray

    $llamaPort = [System.Environment]::GetEnvironmentVariable('LLAMA_PORT')
    if (-not $llamaPort) { $llamaPort = 9780 }

    # Остановка предыдущих инстансов
    $oldLlama = Get-NetTCPConnection -LocalPort $llamaPort -State Listen -ErrorAction SilentlyContinue
    if ($oldLlama) {
        try {
            Stop-Process -Id $oldLlama.OwningProcess -Force -ErrorAction Stop
            Write-Host "✅ Previous llama.cpp (PID: $($oldLlama.OwningProcess)) stopped" -ForegroundColor Green
            Start-Sleep 1
        } catch {
            Write-Host "⚠️  Could not stop previous llama.cpp: $_" -ForegroundColor Yellow
        }
    }

    if ($llamaServerExe) {
        $started = Start-LlamaServer -ServerExe $llamaServerExe -ModelPath $llamaModelPath -Port $llamaPort
        if ($started) {
            $env:LLAMA_BASE_URL = "http://127.0.0.1:$llamaPort/v1"
            Write-Host "🔗 LLAMA_BASE_URL = $env:LLAMA_BASE_URL" -ForegroundColor Green
            # Сохранение PID для очистки
            $llamaRunning = Get-NetTCPConnection -LocalPort $llamaPort -State Listen -ErrorAction SilentlyContinue
            if ($llamaRunning) { $script:LlamaPid = $llamaRunning.OwningProcess }
        }
    } else {
        Write-Host '❌ llama-server.exe not available, skipping auto-start.' -ForegroundColor Red
    }
} elseif ($llamaModelPath) {
    Write-Host '💡 llama.cpp model configured but auto_start=false in config.json (skipping)' -ForegroundColor Gray
} else {
    Write-Host '💡 llama.cpp: no model_path set in config.json (skipping)' -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# Этап 6.5: Остановка installer-сервера (если запущен)
# -----------------------------------------------------------------------------
$InstallerPidFile = Join-Path $Root 'install\.installer.pid'
if (Test-Path $InstallerPidFile) {
    $installerPid = Get-Content $InstallerPidFile -ErrorAction SilentlyContinue
    if ($installerPid) {
        try {
            $installerProc = Get-Process -Id $installerPid -ErrorAction Stop
            Write-Host "⚠️  Installer server still running (PID: $installerPid) — stopping..." -ForegroundColor Yellow
            $installerProc.Kill()
            $installerProc.WaitForExit(3000)
            Write-Host "✅ Installer server stopped" -ForegroundColor Green
        } catch {
            Write-Host "💡 Installer server (PID: $installerPid) already exited" -ForegroundColor Gray
        }
    }
    Remove-Item $InstallerPidFile -Force -ErrorAction SilentlyContinue
}

# -----------------------------------------------------------------------------
# Этап 7: Запуск сервера FastAPI (блокирующий вызов)
# -----------------------------------------------------------------------------
$PidFile = Join-Path $env:TEMP 'fastapi-foundry.pid'

# Очистка предыдущих процессов FastAPI
if (Test-Path $PidFile) {
    $oldPid = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($oldPid) {
        try {
            $oldProcess = Get-Process -Id $oldPid -ErrorAction Stop
            Write-Host "⚠️ Найден предыдущий процесс FastAPI (PID: $oldPid) — останавливаем..." -ForegroundColor Yellow
            $oldProcess.Kill()
            $oldProcess.WaitForExit(5000)
            Write-Host "✅ Предыдущий процесс остановлен" -ForegroundColor Green
        } catch {
            Write-Host "💡 Предыдущий процесс (PID: $oldPid) уже завершён" -ForegroundColor Gray
        }
    }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

Write-Host '🐍 FastAPI server launch...' -ForegroundColor Cyan

if (-not (Test-Path $venvPath)) {
    Write-Host '❌ ОШИБКА: venv Python не найден после этапа установки!' -ForegroundColor Red
    Write-Host "Ожидаемый путь: $venvPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔗 FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT" -ForegroundColor Gray
Write-Host '🌐 FastAPI Foundry starting...' -ForegroundColor Green
Write-Host "📱 Веб-интерфейс:  http://localhost:9696" -ForegroundColor Cyan
if ($docsServerConfig -and $docsServerConfig.enabled) {
    Write-Host "📚 Документация:   http://localhost:$($docsServerConfig.port)" -ForegroundColor Cyan
}
Write-Host ('=' * 60) -ForegroundColor Cyan

try {
    # Основной цикл запуска сервера
    $proc = Start-Process -FilePath $venvPath -ArgumentList "run.py", "--config", $Config `
        -PassThru -NoNewWindow
    $proc.Id | Set-Content $PidFile -Encoding UTF8
    Write-Host "💾 PID $($proc.Id) сохранён в $PidFile" -ForegroundColor Gray

    # Open browser after server starts (wait up to 15s for port to become available)
    $appPort = 9696
    try {
        $cfg = Get-Content (Join-Path $Root 'config.json') -Raw | ConvertFrom-Json
        if ($cfg.fastapi_server.port) { $appPort = [int]$cfg.fastapi_server.port }
    } catch { }

    $browserOpened = $false
    for ($i = 1; $i -le 15; $i++) {
        Start-Sleep 1
        try {
            $tcp = [System.Net.Sockets.TcpClient]::new()
            $tcp.Connect('127.0.0.1', $appPort)
            $tcp.Close()
            Start-Process "http://localhost:$appPort"
            Write-Host "🌐 Браузер открыт: http://localhost:$appPort" -ForegroundColor Green
            $browserOpened = $true
            break
        } catch { }
    }
    if (-not $browserOpened) {
        Write-Host "💡 Откройте браузер вручную: http://localhost:$appPort" -ForegroundColor Yellow
    }

    $proc.WaitForExit()
} catch {
    Write-Host "❌ Ошибка запуска сервера FastAPI: $_" -ForegroundColor Red
    Write-Host "💡 Проверьте логи или запустите вручную: $venvPath run.py" -ForegroundColor Yellow
    exit 1
} finally {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue

    # Остановка фоновых процессов при выходе
    if ($script:MkDocsPid) {
        try {
            Stop-Process -Id $script:MkDocsPid -Force -ErrorAction Stop
            Write-Host "✅ MkDocs остановлен (PID: $script:MkDocsPid)" -ForegroundColor Green
        } catch {
            Write-Host "💡 MkDocs (PID: $script:MkDocsPid) уже завершён" -ForegroundColor Gray
        }
    }
    if ($script:LlamaPid) {
        try {
            Stop-Process -Id $script:LlamaPid -Force -ErrorAction Stop
            Write-Host "✅ llama.cpp остановлен (PID: $script:LlamaPid)" -ForegroundColor Green
        } catch {
            Write-Host "💡 llama.cpp (PID: $script:LlamaPid) уже завершён" -ForegroundColor Gray
        }
    }
}