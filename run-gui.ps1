# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: GUI лончер для FastAPI Foundry
# =============================================================================
# Описание:
#   Графический интерфейс для запуска run.py с полным набором параметров
#   Настройки загружаются из gui-config.json
#
# Примеры:
#   .\run-gui.ps1
#
# File: run-gui.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$configFile = Join-Path $scriptDir "src\config.json"

# Функция для освобождения порта или поиска свободного
function Resolve-PortConflict {
    param(
        [int]$Port,
        [string]$Resolution = "kill_process"
    )
    
    Write-Host "Проверяем порт $Port..." -ForegroundColor Yellow
    
    # Проверка занятости порта
    $result = netstat -ano | Select-String ":$Port\s" | Select-String "LISTENING"
    
    if (-not $result) {
        Write-Host "✅ Порт $Port свободен" -ForegroundColor Green
        return $Port
    }
    
    if ($Resolution -eq "kill_process") {
        # Убить процесс на порту
        foreach ($line in $result) {
            $parts = $line.ToString().Split() | Where-Object { $_ -ne "" }
            if ($parts.Length -ge 5) {
                $pid = $parts[-1]
                Write-Host "⚠️ Найден процесс PID $pid на порту $Port, завершаем..." -ForegroundColor Yellow
                
                try {
                    taskkill /PID $pid /F 2>$null
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "✅ Процесс PID $pid успешно завершен" -ForegroundColor Green
                        Start-Sleep -Seconds 1
                        return $Port
                    }
                } catch {
                    Write-Host "⚠️ Не удалось завершить PID $pid" -ForegroundColor Yellow
                }
            }
        }
    } elseif ($Resolution -eq "find_free_port") {
        # Найти свободный порт
        Write-Host "🔍 Ищем свободный порт начиная с $($Port + 1)..." -ForegroundColor Yellow
        
        for ($testPort = $Port + 1; $testPort -le ($Port + 100); $testPort++) {
            $testResult = netstat -ano | Select-String ":$testPort\s" | Select-String "LISTENING"
            if (-not $testResult) {
                Write-Host "✅ Найден свободный порт: $testPort" -ForegroundColor Green
                return $testPort
            }
        }
        
        Write-Host "❌ Не удалось найти свободный порт" -ForegroundColor Red
        return $null
    }
    
    return $Port
}

# Загрузка конфигурации
if (Test-Path $configFile) {
    $config = Get-Content $configFile -Raw | ConvertFrom-Json
} else {
    Write-Host "Config file not found: $configFile" -ForegroundColor Red
    exit 1
}

# Создание формы
$form = New-Object System.Windows.Forms.Form
$form.Text = "FastAPI Foundry — Launch Configuration"
$form.Size = New-Object System.Drawing.Size(520,750)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

# Создание TabControl
$tabControl = New-Object System.Windows.Forms.TabControl
$tabControl.Location = New-Object System.Drawing.Point(10,10)
$tabControl.Size = New-Object System.Drawing.Size(480,620)
$form.Controls.Add($tabControl)

# === TAB 1: FastAPI Server ===
$tabServer = New-Object System.Windows.Forms.TabPage
$tabServer.Text = "FastAPI Server"
$tabControl.TabPages.Add($tabServer)

$y = 20

# Заголовок секции
$lblServerHeader = New-Object System.Windows.Forms.Label
$lblServerHeader.Text = "FastAPI Server Configuration (Port $($config.fastapi_server.port))"
$lblServerHeader.Location = New-Object System.Drawing.Point(15,$y)
$lblServerHeader.Size = New-Object System.Drawing.Size(400,20)
$lblServerHeader.Font = New-Object System.Drawing.Font("Segoe UI",9,[System.Drawing.FontStyle]::Bold)
$lblServerHeader.ForeColor = [System.Drawing.Color]::DarkBlue
$tabServer.Controls.Add($lblServerHeader)
$y += 30

# Mode
$lblMode = New-Object System.Windows.Forms.Label
$lblMode.Text = "FASTAPI_FOUNDRY_MODE:"
$lblMode.Location = New-Object System.Drawing.Point(15,$y)
$lblMode.Size = New-Object System.Drawing.Size(180,20)
$tabServer.Controls.Add($lblMode)

$cbMode = New-Object System.Windows.Forms.ComboBox
$cbMode.Location = New-Object System.Drawing.Point(200,$y)
$cbMode.Size = New-Object System.Drawing.Size(250,20)
$cbMode.Items.AddRange(@("dev","production"))
$cbMode.Text = $config.fastapi_server.mode
$tabServer.Controls.Add($cbMode)
$y += 35

# Host
$lblHost = New-Object System.Windows.Forms.Label
$lblHost.Text = "HOST:"
$lblHost.Location = New-Object System.Drawing.Point(15,$y)
$lblHost.Size = New-Object System.Drawing.Size(180,20)
$tabServer.Controls.Add($lblHost)

$txtHost = New-Object System.Windows.Forms.TextBox
$txtHost.Location = New-Object System.Drawing.Point(200,$y)
$txtHost.Size = New-Object System.Drawing.Size(250,20)
$txtHost.Text = $config.fastapi_server.host
$tabServer.Controls.Add($txtHost)
$y += 35

# Port (FastAPI Server)
$lblPort = New-Object System.Windows.Forms.Label
$lblPort.Text = "PORT (FastAPI Server):"
$lblPort.Location = New-Object System.Drawing.Point(15,$y)
$lblPort.Size = New-Object System.Drawing.Size(180,20)
$tabServer.Controls.Add($lblPort)

$txtPort = New-Object System.Windows.Forms.TextBox
$txtPort.Location = New-Object System.Drawing.Point(200,$y)
$txtPort.Size = New-Object System.Drawing.Size(250,20)
$txtPort.Text = $config.fastapi_server.port.ToString()
$tabServer.Controls.Add($txtPort)
$y += 35

# API Key
$lblApiKey = New-Object System.Windows.Forms.Label
$lblApiKey.Text = "API_KEY (optional):"
$lblApiKey.Location = New-Object System.Drawing.Point(15,$y)
$lblApiKey.Size = New-Object System.Drawing.Size(180,20)
$tabServer.Controls.Add($lblApiKey)

$txtApiKey = New-Object System.Windows.Forms.TextBox
$txtApiKey.Location = New-Object System.Drawing.Point(200,$y)
$txtApiKey.Size = New-Object System.Drawing.Size(250,20)
$txtApiKey.PasswordChar = '*'
$txtApiKey.Text = $config.fastapi_server.api_key
$tabServer.Controls.Add($txtApiKey)
$y += 35

# Workers
$lblWorkers = New-Object System.Windows.Forms.Label
$lblWorkers.Text = "API_WORKERS:"
$lblWorkers.Location = New-Object System.Drawing.Point(15,$y)
$lblWorkers.Size = New-Object System.Drawing.Size(180,20)
$tabServer.Controls.Add($lblWorkers)

$numWorkers = New-Object System.Windows.Forms.NumericUpDown
$numWorkers.Location = New-Object System.Drawing.Point(200,$y)
$numWorkers.Size = New-Object System.Drawing.Size(100,20)
$numWorkers.Minimum = 1
$numWorkers.Maximum = 16
$numWorkers.Value = $config.fastapi_server.workers
$tabServer.Controls.Add($numWorkers)
$y += 35

# Reload
$chkReload = New-Object System.Windows.Forms.CheckBox
$chkReload.Text = "API_RELOAD (dev mode)"
$chkReload.Location = New-Object System.Drawing.Point(15,$y)
$chkReload.Size = New-Object System.Drawing.Size(200,20)
$chkReload.Checked = $config.fastapi_server.reload
$tabServer.Controls.Add($chkReload)
$y += 35

# Log Level
$lblLogLevel = New-Object System.Windows.Forms.Label
$lblLogLevel.Text = "LOG_LEVEL:"
$lblLogLevel.Location = New-Object System.Drawing.Point(15,$y)
$lblLogLevel.Size = New-Object System.Drawing.Size(180,20)
$tabServer.Controls.Add($lblLogLevel)

$cbLogLevel = New-Object System.Windows.Forms.ComboBox
$cbLogLevel.Location = New-Object System.Drawing.Point(200,$y)
$cbLogLevel.Size = New-Object System.Drawing.Size(150,20)
$cbLogLevel.Items.AddRange(@("DEBUG","INFO","WARNING","ERROR"))
$cbLogLevel.Text = $config.fastapi_server.log_level
$tabServer.Controls.Add($cbLogLevel)

# === TAB 2: Foundry AI Model ===
$tabFoundry = New-Object System.Windows.Forms.TabPage
$tabFoundry.Text = "Foundry AI Model"
$tabControl.TabPages.Add($tabFoundry)

$y = 20

# Заголовок секции
$lblFoundryHeader = New-Object System.Windows.Forms.Label
$lblFoundryHeader.Text = "Foundry AI Model Configuration"
$lblFoundryHeader.Location = New-Object System.Drawing.Point(15,$y)
$lblFoundryHeader.Size = New-Object System.Drawing.Size(400,20)
$lblFoundryHeader.Font = New-Object System.Drawing.Font("Segoe UI",9,[System.Drawing.FontStyle]::Bold)
$lblFoundryHeader.ForeColor = [System.Drawing.Color]::DarkGreen
$tabFoundry.Controls.Add($lblFoundryHeader)
$y += 30

# Foundry Base URL (AI Model Server)
$lblFoundryUrl = New-Object System.Windows.Forms.Label
$lblFoundryUrl.Text = "FOUNDRY_BASE_URL (AI Model):"
$lblFoundryUrl.Location = New-Object System.Drawing.Point(15,$y)
$lblFoundryUrl.Size = New-Object System.Drawing.Size(180,20)
$tabFoundry.Controls.Add($lblFoundryUrl)

$txtFoundryUrl = New-Object System.Windows.Forms.TextBox
$txtFoundryUrl.Location = New-Object System.Drawing.Point(200,$y)
$txtFoundryUrl.Size = New-Object System.Drawing.Size(250,20)
$txtFoundryUrl.Text = $config.foundry_ai.base_url
$tabFoundry.Controls.Add($txtFoundryUrl)
$y += 35

# Default Model
$lblModel = New-Object System.Windows.Forms.Label
$lblModel.Text = "FOUNDRY_DEFAULT_MODEL:"
$lblModel.Location = New-Object System.Drawing.Point(15,$y)
$lblModel.Size = New-Object System.Drawing.Size(180,20)
$tabFoundry.Controls.Add($lblModel)

$txtModel = New-Object System.Windows.Forms.TextBox
$txtModel.Location = New-Object System.Drawing.Point(200,$y)
$txtModel.Size = New-Object System.Drawing.Size(250,20)
$txtModel.Text = $config.foundry_ai.default_model
$tabFoundry.Controls.Add($txtModel)
$y += 35

# Temperature
$lblTemp = New-Object System.Windows.Forms.Label
$lblTemp.Text = "FOUNDRY_TEMPERATURE:"
$lblTemp.Location = New-Object System.Drawing.Point(15,$y)
$lblTemp.Size = New-Object System.Drawing.Size(180,20)
$tabFoundry.Controls.Add($lblTemp)

$numTemp = New-Object System.Windows.Forms.NumericUpDown
$numTemp.Location = New-Object System.Drawing.Point(200,$y)
$numTemp.Size = New-Object System.Drawing.Size(100,20)
$numTemp.DecimalPlaces = 1
$numTemp.Increment = 0.1
$numTemp.Minimum = 0.0
$numTemp.Maximum = 2.0
$numTemp.Value = $config.foundry_ai.temperature
$tabFoundry.Controls.Add($numTemp)
$y += 35

# Top P
$lblTopP = New-Object System.Windows.Forms.Label
$lblTopP.Text = "FOUNDRY_TOP_P:"
$lblTopP.Location = New-Object System.Drawing.Point(15,$y)
$lblTopP.Size = New-Object System.Drawing.Size(180,20)
$tabFoundry.Controls.Add($lblTopP)

$numTopP = New-Object System.Windows.Forms.NumericUpDown
$numTopP.Location = New-Object System.Drawing.Point(200,$y)
$numTopP.Size = New-Object System.Drawing.Size(100,20)
$numTopP.DecimalPlaces = 2
$numTopP.Increment = 0.01
$numTopP.Minimum = 0.0
$numTopP.Maximum = 1.0
$numTopP.Value = $config.foundry_ai.top_p
$tabFoundry.Controls.Add($numTopP)
$y += 35

# Top K
$lblTopK = New-Object System.Windows.Forms.Label
$lblTopK.Text = "FOUNDRY_TOP_K:"
$lblTopK.Location = New-Object System.Drawing.Point(15,$y)
$lblTopK.Size = New-Object System.Drawing.Size(180,20)
$tabFoundry.Controls.Add($lblTopK)

$numTopK = New-Object System.Windows.Forms.NumericUpDown
$numTopK.Location = New-Object System.Drawing.Point(200,$y)
$numTopK.Size = New-Object System.Drawing.Size(100,20)
$numTopK.Minimum = 1
$numTopK.Maximum = 200
$numTopK.Value = $config.foundry_ai.top_k
$tabFoundry.Controls.Add($numTopK)
$y += 35

# Max Tokens
$lblMaxTokens = New-Object System.Windows.Forms.Label
$lblMaxTokens.Text = "FOUNDRY_MAX_TOKENS:"
$lblMaxTokens.Location = New-Object System.Drawing.Point(15,$y)
$lblMaxTokens.Size = New-Object System.Drawing.Size(180,20)
$tabFoundry.Controls.Add($lblMaxTokens)

$numMaxTokens = New-Object System.Windows.Forms.NumericUpDown
$numMaxTokens.Location = New-Object System.Drawing.Point(200,$y)
$numMaxTokens.Size = New-Object System.Drawing.Size(100,20)
$numMaxTokens.Minimum = 1
$numMaxTokens.Maximum = 32768
$numMaxTokens.Value = $config.foundry_ai.max_tokens
$tabFoundry.Controls.Add($numMaxTokens)
$y += 35

# Timeout
$lblTimeout = New-Object System.Windows.Forms.Label
$lblTimeout.Text = "FOUNDRY_TIMEOUT (sec):"
$lblTimeout.Location = New-Object System.Drawing.Point(15,$y)
$lblTimeout.Size = New-Object System.Drawing.Size(180,20)
$tabFoundry.Controls.Add($lblTimeout)

$numTimeout = New-Object System.Windows.Forms.NumericUpDown
$numTimeout.Location = New-Object System.Drawing.Point(200,$y)
$numTimeout.Size = New-Object System.Drawing.Size(100,20)
$numTimeout.Minimum = 10
$numTimeout.Maximum = 3600
$numTimeout.Value = $config.foundry_ai.timeout
$tabFoundry.Controls.Add($numTimeout)

# === TAB 3: RAG Settings ===
$tabRAG = New-Object System.Windows.Forms.TabPage
$tabRAG.Text = "RAG System"
$tabControl.TabPages.Add($tabRAG)

$y = 20

# RAG Enabled
$chkRAG = New-Object System.Windows.Forms.CheckBox
$chkRAG.Text = "RAG_ENABLED"
$chkRAG.Location = New-Object System.Drawing.Point(15,$y)
$chkRAG.Size = New-Object System.Drawing.Size(200,20)
$chkRAG.Checked = $config.rag_system.enabled
$tabRAG.Controls.Add($chkRAG)
$y += 35

# RAG Index Dir
$lblRAGDir = New-Object System.Windows.Forms.Label
$lblRAGDir.Text = "RAG_INDEX_DIR:"
$lblRAGDir.Location = New-Object System.Drawing.Point(15,$y)
$lblRAGDir.Size = New-Object System.Drawing.Size(180,20)
$tabRAG.Controls.Add($lblRAGDir)

$txtRAGDir = New-Object System.Windows.Forms.TextBox
$txtRAGDir.Location = New-Object System.Drawing.Point(200,$y)
$txtRAGDir.Size = New-Object System.Drawing.Size(250,20)
$txtRAGDir.Text = $config.rag_system.index_dir
$tabRAG.Controls.Add($txtRAGDir)
$y += 35

# RAG Model
$lblRAGModel = New-Object System.Windows.Forms.Label
$lblRAGModel.Text = "RAG_MODEL:"
$lblRAGModel.Location = New-Object System.Drawing.Point(15,$y)
$lblRAGModel.Size = New-Object System.Drawing.Size(180,20)
$tabRAG.Controls.Add($lblRAGModel)

$cbRAGModel = New-Object System.Windows.Forms.ComboBox
$cbRAGModel.Location = New-Object System.Drawing.Point(200,$y)
$cbRAGModel.Size = New-Object System.Drawing.Size(250,20)
$cbRAGModel.Items.AddRange(@(
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
))
$cbRAGModel.Text = $config.rag_system.model
$tabRAG.Controls.Add($cbRAGModel)
$y += 50

# === TAB 4: Docker Settings ===
$tabDocker = New-Object System.Windows.Forms.TabPage
$tabDocker.Text = "Docker"
$tabControl.TabPages.Add($tabDocker)

$y = 20

# Docker Mode
$chkDocker = New-Object System.Windows.Forms.CheckBox
$chkDocker.Text = "Запуск из Docker контейнера"
$chkDocker.Location = New-Object System.Drawing.Point(15,$y)
$chkDocker.Size = New-Object System.Drawing.Size(300,20)
$chkDocker.Font = New-Object System.Drawing.Font("Segoe UI",9,[System.Drawing.FontStyle]::Bold)
$chkDocker.ForeColor = [System.Drawing.Color]::DarkBlue
$tabDocker.Controls.Add($chkDocker)
$y += 35

# Docker Info
$lblDockerInfo = New-Object System.Windows.Forms.Label
$lblDockerInfo.Text = "При включении Docker режима run.py будет запущен внутри контейнера`nчерез docker-compose. Убедитесь что Docker Desktop запущен."
$lblDockerInfo.Location = New-Object System.Drawing.Point(15,$y)
$lblDockerInfo.Size = New-Object System.Drawing.Size(430,40)
$lblDockerInfo.ForeColor = [System.Drawing.Color]::Gray
$tabDocker.Controls.Add($lblDockerInfo)
$y += 50

# Container Name
$lblContainerName = New-Object System.Windows.Forms.Label
$lblContainerName.Text = "Container Name:"
$lblContainerName.Location = New-Object System.Drawing.Point(15,$y)
$lblContainerName.Size = New-Object System.Drawing.Size(180,20)
$tabDocker.Controls.Add($lblContainerName)

$txtContainerName = New-Object System.Windows.Forms.TextBox
$txtContainerName.Location = New-Object System.Drawing.Point(200,$y)
$txtContainerName.Size = New-Object System.Drawing.Size(250,20)
$txtContainerName.Text = "fastapi-foundry-docker"
$tabDocker.Controls.Add($txtContainerName)
$y += 35

# Docker Port Mapping
$lblDockerPort = New-Object System.Windows.Forms.Label
$lblDockerPort.Text = "Host Port (внешний):"
$lblDockerPort.Location = New-Object System.Drawing.Point(15,$y)
$lblDockerPort.Size = New-Object System.Drawing.Size(180,20)
$tabDocker.Controls.Add($lblDockerPort)

$txtDockerPort = New-Object System.Windows.Forms.TextBox
$txtDockerPort.Location = New-Object System.Drawing.Point(200,$y)
$txtDockerPort.Size = New-Object System.Drawing.Size(100,20)
$txtDockerPort.Text = "8000"
$tabDocker.Controls.Add($txtDockerPort)
$y += 35

# Docker Build Option
$chkDockerBuild = New-Object System.Windows.Forms.CheckBox
$chkDockerBuild.Text = "Пересобрать образ перед запуском (--build)"
$chkDockerBuild.Location = New-Object System.Drawing.Point(15,$y)
$chkDockerBuild.Size = New-Object System.Drawing.Size(350,20)
$tabDocker.Controls.Add($chkDockerBuild)

# === Buttons ===
$btnRun = New-Object System.Windows.Forms.Button
$btnRun.Location = New-Object System.Drawing.Point(250,670)
$btnRun.Size = New-Object System.Drawing.Size(100,35)
$btnRun.Text = "🚀 RUN"
$btnRun.Font = New-Object System.Drawing.Font("Segoe UI",10,[System.Drawing.FontStyle]::Bold)
$btnRun.BackColor = [System.Drawing.Color]::LightGreen
$form.Controls.Add($btnRun)

$btnClose = New-Object System.Windows.Forms.Button
$btnClose.Location = New-Object System.Drawing.Point(370,670)
$btnClose.Size = New-Object System.Drawing.Size(100,35)
$btnClose.Text = "❌ CLOSE"
$btnClose.Font = New-Object System.Drawing.Font("Segoe UI",10)
$form.Controls.Add($btnClose)

# === Event Handlers ===
$btnRun.Add_Click({
    try {
        # Валидация
        if (-not [int]::TryParse($txtPort.Text.Trim(), [ref]0)) {
            [System.Windows.Forms.MessageBox]::Show("PORT must be a number","Validation Error","OK","Warning") | Out-Null
            return
        }
        
        if ([string]::IsNullOrWhiteSpace($txtHost.Text)) {
            [System.Windows.Forms.MessageBox]::Show("HOST cannot be empty","Validation Error","OK","Warning") | Out-Null
            return
        }

        if ($chkDocker.Checked) {
            # Docker режим - запуск через docker-compose с проверками
            Write-Host "Starting FastAPI Foundry in Docker container..." -ForegroundColor Green
            Write-Host "Container: $($txtContainerName.Text)" -ForegroundColor Cyan
            Write-Host "Host Port: $($txtDockerPort.Text) -> Container Port: 8000" -ForegroundColor Cyan
            
            # Проверка Docker Desktop
            try {
                $dockerCheck = docker --version 2>$null
                if ($LASTEXITCODE -ne 0) {
                    throw "Docker не найден"
                }
            } catch {
                [System.Windows.Forms.MessageBox]::Show("Docker Desktop не запущен или не установлен.`nЗапустите Docker Desktop и повторите попытку.","Docker Error","OK","Error") | Out-Null
                return
            }
            
            # Проверка и разрешение конфликтов портов
            Write-Host "Resolving port conflicts..." -ForegroundColor Yellow
            $portResolution = if ($config.port_management.conflict_resolution) { $config.port_management.conflict_resolution } else { "kill_process" }
            
            $resolvedPort = Resolve-PortConflict -Port ([int]$txtDockerPort.Text.Trim()) -Resolution $portResolution
            $resolvedFoundryPort = Resolve-PortConflict -Port 50477 -Resolution $portResolution
            
            if ($resolvedPort -ne ([int]$txtDockerPort.Text.Trim())) {
                $txtDockerPort.Text = $resolvedPort.ToString()
                Write-Host "🔄 Порт FastAPI изменен на: $resolvedPort" -ForegroundColor Cyan
            }
            
            # Проверка образа и автоматическая сборка
            Write-Host "Checking Docker image..." -ForegroundColor Yellow
            $imageExists = docker images -q fastapi-foundry:0.2.1 2>$null
            if ([string]::IsNullOrEmpty($imageExists) -or $chkDockerBuild.Checked) {
                Write-Host "Building Docker image..." -ForegroundColor Yellow
                
                # Остановить существующий контейнер
                docker-compose down 2>$null
                
                # Собрать образ
                $buildResult = docker-compose build 2>&1
                if ($LASTEXITCODE -ne 0) {
                    [System.Windows.Forms.MessageBox]::Show("Ошибка сборки Docker образа:`n$buildResult","Build Error","OK","Error") | Out-Null
                    return
                }
                Write-Host "✅ Docker image built successfully" -ForegroundColor Green
            }
            
            # Подготовка переменных окружения для Docker
            $envVars = @()
            $envVars += "`$env:PORT='$($txtDockerPort.Text.Trim())'"
            
            if (-not [string]::IsNullOrWhiteSpace($txtApiKey.Text)) {
                $envVars += "`$env:API_KEY='$($txtApiKey.Text)'"
            }
            
            $envVars += "`$env:FOUNDRY_HOST='localhost'"
            $envVars += "`$env:FOUNDRY_PORT='50477'"
            $envVars += "`$env:RAG_ENABLED='$($chkRAG.Checked.ToString().ToLower())'"
            
            # Остановить существующий контейнер
            Write-Host "Stopping existing containers..." -ForegroundColor Yellow
            docker-compose down 2>$null
            
            # Запуск контейнера
            Write-Host "Starting Docker container..." -ForegroundColor Green
            $envString = $envVars -join "; "
            $command = "$envString; Set-Location -LiteralPath '$scriptDir'; docker-compose up -d"
            
            $args = "-NoProfile -NoExit -Command & { $command }"
            
            Start-Process -FilePath "powershell.exe" -ArgumentList $args -WorkingDirectory $scriptDir
            
            # Ждем немного для запуска контейнера
            Start-Sleep -Seconds 3
            
            # Проверяем статус контейнера
            $containerStatus = docker-compose ps -q 2>$null
            if (-not [string]::IsNullOrEmpty($containerStatus)) {
                [System.Windows.Forms.MessageBox]::Show("FastAPI Foundry Docker container started!`n`n🌐 URL: http://localhost:$($txtDockerPort.Text)`n📚 API Docs: http://localhost:$($txtDockerPort.Text)/docs`n❤️ Health: http://localhost:$($txtDockerPort.Text)/api/v1/health`n`nContainer: $($txtContainerName.Text)`n`nДля просмотра логов: docker-compose logs -f`nДля остановки: docker-compose down","Docker Success","OK","Information") | Out-Null
            } else {
                [System.Windows.Forms.MessageBox]::Show("Контейнер запущен, но статус неизвестен.`nПроверьте: docker-compose logs","Docker Warning","OK","Warning") | Out-Null
            }
            
        } else {
            # Обычный режим - прямой запуск run.py
            
            # Проверка и разрешение конфликтов портов
            Write-Host "Resolving port conflicts..." -ForegroundColor Yellow
            $portResolution = if ($config.port_management.conflict_resolution) { $config.port_management.conflict_resolution } else { "kill_process" }
            
            $resolvedPort = Resolve-PortConflict -Port ([int]$txtPort.Text.Trim()) -Resolution $portResolution
            $resolvedFoundryPort = Resolve-PortConflict -Port 50477 -Resolution $portResolution
            
            if ($resolvedPort -ne ([int]$txtPort.Text.Trim())) {
                $txtPort.Text = $resolvedPort.ToString()
                Write-Host "🔄 Порт FastAPI изменен на: $resolvedPort" -ForegroundColor Cyan
            }
            
            # Сборка environment переменных
            $envVars = @()
            $envVars += "`$env:FASTAPI_FOUNDRY_MODE='$($cbMode.Text)'"
            $envVars += "`$env:HOST='$($txtHost.Text.Trim())'"
            $envVars += "`$env:PORT='$($txtPort.Text.Trim())'"
            
            if (-not [string]::IsNullOrWhiteSpace($txtApiKey.Text)) {
                $envVars += "`$env:API_KEY='$($txtApiKey.Text)'"
            }
            
            $envVars += "`$env:API_WORKERS='$($numWorkers.Value)'"
            $envVars += "`$env:API_RELOAD='$($chkReload.Checked.ToString().ToLower())'"
            $envVars += "`$env:LOG_LEVEL='$($cbLogLevel.Text)'"
            
            $envVars += "`$env:FOUNDRY_BASE_URL='$($txtFoundryUrl.Text.Trim())'"
            $envVars += "`$env:FOUNDRY_DEFAULT_MODEL='$($txtModel.Text.Trim())'"
            $envVars += "`$env:FOUNDRY_TEMPERATURE='$($numTemp.Value)'"
            $envVars += "`$env:FOUNDRY_TOP_P='$($numTopP.Value)'"
            $envVars += "`$env:FOUNDRY_TOP_K='$($numTopK.Value)'"
            $envVars += "`$env:FOUNDRY_MAX_TOKENS='$($numMaxTokens.Value)'"
            $envVars += "`$env:FOUNDRY_TIMEOUT='$($numTimeout.Value)'"
            
            $envVars += "`$env:RAG_ENABLED='$($chkRAG.Checked.ToString().ToLower())'"
            $envVars += "`$env:RAG_INDEX_DIR='$($txtRAGDir.Text.Trim())'"
            $envVars += "`$env:RAG_MODEL='$($cbRAGModel.Text)'"

            # Команда запуска
            $envString = $envVars -join "; "
            $command = "$envString; Set-Location -LiteralPath '$scriptDir'; python run.py"
            
            $args = "-NoProfile -NoExit -Command & { $command }"
            
            Write-Host "Starting FastAPI Foundry with configuration:" -ForegroundColor Green
            Write-Host "FastAPI Server - Host: $($txtHost.Text) Port: $($txtPort.Text)" -ForegroundColor Cyan
            Write-Host "Foundry AI Model - URL: $($txtFoundryUrl.Text)" -ForegroundColor Yellow
            Write-Host "Mode: $($cbMode.Text)" -ForegroundColor Cyan
            
            Start-Process -FilePath "powershell.exe" -ArgumentList $args -WorkingDirectory $scriptDir
            
            [System.Windows.Forms.MessageBox]::Show("FastAPI Foundry started successfully!","Success","OK","Information") | Out-Null
        }
        
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Failed to start: $_","Error","OK","Error") | Out-Null
    }
})

$btnClose.Add_Click({
    $form.Close()
})

# Показать форму
[void] $form.ShowDialog()