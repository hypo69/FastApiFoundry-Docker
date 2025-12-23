# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск Docker Desktop для FastApiFoundry
# =============================================================================
# Описание:
#   Автоматический запуск Docker Desktop и ожидание готовности
#
# Примеры:
#   .\start-docker.ps1
#
# File: start-docker.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

Write-Host "🐳 Starting Docker Desktop..." -ForegroundColor Cyan

# Проверка установки Docker Desktop
$dockerPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
if (-not (Test-Path $dockerPath)) {
    Write-Host "❌ Docker Desktop не найден по пути: $dockerPath" -ForegroundColor Red
    Write-Host "Установите Docker Desktop с https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Проверка запущен ли уже
$dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerProcess) {
    Write-Host "ℹ️  Docker Desktop уже запущен" -ForegroundColor Yellow
} else {
    Write-Host "🚀 Запускаем Docker Desktop..." -ForegroundColor Green
    Start-Process -FilePath $dockerPath -WindowStyle Hidden
}

# Ожидание готовности Docker Engine
Write-Host "⏳ Ожидаем готовности Docker Engine..." -ForegroundColor Yellow

$maxAttempts = 60  # 2 минуты
$attempt = 0

do {
    Start-Sleep -Seconds 2
    $attempt++
    
    Write-Host "." -NoNewline -ForegroundColor Gray
    
    try {
        $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Docker Engine готов! Версия: $dockerVersion" -ForegroundColor Green
            
            # Проверка docker-compose
            $composeVersion = docker-compose --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Docker Compose готов: $composeVersion" -ForegroundColor Green
            }
            
            Write-Host ""
            Write-Host "🎉 Docker Desktop полностью готов к работе!" -ForegroundColor Green
            Write-Host "Теперь можно запускать: .\run-gui.ps1" -ForegroundColor Cyan
            exit 0
        }
    } catch {
        # Продолжаем ожидание
    }
    
} while ($attempt -lt $maxAttempts)

Write-Host ""
Write-Host "❌ Docker Engine не готов после $maxAttempts попыток" -ForegroundColor Red
Write-Host "Попробуйте:" -ForegroundColor Yellow
Write-Host "1. Перезапустить Docker Desktop вручную" -ForegroundColor Yellow
Write-Host "2. Проверить системные требования" -ForegroundColor Yellow
Write-Host "3. Перезагрузить компьютер" -ForegroundColor Yellow
exit 1