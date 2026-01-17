# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Microsoft Foundry Installer
# =============================================================================
# Описание:
#   Простой установщик Microsoft Foundry для Windows
#   Скачивает и устанавливает последнюю версию
#
# File: install-foundry.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

Write-Host "🚀 Microsoft Foundry Installer" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Проверяем права администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️ Для установки Foundry нужны права администратора" -ForegroundColor Yellow
    Write-Host "💡 Перезапустите PowerShell от имени администратора" -ForegroundColor Cyan
    
    $restart = Read-Host "Перезапустить с правами администратора? (y/N)"
    if ($restart -eq 'y' -or $restart -eq 'Y') {
        Start-Process powershell -Verb RunAs -ArgumentList "-File `"$PSCommandPath`""
        exit 0
    } else {
        Write-Host "❌ Установка отменена" -ForegroundColor Red
        exit 1
    }
}

# Проверяем существующую установку
if ((Get-Command foundry -ErrorAction SilentlyContinue) -and -not $Force) {
    Write-Host "✅ Foundry уже установлен" -ForegroundColor Green
    & foundry --version
    
    $reinstall = Read-Host "Переустановить? (y/N)"
    if ($reinstall -ne 'y' -and $reinstall -ne 'Y') {
        Write-Host "✅ Установка пропущена" -ForegroundColor Green
        exit 0
    }
}

try {
    Write-Host "📥 Скачивание Microsoft Foundry..." -ForegroundColor Yellow
    
    # Определяем архитектуру
    $arch = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
    Write-Host "🔍 Архитектура: $arch" -ForegroundColor Gray
    
    # URL для скачивания (примерный - нужно обновить на актуальный)
    $downloadUrl = "https://github.com/microsoft/foundry/releases/latest/download/foundry-windows-$arch.zip"
    $tempDir = "$env:TEMP\foundry-installer"
    $zipFile = "$tempDir\foundry.zip"
    $extractDir = "$tempDir\foundry"
    
    # Создаем временную директорию
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    Write-Host "🌐 Скачивание с: $downloadUrl" -ForegroundColor Gray
    
    # Скачиваем файл
    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
        Write-Host "✅ Скачивание завершено" -ForegroundColor Green
    } catch {
        Write-Host "❌ Ошибка скачивания: $_" -ForegroundColor Red
        Write-Host "💡 Попробуйте скачать вручную:" -ForegroundColor Cyan
        Write-Host "   https://github.com/microsoft/foundry/releases" -ForegroundColor Gray
        exit 1
    }
    
    # Распаковываем архив
    Write-Host "📦 Распаковка архива..." -ForegroundColor Yellow
    Expand-Archive -Path $zipFile -DestinationPath $extractDir -Force
    
    # Находим исполняемый файл
    $foundryExe = Get-ChildItem -Path $extractDir -Name "foundry.exe" -Recurse | Select-Object -First 1
    if (-not $foundryExe) {
        Write-Host "❌ foundry.exe не найден в архиве" -ForegroundColor Red
        exit 1
    }
    
    $foundryPath = Join-Path $extractDir $foundryExe
    Write-Host "✅ Найден: $foundryPath" -ForegroundColor Green
    
    # Устанавливаем в Program Files
    $installDir = "$env:ProgramFiles\Microsoft Foundry"
    Write-Host "📁 Установка в: $installDir" -ForegroundColor Yellow
    
    if (Test-Path $installDir) {
        Remove-Item $installDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    
    # Копируем файлы
    Copy-Item -Path "$extractDir\*" -Destination $installDir -Recurse -Force
    
    # Добавляем в PATH
    Write-Host "🔗 Добавление в PATH..." -ForegroundColor Yellow
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    
    if ($currentPath -notlike "*$installDir*") {
        $newPath = "$currentPath;$installDir"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "Machine")
        Write-Host "✅ PATH обновлен" -ForegroundColor Green
    } else {
        Write-Host "✅ PATH уже содержит Foundry" -ForegroundColor Green
    }
    
    # Обновляем PATH в текущей сессии
    $env:PATH = "$env:PATH;$installDir"
    
    # Проверяем установку
    Write-Host "🧪 Проверка установки..." -ForegroundColor Yellow
    Start-Sleep 2
    
    try {
        $version = & "$installDir\foundry.exe" --version 2>&1
        Write-Host "✅ Foundry успешно установлен!" -ForegroundColor Green
        Write-Host "📋 Версия: $version" -ForegroundColor Gray
    } catch {
        Write-Host "⚠️ Установка завершена, но проверка не удалась: $_" -ForegroundColor Yellow
        Write-Host "💡 Перезапустите PowerShell и попробуйте: foundry --version" -ForegroundColor Cyan
    }
    
    # Очистка временных файлов
    Write-Host "🧹 Очистка временных файлов..." -ForegroundColor Gray
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "" -ForegroundColor Green
    Write-Host "🎉 Установка Microsoft Foundry завершена!" -ForegroundColor Green
    Write-Host "💡 Перезапустите PowerShell для применения изменений PATH" -ForegroundColor Cyan
    Write-Host "🚀 Затем запустите: .\start.ps1" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Ошибка установки: $_" -ForegroundColor Red
    Write-Host "💡 Попробуйте установить вручную:" -ForegroundColor Cyan
    Write-Host "   https://github.com/microsoft/foundry/releases" -ForegroundColor Gray
    exit 1
}