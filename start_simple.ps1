# start_simple.ps1 - FastAPI Foundry Simple Launcher
param([string]$Config = 'config.json')

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host '🚀 FastAPI Foundry Simple Launcher' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# Проверка venv
$venvPath = "$Root\venv\Scripts\python.exe"
if (-not (Test-Path $venvPath)) {
    Write-Host '❌ venv not found. Run install.ps1 first!' -ForegroundColor Red
    exit 1
}

# Загрузка .env
$envFile = "$Root\.env"
if (Test-Path $envFile -PathType Leaf) {
    Write-Host '⚙️ Loading .env variables...' -ForegroundColor Gray
    $envVars = 0
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#')) {
            if ($line -match '^([^=]+)=(.*)$') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
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
    Write-Host "✅ Loaded $envVars environment variables" -ForegroundColor Green
} else {
    Write-Host "⚠️ .env file not found" -ForegroundColor Yellow
}

# Проверка Foundry
Write-Host '🔍 Checking Foundry...' -ForegroundColor Cyan
$foundryProcess = Get-Process -Name "foundry" -ErrorAction SilentlyContinue
if ($foundryProcess) {
    Write-Host "✅ Foundry process found (PID: $($foundryProcess.Id))" -ForegroundColor Green
    
    # Попробуем найти порт через netstat
    $netstatOutput = netstat -ano | Select-String "$($foundryProcess.Id)" | Select-String "LISTENING"
    foreach ($line in $netstatOutput) {
        if ($line -match ':(\d+)\s+.*LISTENING') {
            $port = $matches[1]
            $testUrl = "http://localhost:$port/v1/models"
            Write-Host "🔍 Testing Foundry API on port $port..." -ForegroundColor Gray
            
            $webRequest = $null
            try {
                $webRequest = Invoke-WebRequest -Uri $testUrl -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                if ($webRequest.StatusCode -eq 200) {
                    Write-Host "✅ Foundry API confirmed on port $port" -ForegroundColor Green
                    $env:FOUNDRY_DYNAMIC_PORT = $port
                    break
                }
            } catch {
                Write-Host "❌ Port $port not responding to API calls" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "⚠️ Foundry process not found" -ForegroundColor Yellow
    
    # Попробуем запустить Foundry
    $foundryCmd = Get-Command foundry -ErrorAction SilentlyContinue
    if ($foundryCmd) {
        Write-Host '🚀 Starting Foundry service...' -ForegroundColor Yellow
        $foundryOutput = & foundry service start 2>&1
        Write-Host "📋 Foundry output: $foundryOutput" -ForegroundColor Gray
        
        if ($foundryOutput -match 'http://127\.0\.0\.1:(\d+)/') {
            $foundryPort = $matches[1]
            Write-Host "✅ Foundry started on port $foundryPort" -ForegroundColor Green
            $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
        }
    } else {
        Write-Host '⚠️ Foundry CLI not found' -ForegroundColor Yellow
    }
}

# Запуск FastAPI
Write-Host '🐍 Starting FastAPI server...' -ForegroundColor Cyan
Write-Host "🔗 FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT" -ForegroundColor Gray
Write-Host "📱 Web interface: http://localhost:9696" -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

& $venvPath run.py --config $Config