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

# ИСПРАВЛЕНО: Правильная проверка Foundry CLI
function Test-FoundryCli {
    try {
        $null = Get-Command foundry -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# ИСПРАВЛЕНО: Правильная проверка статуса Foundry сервиса
function Test-FoundryService {
    try {
        $output = & foundry service status 2>&1
        # Проверяем что сервис запущен (не содержит "not running")
        return -not ($output -match "not running")
    } catch {
        return $false
    }
}

# ИСПРАВЛЕНО: Проверка API на конкретном порту
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

# ИСПРАВЛЕНО: Пошаговая проверка Foundry
if (-not (Test-FoundryCli)) {
    Write-Host 'Foundry CLI not found in PATH' -ForegroundColor Red
    Write-Host 'Install Microsoft Foundry first' -ForegroundColor Yellow
} else {
    Write-Host 'Foundry CLI found' -ForegroundColor Green
    
    # Проверяем статус сервиса
    if (Test-FoundryService) {
        Write-Host 'Foundry service is running' -ForegroundColor Green
        
        # ИСПРАВЛЕНО: Сначала проверяем фиксированный порт 50477
        if (Test-FoundryAPI -Port 50477) {
            Write-Host 'Foundry API confirmed on port 50477' -ForegroundColor Green
            $foundryPort = 50477
        } else {
            Write-Host 'Port 50477 not responding, checking other ports...' -ForegroundColor Yellow
            
            # Ищем другие порты через netstat
            try {
                $netstat = netstat -ano | Select-String "LISTENING" | Select-String "127.0.0.1"
                foreach ($line in $netstat) {
                    if ($line -match '127\.0\.0\.1:(\d+)') {
                        $port = [int]$matches[1]
                        if ($port -gt 50000 -and $port -lt 60000) {  # Диапазон портов Foundry
                            if (Test-FoundryAPI -Port $port) {
                                Write-Host "Foundry API found on port $port" -ForegroundColor Green
                                $foundryPort = $port
                                break
                            }
                        }
                    }
                }
            } catch {
                Write-Host "Could not scan ports: $_" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host 'Foundry service not running, starting...' -ForegroundColor Yellow
        
        try {
            # ИСПРАВЛЕНО: Запуск без принудительного перезапуска в DEBUG режиме
            $output = & foundry service start 2>&1
            Write-Host "Foundry start output: $output" -ForegroundColor Gray
            
            # Ждем запуска
            Start-Sleep 5
            
            # Проверяем что сервис запустился
            if (Test-FoundryService) {
                Write-Host 'Foundry service started successfully' -ForegroundColor Green
                
                # Проверяем API на стандартном порту
                if (Test-FoundryAPI -Port 50477) {
                    Write-Host 'Foundry API available on port 50477' -ForegroundColor Green
                    $foundryPort = 50477
                } else {
                    Write-Host 'Foundry started but API not responding on 50477' -ForegroundColor Yellow
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