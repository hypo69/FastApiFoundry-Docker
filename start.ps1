# start.ps1 — FastAPI Foundry Smart Launcher
# =============================================================================
# Автоматически устанавливает зависимости при первом запуске
# =============================================================================

param(
    [string]$Config = 'config.json'
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host 'FastAPI Foundry Smart Launcher' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

$venvPath = "$Root\venv\Scripts\python311.exe"

if (-not (Test-Path $venvPath)) {
    Write-Host 'Python venv not found!' -ForegroundColor Red
    Write-Host "Expected path: $venvPath" -ForegroundColor Yellow
    exit 1
}

Write-Host 'Managing Foundry Windows Service...' -ForegroundColor Cyan

# ПРИНУДИТЕЛЬНАЯ ОСТАНОВКА FOUNDRY СЕРВИСА
Write-Host 'Stopping Foundry service...' -ForegroundColor Yellow
try {
    $stopOutput = & foundry service stop 2>&1
    Write-Host "Stop result: $stopOutput" -ForegroundColor Gray
} catch {
    Write-Host "Stop command failed: $_" -ForegroundColor Red
}

# Освобождаем порт 50477 если занят
$processOnPort = netstat -ano | Select-String ":50477" | Select-String "LISTENING"
if ($processOnPort) {
    Write-Host 'Port 50477 is occupied, freeing it...' -ForegroundColor Yellow
    $processOnPort | ForEach-Object {
        if ($_ -match '\s+(\d+)$') {
            $pid = $matches[1]
            Write-Host "Killing process $pid on port 50477" -ForegroundColor Yellow
            try {
                taskkill /f /pid $pid 2>&1 | Out-Null
            } catch {
                Write-Host "Could not kill PID $pid" -ForegroundColor Red
            }
        }
    }
}

# ЗАПУСК FOUNDRY СЕРВИСА
Write-Host 'Starting Foundry Windows service...' -ForegroundColor Green
try {
    $startOutput = & foundry service start 2>&1
    Write-Host "Start command executed" -ForegroundColor Gray
    Write-Host "Output: $startOutput" -ForegroundColor White
    
    # Ждем запуска сервиса
    Write-Host 'Waiting for Windows service to initialize...' -ForegroundColor Gray
    Start-Sleep 10
    
    # Проверяем статус сервиса
    Write-Host 'Checking service status...' -ForegroundColor Gray
    $statusOutput = & foundry service status 2>&1
    Write-Host "Status: $statusOutput" -ForegroundColor White
    
    # Проверяем что API работает на 50477
    Write-Host 'Testing Foundry API on port 50477...' -ForegroundColor Gray
    $apiWorking = $false
    for ($i = 1; $i -le 6; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:50477/v1/models" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "SUCCESS: Foundry API confirmed on port 50477 (attempt $i)" -ForegroundColor Green
                $apiWorking = $true
                break
            }
        } catch {
            Write-Host "API test attempt $i failed, retrying..." -ForegroundColor Yellow
            Start-Sleep 5
        }
    }
    
    if ($apiWorking) {
        $env:FOUNDRY_DYNAMIC_PORT = 50477
        Write-Host 'Foundry service is ready!' -ForegroundColor Green
    } else {
        Write-Host 'Foundry service started but API not responding' -ForegroundColor Red
        Write-Host 'Check if models are loaded: foundry service list' -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "Error managing Foundry service: $_" -ForegroundColor Red
}

Write-Host "FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT" -ForegroundColor Green
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "Web interface: http://localhost:9696" -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

try {
    & $venvPath run.py --config $Config
} catch {
    Write-Host "Failed to start server: $_" -ForegroundColor Red
    exit 1
}