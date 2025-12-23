# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: GUI лончер для FastAPI Foundry
# =============================================================================
# Описание:
#   Графический интерфейс для запуска run.py с полным набором параметров
#   Поддерживает все environment переменные и аргументы командной строки
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

# Создание формы
$form = New-Object System.Windows.Forms.Form
$form.Text = "FastAPI Foundry — Launch Configuration"
$form.Size = New-Object System.Drawing.Size(520,680)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

# Создание TabControl
$tabControl = New-Object System.Windows.Forms.TabControl
$tabControl.Location = New-Object System.Drawing.Point(10,10)
$tabControl.Size = New-Object System.Drawing.Size(480,580)
$form.Controls.Add($tabControl)

# === TAB 1: FastAPI Server ===
$tabServer = New-Object System.Windows.Forms.TabPage
$tabServer.Text = "FastAPI Server"
$tabControl.TabPages.Add($tabServer)

$y = 20

# Заголовок секции
$lblServerHeader = New-Object System.Windows.Forms.Label
$lblServerHeader.Text = "FastAPI Server Configuration (Port 8000)"
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
$cbMode.SelectedIndex = 0
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
$txtHost.Text = "0.0.0.0"
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
$txtPort.Text = "8000"
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
$numWorkers.Value = 1
$tabServer.Controls.Add($numWorkers)
$y += 35

# Reload
$chkReload = New-Object System.Windows.Forms.CheckBox
$chkReload.Text = "API_RELOAD (dev mode)"
$chkReload.Location = New-Object System.Drawing.Point(15,$y)
$chkReload.Size = New-Object System.Drawing.Size(200,20)
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
$cbLogLevel.SelectedIndex = 1
$tabServer.Controls.Add($cbLogLevel)

# === TAB 2: Foundry AI Model ===
$tabFoundry = New-Object System.Windows.Forms.TabPage
$tabFoundry.Text = "Foundry AI Model"
$tabControl.TabPages.Add($tabFoundry)

$y = 20

# Заголовок секции
$lblFoundryHeader = New-Object System.Windows.Forms.Label
$lblFoundryHeader.Text = "Foundry AI Model Configuration (Port 50477)"
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
$txtFoundryUrl.Text = "http://localhost:50477/v1/"
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
$txtModel.Text = "deepseek-r1-distill-qwen-7b-generic-cpu:3"
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
$numTemp.Value = 0.6
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
$numTopP.Value = 0.9
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
$numTopK.Value = 40
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
$numMaxTokens.Value = 2048
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
$numTimeout.Value = 300
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
$chkRAG.Checked = $true
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
$txtRAGDir.Text = "./rag_index"
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
$cbRAGModel.SelectedIndex = 0
$tabRAG.Controls.Add($cbRAGModel)

# === Buttons ===
$btnRun = New-Object System.Windows.Forms.Button
$btnRun.Location = New-Object System.Drawing.Point(250,600)
$btnRun.Size = New-Object System.Drawing.Size(100,35)
$btnRun.Text = "🚀 RUN"
$btnRun.Font = New-Object System.Drawing.Font("Segoe UI",10,[System.Drawing.FontStyle]::Bold)
$btnRun.BackColor = [System.Drawing.Color]::LightGreen
$form.Controls.Add($btnRun)

$btnClose = New-Object System.Windows.Forms.Button
$btnClose.Location = New-Object System.Drawing.Point(370,600)
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
        
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Failed to start: $_","Error","OK","Error") | Out-Null
    }
})

$btnClose.Add_Click({
    $form.Close()
})

# Показать форму
[void] $form.ShowDialog()