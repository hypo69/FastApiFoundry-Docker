# start.ps1 - Полный запуск FastAPI Foundry с AI моделями
# =============================================================================
# Описание:
#   Автоматизированный запуск системы: Foundry + AI модель + FastAPI сервер + веб-интерфейс
#
# Использование:
#   .\start.ps1 [-Port <port>] [-Model <model_name>]
#
# Примеры:
#   .\start.ps1
#   .\start.ps1 -Port 8080
#   .\start.ps1 -Model "deepseek-r1-7b"
#
# File: start.ps1
# Project: FastApiFoundry-Docker
# Version: 2.0.0
# Author: hypo69
# Date: 27 декабря 2025
# =============================================================================

param(
    [int]$Port = 8000,
    [string]$Model = "qwen2.5-0.5b-instruct-generic-cpu:4"
)

# Глобальные переменные
$script:FoundryPort = $null
$script:ServerProcess = $null

Write-Host "🚀 FastAPI Foundry с AI моделями" -ForegroundColor Cyan
Write-Host "Модель: $Model | Порт: $Port" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Функция для проверки и освобождения порта
function Free-Port {
    param([int]$PortNumber)

    Write-Host "🔍 Проверяем порт $PortNumber..." -ForegroundColor Yellow

    $connections = netstat -ano | findstr ":$PortNumber"
    if ($connections) {
        Write-Host "⚠️  Порт $PortNumber занят. Освобождаем..." -ForegroundColor Yellow

        foreach ($line in $connections) {
            $parts = $line -split '\s+'
            $processId = $parts[-1]

            if ($processId -and $processId -ne "0") {
                Write-Host "🛑 Убиваем процесс PID: $processId" -ForegroundColor Red
                taskkill /PID $processId /F | Out-Null
            }
        }

        Start-Sleep -Seconds 2
        Write-Host "✅ Порт $PortNumber освобожден" -ForegroundColor Green
    } else {
        Write-Host "✅ Порт $PortNumber свободен" -ForegroundColor Green
    }
}

# Функция для проверки Foundry
function Check-Foundry {
    # Проверяем распространенные порты Foundry
    $ports = @(50477, 49788, 58717, 51601, 5272)

    foreach ($port in $ports) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$port/v1/models" -TimeoutSec 3 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $models = ($response.Content | ConvertFrom-Json).data.Count
                Write-Host "✅ Foundry работает на порту $port, моделей: $models" -ForegroundColor Green
                # Сохраняем рабочий порт в глобальную переменную
                $script:FoundryPort = $port
                return $true
            }
        } catch {
            # Продолжаем проверку следующего порта
        }
    }

    Write-Host "❌ Foundry не найден на стандартных портах" -ForegroundColor Red
    return $false
}

# Функция для получения порта Foundry
function Get-Foundry-Port {
    # Если порт уже сохранен, возвращаем его
    if ($script:FoundryPort) {
        return $script:FoundryPort
    }

    # Ищем Foundry на стандартных портах
    $ports = @(49788, 50477, 8000, 8080)
    foreach ($port in $ports) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$port/v1/models" -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $script:FoundryPort = $port
                return $port
            }
        } catch {
            # Продолжаем проверку
        }
    }

    return $null
}

# Функция для запуска Foundry
function Start-Foundry {
    Write-Host "🚀 Запускаем Foundry service..." -ForegroundColor Yellow
    $foundryProcess = Start-Process -FilePath "foundry" -ArgumentList "service", "start" -NoNewWindow -PassThru

    Write-Host "⏳ Ждем запуска Foundry (15 сек)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15

    return $foundryProcess
}

# Функция для запуска модели
function Start-Model {
    param([string]$ModelName)

    Write-Host "🤖 Запускаем модель: $ModelName" -ForegroundColor Yellow

    # Проверяем, не запущена ли уже модель (пробуем через API)
    try {
        $foundryPort = Get-Foundry-Port
        if ($foundryPort) {
            $response = Invoke-WebRequest -Uri "http://localhost:$foundryPort/v1/models" -TimeoutSec 5 -ErrorAction Stop
            $modelsData = $response.Content | ConvertFrom-Json
            $runningModels = $modelsData.data | Where-Object { $_.id -eq $ModelName }

            if ($runningModels) {
                Write-Host "✅ Модель $ModelName уже запущена" -ForegroundColor Green
                return $true
            }
        }
    } catch {
        Write-Host "⚠️  Не удалось проверить статус модели через API" -ForegroundColor Yellow
    }

    # Запускаем модель через foundry CLI
    Write-Host "📥 Загружаем модель $ModelName..." -ForegroundColor Cyan
    try {
        $runResult = & foundry model run $ModelName 2>&1
        $runOutput = $runResult -join "`n"

        if ($LASTEXITCODE -eq 0 -or $runOutput -match "loaded successfully") {
            Write-Host "✅ Модель $ModelName запущена успешно" -ForegroundColor Green
            return $true
        } elseif ($runOutput -match "already running") {
            Write-Host "✅ Модель $ModelName уже была запущена" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Ошибка запуска модели: $runOutput" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Ошибка запуска модели: $_" -ForegroundColor Red
        return $false
    }
}

# Основная логика
try {
    # 1. Освобождаем порт
    Free-Port -PortNumber $Port

    # 2. Проверяем Foundry
    $foundryRunning = Check-Foundry
    if (-not $foundryRunning) {
        $foundryProcess = Start-Foundry
        Start-Sleep -Seconds 5  # Дополнительное ожидание
        $foundryRunning = Check-Foundry
        if (-not $foundryRunning) {
            Write-Host "❌ Не удалось запустить Foundry" -ForegroundColor Red
            exit 1
        }
    }

    # 3. Запускаем модель Deepseek R1
    $modelStarted = Start-Model -ModelName $Model
    if (-not $modelStarted) {
        Write-Host "❌ Не удалось запустить модель $Model" -ForegroundColor Red
        exit 1
    }

    # 4. Запускаем FastAPI сервер
    Write-Host "🌐 Запуск FastAPI сервера на порту $Port..." -ForegroundColor Cyan
    Write-Host "📚 Документация: http://localhost:$Port/docs" -ForegroundColor Cyan
    Write-Host "💬 Чат: http://localhost:$Port/static/chat.html" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Cyan

    # Активируем venv и запускаем сервер
    Write-Host "🔧 Активируем виртуальное окружение..." -ForegroundColor Yellow
    & "$PSScriptRoot\venv\Scripts\Activate.ps1"

    Write-Host "🚀 Запускаем FastAPI сервер..." -ForegroundColor Green
    $script:ServerProcess = Start-Process -FilePath "python" -ArgumentList "simple_server.py", $Port -NoNewWindow -PassThru

    # Ждем запуска сервера
    Start-Sleep -Seconds 3

    # Проверяем, запустился ли сервер
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/api/v1/health" -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ FastAPI сервер запущен успешно" -ForegroundColor Green

            # Открываем браузер
            Write-Host "🌐 Открываем веб-интерфейс..." -ForegroundColor Cyan
            Start-Process "http://localhost:$Port/static/chat.html"

            Write-Host "" -ForegroundColor Cyan
            Write-Host "🎉 Система готова к работе!" -ForegroundColor Green
            Write-Host "📱 Чат: http://localhost:$Port/static/chat.html" -ForegroundColor Cyan
            Write-Host "📚 API: http://localhost:$Port/docs" -ForegroundColor Cyan
            Write-Host "" -ForegroundColor Cyan
            Write-Host "Для остановки нажмите Ctrl+C" -ForegroundColor Yellow

            # Ждем завершения сервера
            $script:ServerProcess.WaitForExit()
        } else {
            Write-Host "❌ FastAPI сервер не отвечает" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Ошибка запуска FastAPI сервера: $_" -ForegroundColor Red
        exit 1
    }

} catch {
    Write-Host "❌ Критическая ошибка: $_" -ForegroundColor Red
    exit 1
} finally {
    # Очистка при завершении
    if ($script:ServerProcess -and -not $script:ServerProcess.HasExited) {
        Write-Host "🛑 Останавливаем сервер..." -ForegroundColor Yellow
        $script:ServerProcess.Kill()
    }
}