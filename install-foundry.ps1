# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Microsoft Foundry Local - Установщик
# =============================================================================
# Описание:
#   Устанавливает Microsoft Foundry Local CLI через winget.
#   После установки запускает сервис и предлагает скачать модель.
#
# Использование:
#   .\install-foundry.ps1
#   .\install-foundry.ps1 -Model "qwen2.5-0.5b-instruct-generic-cpu"
#
# File: install-foundry.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

param(
    [string]$Model = "qwen2.5-0.5b-instruct-generic-cpu"
)

$ErrorActionPreference = "Stop"

Write-Host "Microsoft Foundry Local - Installer" -ForegroundColor Cyan
Write-Host ("=" * 50)

# --- Проверка winget ---
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget не найден." -ForegroundColor Red
    Write-Host "Установите App Installer из Microsoft Store:" -ForegroundColor Cyan
    Write-Host "  https://apps.microsoft.com/detail/9NBLGGH4NNS1" -ForegroundColor Gray
    exit 1
}

# --- Проверка существующей установки ---
if (Get-Command foundry -ErrorAction SilentlyContinue) {
    $ver = & foundry --version 2>&1
    Write-Host "Foundry уже установлен: $ver" -ForegroundColor Green
} else {
    # --- Установка через winget ---
    Write-Host "`nУстановка Microsoft Foundry Local..." -ForegroundColor Yellow
    try {
        winget install Microsoft.FoundryLocal --accept-source-agreements --accept-package-agreements
        Write-Host "Foundry Local установлен" -ForegroundColor Green
    } catch {
        Write-Host "Ошибка установки через winget: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Установите вручную:" -ForegroundColor Cyan
        Write-Host "  winget install Microsoft.FoundryLocal" -ForegroundColor Gray
        Write-Host "  или скачайте с: https://aka.ms/foundry-local" -ForegroundColor Gray
        exit 1
    }

    # Обновляем PATH в текущей сессии
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

# --- Запуск сервиса ---
Write-Host "`nЗапуск Foundry сервиса..." -ForegroundColor Yellow
try {
    & foundry service start
    Start-Sleep 3
    Write-Host "Сервис запущен" -ForegroundColor Green
} catch {
    Write-Host "Не удалось запустить сервис: $_" -ForegroundColor Yellow
    Write-Host "Запустите вручную: foundry service start" -ForegroundColor Cyan
}

# --- Скачивание модели ---
Write-Host "`nСкачивание модели: $Model" -ForegroundColor Yellow
Write-Host "Это может занять несколько минут..." -ForegroundColor Gray
try {
    & foundry model download $Model
    Write-Host "Модель скачана: $Model" -ForegroundColor Green
} catch {
    Write-Host "Не удалось скачать модель: $_" -ForegroundColor Yellow
    Write-Host "Скачайте вручную: foundry model download $Model" -ForegroundColor Cyan
}

# --- Проверка ---
Write-Host "`nПроверка API..." -ForegroundColor Yellow
Start-Sleep 2
try {
    $response = Invoke-RestMethod "http://localhost:50477/v1/models" -TimeoutSec 5
    Write-Host "Foundry API доступен на порту 50477" -ForegroundColor Green
    Write-Host "Моделей загружено: $($response.data.Count)" -ForegroundColor Gray
} catch {
    Write-Host "API пока недоступен — Foundry может использовать другой порт." -ForegroundColor Yellow
    Write-Host "Сервер найдёт его автоматически при запуске." -ForegroundColor Cyan
}

Write-Host "`n$("=" * 50)" -ForegroundColor Green
Write-Host "Foundry Local готов к работе!" -ForegroundColor Green
Write-Host ""
Write-Host "Запустите FastAPI сервер:"
Write-Host "  venv\Scripts\python.exe run.py"
