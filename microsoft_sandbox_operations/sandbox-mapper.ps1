# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Синхронизация проекта с директорией песочницы (Sandbox)
# =============================================================================
# Описание:
#   Зеркалирование исходного кода проекта в целевую директорию песочницы.
#   Использование утилиты robocopy для обеспечения высокой скорости и
#   надежности передачи данных с автоматическим исключением виртуальных
#   окружений, кешей и артефактов сборки.
 #
# Примеры:
#   powershell -ExecutionPolicy Bypass -File .\sandbox-mapper.ps1
#   powershell -ExecutionPolicy Bypass -File .\sandbox-mapper.ps1 -Source D:\repos\public_repositories\FastApiFoundry-Docker -Target D:\FastApiFoundry-Docker-Sandbox
#
# File: sandbox-mapper.ps1
# Project: FastApiFoundry (Docker)
# Version: 0.4.2
# Автор: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

# --- Параметры запуска ---
# Источник и целевая директория задаются как параметры скрипта.
param (
    [Parameter(Mandatory=$false)]
    [string]$Source = 'D:\repos\public_repositories\FastApiFoundry-Docker', # Путь к исходному коду

    [Parameter(Mandatory=$false)]
    [string]$Target = 'D:\FastApiFoundry-Docker-Sandbox' # Путь к директории песочницы
)

# --- Глобальная политика обработки ошибок ---
$ErrorActionPreference = 'Stop'

<#
.SYNOPSIS
    Зеркалирование исходной директории в целевую папку через robocopy.

.DESCRIPTION
    Выполнение полной синхронизации структуры каталогов.
    Использование режима /MIR позволяет поддерживать целевую директорию
    в идентичном состоянии с источником, включая удаление лишних файлов.

.PARAMETER Source
    [string] Путь к исходной директории проекта на хосте.

.PARAMETER Target
    [string] Путь к целевой директории для монтирования песочницы.

.RETURNS
    [bool] — True при успешном зеркалировании, False при системном сбое.
#>
[OutputType([bool])]
function Sync-Project {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Source, # Исходный путь

        [Parameter(Mandatory=$true)]
        [string]$Target  # Целевой путь
    )

    # Объявление локальных переменных
    [int]$code = 0

    try {
        # Использование Robocopy для эффективного зеркалирования ФС.
        # /MIR - Режим зеркала.
        # /XD, /XF - Исключение мусора (кеши, git, venv).
        # /R:1 /W:1 - Ограничение ожидания при занятых файлах.
        # /NFL /NDL /NJH /NJS - Скрытие подробностей вывода для чистоты логов.
        
        robocopy $Source $Target `
            /MIR `
            /XD venv .git __pycache__ node_modules .mypy_cache .pytest_cache `
            /XF *.pyc *.pyo *.log `
            /R:1 /W:1 `
            /NFL /NDL /NJH /NJS
            
        # Извлечение кода завершения процесса
        $code = $LASTEXITCODE

        # Обработка специфичных кодов завершения robocopy: 0-7 считаются успехом
        if ($code -lt 8) {
            return $true
        }
        
        Write-Host "❌ Sync-Project: Критическая ошибка Robocopy. Код: $code" -ForegroundColor Red
        return $false
    }
    catch {
        Write-Host "⚠️ Sync-Project: Системное исключение: $_" -ForegroundColor Yellow
        return $false
    }
}


# --- main ---

# Информирование о начале процесса
Write-Host '🔄 Запуск синхронизации проекта...' -ForegroundColor Cyan

# Вызов функции синхронизации
$result = Sync-Project -Source $Source -Target $Target

# Вывод финального статуса
if ($result) {
    Write-Host '✅ Синхронизация успешно завершена' -ForegroundColor Green
} else {
    Write-Host '❌ Ошибка синхронизации' -ForegroundColor Red
}