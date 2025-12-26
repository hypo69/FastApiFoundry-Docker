# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker FastAPI Foundry Launcher (PowerShell)
# =============================================================================
# Описание:
#   PowerShell скрипт для запуска FastAPI Foundry через Docker
#   Автоматически запускает GUI лончер для удобного управления
#
# Примеры:
#   .\start-docker.ps1
#   powershell -ExecutionPolicy Bypass -File start-docker.ps1
#
# File: start-docker.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

param(
    [switch]$NoGUI,
    [int]$Port = 8000
)

# Цвета для вывода
$Host.UI.RawUI.ForegroundColor = "White"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = "White"
}

function Test-VirtualEnv {
    if ($env:VIRTUAL_ENV) {
        return $true
    }
    if (Test-Path "venv\Scripts\activate.ps1") {
        return "exists"
    }
    return $false
}

function Activate-VirtualEnv {
    try {
        Write-ColorOutput "🔧 Активируем venv..." "Yellow"
        & ".\venv\Scripts\Activate.ps1"
        return $true
    }
    catch {
        Write-ColorOutput "⚠️ Ошибка активации venv" "Yellow"
        return $false
    }
}

function Test-DockerInstalled {
    try {
        $null = docker --version 2>$null
        return $true
    }
    catch {
        return $false
    }
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

function Test-PythonInstalled {
    try {
        $null = python --version 2>$null
        return $true
    }
    catch {
        return $false
    }
}

function Stop-ProcessOnPort {
    param([int]$PortNumber)
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $PortNumber -ErrorAction SilentlyContinue
        if ($processes) {
            foreach ($process in $processes) {
                $pid = $process.OwningProcess
                Write-ColorOutput "🔄 Останавливаем процесс $pid на порту $PortNumber" "Yellow"
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        }
    }
    catch {
        Write-ColorOutput "⚠️  Не удалось проверить порт $PortNumber" "Yellow"
    }
}

# Заголовок
Clear-Host
Write-ColorOutput "🐳 Docker FastAPI Foundry Launcher" "Cyan"
Write-ColorOutput "=" * 50 "Cyan"
Write-Host ""

# Проверка Docker
Write-ColorOutput "🔍 Проверяем Docker..." "Yellow"
if (-not (Test-DockerInstalled)) {
    Write-ColorOutput "❌ Docker не найден!" "Red"
    Write-ColorOutput "📥 Установите Docker Desktop: https://www.docker.com/products/docker-desktop" "White"
    Read-Host "Нажмите Enter для выхода"
    exit 1
}
Write-ColorOutput "✅ Docker найден" "Green"

# Проверка Python (для GUI)
if (-not $NoGUI) {
    Write-ColorOutput "🔍 Проверяем Python..." "Yellow"
    
    $pythonCheck = Test-PythonVersion
    
    if (-not $pythonCheck.Compatible) {
        if ($pythonCheck.Version -eq "Not Found") {
            Write-ColorOutput "❌ Python не найден" "Red"
        } else {
            Write-ColorOutput "⚠️  Несовместимая версия Python: $($pythonCheck.Version)" "Yellow"
            Write-ColorOutput "📝 Требуется: Python $($pythonCheck.RequiredVersion) (как в Docker)" "White"
        }
        Write-ColorOutput "🐳 Используем Docker режим..." "Cyan"
        $NoGUI = $true
    } else {
        Write-ColorOutput "✅ Python совместим: $($pythonCheck.Version)" "Green"
        
        # Проверка venv
        $venvStatus = Test-VirtualEnv
        if ($venvStatus -eq "exists") {
            Write-ColorOutput "🔧 Найдено venv, активируем..." "Yellow"
            Activate-VirtualEnv | Out-Null
        }
        elseif ($venvStatus -eq $true) {
            Write-ColorOutput "✅ venv уже активно" "Green"
        }
    }
}

# Проверка образа Docker
Write-ColorOutput "🔍 Проверяем Docker образ..." "Yellow"
$imageExists = docker images -q fastapi-foundry:0.2.1 2>$null
if (-not $imageExists) {
    Write-ColorOutput "🔨 Собираем Docker образ..." "Yellow"
    docker build -t fastapi-foundry:0.2.1 .
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Ошибка сборки Docker образа" "Red"
        Read-Host "Нажмите Enter для выхода"
        exit 1
    }
    Write-ColorOutput "✅ Docker образ собран" "Green"
} else {
    Write-ColorOutput "✅ Docker образ найден" "Green"
}

# Освобождение порта
Write-ColorOutput "🔄 Проверяем порт $Port..." "Yellow"
Stop-ProcessOnPort -PortNumber $Port

# Запуск
Write-Host ""
if ($NoGUI) {
    # Прямой запуск через Docker
    Write-ColorOutput "🚀 Запуск FastAPI Foundry через Docker..." "Green"
    Write-ColorOutput "🌐 Веб-интерфейс: http://localhost:$Port" "Cyan"
    Write-ColorOutput "📚 API документация: http://localhost:$Port/docs" "Cyan"
    Write-Host ""
    
    docker run --rm -it `
        -v "${PWD}:/app" `
        -p "${Port}:8000" `
        -w /app `
        fastapi-foundry:0.2.1 `
        python run.py
} else {
    # Запуск GUI лончера
    Write-ColorOutput "🖥️  Запуск GUI лончера..." "Green"
    Write-ColorOutput "💡 GUI лончер откроется в новом окне" "Cyan"
    Write-ColorOutput "🐳 Выберите вкладку 'Docker' для запуска в контейнере" "Cyan"
    Write-Host ""
    
    try {
        # Проверяем, существует ли run-gui.py
        if (Test-Path "run-gui.py") {
            python run-gui.py
        } else {
            Write-ColorOutput "❌ Файл run-gui.py не найден" "Red"
            Write-ColorOutput "🔄 Запуск напрямую через Docker..." "Yellow"
            
            docker run --rm -it `
                -v "${PWD}:/app" `
                -p "${Port}:8000" `
                -w /app `
                fastapi-foundry:0.2.1 `
                python run.py
        }
    }
    catch {
        Write-ColorOutput "❌ Ошибка запуска GUI: $($_.Exception.Message)" "Red"
        Write-ColorOutput "🔄 Запуск напрямую через Docker..." "Yellow"
        
        docker run --rm -it `
            -v "${PWD}:/app" `
            -p "${Port}:8000" `
            -w /app `
            fastapi-foundry:0.2.1 `
            python run.py
    }
}

# Завершение
Write-Host ""
Write-ColorOutput "👋 Завершение работы" "Yellow"
if (-not $NoGUI) {
    Read-Host "Нажмите Enter для выхода"
}