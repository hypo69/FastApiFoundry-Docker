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

# Проверка Foundry на фиксированном порту 50477
try {
    $response = Invoke-WebRequest -Uri "http://localhost:50477/v1/models" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "Foundry running on port 50477" -ForegroundColor Green
        $env:FOUNDRY_DYNAMIC_PORT = 50477
    }
} catch {
    Write-Host "Foundry not available on port 50477" -ForegroundColor Yellow
}

Write-Host "FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT" -ForegroundColor Gray
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "Web interface: http://localhost:9696" -ForegroundColor Cyan

# Запуск Python
try {
    & $venvPath run.py --config $Config
} catch {
    Write-Host "Failed to start server: $_" -ForegroundColor Red
    exit 1
}