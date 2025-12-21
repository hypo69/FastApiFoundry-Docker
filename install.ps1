# Скрипт первоначальной установки FastAPI Foundry
# ============================================================================
# Создает venv, устанавливает зависимости и настраивает окружение

param(
    [switch]$SkipPython = $false,
    [switch]$SkipFoundry = $false,
    [switch]$Force = $false
)

# Цвета
$colors = @{
    'Success' = 'Green'
    'Error'   = 'Red'
    'Warning' = 'Yellow'
    'Info'    = 'Cyan'
    'Highlight' = 'Magenta'
}

function Write-Log {
    param([string]$Message, [string]$Type = 'Info')
    $timestamp = Get-Date -Format "HH:mm:ss"
    $color = $colors[$Type] ?? 'White'
    Write-Host "[$timestamp] " -ForegroundColor Gray -NoNewline
    Write-Host $Message -ForegroundColor $color
}

function Show-Header {
    Clear-Host
    Write-Host @"
╔════════════════════════════════════════════════════════════════════════╗
║         FastAPI Foundry - Installation Wizard                         ║
║                                                                        ║
║  REST API для локальных AI моделей через Foundry с RAG поддержкой   ║
╚════════════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta
}

function Test-Admin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Python {
    Write-Log "🐍 Проверка Python..." "Info"

    try {
        $pythonVersion = python --version 2>&1
        Write-Log "✅ Python уже установлен: $pythonVersion" "Success"
        return $true
    } catch {
        Write-Log "⚠️  Python не установлен" "Warning"
        Write-Log ""
        Write-Log "Загрузить Python можно с: https://www.python.org" "Info"
        Write-Log ""
        Write-Log "При установке НЕ ЗАБЫТЬ отметить:" "Warning"
        Write-Log "  ☑️ Add Python to PATH" "Warning"
        Write-Log "  ☑️ Install pip" "Warning"
        Write-Log ""

        $install = Read-Host "Установить Python сейчас? (y/n)"
        if ($install -eq 'y' -or $install -eq 'Y') {
            Write-Log "Скачивание Python..." "Info"
            $pythonUrl = "https://www.python.org/downloads/"
            Start-Process $pythonUrl
            Write-Log "Установите Python и запустите этот скрипт снова" "Warning"
            exit 0
        }
        return $false
    }
}

function Install-Git {
    Write-Log "💻 Проверка Git..." "Info"

    try {
        $gitVersion = git --version 2>&1
        Write-Log "✅ Git уже установлен: $gitVersion" "Success"
        return $true
    } catch {
        Write-Log "⚠️  Git не установлен" "Warning"
        Write-Log ""
        Write-Log "Git нужен для клонирования репозиториев" "Info"
        Write-Log ""

        $install = Read-Host "Установить Git через winget? (y/n)"
        if ($install -eq 'y' -or $install -eq 'Y') {
            try {
                Write-Log "Установка Git..." "Info"
                winget install Git.Git --accept-package-agreements --accept-source-agreements
                if ($LASTEXITCODE -eq 0) {
                    Write-Log "✅ Git установлен успешно" "Success"
                    Write-Log "Перезапустите PowerShell для обновления PATH" "Warning"
                    return $true
                } else {
                    Write-Log "⚠️  Ошибка установки через winget" "Warning"
                }
            } catch {
                Write-Log "⚠️  winget не доступен" "Warning"
            }
            
            Write-Log "Открываю страницу загрузки Git..." "Info"
            Start-Process "https://git-scm.com/download/win"
            Write-Log "Установите Git и перезапустите PowerShell" "Warning"
            return $false
        }
        return $true
    }
}

function Install-Docker {
    Write-Log "🐳 Проверка Docker..." "Info"

    try {
        $dockerVersion = docker --version 2>&1
        Write-Log "✅ Docker уже установлен: $dockerVersion" "Success"
        return $true
    } catch {
        Write-Log "⚠️  Docker не установлен" "Warning"
        Write-Log ""
        Write-Log "Docker нужен для контейнеризации (опционально)" "Info"
        Write-Log ""

        $install = Read-Host "Установить Docker Desktop? (y/n)"
        if ($install -eq 'y' -or $install -eq 'Y') {
            try {
                Write-Log "Установка Docker Desktop..." "Info"
                winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
                if ($LASTEXITCODE -eq 0) {
                    Write-Log "✅ Docker Desktop установлен успешно" "Success"
                    Write-Log "Перезагрузите компьютер и запустите Docker Desktop" "Warning"
                    return $true
                } else {
                    Write-Log "⚠️  Ошибка установки через winget" "Warning"
                }
            } catch {
                Write-Log "⚠️  winget не доступен" "Warning"
            }
            
            Write-Log "Открываю страницу загрузки Docker..." "Info"
            Start-Process "https://www.docker.com/products/docker-desktop/"
            Write-Log "Установите Docker Desktop и перезагрузите компьютер" "Warning"
            return $false
        }
        return $true
    }
}

function Create-VirtualEnv {
    Write-Log ""
    Write-Log "🐍 Создание виртуальной окружения..." "Info"

    if (Test-Path "venv") {
        Write-Log "✅ venv уже существует" "Success"
        return $true
    }

    try {
        Write-Log "Создание venv..." "Info"
        python -m venv venv 2>&1 | Out-Null

        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ venv создана успешно" "Success"
            return $true
        } else {
            Write-Log "❌ Ошибка при создании venv" "Error"
            return $false
        }
    } catch {
        Write-Log "❌ Ошибка при создании venv: $_" "Error"
        return $false
    }
}

function Install-Dependencies {
    Write-Log ""
    Write-Log "📦 Установка зависимостей в venv..." "Info"

    if (-not (Test-Path "requirements.txt")) {
        Write-Log "❌ requirements.txt не найден!" "Error"
        return $false
    }

    try {
        Write-Log "Активация venv..." "Info"
        & .\venv\Scripts\Activate.ps1

        Write-Log "Это может занять несколько минут..." "Info"

        Write-Log "Обновление pip..." "Info"
        python -m pip install --upgrade pip 2>&1 | Where-Object {$_ -match "Successfully"} | ForEach-Object {
            Write-Log "  ✅ pip обновлен" "Success"
        }

        Write-Log "Установка пакетов из requirements.txt..." "Info"
        python -m pip install -r requirements.txt 2>&1 | Where-Object {$_ -match "Successfully installed"} | ForEach-Object {
            Write-Log "  ✅ Пакеты установлены" "Success"
        }

        Write-Log "✅ Зависимости установлены в venv" "Success"
        return $true
    } catch {
        Write-Log "❌ Ошибка при установке зависимостей: $_" "Error"
        return $false
    }
}

function Install-Foundry {
    Write-Log ""
    Write-Log "🔧 Проверка Foundry CLI..." "Info"

    try {
        $foundryVersion = foundry --version 2>&1
        Write-Log "✅ Foundry уже установлена: $foundryVersion" "Success"
        return $true
    } catch {
        Write-Log "⚠️  Foundry не установлена (опционально)" "Warning"
        Write-Log ""
        Write-Log "Foundry требуется для работы с локальными AI моделями" "Info"
        Write-Log "Скачать можно с: https://github.com/foundryai/foundry" "Info"
        Write-Log ""

        $install = Read-Host "Установить Foundry? (y/n)"
        if ($install -eq 'y' -or $install -eq 'Y') {
            Write-Log "Перейдите на https://github.com/foundryai/foundry" "Info"
            Write-Log "и скачайте последнюю версию" "Info"
            Write-Log "После установки перезагрузите PowerShell и запустите этот скрипт снова" "Warning"
            Start-Process "https://github.com/foundryai/foundry/releases"
            return $false
        }
        return $true
    }
}

function Setup-Environment {
    Write-Log ""
    Write-Log "⚙️  Настройка окружения..." "Info"

    # Проверить .env
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-Log "Создание .env из шаблона..." "Info"
            Copy-Item ".env.example" ".env" -Force
            Write-Log "✅ .env создан" "Success"
        } else {
            Write-Log "⚠️  .env.example не найден" "Warning"
        }
    } else {
        Write-Log "✅ .env уже существует" "Success"
    }

    # Создать директории
    $dirs = @("logs", "rag_index", "static")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "  ✅ Создана директория: $dir" "Success"
        }
    }
}

function Test-Installation {
    Write-Log ""
    Write-Log "🧪 Тестирование установки в venv..." "Info"

    try {
        & .\venv\Scripts\Activate.ps1

        $passed = 0
        $failed = 0

        # Test Python
        try {
            $pythonVersion = python --version 2>&1
            Write-Log "  ✅ Python: $pythonVersion" "Success"
            $passed++
        } catch {
            Write-Log "  ❌ Python: не найден в venv" "Error"
            $failed++
        }

        # Test FastAPI
        try {
            $result = python -c "import fastapi; print(fastapi.__version__)" 2>&1
            Write-Log "  ✅ FastAPI: версия $result" "Success"
            $passed++
        } catch {
            Write-Log "  ❌ FastAPI: не установлен" "Error"
            $failed++
        }

        # Test uvicorn
        try {
            $result = python -c "import uvicorn; print(uvicorn.__version__)" 2>&1
            Write-Log "  ✅ Uvicorn: версия $result" "Success"
            $passed++
        } catch {
            Write-Log "  ❌ Uvicorn: не установлен" "Error"
            $failed++
        }

        Write-Log ""
        if ($failed -eq 0) {
            Write-Log "✅ Все тесты пройдены!" "Success"
            return $true
        } else {
            Write-Log "❌ $failed тестов не пройдено" "Error"
            return $false
        }
    } catch {
        Write-Log "❌ Ошибка при тестировании: $_" "Error"
        return $false
    }
}

function Setup-ExecutionPolicy {
    Write-Log ""
    Write-Log "🔐 Настройка политики выполнения PowerShell..." "Info"

    try {
        $policy = Get-ExecutionPolicy
        if ($policy -eq "Restricted") {
            Write-Log "Текущая политика: $policy" "Warning"
            Write-Log "Требуется изменить на RemoteSigned..." "Info"

            if (Test-Admin) {
                Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                Write-Log "✅ Политика обновлена" "Success"
            } else {
                Write-Log "⚠️  Требуются права администратора для изменения политики" "Warning"
                Write-Log "Запустите PowerShell от администратора и выполните:" "Info"
                Write-Log "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" "Info"
            }
        } else {
            Write-Log "✅ Политика: $policy" "Success"
        }
    } catch {
        Write-Log "⚠️  Ошибка при проверке политики: $_" "Warning"
    }
}

function Show-NextSteps {
    Write-Log ""
    Write-Host "╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                    ✅ УСТАНОВКА ЗАВЕРШЕНА!                            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Log ""
    Write-Log "🎉 Следующие шаги:" "Highlight"
    Write-Log ""
    Write-Log "1. Запустить на порту по умолчанию (8000):" "Info"
    Write-Log "   python run.py" "Info"
    Write-Log ""
    Write-Log "2. Запустить с проверкой занятости порта (если порт занят - подключиться к существующему):" "Info"
    Write-Log "   python run.py --fixed-port 8000" "Info"
    Write-Log ""
    Write-Log "3. Запустить с автопоиском свободного порта:" "Info"
    Write-Log "   python run.py --auto-port" "Info"
    Write-Log ""
    Write-Log "4. Запустить с MCP консолью и браузером:" "Info"
    Write-Log "   python run.py --mcp --browser" "Info"
    Write-Log ""
    Write-Log "5. Production режим:" "Info"
    Write-Log "   python run.py --prod" "Info"
    Write-Log ""
    Write-Log "6. Справка:" "Info"
    Write-Log "   python run.py --help" "Info"
    Write-Log ""
    Write-Log "📚 Документация:" "Info"
    Write-Log "   - README.md - основная информация" "Info"
    Write-Log "   - docs/ - полная документация" "Info"
    Write-Log ""
    Write-Log "🌐 После запуска:" "Info"
    Write-Log "   - Веб-интерфейс: http://localhost:8000" "Info"
    Write-Log "   - API документация: http://localhost:8000/docs" "Info"
    Write-Log "   - Health Check: http://localhost:8000/api/v1/health" "Info"
    Write-Log ""
    Write-Log "💡 Порт можно изменить через --port или --fixed-port" "Info"
    Write-Log "   .\StartFastApiFoundry.ps1 --dev --ssl --mcp --auto-port --browser" "Info"
    Write-Log ""
    Write-Log "2. Или запустить через новый launcher:" "Info"
    Write-Log "   .\start.ps1 --dev --ssl --mcp --auto-port --browser" "Info"
    Write-Log ""
    Write-Log "3. Production режим:" "Info"
    Write-Log "   .\StartFastApiFoundry.ps1 --prod --ssl --mcp --auto-port" "Info"
    Write-Log ""
    Write-Log "4. Справка:" "Info"
    Write-Log "   .\StartFastApiFoundry.ps1 --help" "Info"
    Write-Log ""
    Write-Log "📖 Документация: START_HERE.md, QUICK_START.md" "Info"
}

# ============================================================================
# MAIN
# ============================================================================

Show-Header
Write-Log "Начало установки FastAPI Foundry..." "Highlight"
Write-Log ""

# Check and setup execution policy
Setup-ExecutionPolicy

# Install Python
if (-not $SkipPython) {
    if (-not (Install-Python)) {
        exit 1
    }
}

# Install Git
if (-not (Install-Git)) {
    Write-Log "⚠️  Git не установлен, но продолжаем..." "Warning"
}

# Install Docker (optional)
if (-not (Install-Docker)) {
    Write-Log "⚠️  Docker не установлен, но продолжаем..." "Warning"
}

# Create virtual environment
if (-not (Create-VirtualEnv)) {
    exit 1
}

# Install dependencies
if (-not (Install-Dependencies)) {
    Write-Log "⚠️  Попытка переустановки с параметром --upgrade" "Warning"
    & .\venv\Scripts\Activate.ps1
    python -m pip install --upgrade -r requirements.txt
}

# Install Foundry
if (-not $SkipFoundry) {
    Install-Foundry
}

# Setup environment
Setup-Environment

# Test installation
if (-not (Test-Installation)) {
    Write-Log ""
    Write-Log "❌ Некоторые компоненты не прошли проверку" "Error"
    Write-Log "Пожалуйста, проверьте установку вручную" "Warning"
}

# Show completion
Show-NextSteps

Write-Log ""
Write-Log "Нажмите любую клавишу для выхода..." "Info"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
