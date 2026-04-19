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
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Автор: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

param(
    # Путь к JSON-файлу конфигурации (относительно корня проекта)
    [string]$Config = 'config.json'
)

# Настройка продолжения выполнения при некритических ошибках
$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host '🚀 FastAPI Foundry Smart Launcher - Запуск' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Этап 1: Проверка зависимостей и автоматическая установка
# Если venv отсутствует, инициируется запуск install.ps1.
# -----------------------------------------------------------------------------

# Активация виртуального окружения (настройка путей для pip/python)
$ActivateScript = "$Root\venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    . $ActivateScript
    Write-Host '✅ venv активирован' -ForegroundColor Green
} else {
    Write-Host '⚠️ venv/Scripts/Activate.ps1 не найден' -ForegroundColor Yellow
}

# Определение пути к интерпретатору (стандартный или python311)
$venvPath = "$Root\venv\Scripts\python.exe"
if (-not (Test-Path $venvPath)) {
    $venvPath = "$Root\venv\Scripts\python311.exe"
}

if (-not (Test-Path $venvPath)) {
    Write-Host '📦 Первый запуск - установка зависимостей...' -ForegroundColor Yellow
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

# -----------------------------------------------------------------------------
# Этап 2: Загрузка переменных .env в текущее окружение процесса
# -----------------------------------------------------------------------------
function Load-EnvFile {
    <#
    .SYNOPSIS
        Чтение .env файла и экспорт пар КЛЮЧ=ЗНАЧЕНИЕ.
    .PARAMETER EnvPath
        Полный путь к файлу .env.
    .NOTES
        - Пропуск пустых строк и комментариев (#).
        - Очистка кавычек вокруг значений.
        - Маскировка секретных данных в консольном выводе.
    #>
    param([string]$EnvPath)
    
    if (-not (Test-Path $EnvPath -PathType Leaf)) {
        if (Test-Path $EnvPath -PathType Container) {
            Write-Host "⚠️ .env — это папка, а не файл: $EnvPath" -ForegroundColor Yellow
        } else {
            Write-Host "⚠️ Файл .env не найден: $EnvPath" -ForegroundColor Yellow
            Write-Host "💡 Создайте .env на основе .env.example" -ForegroundColor Cyan
        }
        return
    }
    
    Write-Host '⚙️ Загрузка переменных .env...' -ForegroundColor Gray
    
    $envVars = 0
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
                    $envVars++
                    
                    if ($key -notmatch '(PASSWORD|SECRET|KEY|TOKEN|PAT)') {
                        Write-Host "  ✓ $key = $value" -ForegroundColor DarkGray
                    } else {
                        Write-Host "  ✓ $key = ***" -ForegroundColor DarkGray
                    }
                }
            }
        }
        Write-Host "✅ Загружено переменных окружения: $envVars" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ошибка загрузки .env: $_" -ForegroundColor Red
    }
}

Load-EnvFile "$Root\.env"

# -----------------------------------------------------------------------------
# Этап 3: Вспомогательные функции обнаружения Foundry
# -----------------------------------------------------------------------------
function Test-FoundryCli {
    <#
    .SYNOPSIS
        Проверка доступности утилиты 'foundry' в PATH.
    .OUTPUTS
        [bool]
    #>
    try {
        Get-Command foundry -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Get-FoundryPort {
    <#
    .SYNOPSIS
        Поиск TCP-порта службы инференса Foundry.
    .DESCRIPTION
        Поиск процесса 'Inference.Service.Agent', сканирование его LISTENING портов
        через netstat и проверка каждого порта через запрос к API /v1/models.
        Возврат первого порта, ответившего HTTP 200.
    .OUTPUTS
        [string] | $null — номер порта или null при отсутствии.
    #>
    $foundryProcess = Get-Process | Where-Object { $_.ProcessName -like "Inference.Service.Agent*" }
    if (-not $foundryProcess) { return $null }
    
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
# Использование динамического порта — определение порта во время выполнения 
# и передача в FastAPI.
# -----------------------------------------------------------------------------
Write-Host '🔍 Проверка локального Foundry...' -ForegroundColor Cyan

# Проверка статуса запуска Foundry (ручной запуск или автозагрузка)
$foundryPort = Get-FoundryPort

if ($foundryPort) {
    # Фиксация порта для FastAPI при активном Foundry
    Write-Host "✅ Foundry уже запущен на порту $foundryPort" -ForegroundColor Green
    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
} else {
    if (-not (Test-FoundryCli)) {
        # Пропуск запуска AI при отсутствии Foundry CLI (сервер запустится без поддержки AI)
        Write-Host '⚠️ Foundry CLI не найден. Пропуск запуска AI.' -ForegroundColor Yellow
        Write-Host 'Установка Foundry от Microsoft' -ForegroundColor Gray
    } else {
        Write-Host '🚀 Запуск службы Foundry...' -ForegroundColor Yellow
        
        try {
            # Запуск Foundry в свернутом окне для предотвращения блокировки текущей консоли
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

# Экспорт полного базового URL для формирования запросов в FastAPI
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
try {
    $configContent = Get-Content "$Root\$Config" | Out-String
    $parsedConfig = $configContent | ConvertFrom-Json
    $docsServerConfig = $parsedConfig.docs_server
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
        # Пересборка site/ перед запуском сервера
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
        Start-Process powershell.exe -ArgumentList @(
            '-NonInteractive', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-Command', "cd '$Root'; & '$venvPath' -m mkdocs serve -a 0.0.0.0:$docsPort"
        ) -WindowStyle Minimized -PassThru | Out-Null
        Write-Host "✅ Сервер MkDocs запущен на http://localhost:$docsPort" -ForegroundColor Green
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

function Ensure-LlamaBin {
    <#
    .SYNOPSIS
        Ensures llama-server binary is extracted from the latest zip in bin/.
        Version is read from / written to config.json (llama_cpp.bin_version).
        If a newer zip is found, prompts the user before extracting.
    .OUTPUTS
        [string] Path to llama-server.exe, or $null if unavailable.
    #>
    $binDir     = Join-Path $Root 'bin'
    $configPath = Join-Path $Root 'config.json'

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
    $installedVersion = $null
    $cfg = $null
    try {
        $cfg = Get-Content $configPath -Raw | ConvertFrom-Json
        $installedVersion = $cfg.llama_cpp.bin_version
    } catch { }

    $isUpToDate = ($installedVersion -eq $latestStem) -and (Test-Path $serverExe)

    if ($isUpToDate) {
        Write-Host "✅ llama.cpp binary up-to-date: $latestStem" -ForegroundColor Green
        return $serverExe
    }

    # New version available — prompt user
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

    # Remove old dir and extract fresh
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

    # Persist new version to config.json
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

function Start-LlamaServer {
    <#
    .SYNOPSIS
        Starts llama.cpp server. On failure — ensures binary and retries once.
    .PARAMETER ServerExe
        Path to llama-server.exe.
    .PARAMETER ModelPath
        Path to .gguf model file.
    .PARAMETER Port
        TCP port for the server.
    .OUTPUTS
        [bool] True if started successfully.
    #>
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

        # Wait up to 10 s for the HTTP health endpoint
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

        # Process exited immediately — binary likely broken
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

# Read llama.cpp settings from config.json (not .env — no secrets there)
try {
    $cfg        = Get-Content (Join-Path $Root 'config.json') -Raw | ConvertFrom-Json
    $llamaCfg   = $cfg.llama_cpp
    $llamaModelPath = $llamaCfg.model_path
    $llamaAutoStart = [bool]$llamaCfg.auto_start
    $llamaPort      = if ($llamaCfg.port) { [int]$llamaCfg.port } else { 9780 }
} catch {
    Write-Host "⚠️  Could not read llama_cpp from config.json: $_" -ForegroundColor Yellow
}

# LLAMA_SERVER_PATH override still lives in .env (it's a machine-specific binary path)
$llamaServerPathEnv = [System.Environment]::GetEnvironmentVariable('LLAMA_SERVER_PATH')

# Always ensure binary is up-to-date (fast no-op if already correct)
$llamaServerExe = Ensure-LlamaBin

if ($llamaModelPath -and $llamaAutoStart) {
    Write-Host '🦙 Auto-starting llama.cpp server...' -ForegroundColor Cyan
    Write-Host "   Model : $llamaModelPath" -ForegroundColor Gray
    Write-Host "   Port  : $llamaPort" -ForegroundColor Gray

    $llamaPort = [System.Environment]::GetEnvironmentVariable('LLAMA_PORT')
    if (-not $llamaPort) { $llamaPort = 9780 }

    # Stop previous instance on this port
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
# Этап 7: Запуск сервера FastAPI (блокирующий вызов)
# -----------------------------------------------------------------------------
$PidFile = Join-Path $env:TEMP 'fastapi-foundry.pid'

# Kill previous instance if PID file exists
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

Write-Host '🐍 Запуск сервера FastAPI...' -ForegroundColor Cyan

if (-not (Test-Path $venvPath)) {
    Write-Host '❌ ОШИБКА: venv Python не найден после этапа установки!' -ForegroundColor Red
    Write-Host "Ожидаемый путь: $venvPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "🔗 FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT" -ForegroundColor Gray
Write-Host '🌐 FastAPI Foundry запускается...' -ForegroundColor Green
Write-Host "📱 Веб-интерфейс будет доступен по адресу: http://localhost:9696" -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# Start server, save PID, clean up on exit
try {
    $proc = Start-Process -FilePath $venvPath -ArgumentList "run.py", "--config", $Config `
        -PassThru -NoNewWindow
    $proc.Id | Set-Content $PidFile -Encoding UTF8
    Write-Host "💾 PID $($proc.Id) сохранён в $PidFile" -ForegroundColor Gray
    $proc.WaitForExit()
} catch {
    Write-Host "❌ Ошибка запуска сервера FastAPI: $_" -ForegroundColor Red
    Write-Host "💡 Проверьте логи или запустите вручную: $venvPath run.py" -ForegroundColor Yellow
    exit 1
} finally {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}