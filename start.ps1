# start.ps1 — FastAPI Foundry DEV launcher
# =============================================================================

param(
    [string]$Config = 'config.json'
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host 'FastAPI Foundry DEV launcher'
Write-Host ('=' * 60)

# -----------------------------------------------------------------------------
# Load .env
# -----------------------------------------------------------------------------
if (Test-Path "$Root\.env") {
    Write-Host 'Loading .env...'
    Get-Content "$Root\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}

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
        Write-Host "Found Foundry process (PID: $($process.Id))"
        return $process
    } catch {
        Write-Host "No Foundry process found"
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
                    Write-Host "Foundry API confirmed on port $port"
                    return $port
                } catch {
                    continue
                }
            }
        }
    } catch {
        Write-Host "Could not determine Foundry port"
    }
    return $null
}

# -----------------------------------------------------------------------------
# Foundry logic
# -----------------------------------------------------------------------------
Write-Host 'Checking Local Foundry...'

$foundryProcess = Find-FoundryProcess
$foundryPort = Get-FoundryPort $foundryProcess

if ($foundryPort) {
    Write-Host "Foundry already running on port $foundryPort"
    $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
}
else {
    if (-not (Test-FoundryCli)) {
        Write-Host 'Foundry CLI not found. Skipping AI startup.'
    }
    else {
        Write-Host 'Foundry not running, starting service...'

        $output = & foundry service start 2>&1
        Write-Host "Foundry output: $output"
        
        # Парсим порт из вывода
        if ($output -match "http://127\.0\.0\.1:(\d+)/") {
            $foundryPort = $matches[1]
            Write-Host "Foundry started on port $foundryPort"
            $env:FOUNDRY_DYNAMIC_PORT = $foundryPort
        } else {
            Write-Host 'Could not parse Foundry port from output. Continuing without AI.'
        }
    }
}

# -----------------------------------------------------------------------------
# Python
# -----------------------------------------------------------------------------
$python = "$Root\venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host 'ERROR: Python venv not found'
    exit 1
}

Write-Host 'Starting FastAPI server...'
Write-Host "FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT"

# Передаем переменную окружения в Python процесс
if ($env:FOUNDRY_DYNAMIC_PORT) {
    $env:FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT
}

& $python run.py --config $Config
