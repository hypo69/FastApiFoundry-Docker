# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry GUI Installer
# =============================================================================
# Описание:
#   Windows Forms GUI для установки FastAPI Foundry.
#   Вызывает install.ps1 и install-foundry.ps1.
#
# File: install-gui.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Root = $PSScriptRoot

$form = New-Object System.Windows.Forms.Form
$form.Text = "FastAPI Foundry - Installer"
$form.Size = New-Object System.Drawing.Size(520, 420)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

# Заголовок
$title = New-Object System.Windows.Forms.Label
$title.Text = "FastAPI Foundry Installer"
$title.Font = New-Object System.Drawing.Font("Segoe UI", 13, [System.Drawing.FontStyle]::Bold)
$title.Location = New-Object System.Drawing.Point(20, 15)
$title.Size = New-Object System.Drawing.Size(470, 28)
$title.TextAlign = "MiddleCenter"
$form.Controls.Add($title)

$subtitle = New-Object System.Windows.Forms.Label
$subtitle.Text = "Выберите компоненты для установки:"
$subtitle.Location = New-Object System.Drawing.Point(20, 50)
$subtitle.Size = New-Object System.Drawing.Size(470, 20)
$form.Controls.Add($subtitle)

# Чекбоксы
$chkPython = New-Object System.Windows.Forms.CheckBox
$chkPython.Text = "Python venv + зависимости (обязательно)"
$chkPython.Location = New-Object System.Drawing.Point(30, 80)
$chkPython.Size = New-Object System.Drawing.Size(440, 24)
$chkPython.Checked = $true
$form.Controls.Add($chkPython)

$chkRag = New-Object System.Windows.Forms.CheckBox
$chkRag.Text = "RAG зависимости (torch, sentence-transformers, faiss-cpu) ~2 GB"
$chkRag.Location = New-Object System.Drawing.Point(30, 110)
$chkRag.Size = New-Object System.Drawing.Size(440, 24)
$chkRag.Checked = $false
$form.Controls.Add($chkRag)

$chkFoundry = New-Object System.Windows.Forms.CheckBox
$chkFoundry.Text = "Microsoft Foundry Local (AI бэкенд, через winget)"
$chkFoundry.Location = New-Object System.Drawing.Point(30, 140)
$chkFoundry.Size = New-Object System.Drawing.Size(440, 24)
$chkFoundry.Checked = $false
$form.Controls.Add($chkFoundry)

# Разделитель
$sep = New-Object System.Windows.Forms.Label
$sep.BorderStyle = "Fixed3D"
$sep.Location = New-Object System.Drawing.Point(20, 175)
$sep.Size = New-Object System.Drawing.Size(470, 2)
$form.Controls.Add($sep)

# Прогресс
$progress = New-Object System.Windows.Forms.ProgressBar
$progress.Location = New-Object System.Drawing.Point(20, 185)
$progress.Size = New-Object System.Drawing.Size(470, 22)
$form.Controls.Add($progress)

# Лог
$log = New-Object System.Windows.Forms.TextBox
$log.Location = New-Object System.Drawing.Point(20, 215)
$log.Size = New-Object System.Drawing.Size(470, 130)
$log.Multiline = $true
$log.ScrollBars = "Vertical"
$log.ReadOnly = $true
$log.Font = New-Object System.Drawing.Font("Consolas", 9)
$log.Text = "Готов к установке..."
$form.Controls.Add($log)

# Кнопки
$btnInstall = New-Object System.Windows.Forms.Button
$btnInstall.Text = "Установить"
$btnInstall.Location = New-Object System.Drawing.Point(300, 355)
$btnInstall.Size = New-Object System.Drawing.Size(90, 28)
$form.Controls.Add($btnInstall)

$btnClose = New-Object System.Windows.Forms.Button
$btnClose.Text = "Закрыть"
$btnClose.Location = New-Object System.Drawing.Point(400, 355)
$btnClose.Size = New-Object System.Drawing.Size(90, 28)
$form.Controls.Add($btnClose)

function Write-Log([string]$msg) {
    $log.AppendText("$msg`r`n")
    $log.SelectionStart = $log.Text.Length
    $log.ScrollToCaret()
    $form.Refresh()
}

function Set-Progress([int]$val) {
    $progress.Value = [Math]::Min($val, 100)
    $form.Refresh()
}

$btnInstall.Add_Click({
    $btnInstall.Enabled = $false
    $log.Clear()

    $steps = @()
    if ($chkPython.Checked)  { $steps += "python" }
    if ($chkRag.Checked)     { $steps += "rag" }
    if ($chkFoundry.Checked) { $steps += "foundry" }

    if ($steps.Count -eq 0) {
        Write-Log "Не выбрано ни одного компонента."
        $btnInstall.Enabled = $true
        return
    }

    $i = 0
    foreach ($step in $steps) {
        Set-Progress ([int](($i / $steps.Count) * 90))

        switch ($step) {
            "python" {
                Write-Log "--- Python venv + зависимости ---"
                $script = Join-Path $Root "install.ps1"
                if (Test-Path $script) {
                    try {
                        $out = & powershell -NoProfile -ExecutionPolicy Bypass -File $script 2>&1
                        $out | ForEach-Object { Write-Log $_ }
                    } catch { Write-Log "Ошибка: $_" }
                } else { Write-Log "install.ps1 не найден" }
            }
            "rag" {
                Write-Log "--- RAG зависимости ---"
                $py = Join-Path $Root "venv\Scripts\python.exe"
                $script = Join-Path $Root "install_rag_deps.py"
                if ((Test-Path $py) -and (Test-Path $script)) {
                    try {
                        $out = & $py $script 2>&1
                        $out | ForEach-Object { Write-Log $_ }
                    } catch { Write-Log "Ошибка: $_" }
                } else { Write-Log "Сначала установите Python venv" }
            }
            "foundry" {
                Write-Log "--- Microsoft Foundry Local ---"
                $script = Join-Path $Root "install-foundry.ps1"
                if (Test-Path $script) {
                    try {
                        $out = & powershell -NoProfile -ExecutionPolicy Bypass -File $script 2>&1
                        $out | ForEach-Object { Write-Log $_ }
                    } catch { Write-Log "Ошибка: $_" }
                } else { Write-Log "install-foundry.ps1 не найден" }
            }
        }
        $i++
    }

    Set-Progress 100
    Write-Log ""
    Write-Log "Готово! Запустите: venv\Scripts\python.exe run.py"
    $btnInstall.Enabled = $true
})

$btnClose.Add_Click({ $form.Close() })

# Отметить уже установленное
if (Test-Path (Join-Path $Root "venv\Scripts\python.exe")) {
    $chkPython.Text += " [уже установлено]"
    $chkPython.Checked = $false
}
if (Get-Command foundry -ErrorAction SilentlyContinue) {
    $chkFoundry.Text += " [уже установлено]"
    $chkFoundry.Checked = $false
}

$form.ShowDialog() | Out-Null
