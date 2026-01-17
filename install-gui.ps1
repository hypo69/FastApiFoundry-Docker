# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry GUI Installer
# =============================================================================
# Описание:
#   Windows Forms GUI для установки FastAPI Foundry и зависимостей
#   Объединяет все установщики в одном интерфейсе
#
# File: install-gui.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Root = $PSScriptRoot

# Создаем главную форму
$form = New-Object System.Windows.Forms.Form
$form.Text = "FastAPI Foundry - Установщик"
$form.Size = New-Object System.Drawing.Size(500, 400)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

# Заголовок
$titleLabel = New-Object System.Windows.Forms.Label
$titleLabel.Text = "🚀 FastAPI Foundry Installer"
$titleLabel.Font = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
$titleLabel.Location = New-Object System.Drawing.Point(20, 20)
$titleLabel.Size = New-Object System.Drawing.Size(450, 30)
$titleLabel.TextAlign = "MiddleCenter"
$form.Controls.Add($titleLabel)

# Описание
$descLabel = New-Object System.Windows.Forms.Label
$descLabel.Text = "Выберите компоненты для установки:"
$descLabel.Location = New-Object System.Drawing.Point(20, 60)
$descLabel.Size = New-Object System.Drawing.Size(450, 20)
$form.Controls.Add($descLabel)

# Чекбоксы для компонентов
$pythonCheck = New-Object System.Windows.Forms.CheckBox
$pythonCheck.Text = "🐍 Python зависимости (venv + packages)"
$pythonCheck.Location = New-Object System.Drawing.Point(30, 90)
$pythonCheck.Size = New-Object System.Drawing.Size(400, 25)
$pythonCheck.Checked = $true
$form.Controls.Add($pythonCheck)

$foundryCheck = New-Object System.Windows.Forms.CheckBox
$foundryCheck.Text = "🤖 Microsoft Foundry (AI модели)"
$foundryCheck.Location = New-Object System.Drawing.Point(30, 120)
$foundryCheck.Size = New-Object System.Drawing.Size(400, 25)
$foundryCheck.Checked = $false
$form.Controls.Add($foundryCheck)

$ragCheck = New-Object System.Windows.Forms.CheckBox
$ragCheck.Text = "🔍 RAG система (дополнительные зависимости)"
$ragCheck.Location = New-Object System.Drawing.Point(30, 150)
$ragCheck.Size = New-Object System.Drawing.Size(400, 25)
$ragCheck.Checked = $false
$form.Controls.Add($ragCheck)

$envCheck = New-Object System.Windows.Forms.CheckBox
$envCheck.Text = "⚙️ Настройка переменных окружения (.env)"
$envCheck.Location = New-Object System.Drawing.Point(30, 180)
$envCheck.Size = New-Object System.Drawing.Size(400, 25)
$envCheck.Checked = $false
$form.Controls.Add($envCheck)

# Прогресс бар
$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(20, 220)
$progressBar.Size = New-Object System.Drawing.Size(450, 25)
$progressBar.Style = "Continuous"
$form.Controls.Add($progressBar)

# Лог текстбокс
$logBox = New-Object System.Windows.Forms.TextBox
$logBox.Location = New-Object System.Drawing.Point(20, 255)
$logBox.Size = New-Object System.Drawing.Size(450, 80)
$logBox.Multiline = $true
$logBox.ScrollBars = "Vertical"
$logBox.ReadOnly = $true
$logBox.Text = "Готов к установке..."
$form.Controls.Add($logBox)

# Кнопки
$installButton = New-Object System.Windows.Forms.Button
$installButton.Text = "🚀 Установить"
$installButton.Location = New-Object System.Drawing.Point(280, 345)
$installButton.Size = New-Object System.Drawing.Size(90, 30)
$form.Controls.Add($installButton)

$cancelButton = New-Object System.Windows.Forms.Button
$cancelButton.Text = "❌ Отмена"
$cancelButton.Location = New-Object System.Drawing.Point(380, 345)
$cancelButton.Size = New-Object System.Drawing.Size(90, 30)
$form.Controls.Add($cancelButton)

# Функция логирования
function Write-Log {
    param([string]$Message)
    $logBox.AppendText("$Message`r`n")
    $logBox.SelectionStart = $logBox.Text.Length
    $logBox.ScrollToCaret()
    $form.Refresh()
}

# Функция обновления прогресса
function Update-Progress {
    param([int]$Value)
    $progressBar.Value = $Value
    $form.Refresh()
}

# Обработчик кнопки установки
$installButton.Add_Click({
    $installButton.Enabled = $false
    $cancelButton.Text = "Закрыть"
    
    try {
        $totalSteps = 0
        if ($pythonCheck.Checked) { $totalSteps++ }
        if ($foundryCheck.Checked) { $totalSteps++ }
        if ($ragCheck.Checked) { $totalSteps++ }
        if ($envCheck.Checked) { $totalSteps++ }
        
        if ($totalSteps -eq 0) {
            Write-Log "❌ Не выбрано ни одного компонента"
            $installButton.Enabled = $true
            return
        }
        
        $currentStep = 0
        
        # Установка Python зависимостей
        if ($pythonCheck.Checked) {
            Write-Log "🐍 Установка Python зависимостей..."
            Update-Progress ([int](($currentStep / $totalSteps) * 100))
            
            if (Test-Path "$Root\install.ps1") {
                try {
                    & "$Root\install.ps1" *>&1 | ForEach-Object { Write-Log $_ }
                    Write-Log "✅ Python зависимости установлены"
                } catch {
                    Write-Log "❌ Ошибка установки Python: $_"
                }
            } else {
                Write-Log "❌ install.ps1 не найден"
            }
            $currentStep++
        }
        
        # Установка Foundry
        if ($foundryCheck.Checked) {
            Write-Log "🤖 Установка Microsoft Foundry..."
            Update-Progress ([int](($currentStep / $totalSteps) * 100))
            
            if (Test-Path "$Root\install-foundry.ps1") {
                try {
                    & "$Root\install-foundry.ps1" *>&1 | ForEach-Object { Write-Log $_ }
                    Write-Log "✅ Foundry установлен"
                } catch {
                    Write-Log "❌ Ошибка установки Foundry: $_"
                }
            } else {
                Write-Log "❌ install-foundry.ps1 не найден"
            }
            $currentStep++
        }
        
        # Установка RAG зависимостей
        if ($ragCheck.Checked) {
            Write-Log "🔍 Установка RAG зависимостей..."
            Update-Progress ([int](($currentStep / $totalSteps) * 100))
            
            $pythonExe = "$Root\venv\Scripts\python.exe"
            if (Test-Path $pythonExe) {
                try {
                    & $pythonExe "$Root\install_rag_deps.py" *>&1 | ForEach-Object { Write-Log $_ }
                    Write-Log "✅ RAG зависимости установлены"
                } catch {
                    Write-Log "❌ Ошибка установки RAG: $_"
                }
            } else {
                Write-Log "❌ Python venv не найден"
            }
            $currentStep++
        }
        
        # Настройка переменных окружения
        if ($envCheck.Checked) {
            Write-Log "⚙️ Настройка переменных окружения..."
            Update-Progress ([int](($currentStep / $totalSteps) * 100))
            
            if (Test-Path "$Root\setup-env.ps1") {
                try {
                    & "$Root\setup-env.ps1" -Force *>&1 | ForEach-Object { Write-Log $_ }
                    Write-Log "✅ Переменные окружения настроены"
                } catch {
                    Write-Log "❌ Ошибка настройки .env: $_"
                }
            } else {
                Write-Log "❌ setup-env.ps1 не найден"
            }
            $currentStep++
        }
        
        Update-Progress 100
        Write-Log ""
        Write-Log "🎉 Установка завершена!"
        Write-Log "💡 Теперь можете запустить: python311 run.py"
        
    } catch {
        Write-Log "❌ Критическая ошибка: $_"
    } finally {
        $installButton.Enabled = $true
    }
})

# Обработчик кнопки отмены
$cancelButton.Add_Click({
    $form.Close()
})

# Проверяем что уже установлено
if (Test-Path "$Root\venv\Scripts\python.exe") {
    $pythonCheck.Text += " ✅"
    $pythonCheck.Checked = $false
}

try {
    Get-Command foundry -ErrorAction Stop | Out-Null
    $foundryCheck.Text += " ✅"
    $foundryCheck.Checked = $false
} catch {
    # Foundry не установлен
}

if (Test-Path "$Root\.env") {
    $envCheck.Text += " ✅"
    $envCheck.Checked = $false
}

# Показываем форму
$form.ShowDialog() | Out-Null