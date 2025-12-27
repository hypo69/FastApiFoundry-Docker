# create_symbolic_links.ps1
# Создание символических ссылок на python-3.11.0-embed-amd64

param(
    [string]$LinkDirectory = "$env:USERPROFILE\bin"
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$PythonPath = "$Root\python-3.11.0-embed-amd64"
$PythonExe = "$PythonPath\python.exe"

Write-Host '🔗 Creating Python symbolic links...' -ForegroundColor Cyan

# Проверка Python
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Python not found: $PythonExe" -ForegroundColor Red
    exit 1
}

# Проверка прав администратора
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host '⚠️ Restarting as Administrator...' -ForegroundColor Yellow
    $arguments = "-File `"$PSCommandPath`" -LinkDirectory `"$LinkDirectory`""
    Start-Process PowerShell -Verb RunAs -ArgumentList $arguments
    exit 0
}

# Создание директории
if (-not (Test-Path $LinkDirectory)) {
    New-Item -ItemType Directory -Path $LinkDirectory -Force | Out-Null
}

# Создание ссылок
$links = @(
    @{ Name = "python.exe"; Target = $PythonExe },
    @{ Name = "python3.exe"; Target = $PythonExe }
)

foreach ($link in $links) {
    $linkPath = Join-Path $LinkDirectory $link.Name
    if (Test-Path $linkPath) {
        Write-Host "⚠️ Already exists: $($link.Name)" -ForegroundColor Yellow
        continue
    }
    
    try {
        New-Item -ItemType SymbolicLink -Path $linkPath -Target $link.Target -Force | Out-Null
        Write-Host "✅ Created: $($link.Name)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed: $($link.Name)" -ForegroundColor Red
    }
}

# Добавление в PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$LinkDirectory*") {
    $newPath = "$LinkDirectory;$currentPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "✅ Added to PATH: $LinkDirectory" -ForegroundColor Green
}

Write-Host '✅ Done! Restart terminal to use python command.' -ForegroundColor Green