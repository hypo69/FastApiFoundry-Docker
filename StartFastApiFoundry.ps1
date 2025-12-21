# -*- coding: utf-8 -*-
# FastAPI Foundry Starter Script
# ============================================================================
# Запуск приложения FastAPI Foundry с проверкой всех зависимостей
# Активирует venv и запускает run.py с параметрами
# ============================================================================

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

# Цвета для вывода
$colors = @{
    'Success' = 'Green'
    'Error'   = 'Red'
    'Warning' = 'Yellow'
    'Info'    = 'Cyan'
    'Highlight' = 'Magenta'
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Type = 'Info'
    )
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = if ($colors.ContainsKey($Type)) { $colors[$Type] } else { 'White' }
    Write-Host "[$timestamp] " -ForegroundColor Gray -NoNewline
    Write-Host $Message -ForegroundColor $color
}

function Show-Quick-Help {
    Write-Host ""
    Write-Host "🚀 FastAPI Foundry - Launcher" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Использование:" -ForegroundColor Cyan
    Write-Host "  .\StartFastApiFoundry.ps1 [аргументы]" -ForegroundColor White
    Write-Host ""
    Write-Host "Самые популярные команды:" -ForegroundColor Green
    Write-Host "  .\StartFastApiFoundry.ps1 --dev --ssl --mcp --auto-port --browser" -ForegroundColor Green
    Write-Host "  .\StartFastApiFoundry.ps1 --prod --ssl --mcp --auto-port" -ForegroundColor White
    Write-Host "  .\StartFastApiFoundry.ps1 --help                                 # Все параметры" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Документация: START_HERE.md, VENV_SETUP.md" -ForegroundColor Yellow
    Write-Host ""
}

# Показать быструю справку если нет аргументов
if ($Args.Count -eq 0) {
    Show-Quick-Help
    exit 0
}

# Очистка консоли и заголовок
Clear-Host
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║                   🚀 FastAPI Foundry Launcher 🚀                      ║" -ForegroundColor Magenta
Write-Host "║                                                                        ║" -ForegroundColor Magenta
Write-Host "║  REST API для локальных AI моделей через Foundry с RAG поддержкой   ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

Write-Log "Запуск приложения..." "Highlight"
Write-Log "Текущая директория: $(Get-Location)" "Info"
Write-Log ""

# ============================================================================
# 1. ПРОВЕРКА run.py
# ============================================================================
Write-Log "📋 Проверка файлов..." "Info"

if (-not (Test-Path "run.py")) {
    Write-Log "❌ run.py не найден!" "Error"
    Write-Log "Пожалуйста, запустите скрипт из директории FastApiFoundry" "Warning"
    exit 1
}
Write-Log "✅ run.py найден" "Success"

# ============================================================================
# 2. ПРОВЕРКА VENV И АВТОМАТИЧЕСКАЯ УСТАНОВКА
# ============================================================================
Write-Log ""
Write-Log "🐍 Проверка виртуальной окружения..." "Info"

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Log "❌ Виртуальная окружение не найдена!" "Warning"
    Write-Log ""
    Write-Log "📦 Необходимо установить зависимости..." "Info"
    Write-Log ""

    if (Test-Path "install.ps1") {
        Write-Log "🔧 Запуск автоматической установки..." "Info"
        Write-Log ""

        # Запускаем install.ps1
        & .\install.ps1

        if ($LASTEXITCODE -ne 0) {
            Write-Log "❌ Ошибка при установке зависимостей!" "Error"
            Write-Log "Пожалуйста, проверьте логи выше" "Warning"
            exit 1
        }

        Write-Log ""
        Write-Log "✅ Установка завершена успешно!" "Success"
        Write-Log ""
        Write-Log "Продолжаем запуск приложения..." "Info"
    } else {
        Write-Log "❌ Файл install.ps1 не найден!" "Error"
        Write-Log "Создайте venv вручную командой:" "Warning"
        Write-Log "  python -m venv venv" "Info"
        Write-Log ""
        Write-Log "Затем установите зависимости:" "Warning"
        Write-Log "  .\\venv\\Scripts\\Activate.ps1" "Info"
        Write-Log "  pip install -r requirements.txt" "Info"
        exit 1
    }
} else {
    Write-Log "✅ venv найдена" "Success"
}

# ============================================================================
# 3. АКТИВАЦИЯ VENV
# ============================================================================
Write-Log ""
Write-Log "📦 Активация виртуальной окружения..." "Info"

try {
    & .\venv\Scripts\Activate.ps1
    Write-Log "✅ venv активирована" "Success"
} catch {
    Write-Log "❌ Ошибка при активации venv!" "Error"
    Write-Log $_.Exception.Message "Error"
    exit 1
}

# ============================================================================
# 4. ПРОВЕРКА PYTHON В VENV
# ============================================================================
Write-Log ""
Write-Log "🔍 Проверка Python в venv..." "Info"

try {
    $pythonVersion = python --version 2>&1
    Write-Log "✅ $pythonVersion найден" "Success"
} catch {
    Write-Log "❌ Python не найден в venv!" "Error"
    exit 1
}

# ============================================================================
# 5. ПРОВЕРКА ЗАВИСИМОСТЕЙ
# ============================================================================
Write-Log ""
Write-Log "📦 Проверка зависимостей..." "Info"

if (Test-Path "requirements.txt") {
    Write-Log "✅ requirements.txt найден" "Success"
    Write-Log "   Убедитесь что все зависимости установлены" "Info"
    Write-Log "   (они должны быть установлены при настройке venv)" "Info"
} else {
    Write-Log "⚠️  requirements.txt не найден" "Warning"
}

# ============================================================================
# 6. ИНФОРМАЦИЯ О СТАРТЕ
# ============================================================================
Write-Log ""
Write-Host "╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    🚀 ЗАПУСК ПРИЛОЖЕНИЯ                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Log ""
Write-Log "📊 АРГУМЕНТЫ:" "Highlight"

if ($Args.Count -gt 0) {
    $ArgString = $Args -join " "
    Write-Log "   $ArgString" "Info"
} else {
    Write-Log "   (нет)" "Info"
}

Write-Log ""
Write-Log "🌐 АДРЕСА:" "Highlight"
Write-Log "   FastAPI:       https://localhost:8443 (или авто-порт)" "Info"
Write-Log "   MCP Console:   https://localhost:8765 (или авто-порт)" "Info"
Write-Log "   API Docs:      https://localhost:8443/docs" "Info"
Write-Log "   Web UI:        https://localhost:8443/" "Info"
Write-Log ""

# ============================================================================
# 7. ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================================================
Write-Log "Запуск FastAPI приложение через venv..." "Highlight"
Write-Log ""

# Запустить приложение с переданными аргументами
python run.py @Args

# Если приложение закрылось
Write-Log ""
Write-Log "❌ Приложение остановлено" "Warning"
Write-Log "Нажмите любую клавишу для выхода..." "Info"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
