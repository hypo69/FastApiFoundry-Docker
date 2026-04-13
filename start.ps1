# start.ps1 — FastAPI Foundry Smart Launcher
# =============================================================================
# Автоматически устанавливает зависимости при первом запуске
# =============================================================================
#$
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
# ИСПРАВЛЕНО: Используем правильный путь к python311.exe в venv
$venvPath = "$Root\venv\Scripts\python311.exe"

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
    try {
        Get-Content $EnvPath | ForEach-Object {
            $line = $_.Trim()
            
            # Пропускаем пустые строки и комментарии
            if ($line -and -not $line.StartsWith('#')) {
                # ИСПРАВЛЕНО: Упрощено регулярное выражение для совместимости
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
    } catch {
        Write-Host "❌ Error loading .env file: $_" -ForegroundColor Red
    }
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

function Get-FoundryPort {
    $foundryProcess = Get-Process | Where-Object { $_.ProcessName -like "Inference.Service.Agent*" }
    if (-not $foundryProcess) { return $null }
    
    $netstatOutput = netstat -ano | Select-String "$($foundryProcess.Id)" | Select-String "LISTENING"
    foreach ($line in $netstatOutput) {
        if ($line -match ':(\d+)\s') {
            $port = $matches[1]
            try {
                $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/v1/models" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ Foundry API found on port $port" -ForegroundColor Green
                    return $port
                }
            } catch { }
        }
    }
    return $null
}

# -----------------------------------------------------------------------------
# Foundry logic
# -----------------------------------------------------------------------------
Write-Host '🔍 Checking Local Foundry...' -ForegroundColor Cyan

# Проверяем запущен ли Foundry
$foundryPort = Get-FoundryPort

if ($foundryPort) {
    Write-Host "✅ Foundry already running on port $foundryPort" -ForegroundColor Green
    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
} else {
    if (-not (Test-FoundryCli)) {
        Write-Host '⚠️ Foundry CLI not found. Skipping AI startup.' -ForegroundColor Yellow
        Write-Host 'Install Foundry from Microsoft' -ForegroundColor Gray
    } else {
        Write-Host '🚀 Starting Foundry service...' -ForegroundColor Yellow
        
        try {
            & foundry service start | Out-Null
            Write-Host "Foundry service start command executed" -ForegroundColor Gray
            
            # Ждем запуска и ищем порт
            for ($i = 1; $i -le 10; $i++) {
                Start-Sleep 2
                $foundryPort = Get-FoundryPort
                if ($foundryPort) {
                    Write-Host "✅ Foundry started on port $foundryPort" -ForegroundColor Green
                    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
                    break
                }
                Write-Host "⏳ Waiting for Foundry to start... ($i/10)" -ForegroundColor Gray
            }
            
            if (-not $foundryPort) {
                Write-Host "❌ Foundry failed to start or port not found" -ForegroundColor Red
                Write-Host '⚠️ Continuing without AI support.' -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Failed to start Foundry: $_" -ForegroundColor Red
            Write-Host '⚠️ Continuing without AI support.' -ForegroundColor Yellow
        }
    }
}

# Устанавливаем переменную окружения для FastAPI
if ($foundryPort) {
    $env:FOUNDRY_BASE_URL = "http://localhost:$foundryPort/v1/"
    Write-Host "🔗 FOUNDRY_BASE_URL = $env:FOUNDRY_BASE_URL" -ForegroundColor Green
} else {
    Write-Host "⚠️ Foundry not available - AI features disabled" -ForegroundColor Yellow
}

# -----------------------------------------------------------------------------
# Python
# -----------------------------------------------------------------------------
Write-Host '🐍 Starting FastAPI server...' -ForegroundColor Cyan

if (-not (Test-Path $venvPath)) {
    Write-Host '❌ ERROR: Python venv still not found after installation!' -ForegroundColor Red
    Write-Host "Expected path: $venvPath" -ForegroundColor Yellow
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
    Write-Host "💡 Or check if all dependencies are installed: $venvPath -m pip list" -ForegroundColor Yellow
    exit 1
}