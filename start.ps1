# start.ps1 — FastAPI Foundry Smart Launcher
# =============================================================================
# Automatically installs dependencies on first run
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
# Dependency check and installation
# -----------------------------------------------------------------------------
# Virtual environment activation
$ActivateScript = "$Root\venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    . $ActivateScript
    Write-Host '✅ venv activated' -ForegroundColor Green
} else {
    Write-Host '⚠️ venv/Scripts/Activate.ps1 not found' -ForegroundColor Yellow
}

$venvPath = "$Root\venv\Scripts\python.exe"
if (-not (Test-Path $venvPath)) {
    $venvPath = "$Root\venv\Scripts\python311.exe"
}

if (-not (Test-Path $venvPath)) {
    Write-Host '📦 First run - installing dependencies...' -ForegroundColor Yellow
    Write-Host 'This may take several minutes...' -ForegroundColor Yellow
    
    if (Test-Path "$Root\install.ps1") {
        try {
            & "$Root\install.ps1"
            Write-Host '✅ Installation complete!' -ForegroundColor Green
        } catch {
            Write-Host "❌ Installation error: $_" -ForegroundColor Red
            Write-Host 'Try running install.ps1 manually' -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host '❌ install.ps1 not found!' -ForegroundColor Red
        Write-Host 'Create venv manually: python311 -m venv venv' -ForegroundColor Yellow
        exit 1
    }
}

# -----------------------------------------------------------------------------
# Load .env
# -----------------------------------------------------------------------------
function Load-EnvFile {
    param([string]$EnvPath)
    
    # Check that it's a file, not a directory
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
            
            # Skip empty lines and comments
            if ($line -and -not $line.StartsWith('#')) {
                # FIXED: Simplified regular expression for compatibility
                if ($line -match '^([^=]+)=(.*)$') {
                    $key = $matches[1].Trim()
                    $value = $matches[2].Trim()
                    
                    # Remove quotes if present
                    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                        $value = $value.Substring(1, $value.Length - 2)
                    }
                    if ($value.StartsWith("'") -and $value.EndsWith("'")) {
                        $value = $value.Substring(1, $value.Length - 2)
                    }
                    
                    [System.Environment]::SetEnvironmentVariable($key, $value)
                    $envVars++
                    
                    # Show only safe variables
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

# Load .env file
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

# Check if Foundry is running
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
            Start-Process -FilePath "foundry" -ArgumentList "service", "start" -WindowStyle Minimized -NoNewWindow:$false
            Write-Host "Foundry service start command executed" -ForegroundColor Gray
            
            # Wait for startup and find the port
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

# Set environment variable for FastAPI
if ($foundryPort) {
    $env:FOUNDRY_BASE_URL = "http://localhost:$foundryPort/v1/"
    Write-Host "🔗 FOUNDRY_BASE_URL = $env:FOUNDRY_BASE_URL" -ForegroundColor Green
} else {
    Write-Host "⚠️ Foundry not available - AI features disabled" -ForegroundColor Yellow
}

# -----------------------------------------------------------------------------
# Docs Server (mkdocs serve)
# -----------------------------------------------------------------------------
Write-Host '🔍 Checking Docs Server configuration...' -ForegroundColor Cyan

# Read config.json
try {
    $configContent = Get-Content "$Root\$Config" | Out-String
    $parsedConfig = $configContent | ConvertFrom-Json
    $docsServerConfig = $parsedConfig.docs_server
} catch {
    Write-Host "❌ Error reading config.json for docs_server: $_" -ForegroundColor Red
    $docsServerConfig = $null
}

if ($docsServerConfig -and $docsServerConfig.enabled) {
    Write-Host "🚀 Starting MkDocs server on port $($docsServerConfig.port)..." -ForegroundColor Yellow
    try {
        Start-Process powershell.exe -ArgumentList @(
            '-NonInteractive', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-Command', "mkdocs serve -a 0.0.0.0:$($docsServerConfig.port)"
        ) -WindowStyle Minimized -PassThru | Out-Null
        Write-Host "✅ MkDocs server started in background" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to start MkDocs server: $_" -ForegroundColor Red
        Write-Host "⚠️ Continuing without docs server." -ForegroundColor Yellow
    }
} else {
    Write-Host "💡 Docs server is disabled in config.json (skipping)" -ForegroundColor Gray
}

# -----------------------------------------------------------------------------
# llama.cpp (optional — if LLAMA_MODEL_PATH is set in .env)
# -----------------------------------------------------------------------------
$llamaModelPath = [System.Environment]::GetEnvironmentVariable('LLAMA_MODEL_PATH')
$llamaAutoStart = [System.Environment]::GetEnvironmentVariable('LLAMA_AUTO_START')

if ($llamaModelPath -and $llamaAutoStart -eq 'true') {
    Write-Host '🦙 Starting llama.cpp server...' -ForegroundColor Cyan

    $llamaScript = Join-Path $Root 'scripts\llama-start.ps1'
    if (Test-Path $llamaScript) {
        $llamaPort = [System.Environment]::GetEnvironmentVariable('LLAMA_PORT')
        if (-not $llamaPort) { $llamaPort = 8080 }

        # Start in a separate window to avoid blocking
        Start-Process powershell.exe -ArgumentList @(
            '-NonInteractive', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', $llamaScript,
            '-ModelPath', $llamaModelPath,
            '-Port', $llamaPort
        ) -WindowStyle Minimized

        $env:LLAMA_BASE_URL = "http://127.0.0.1:$llamaPort/v1"
        Write-Host "✅ llama.cpp starting (port $llamaPort)" -ForegroundColor Green
        Write-Host "🔗 LLAMA_BASE_URL = $env:LLAMA_BASE_URL" -ForegroundColor Green
    } else {
        Write-Host '⚠️ scripts\llama-start.ps1 not found, skipping llama.cpp' -ForegroundColor Yellow
    }
} elseif ($llamaModelPath) {
    Write-Host "💡 llama.cpp model configured but LLAMA_AUTO_START != true (skipping)" -ForegroundColor Gray
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

# Pass environment variable to Python process
if ($env:FOUNDRY_DYNAMIC_PORT) {
    $env:FOUNDRY_DYNAMIC_PORT = $env:FOUNDRY_DYNAMIC_PORT
}

Write-Host '🌐 FastAPI Foundry starting...' -ForegroundColor Green
Write-Host "📱 Web interface will be available at: http://localhost:9696" -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# RESTORED: Full try-catch block for starting Python
try {
    & $venvPath run.py --config $Config
} catch {
    Write-Host "❌ Failed to start FastAPI server: $_" -ForegroundColor Red
    Write-Host "💡 Check logs and try running manually: $venvPath run.py" -ForegroundColor Yellow
    Write-Host "💡 Or check if all dependencies are installed: $venvPath -m pip list" -ForegroundColor Yellow
    exit 1
}