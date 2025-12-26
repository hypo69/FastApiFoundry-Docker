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
Write-ColorOutput "=" * 40 "Cyan"
Write-Host ""

# Проверка Docker
try {
    $null = docker --version 2>$null
    Write-ColorOutput "✅ Docker найден" "Green"
    
    # Проверка run-gui.py
    if (Test-Path "run-gui.py") {
        Write-ColorOutput "🖥️  Запуск GUI лончера через Docker..." "Yellow"
        Write-ColorOutput "🐳 Используем Python 3.11 из Docker контейнера" "Cyan"
        
        # Запуск через start-docker.ps1
        & ".\start-docker.ps1"
    } else {
        Write-ColorOutput "❌ run-gui.py не найден" "Red"
        Write-ColorOutput "🔄 Попробуйте: .\start-docker.ps1 -NoGUI" "Yellow"
    }
}
catch {
    Write-ColorOutput "❌ Docker не найден" "Red"
    Write-ColorOutput "📥 Установите Docker Desktop: https://www.docker.com/products/docker-desktop" "White"
    Write-ColorOutput "📝 Или создайте venv и установите Python 3.11+" "Yellow"
}

Write-Host ""
Read-Host "Нажмите Enter для выхода"