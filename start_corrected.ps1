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
        Write-Host 'Создайте venv вручную: python -m venv venv' -ForegroundColor Yellow
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
            # ИСПРАВЛЕНО: Упрощено регулярное выражение для совместимости с PowerShell
            if ($line -match '^([^=]+)=(.*)$') {
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

# Загружаем .env файл
Load-EnvFile "$Root\.env"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
function Test-FoundryCli {
    try {
        Get-Command foundry -ErrorAction Stop | Out-Null
        return $true
    } catch {
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
            # ИСПРАВЛЕНО: Упрощено регулярное выражение для поиска порта
            if ($conn -match ':([0-9]+)\s+.*LISTENING') {
                $port = $matches[1]
                # Проверяем что это действительно Foundry API
                try {
                    Invoke-WebRequest -Uri "http://localhost:$port/v1/models" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop | Out-Null
                    Write-Host "✅ Foundry API confirmed on port $port" -ForegroundColor Green
                    return $port
                } catch {
                    # ДОКУМЕНТИРОВАНО: Продолжаем поиск если порт не отвечает
                    Write-Host "⚠️ Port $port not responding, trying next..." -ForegroundColor Yellow
                    continue
                }
            }
        }
    } catch {
        Write-Host "⚠️ Could not determine Foundry port: $_" -ForegroundColor Yellow
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
    if (-not (Test-FoundryCli)) {
        Write-Host '⚠️ Foundry CLI not found. Skipping AI startup.' -ForegroundColor Yellow
        Write-Host 'Install Foundry: https://github.com/foundry-rs/foundry' -ForegroundColor Gray
    }
    else {
        Write-Host '🚀 Foundry not running, starting service...' -ForegroundColor Yellow

        try {
            $output = & foundry service start 2>&1
            Write-Host "📋 Foundry output: $output" -ForegroundColor Gray
            
            # ИСПРАВЛЕНО: Упрощено регулярное выражение для парсинга порта
            if ($output -match 'http://127\.0\.0\.1:([0-9]+)/') {
                $foundryPort = $matches[1]
                Write-Host "✅ Foundry started on port $foundryPort" -ForegroundColor Green
                $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
            } else {
                Write-Host '⚠️ Could not parse Foundry port from output. Continuing without AI.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Failed to start Foundry: $_" -ForegroundColor Red
            Write-Host '⚠️ Continuing without AI support.' -ForegroundColor Yellow
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

# ВОССТАНОВЛЕНО: Полный try-catch блок для запуска Python
try {
    & $venvPath run.py --config $Config
} catch {
    Write-Host "❌ Failed to start FastAPI server: $_" -ForegroundColor Red
    Write-Host "💡 Check logs and try running manually: $venvPath run.py" -ForegroundColor Yellow
    exit 1
}