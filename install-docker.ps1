# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Установка Docker Desktop для FastApiFoundry (Docker)
# =============================================================================
# Описание:
#   PowerShell скрипт для автоматической установки Docker Desktop
#   Включает Docker Engine и Docker Compose
#
# Примеры:
#   .\install-docker.ps1
#   .\install-docker.ps1 -Force
#
# File: install-docker.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

# Установка политики выполнения для текущего пользователя
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Проверка прав администратора
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ Требуются права администратора!" -ForegroundColor Red
    Write-Host "Запустите PowerShell от имени администратора" -ForegroundColor Yellow
    exit 1
}

Write-Host "🐳 Docker Desktop Installer for FastApiFoundry" -ForegroundColor Cyan
Write-Host "=" * 60

# Проверка существующей установки
function Test-DockerInstalled {
    try {
        $dockerVersion = docker --version 2>$null
        $composeVersion = docker compose version 2>$null
        
        if ($dockerVersion -and $composeVersion) {
            Write-Host "✅ Docker уже установлен:" -ForegroundColor Green
            Write-Host "   $dockerVersion"
            Write-Host "   $composeVersion"
            return $true
        }
    } catch {
        # Docker не найден
    }
    return $false
}

# Установка Docker Desktop
function Install-DockerDesktop {
    Write-Host "📥 Скачивание Docker Desktop..." -ForegroundColor Yellow
    
    $downloadUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
    $installerPath = "$env:TEMP\DockerDesktopInstaller.exe"
    
    try {
        # Скачивание установщика
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Host "🔧 Установка Docker Desktop..." -ForegroundColor Yellow
        Write-Host "   Это может занять несколько минут..." -ForegroundColor Gray
        
        # Запуск установщика
        Start-Process -FilePath $installerPath -ArgumentList "install", "--quiet" -Wait
        
        # Очистка
        Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        
        Write-Host "✅ Docker Desktop установлен!" -ForegroundColor Green
        Write-Host "⚠️  Требуется перезагрузка системы" -ForegroundColor Yellow
        
        return $true
        
    } catch {
        Write-Host "❌ Ошибка установки: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Проверка WSL2
function Test-WSL2 {
    try {
        $wslVersion = wsl --version 2>$null
        if ($wslVersion) {
            Write-Host "✅ WSL2 доступен" -ForegroundColor Green
            return $true
        }
    } catch {
        # WSL2 не найден
    }
    
    Write-Host "⚠️  WSL2 не найден. Установка..." -ForegroundColor Yellow
    
    try {
        # Включение WSL
        Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart
        Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart
        
        # Установка WSL2
        wsl --install --no-distribution
        
        Write-Host "✅ WSL2 установлен" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Ошибка установки WSL2: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Основная логика
$Force = $false
if ($args -contains "-Force") {
    $Force = $true
}

if (Test-DockerInstalled -and !$Force) {
    Write-Host "✅ Docker уже установлен и готов к использованию" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Теперь можно запустить:" -ForegroundColor Cyan
    Write-Host "   docker-compose up -d" -ForegroundColor White
    exit 0
}

Write-Host "🔍 Проверка системных требований..." -ForegroundColor Cyan

# Проверка WSL2
if (-not (Test-WSL2)) {
    Write-Host "❌ Не удалось настроить WSL2" -ForegroundColor Red
    exit 1
}

# Установка Docker Desktop
if (Install-DockerDesktop) {
    Write-Host ""
    Write-Host "🎉 Установка завершена!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Следующие шаги:" -ForegroundColor Cyan
    Write-Host "1. Перезагрузите компьютер" -ForegroundColor White
    Write-Host "2. Запустите Docker Desktop" -ForegroundColor White
    Write-Host "3. Дождитесь полной инициализации" -ForegroundColor White
    Write-Host "4. Запустите: docker-compose up -d" -ForegroundColor White
    Write-Host ""
    
    $restart = Read-Host "Перезагрузить сейчас? (y/N)"
    if ($restart -eq 'y' -or $restart -eq 'Y') {
        Restart-Computer -Force
    }
} else {
    Write-Host "❌ Установка не удалась" -ForegroundColor Red
    exit 1
}