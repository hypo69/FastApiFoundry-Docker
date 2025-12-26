# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Quick GUI Launcher (Docker Only)
# =============================================================================
# Описание:
#   Быстрый запуск GUI лончера FastAPI Foundry через Docker
#   Использует Python 3.11 из Docker контейнера
#
# File: start-gui.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

# Цвета для вывода
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = "White"
}

Clear-Host
Write-ColorOutput "🚀 FastAPI Foundry - Quick Start" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-Host ""

# Проверка Docker и локального Python
try {
    $null = docker --version 2>$null
    Write-ColorOutput "✅ Docker найден" "Green"
    
    # Проверка локального Python для GUI
    $pythonFound = $false
    $pythonCmd = "python"
    
    try {
        $null = python --version 2>$null
        $pythonFound = $true
    } catch {
        try {
            $null = python3 --version 2>$null
            $pythonCmd = "python3"
            $pythonFound = $true
        } catch {
            $pythonFound = $false
        }
    }
    
    if ($pythonFound -and (Test-Path "run-gui.py")) {
        Write-ColorOutput "🖥️  Запуск GUI лончера локально..." "Yellow"
        Write-ColorOutput "🐳 FastAPI сервер будет запущен в Docker" "Cyan"
        Write-ColorOutput "📝 Выберите вкладку 'Docker' в GUI" "Cyan"
        
        & $pythonCmd run-gui.py
    } elseif (-not $pythonFound) {
        Write-ColorOutput "❌ Локальный Python не найден" "Red"
        Write-ColorOutput "🔄 Запуск через start-docker.ps1 -NoGUI" "Yellow"
        & ".\start-docker.ps1" -NoGUI
    } else {
        Write-ColorOutput "❌ run-gui.py не найден" "Red"
        Write-ColorOutput "🔄 Запуск через start-docker.ps1 -NoGUI" "Yellow"
        & ".\start-docker.ps1" -NoGUI
    }
}
catch {
    Write-ColorOutput "❌ Docker не найден" "Red"
    Write-ColorOutput "📥 Установите Docker Desktop: https://www.docker.com/products/docker-desktop" "White"
    Write-ColorOutput "📝 Или создайте venv и установите зависимости" "Yellow"
}

Write-Host ""
Read-Host "Нажмите Enter для выхода"