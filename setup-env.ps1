# setup-env.ps1 — Environment Variables Setup
# =============================================================================
# Interactive environment variables setup for FastAPI Foundry
# =============================================================================

param(
    [switch]$Force,
    [switch]$GenerateKeys
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

Write-Host '🔐 FastAPI Foundry - Environment Setup' -ForegroundColor Cyan
Write-Host ('=' * 60) -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# Check existing .env file
# -----------------------------------------------------------------------------
$envPath = "$Root\.env"
$envExamplePath = "$Root\.env.example"

if ((Test-Path $envPath) -and -not $Force) {
    Write-Host '⚠️ .env file already exists!' -ForegroundColor Yellow
    $response = Read-Host 'Overwrite? (y/N)'
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host '❌ Setup cancelled' -ForegroundColor Red
        exit 0
    }
}

# -----------------------------------------------------------------------------
# Copy example
# -----------------------------------------------------------------------------
if (Test-Path $envExamplePath) {
    Copy-Item $envExamplePath $envPath -Force
    Write-Host '✅ Copied .env.example to .env' -ForegroundColor Green
} else {
    Write-Host '❌ .env.example not found!' -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# Generate secure keys
# -----------------------------------------------------------------------------
function Generate-SecureKey {
    param([int]$Length = 32)
    
    $bytes = New-Object byte[] $Length
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
    return [Convert]::ToBase64String($bytes) -replace '[+/=]', ''
}

if ($GenerateKeys) {
    Write-Host '🔑 Generating secure keys...' -ForegroundColor Yellow
    
    $apiKey = Generate-SecureKey 32
    $secretKey = Generate-SecureKey 64
    
    # Update .env file
    $content = Get-Content $envPath
    $content = $content -replace '^API_KEY=.*', "API_KEY=$apiKey"
    $content = $content -replace '^SECRET_KEY=.*', "SECRET_KEY=$secretKey"
    $content | Set-Content $envPath
    
    Write-Host "✅ Generated API_KEY: $($apiKey.Substring(0,8))..." -ForegroundColor Green
    Write-Host "✅ Generated SECRET_KEY: $($secretKey.Substring(0,8))..." -ForegroundColor Green
}

# -----------------------------------------------------------------------------
# Interactive Setup
# -----------------------------------------------------------------------------
Write-Host "`n🛠️ Interactive Setup" -ForegroundColor Cyan
Write-Host "Press Enter to skip any field`n" -ForegroundColor Gray

# GitHub settings
Write-Host '🐙 GitHub Configuration:' -ForegroundColor Yellow
$githubUser = Read-Host 'GitHub Username'
if ($githubUser) {
    $content = Get-Content $envPath
    $content = $content -replace '^GITHUB_USER=.*', "GITHUB_USER=$githubUser"
    $content | Set-Content $envPath
}

$githubPat = Read-Host 'GitHub Personal Access Token (PAT)'
if ($githubPat) {
    $content = Get-Content $envPath
    $content = $content -replace '^GITHUB_PAT=.*', "GITHUB_PAT=$githubPat"
    $content | Set-Content $envPath
}

# API settings
Write-Host "`n🔑 API Configuration:" -ForegroundColor Yellow
if (-not $GenerateKeys) {
    $apiKey = Read-Host 'API Key (leave empty to generate)'
    if (-not $apiKey) {
        $apiKey = Generate-SecureKey 32
        Write-Host "Generated API Key: $($apiKey.Substring(0,8))..." -ForegroundColor Green
    }
    
    $secretKey = Read-Host 'Secret Key (leave empty to generate)'
    if (-not $secretKey) {
        $secretKey = Generate-SecureKey 64
        Write-Host "Generated Secret Key: $($secretKey.Substring(0,8))..." -ForegroundColor Green
    }
    
    $content = Get-Content $envPath
    $content = $content -replace '^API_KEY=.*', "API_KEY=$apiKey"
    $content = $content -replace '^SECRET_KEY=.*', "SECRET_KEY=$secretKey"
    $content | Set-Content $envPath
}

# Foundry settings
Write-Host "`n🤖 Foundry Configuration:" -ForegroundColor Yellow
$foundryUrl = Read-Host 'Foundry Base URL (default: http://localhost:50477/v1)'
if ($foundryUrl) {
    $content = Get-Content $envPath
    $content = $content -replace '^FOUNDRY_BASE_URL=.*', "FOUNDRY_BASE_URL=$foundryUrl"
    $content | Set-Content $envPath
}

# Environment settings
Write-Host "`n🌍 Environment Configuration:" -ForegroundColor Yellow
$environment = Read-Host 'Environment (development/production)'
if ($environment) {
    $content = Get-Content $envPath
    $content = $content -replace '^ENVIRONMENT=.*', "ENVIRONMENT=$environment"
    $content | Set-Content $envPath
}

# -----------------------------------------------------------------------------
# Check results
# -----------------------------------------------------------------------------
Write-Host "`n✅ Setup completed!" -ForegroundColor Green
Write-Host "📁 Configuration saved to: $envPath" -ForegroundColor Gray

Write-Host "`n🔍 Checking configuration..." -ForegroundColor Cyan
if (Test-Path "$Root\check_env.py") {
    try {
        $pythonPath = "$Root\venv\Scripts\python.exe"
        if (Test-Path $pythonPath) {
            & $pythonPath "$Root\check_env.py"
        } else {
            python "$Root\check_env.py"
        }
    } catch {
        Write-Host "⚠️ Could not run environment check: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ check_env.py not found, skipping validation" -ForegroundColor Yellow
}

Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
Write-Host "1. Review and edit .env file if needed" -ForegroundColor Gray
Write-Host "2. Run: python run.py" -ForegroundColor Gray
Write-Host "3. Open: http://localhost:9696" -ForegroundColor Gray

Write-Host "`n💡 Tips:" -ForegroundColor Yellow
Write-Host "- Never commit .env file to Git" -ForegroundColor Gray
Write-Host "- Use strong passwords and tokens" -ForegroundColor Gray
Write-Host "- Run 'python check_env.py' to validate" -ForegroundColor Gray
