# -*- coding: utf-8 -*-
# FastAPI Foundry HTTPS Server Launcher
# Запуск FastAPI сервера через HTTPS

param(
    [ValidateSet('dev', 'prod')]
    [string]$Mode = 'dev',

    [int]$Port = 8443,

    [string]$Host = '0.0.0.0',

    [string]$SslKeyFile,

    [string]$SslCertFile,

    [switch]$Mcp,

    [switch]$AutoPort,

    [switch]$Browser
)

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "🚀 FastAPI Foundry HTTPS Server"
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host ""

# Определяем директорию скрипта
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
cd $ScriptDir

# Если не указаны сертификаты, используем по умолчанию из ~/.ssh
if (-not $SslKeyFile) {
    $SslKeyFile = Join-Path $env:USERPROFILE ".ssh\server.key"
}

if (-not $SslCertFile) {
    $SslCertFile = Join-Path $env:USERPROFILE ".ssh\server.crt"
}

# Проверяем наличие сертификатов
if (-not (Test-Path $SslKeyFile)) {
    Write-Host "❌ Error: SSL key file not found: $SslKeyFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Generate certificates first:"
    Write-Host "   openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes -subj '/C=RU/ST=Moscow/L=Moscow/O=AiStros/CN=localhost'"
    exit 1
}

if (-not (Test-Path $SslCertFile)) {
    Write-Host "❌ Error: SSL certificate file not found: $SslCertFile" -ForegroundColor Red
    exit 1
}

# Активируем venv если существует
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "📦 Activating virtual environment..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
    Write-Host ""
}

# Выводим информацию
Write-Host "📋 Configuration:"
Write-Host "   Mode: $Mode"
Write-Host "   Host: $Host"
if ($AutoPort) {
    Write-Host "   Port: Auto-detect"
} else {
    Write-Host "   Port: $Port"
}
Write-Host "   Protocol: HTTPS 🔒"
Write-Host "   SSL Key: $SslKeyFile"
Write-Host "   SSL Cert: $SslCertFile"
if ($Mcp) {
    Write-Host "   MCP Console: Enabled"
}
if ($Browser) {
    Write-Host "   Auto-open browser: Yes"
}
Write-Host ""

# Строим команду запуска
$Command = "python run.py --$Mode --ssl"

if ($Host -ne '0.0.0.0') {
    $Command += " --host $Host"
}

if ($AutoPort) {
    $Command += " --auto-port"
} elseif ($Port -ne 8443) {
    $Command += " --port $Port"
}

if ($Mcp) {
    $Command += " --mcp"
}

if ($Browser) {
    $Command += " --browser"
}

if ($SslKeyFile) {
    $Command += " --ssl-keyfile '$SslKeyFile'"
}

if ($SslCertFile) {
    $Command += " --ssl-certfile '$SslCertFile'"
}

Write-Host "▶️  Running: $Command"
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host ""

# Запускаем сервер
Invoke-Expression $Command
