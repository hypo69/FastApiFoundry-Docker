# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Quick GUI Launcher
# =============================================================================
# Описание:
#   Быстрый запуск GUI лончера FastAPI Foundry
#   Автоматически определяет лучший способ запуска
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

function Test-PythonVersion {
    try {
        $pythonOutput = python --version 2>$null
        if ($pythonOutput -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            # Минимальная версия Python 3.11 (как в Docker)
            if ($major -eq 3 -and $minor -ge 11) {
                return @{
                    Compatible = $true
                    Version = $pythonOutput
                    Major = $major
                    Minor = $minor
                }
            } else {
                return @{
                    Compatible = $false
                    Version = $pythonOutput
                    Major = $major
                    Minor = $minor
                    RequiredVersion = "3.11+"
                }
            }
        }
        return @{ Compatible = $false; Version = "Unknown" }
    }
    catch {
        return @{ Compatible = $false; Version = "Not Found" }
    }
}

function Test-VirtualEnv {
    # Проверяем, активирован ли venv
    if ($env:VIRTUAL_ENV) {
        return $true
    }
    
    # Проверяем, существует ли папка venv
    if (Test-Path "venv\Scripts\activate.ps1") {
        return "exists"
    }
    
    return $false
}

function Activate-VirtualEnv {
    try {
        Write-ColorOutput "🔧 Активируем виртуальное окружение..." "Yellow"
        & ".\venv\Scripts\Activate.ps1"
        return $true
    }
    catch {
        Write-ColorOutput "❌ Ошибка активации venv: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Install-Requirements {
    try {
        Write-ColorOutput "📦 Устанавливаем зависимости..." "Yellow"
        pip install -r requirements.txt
        return $true
    }
    catch {
        Write-ColorOutput "❌ Ошибка установки зависимостей: $($_.Exception.Message)" "Red"
        return $false
    }
}

Clear-Host
Write-ColorOutput "🚀 FastAPI Foundry - Quick Start" "Cyan"
Write-ColorOutput "=" * 40 "Cyan"
Write-Host ""

# Проверка Python
try {
    $pythonCheck = Test-PythonVersion
    
    if ($pythonCheck.Compatible) {
        Write-ColorOutput "✅ Python совместим: $($pythonCheck.Version)" "Green"
        
        # Детальная проверка через Python скрипт
        if (Test-Path "utils\python_version_check.py") {
            Write-ColorOutput "🔍 Детальная проверка совместимости..." "Yellow"
            python utils\python_version_check.py
            Write-Host ""
        }
        
        # Проверка виртуального окружения
        $venvStatus = Test-VirtualEnv
        
        if ($venvStatus -eq $true) {
            Write-ColorOutput "✅ Виртуальное окружение активно" "Green"
        }
        elseif ($venvStatus -eq "exists") {
            Write-ColorOutput "🔧 Виртуальное окружение найдено, активируем..." "Yellow"
            if (-not (Activate-VirtualEnv)) {
                Write-ColorOutput "⚠️ Продолжаем без venv" "Yellow"
            }
        }
        else {
            Write-ColorOutput "⚠️ Виртуальное окружение не найдено" "Yellow"
            Write-ColorOutput "📝 Создайте venv: python -m venv venv" "White"
            Write-ColorOutput "📝 Активируйте: .\venv\Scripts\activate" "White"
        }
        
        # Проверка run-gui.py
        if (Test-Path "run-gui.py") {
            Write-ColorOutput "🖥️  Запуск GUI лончера..." "Yellow"
            python run-gui.py
        } else {
            Write-ColorOutput "❌ run-gui.py не найден" "Red"
            Write-ColorOutput "🔄 Попробуйте: .\start-docker.ps1" "Yellow"
        }
    } else {
        if ($pythonCheck.Version -eq "Not Found") {
            Write-ColorOutput "❌ Python не найден" "Red"
            Write-ColorOutput "📥 Установите Python 3.11+: https://www.python.org/downloads/" "White"
        } else {
            Write-ColorOutput "⚠️ Несовместимая версия: $($pythonCheck.Version)" "Yellow"
            Write-ColorOutput "📝 Требуется: Python $($pythonCheck.RequiredVersion) (как в Docker)" "White"
        }
        Write-ColorOutput "🐳 Используйте: .\start-docker.ps1 -NoGUI" "Cyan"
    }
}

Write-Host ""
Read-Host "Нажмите Enter для выхода"