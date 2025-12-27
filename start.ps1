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
#   .\start.ps1 -Port 9696
#   .\start.ps1 -Model "deepseek-r1-7b"
#
# File: start.ps1
# Project: FastApiFoundry-Docker
# Version: 2.0.0
# Author: hypo69
# Date: 27 декабря 2025
# =============================================================================

param(
    [string]$Model = $null
)

# Глобальные переменные
$script:FoundryPort = $null
$script:ServerProcess = $null
$script:ServerPort = $null

Write-Host "🚀 FastAPI Foundry с AI моделями" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Функция для проверки и освобождения порта
function Free-Port {
    param([int]$PortNumber)

    Write-Host "🔍 Проверка порта $PortNumber..." -ForegroundColor Yellow

    $connections = netstat -ano | findstr ":$PortNumber"
    if ($connections) {
        Write-Host "⚠️  Порт $PortNumber занят. Проверка процессов..." -ForegroundColor Yellow

        foreach ($line in $connections) {
            $parts = $line -split '\s+'
            $processId = $parts[-1]

            if ($processId -and $processId -ne "0") {
                try {
                    $process = Get-Process -Id $processId -ErrorAction Stop
                    $processName = $process.ProcessName.ToLower()
                    
                    # Убиваем только FastAPI/uvicorn/python процессы, НЕ IDE
                    if ($processName -match "python|uvicorn|fastapi" -and 
                        $processName -notmatch "code|pycharm|idea|studio|devenv") {
                        Write-Host "🛑 Киллинг FastAPI процесса: $processName (PID: $processId)" -ForegroundColor Red
                        taskkill /PID $processId /F 2>$null
                    } else {
                        Write-Host "⚠️  Пропускаем процесс: $processName (PID: $processId) - возможно IDE" -ForegroundColor Yellow
                    }
                } catch {
                    Write-Host "⚠️  Не удалось получить информацию о процессе PID: $processId" -ForegroundColor Yellow
                }
            }
        }

        Start-Sleep -Seconds 2
        Write-Host "✅ Порт $PortNumber проверен" -ForegroundColor Green
    } else {
        Write-Host "✅ Порт $PortNumber свободен" -ForegroundColor Green
    }
}

# Основная логика
try {
    # 1. Поиск уже запущенного Foundry
    Write-Host "🔍 Поиск запущенного Foundry..." -ForegroundColor Yellow
    $foundryPort = $null
    
    # Ищем процесс foundry и его порт
    $foundryProcesses = Get-Process -Name "foundry" -ErrorAction SilentlyContinue
    if ($foundryProcesses) {
        $netstatOutput = netstat -ano | Select-String "$($foundryProcesses[0].Id)"
        foreach ($line in $netstatOutput) {
            if ($line -match ":([0-9]+)\s+.*LISTENING") {
                $port = $matches[1]
                try {
                    $response = Invoke-WebRequest -Uri "http://localhost:$port/v1/models" -TimeoutSec 2 -ErrorAction Stop
                    if ($response.StatusCode -eq 200) {
                        $foundryPort = $port
                        Write-Host "✅ Foundry найден на порту $port" -ForegroundColor Green
                        break
                    }
                } catch { }
            }
        }
    }
    
    if (-not $foundryPort) {
        Write-Host "🚀 Foundry не найден, запускаем..." -ForegroundColor Yellow
        $foundryOutput = & foundry service start 2>&1
        
        # Парсинг порта из вывода
        foreach ($line in $foundryOutput) {
            if ($line -match "http://127\.0\.0\.1:(\d+)/") {
                $foundryPort = $matches[1]
                Write-Host "✅ Foundry запущен на порту $foundryPort" -ForegroundColor Green
                break
            }
        }
        
        if (-not $foundryPort) {
            Write-Host "❌ Не удалось запустить Foundry" -ForegroundColor Red
            exit 1
        }
    }
    
    $script:FoundryPort = $foundryPort

    # 2. Запуск FastAPI сервера
    Write-Host "🌐 Запуск FastAPI сервера..." -ForegroundColor Cyan
    Write-Host "📚 Порт будет определен автоматически из config.json" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Cyan

    # Активация venv и запуск сервера
    Write-Host "🔧 Активация виртуального окружения..." -ForegroundColor Yellow
    
    if (Test-Path "$PSScriptRoot\venv\Scripts\Activate.ps1") {
        & "$PSScriptRoot\venv\Scripts\Activate.ps1"
        $pythonExe = "$PSScriptRoot\venv\Scripts\python.exe"
    } else {
        Write-Host "⚠️  venv не найден, используем embedded Python" -ForegroundColor Yellow
        $pythonExe = "$PSScriptRoot\python.exe"
    }

    Write-Host "🚀 Запуск FastAPI сервера..." -ForegroundColor Green
    
    # Передача порта Foundry в приложение
    $env:FOUNDRY_BASE_URL = "http://localhost:$foundryPort/v1/"
    $env:FOUNDRY_PORT = $foundryPort
    Write-Host "🔗 Foundry URL: $env:FOUNDRY_BASE_URL" -ForegroundColor Green
    Write-Host "🔗 Foundry Port: $env:FOUNDRY_PORT" -ForegroundColor Green
    
    # Запуск с выводом в консоль
    Write-Host "📋 Вывод сервера:" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Cyan
    
    # Запуск сервера в фоновом режиме
    $serverJob = Start-Job -ScriptBlock {
        param($pythonPath, $workingDir, $foundryUrl, $foundryPort)
        Set-Location $workingDir
        $env:FOUNDRY_BASE_URL = $foundryUrl
        $env:FOUNDRY_PORT = $foundryPort
        & $pythonPath "run.py"
    } -ArgumentList $pythonExe, $PWD, $env:FOUNDRY_BASE_URL, $env:FOUNDRY_PORT
    
    # Ожидание запуска сервера
    Write-Host "⏳ Ожидание запуска сервера..." -ForegroundColor Yellow
    
    $maxWait = 30
    $waited = 0
    $serverReady = $false
    
    while ($waited -lt $maxWait -and -not $serverReady) {
        Start-Sleep -Seconds 2
        $waited += 2
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:9696/api/v1/health" -TimeoutSec 3 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $serverReady = $true
                Write-Host "✅ Сервер готов!" -ForegroundColor Green
                $script:ServerPort = 9696
            }
        } catch {
            # Пробуем другие порты в диапазоне
            for ($testPort = 9696; $testPort -le 9796; $testPort++) {
                try {
                    $response = Invoke-WebRequest -Uri "http://localhost:$testPort/api/v1/health" -TimeoutSec 1 -ErrorAction Stop
                    if ($response.StatusCode -eq 200) {
                        $serverReady = $true
                        Write-Host "✅ Сервер готов на порту $testPort!" -ForegroundColor Green
                        $script:ServerPort = $testPort
                        break
                    }
                } catch { }
            }
            if (-not $serverReady) {
                Write-Host ".⏳" -NoNewline -ForegroundColor Yellow
            }
        }
    }
    
    if ($serverReady) {
        Write-Host "" -ForegroundColor Cyan
        Write-Host "🎉 Система готова к работе!" -ForegroundColor Green
        Write-Host "📱 Веб-интерфейс: http://localhost:$script:ServerPort" -ForegroundColor Cyan
        Write-Host "📚 API: http://localhost:$script:ServerPort/docs" -ForegroundColor Cyan
        Write-Host "" -ForegroundColor Cyan
        
        # Открытие браузера ТОЛЬКО после полного запуска
        Write-Host "🌐 Открытие веб-интерфейса..." -ForegroundColor Cyan
        Start-Process "http://localhost:$script:ServerPort"
        
        Write-Host "Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
        
        # Ожидание завершения работы
        Wait-Job $serverJob
    } else {
        Write-Host "" -ForegroundColor Red
        Write-Host "❌ Сервер не запустился за $maxWait секунд" -ForegroundColor Red
        Stop-Job $serverJob
        Remove-Job $serverJob
        exit 1
    }

} catch {
    Write-Host "❌ Критическая ошибка: $_" -ForegroundColor Red
    exit 1
}