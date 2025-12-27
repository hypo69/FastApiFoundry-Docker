# FastAPI Foundry - Complete Installer
# =============================================================================
# Устанавливает все необходимое: Python venv, Foundry, символические ссылки
# =============================================================================

param(
    [switch]$SkipFoundry,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 FastAPI Foundry - Complete Installer" -ForegroundColor Green
Write-Host "=" * 50

# Переменные
$projectRoot = $PSScriptRoot
$venvPath = Join-Path $projectRoot "venv"
$embeddedPython = Join-Path $projectRoot "python-3.11.0-embed-amd64\python.exe"
$foundryPath = Join-Path $env:USERPROFILE ".foundry\bin\foundry.exe"

# 1. Создание venv
Write-Host "📦 Создание виртуального окружения..." -ForegroundColor Yellow
if (Test-Path $venvPath) {
    if ($Force) {
        Remove-Item $venvPath -Recurse -Force
    } else {
        Write-Host "✅ venv уже существует"
    }
}

if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
    Write-Host "✅ venv создан"
}

# 2. Активация и установка зависимостей
Write-Host "📚 Установка Python зависимостей..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r requirements.txt

# Установка RAG зависимостей
Write-Host "🔍 Установка RAG зависимостей..." -ForegroundColor Yellow
try {
    pip install sentence-transformers faiss-cpu torch transformers
    Write-Host "✅ RAG зависимости установлены"
} catch {
    Write-Warning "Не удалось установить RAG зависимости: $_"
    Write-Host "Попробуйте позже: python install_rag_deps.py" -ForegroundColor Yellow
}

Write-Host "✅ Python зависимости установлены"

# 3. Установка Foundry
if (-not $SkipFoundry) {
    Write-Host "🔧 Установка Foundry..." -ForegroundColor Yellow
    
    if (Test-Path $foundryPath) {
        Write-Host "✅ Foundry уже установлен: $foundryPath"
    } else {
        try {
            # Скачиваем и устанавливаем Foundry
            $foundryInstaller = "https://raw.githubusercontent.com/foundry-rs/foundry/master/foundryup/foundryup"
            $tempScript = Join-Path $env:TEMP "foundryup.ps1"
            
            # Создаем PowerShell версию установщика
            @"
# Foundry installer for Windows
`$foundryDir = Join-Path `$env:USERPROFILE ".foundry"
`$binDir = Join-Path `$foundryDir "bin"
New-Item -ItemType Directory -Path `$binDir -Force | Out-Null

# Скачиваем последний релиз
`$releases = Invoke-RestMethod "https://api.github.com/repos/foundry-rs/foundry/releases/latest"
`$asset = `$releases.assets | Where-Object { `$_.name -like "*x86_64-pc-windows-msvc.zip" }

if (`$asset) {
    `$zipPath = Join-Path `$env:TEMP "foundry.zip"
    Invoke-WebRequest `$asset.browser_download_url -OutFile `$zipPath
    Expand-Archive `$zipPath -DestinationPath `$binDir -Force
    Remove-Item `$zipPath
    Write-Host "✅ Foundry установлен в `$binDir"
} else {
    throw "Не найден релиз для Windows"
}
"@ | Out-File $tempScript -Encoding UTF8
            
            & $tempScript
            Remove-Item $tempScript
            
            # Добавляем в PATH
            $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
            $foundryBinDir = Join-Path $env:USERPROFILE ".foundry\bin"
            if ($currentPath -notlike "*$foundryBinDir*") {
                [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$foundryBinDir", "User")
                $env:PATH += ";$foundryBinDir"
                Write-Host "✅ Foundry добавлен в PATH"
            }
            
        } catch {
            Write-Warning "Не удалось установить Foundry автоматически: $_"
            Write-Host "Установите вручную: https://github.com/foundry-rs/foundry" -ForegroundColor Yellow
        }
    }
}

# 4. Создание символических ссылок
Write-Host "🔗 Создание символических ссылок..." -ForegroundColor Yellow
if (Test-Path $embeddedPython) {
    try {
        $pythonLink = Join-Path $projectRoot "python.exe"
        $pyLink = Join-Path $projectRoot "py.exe"
        
        if (-not (Test-Path $pythonLink)) {
            New-Item -ItemType SymbolicLink -Path $pythonLink -Target $embeddedPython -Force
            Write-Host "✅ python.exe -> embedded Python"
        }
        
        if (-not (Test-Path $pyLink)) {
            New-Item -ItemType SymbolicLink -Path $pyLink -Target $embeddedPython -Force
            Write-Host "✅ py.exe -> embedded Python"
        }
    } catch {
        Write-Warning "Не удалось создать символические ссылки. Запустите PowerShell от имени администратора или включите Developer Mode"
    }
} else {
    Write-Warning "Embedded Python не найден: $embeddedPython"
}

# 5. Создание .env если нет
Write-Host "⚙️ Настройка конфигурации..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env создан из .env.example"
    } else {
        @"
# FastAPI Foundry Configuration
FOUNDRY_BASE_URL=http://localhost:50477/v1/
FOUNDRY_DEFAULT_MODEL=deepseek-r1:14b
API_HOST=0.0.0.0
API_PORT=8000
RAG_ENABLED=true
LOG_LEVEL=INFO
"@ | Out-File ".env" -Encoding UTF8
        Write-Host "✅ .env создан с настройками по умолчанию"
    }
}

# 6. Создание RAG индекса
Write-Host "🔍 Создание RAG индекса..." -ForegroundColor Yellow
if (-not (Test-Path "rag_index")) {
    try {
        & "$venvPath\Scripts\python.exe" create_rag_index.py
        Write-Host "✅ RAG индекс создан"
    } catch {
        Write-Warning "Не удалось создать RAG индекс: $_"
        Write-Host "Попробуйте позже: python create_rag_index.py" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ RAG индекс уже существует"
}

# 7. Проверка установки
Write-Host "🧪 Проверка установки..." -ForegroundColor Yellow

# Проверяем Python
try {
    & "$venvPath\Scripts\python.exe" --version
    Write-Host "✅ Python в venv работает"
} catch {
    Write-Warning "Проблема с Python в venv"
}

# Проверяем Foundry
if (-not $SkipFoundry) {
    try {
        if (Get-Command foundry -ErrorAction SilentlyContinue) {
            foundry --version
            Write-Host "✅ Foundry доступен в PATH"
        } else {
            Write-Warning "Foundry не найден в PATH"
        }
    } catch {
        Write-Warning "Проблема с Foundry"
    }
}

Write-Host ""
Write-Host "🎉 Установка завершена!" -ForegroundColor Green
Write-Host "=" * 50
Write-Host "Запуск:"
Write-Host "  1. Активировать venv: .\venv\Scripts\Activate.ps1"
Write-Host "  2. Запустить Foundry: foundry"
Write-Host "  3. Запустить FastAPI: python run.py"
Write-Host ""
Write-Host "Или использовать embedded Python:"
Write-Host "  .\python.exe run.py"
Write-Host ""
<<<<<<< HEAD
Write-Host "Веб-интерфейс: http://localhost:8000"
Write-Host "🔍 RAG система: http://localhost:8000/api/v1/rag/status"
=======
Write-Host "Веб-интерфейс: http://localhost:9696"
>>>>>>> a76fcff509d3210e0d5dbe66516b2c1d02333d90
