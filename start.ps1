# start.ps1 — FastAPI Foundry Smart Launcher
# =============================================================================
# Автоматически устанавливает зависимости при первом запуске
# =============================================================================

param(
    [string]$Config = 'config.json'
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host '🚀 FastAPI Foundry Smart Launcher' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Проверка и установка зависимостей
# -----------------------------------------------------------------------------
$venvPath = "$Root\venv\Scripts\python.exe"
Начиная со строки ниже, скрипт проверяет наличие виртуального окружения Python.







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
# Load .env
# -----------------------------------------------------------------------------
function Load-EnvFile {
    param([string]$EnvPath)
    
    # Проверяем что это файл, а не директория
    if (-not (Test-Path $EnvPath -PathType Leaf)) {
        if (Test-Path $EnvPath -PathType Container) {
            Write-Host "⚠️ .env is a directory, not a file: $EnvPath" -ForegroundColor Yellow
            Write-Host "💡 Create .env file from .env.example template" -ForegroundColor Cyan
        } else {
            Write-Host "⚠️ .env file not found: $EnvPath" -ForegroundColor Yellow
            Write-Host "💡 Copy .env.example to .env and configure your settings" -ForegroundColor Cyan
        }
        return
    }
    
    Write-Host '⚙️ Loading .env variables...' -ForegroundColor Gray
    
    $envVars = 0
    Get-Content $EnvPath | ForEach-Object {
        $line = $_.Trim()
        
        # Пропускаем пустые строки и комментарии
        if ($line -and -not $line.StartsWith('#')) {
            if ($line -match '^\s*([^#=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                
                # Убираем кавычки если есть
                if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
                if ($value.StartsWith("'") -and $value.EndsWith("'")) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
                
                [System.Environment]::SetEnvironmentVariable($key, $value)
                $envVars++
                
                # Показываем только безопасные переменные
                if ($key -notmatch '(PASSWORD|SECRET|KEY|TOKEN|PAT)') {
                    Write-Host "  ✓ $key = $value" -ForegroundColor DarkGray
                } else {
                    Write-Host "  ✓ $key = ***" -ForegroundColor DarkGray
                }
            }
        }
    }
    
    Write-Host "✅ Loaded $envVars environment variables" -ForegroundColor Green
}

# -----------------------------------------------------------------------------
# Generate API Keys if needed
# -----------------------------------------------------------------------------
function Generate-ApiKeys {
    # Фиксированные ключи для проекта
    $apiKey = "fastapi-foundry-2025-xK9mP2vR8qL5nW3tY7uI0oE4rT6yU1sA"
    $secretKey = "jwt-secret-2025-aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5A1bC2dE3fG4hI5jK6lM7nO8pQ9rS0tU1vW2xY3z"
    
    # Устанавливаем переменные окружения если не заданы
    if (-not $env:API_KEY) {
        $env:API_KEY = $apiKey
        Write-Host "🔑 API_KEY установлен" -ForegroundColor Green
    }
    
    if (-not $env:SECRET_KEY) {
        $env:SECRET_KEY = $secretKey
        Write-Host "🔐 SECRET_KEY установлен" -ForegroundColor Green
    }
}

# Генерируем ключи если нужно
Generate-ApiKeys

# Загружаем .env файл
Load-EnvFile "$Root\.env"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
function Test-FoundryCli {
    try {
        $foundryCmd = Get-Command foundry -ErrorAction Stop
        Write-Host "✅ Foundry CLI найден: $($foundryCmd.Source)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Foundry CLI не найден в PATH" -ForegroundColor Red
        Write-Host "💡 Установите Microsoft Foundry: https://github.com/microsoft/foundry" -ForegroundColor Cyan
        return $false
    }
}

function Find-FoundryProcess {
    try {
        $process = Get-Process -Name "foundry" -ErrorAction Stop
        Write-Host "✅ Found Foundry process (PID: $($process.Id))" -ForegroundColor Green
        return $process
    } catch {
        Write-Host "🔍 No Foundry process found" -ForegroundColor Gray
        return $null
    }
}

function Get-FoundryPort {
    param($Process)
    
    if (-not $Process) { return $null }
    
    try {
        $connections = netstat -ano | Select-String "$($Process.Id)" | Select-String "LISTENING"
        foreach ($conn in $connections) {
            if ($conn -match ":([0-9]+)\s+.*LISTENING") {
                $port = $matches[1]
                # Проверяем что это действительно Foundry API
                try {
                    Invoke-WebRequest -Uri "http://localhost:$port/v1/models" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop | Out-Null
                    Write-Host "✅ Foundry API confirmed on port $port" -ForegroundColor Green
                    return $port
                } catch {
                    continue
                }
            }
        }
    } catch {
        Write-Host "⚠️ Could not determine Foundry port" -ForegroundColor Yellow
    }
    return $null
}

# -----------------------------------------------------------------------------
# Foundry logic
# -----------------------------------------------------------------------------
Write-Host '🔍 Checking Local Foundry...' -ForegroundColor Cyan

$foundryProcess = Find-FoundryProcess
$foundryPort = Get-FoundryPort $foundryProcess

if ($foundryPort) {
    Write-Host "✅ Foundry already running on port $foundryPort" -ForegroundColor Green
    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
}
else {
    $foundryInstalled = Test-FoundryCli
    
    if (-not $foundryInstalled) {
        Write-Host '⚠️ Foundry CLI не установлен. Пропускаем AI запуск.' -ForegroundColor Yellow
        Write-Host ''
        Write-Host '🤖 Хотите установить Microsoft Foundry для AI функций?' -ForegroundColor Cyan
        Write-Host '   Foundry позволяет запускать локальные AI модели' -ForegroundColor Gray
        Write-Host ''
        $install = Read-Host 'Установить Foundry? (y/N)'
        
        if ($install -eq 'y' -or $install -eq 'Y') {
            Write-Host '🚀 Запуск GUI установщика...' -ForegroundColor Green
            
            if (Test-Path "$Root\install-gui.ps1") {
                try {
                    & "$Root\install-gui.ps1"
                    Write-Host '✅ Установка завершена!' -ForegroundColor Green
                } catch {
                    Write-Host "❌ Ошибка запуска GUI: $_" -ForegroundColor Red
                    
                    # Фолбэк на консольный установщик
                    if (Test-Path "$Root\install-foundry.ps1") {
                        Write-Host '🔄 Переход на консольный установщик...' -ForegroundColor Yellow
                        & "$Root\install-foundry.ps1"
                    }
                }
            } else {
                Write-Host '📥 Открываем страницу загрузки...' -ForegroundColor Yellow
                Start-Process 'https://github.com/microsoft/foundry/releases'
            }
        } else {
            Write-Host '⏭️ Продолжаем без AI функций' -ForegroundColor Yellow
        }
    }
    else {
        Write-Host '🚀 Foundry не запущен, пытаемся запустить...' -ForegroundColor Yellow

        try {
            Write-Host '🔄 Выполняем: foundry service start' -ForegroundColor Gray
            $output = & foundry service start 2>&1
            
            Write-Host "📋 Вывод Foundry:" -ForegroundColor Gray
            $output | ForEach-Object { Write-Host "   $_" -ForegroundColor DarkGray }
            
            # Парсим порт из вывода
            $foundryPort = $null
            foreach ($line in $output) {
                if ($line -match "http://127\.0\.0\.1:(\d+)/") {
                    $foundryPort = $matches[1]
                    break
                }
                if ($line -match "localhost:(\d+)") {
                    $foundryPort = $matches[1]
                    break
                }
                if ($line -match "port\s+(\d+)") {
                    $foundryPort = $matches[1]
                    break
                }
            }
            
            if ($foundryPort) {
                Write-Host "✅ Foundry запущен на порту $foundryPort" -ForegroundColor Green
                $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
                
                # Проверяем что API действительно работает
                Start-Sleep 3
                try {
                    $response = Invoke-WebRequest -Uri "http://localhost:$foundryPort/v1/models" -TimeoutSec 5 -UseBasicParsing
                    Write-Host "✅ Foundry API подтвержден" -ForegroundColor Green
                } catch {
                    Write-Host "⚠️ Foundry запущен, но API не отвечает: $_" -ForegroundColor Yellow
                }
            } else {
                Write-Host '⚠️ Не удалось определить порт Foundry. Продолжаем без AI.' -ForegroundColor Yellow
                Write-Host '💡 Попробуйте запустить Foundry вручную' -ForegroundColor Cyan
            }
        } catch {
            Write-Host "❌ Ошибка запуска Foundry: $_" -ForegroundColor Red
            Write-Host '💡 Попробуйте:' -ForegroundColor Cyan
            Write-Host '   foundry --help' -ForegroundColor Gray
            Write-Host '   foundry service --help' -ForegroundColor Gray
        }
    }
}

# -----------------------------------------------------------------------------
# Python
# -----------------------------------------------------------------------------
Write-Host '🐍 Starting FastAPI server...' -ForegroundColor Cyan

if (-not (Test-Path $venvPath)) {
    Write-Host '❌ ERROR: Python venv still not found after installation!' -ForegroundColor Red
    exit 1
}

Write-Host "🔗 FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT" -ForegroundColor Gray

# Передаем переменную окружения в Python процесс
if ($env:FOUNDRY_DYNAMIC_PORT) {
    $env:FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT
}

Write-Host '🌐 FastAPI Foundry starting...' -ForegroundColor Green
Write-Host "📱 Web interface will be available at: http://localhost:9696" -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

& $venvPath run.py --config $Config