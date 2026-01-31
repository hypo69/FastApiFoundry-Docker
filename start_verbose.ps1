param([string]$Config = 'config.json')

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host 'FastAPI Foundry Smart Launcher' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# Путь к Python
$venvPath = "$Root\venv\Scripts\python311.exe"

if (-not (Test-Path $venvPath)) {
    Write-Host 'Python venv not found!' -ForegroundColor Red
    Write-Host "Expected path: $venvPath" -ForegroundColor Yellow
    exit 1
}

# Функции проверки Foundry
function Test-FoundryCli {
    try {
        $null = Get-Command foundry -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Test-FoundryService {
    try {
        Write-Host 'Checking Foundry service status...' -ForegroundColor Gray
        $output = & foundry service status 2>&1
        
        # ПЕРЕДАЕМ ВЕСЬ ВЫВОД FOUNDRY
        Write-Host "=== FOUNDRY SERVICE STATUS ===" -ForegroundColor Yellow
        $output | ForEach-Object { Write-Host $_ -ForegroundColor White }
        Write-Host "===============================" -ForegroundColor Yellow
        
        return -not ($output -match "not running")
    } catch {
        Write-Host "Error checking Foundry status: $_" -ForegroundColor Red
        return $false
    }
}

function Test-FoundryAPI {
    param([int]$Port)
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/v1/models" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        return ($response.StatusCode -eq 200)
    } catch {
        return $false
    }
}

Write-Host 'Checking Foundry...' -ForegroundColor Cyan

$foundryPort = $null

if (-not (Test-FoundryCli)) {
    Write-Host 'Foundry CLI not found in PATH' -ForegroundColor Red
    Write-Host 'Install Microsoft Foundry first' -ForegroundColor Yellow
} else {
    Write-Host 'Foundry CLI found' -ForegroundColor Green
    
    # Проверяем статус сервиса
    if (Test-FoundryService) {
        Write-Host 'Foundry service is running' -ForegroundColor Green
        
        # Проверяем API на порту 50477
        Write-Host 'Testing API on port 50477...' -ForegroundColor Gray
        if (Test-FoundryAPI -Port 50477) {
            Write-Host 'Foundry API confirmed on port 50477' -ForegroundColor Green
            $foundryPort = 50477
        } else {
            Write-Host 'Port 50477 not responding' -ForegroundColor Yellow
        }
    } else {
        Write-Host 'Foundry service not running, starting...' -ForegroundColor Yellow
        
        try {
            Write-Host 'Executing: foundry service start' -ForegroundColor Gray
            
            # ПЕРЕДАЕМ ВЕСЬ ВЫВОД FOUNDRY ПРИ ЗАПУСКЕ
            Write-Host "=== FOUNDRY SERVICE START ===" -ForegroundColor Yellow
            $output = & foundry service start 2>&1
            $output | ForEach-Object { Write-Host $_ -ForegroundColor White }
            Write-Host "=============================" -ForegroundColor Yellow
            
            # Ждем запуска
            Write-Host 'Waiting for Foundry to start...' -ForegroundColor Gray
            Start-Sleep 5
            
            # Проверяем что сервис запустился
            Write-Host 'Checking if service started...' -ForegroundColor Gray
            if (Test-FoundryService) {
                Write-Host 'Foundry service started successfully' -ForegroundColor Green
                
                # Проверяем API
                Write-Host 'Testing API after start...' -ForegroundColor Gray
                if (Test-FoundryAPI -Port 50477) {
                    Write-Host 'Foundry API available on port 50477' -ForegroundColor Green
                    $foundryPort = 50477
                } else {
                    Write-Host 'Foundry started but API not responding on 50477' -ForegroundColor Yellow
                    
                    # Дополнительная проверка других портов
                    Write-Host 'Scanning for Foundry API on other ports...' -ForegroundColor Gray
                    for ($port = 50470; $port -le 50490; $port++) {
                        if (Test-FoundryAPI -Port $port) {
                            Write-Host "Found Foundry API on port $port" -ForegroundColor Green
                            $foundryPort = $port
                            break
                        }
                    }
                }
            } else {
                Write-Host 'Failed to start Foundry service' -ForegroundColor Red
            }
        } catch {
            Write-Host "Error starting Foundry: $_" -ForegroundColor Red
        }
    }
}

# Устанавливаем переменную окружения
if ($foundryPort) {
    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
    Write-Host "FOUNDRY_DYNAMIC_PORT = $foundryPort" -ForegroundColor Green
} else {
    Write-Host "Foundry not available - AI features disabled" -ForegroundColor Yellow
    Write-Host "FOUNDRY_DYNAMIC_PORT = (not set)" -ForegroundColor Gray
}

Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "Web interface: http://localhost:9696" -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# Запуск Python
try {
    & $venvPath run.py --config $Config
} catch {
    Write-Host "Failed to start server: $_" -ForegroundColor Red
    exit 1
}