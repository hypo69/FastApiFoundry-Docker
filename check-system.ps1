# Проверка системы и зависимостей
# ============================================================================

$colors = @{
    'Success' = 'Green'
    'Error'   = 'Red'
    'Warning' = 'Yellow'
    'Info'    = 'Cyan'
}

function Write-Status {
    param([string]$Item, [string]$Status, [string]$Type = 'Info')
    $color = $colors[$Type]
    $symbol = if ($Type -eq 'Success') { '✅' } elseif ($Type -eq 'Error') { '❌' } else { '⚠️ ' }
    Write-Host "$symbol $Item " -ForegroundColor Gray -NoNewline
    Write-Host $Status -ForegroundColor $color
}

Clear-Host
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        FastAPI Foundry - System Health Check                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Python
Write-Host "🐍 PYTHON" -ForegroundColor Magenta
try {
    $pythonVersion = python --version 2>&1
    Write-Status "Python Version" "$pythonVersion" "Success"
    $pythonPath = (python -c "import sys; print(sys.executable)") 2>&1
    Write-Status "Python Path" "$pythonPath" "Info"
} catch {
    Write-Status "Python" "NOT FOUND" "Error"
}

# 2. pip
Write-Host ""
Write-Host "📦 PIP" -ForegroundColor Magenta
try {
    $pipVersion = pip --version 2>&1
    Write-Status "pip Version" "$pipVersion" "Success"
} catch {
    Write-Status "pip" "NOT FOUND" "Error"
}

# 3. FastAPI & Dependencies
Write-Host ""
Write-Host "📚 DEPENDENCIES" -ForegroundColor Magenta

$packages = @("fastapi", "uvicorn", "pydantic", "aiohttp", "sentence-transformers", "faiss-cpu")
foreach ($pkg in $packages) {
    try {
        $version = python -m pip show $pkg 2>&1 | Select-String "^Version:" | ForEach-Object { $_ -replace 'Version: ', '' }
        if ($version) {
            Write-Status "$pkg" "$version" "Success"
        } else {
            Write-Status "$pkg" "NOT INSTALLED" "Error"
        }
    } catch {
        Write-Status "$pkg" "ERROR" "Error"
    }
}

# 4. Foundry CLI
Write-Host ""
Write-Host "🔧 FOUNDRY CLI" -ForegroundColor Magenta
try {
    $foundryVersion = foundry --version 2>&1
    Write-Status "Foundry Version" "$foundryVersion" "Success"

    $status = foundry service status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Foundry Service" "RUNNING" "Success"
    } else {
        Write-Status "Foundry Service" "NOT RUNNING" "Warning"
    }
} catch {
    Write-Status "Foundry CLI" "NOT INSTALLED" "Warning"
}

# 5. Configuration Files
Write-Host ""
Write-Host "⚙️  CONFIGURATION FILES" -ForegroundColor Magenta
$files = @(".env", "requirements.txt", "launcher.ps1", "main.py", "config.py")
foreach ($file in $files) {
    $exists = Test-Path $file
    $status = if ($exists) { "FOUND" } else { "NOT FOUND" }
    $type = if ($exists) { "Success" } else { "Error" }
    Write-Status $file $status $type
}

# 6. Directories
Write-Host ""
Write-Host "📁 DIRECTORIES" -ForegroundColor Magenta
$dirs = @("logs", "rag_index", "static")
foreach ($dir in $dirs) {
    $exists = Test-Path $dir
    if (-not $exists) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $exists = Test-Path $dir
    Write-Status $dir $(if ($exists) { "EXISTS" } else { "ERROR" }) $(if ($exists) { "Success" } else { "Error" })
}

# 7. Ports Check
Write-Host ""
Write-Host "🔌 NETWORK PORTS" -ForegroundColor Magenta
$ports = @(8000, 5272, 55581)
foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    $status = if ($connection.TcpTestSucceeded) { "OPEN" } else { "CLOSED" }
    $type = if ($connection.TcpTestSucceeded) { "Success" } else { "Warning" }
    Write-Status "Port $port" $status $type
}

Write-Host ""
Write-Host "✅ SYSTEM CHECK COMPLETED" -ForegroundColor Green
Write-Host ""
