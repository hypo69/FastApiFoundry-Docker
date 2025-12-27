<!--
===============================================================================
Название процесса: PowerShell скрипты для управления Foundry
===============================================================================
Описание:
    PowerShell скрипты для автоматизации управления Foundry AI моделями.
    Включают загрузку, управление и мониторинг моделей и сервисов.

Примеры:
    Загрузка модели:
    .\scripts\download-model.ps1 -ModelId "deepseek-r1-distill-qwen-7b"
    .\scripts\load-model.ps1 -ModelId "deepseek-r1-distill-qwen-7b"

File: scripts/README.md
Project: FastApiFoundry (Docker)
Version: 0.2.1
Author: hypo69
License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
Copyright: © 2025 AiStros
Date: 9 декабря 2025
===============================================================================
-->

# 📜 Scripts

**PowerShell скрипты для управления Foundry моделями и сервисами**

---

## 📋 Описание

Эта директория содержит PowerShell скрипты для автоматизации управления Foundry AI моделями и мониторинга системы.

## 📁 Скрипты

| Файл | Описание | Использование |
|------|----------|---------------|
| **`download-model.ps1`** | Загрузка моделей в кэш Foundry | Скачивание моделей для офлайн использования |
| **`load-model.ps1`** | Загрузка модели в память | Запуск модели для генерации |
| **`unload-model.ps1`** | Выгрузка модели из памяти | Освобождение ресурсов |
| **`list-models.ps1`** | Список доступных моделей | Просмотр установленных и доступных моделей |
| **`service-status.ps1`** | Проверка статуса сервисов | Мониторинг Foundry и FastAPI |

## 🚀 Использование

### 📥 Загрузка моделей

#### Скачать модель в кэш
```powershell
# Загрузить рекомендуемую модель
.\scripts\download-model.ps1 -ModelId "deepseek-r1-distill-qwen-7b"

# Загрузить легкую модель
.\scripts\download-model.ps1 -ModelId "phi-3-mini-4k"

# Загрузить модель Llama
.\scripts\download-model.ps1 -ModelId "llama-3.2-1b"
```

#### Загрузить модель в память
```powershell
# Запустить модель для использования
.\scripts\load-model.ps1 -ModelId "deepseek-r1-distill-qwen-7b"

# Загрузить с параметрами
.\scripts\load-model.ps1 -ModelId "qwen2.5-7b" -MaxTokens 4096
```

### 📤 Управление моделями

#### Выгрузить модель
```powershell
# Освободить память от модели
.\scripts\unload-model.ps1 -ModelId "deepseek-r1-distill-qwen-7b"

# Выгрузить все модели
.\scripts\unload-model.ps1 -All
```

#### Список моделей
```powershell
# Показать все доступные модели
.\scripts\list-models.ps1

# Показать только загруженные
.\scripts\list-models.ps1 -LoadedOnly

# Экспорт в JSON
.\scripts\list-models.ps1 -Format JSON -Output models.json
```

### 📊 Мониторинг

#### Статус сервисов
```powershell
# Проверить все сервисы
.\scripts\service-status.ps1

# Проверить только Foundry
.\scripts\service-status.ps1 -Service Foundry

# Проверить с детальной информацией
.\scripts\service-status.ps1 -Detailed
```

## 🎯 Основные функции

### 📥 Download Model
```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$ModelId,
    
    [string]$CachePath = $null,
    [switch]$Force
)

# Загрузка модели с проверкой
foundry model download $ModelId
```

### 🚀 Load Model  
```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$ModelId,
    
    [int]$MaxTokens = 2048,
    [double]$Temperature = 0.7,
    [switch]$Verbose
)

# Загрузка в память с параметрами
foundry model load $ModelId --max-tokens $MaxTokens
```

### 📤 Unload Model
```powershell
param(
    [string]$ModelId = $null,
    [switch]$All,
    [switch]$Force
)

# Выгрузка модели или всех моделей
if ($All) {
    foundry model unload --all
} else {
    foundry model unload $ModelId
}
```

### 📋 List Models
```powershell
param(
    [switch]$LoadedOnly,
    [switch]$AvailableOnly,
    [ValidateSet("Table", "JSON", "CSV")]
    [string]$Format = "Table",
    [string]$Output = $null
)

# Получение списка с форматированием
$models = foundry model list --format json | ConvertFrom-Json
```

### 📊 Service Status
```powershell
param(
    [ValidateSet("All", "Foundry", "FastAPI")]
    [string]$Service = "All",
    [switch]$Detailed,
    [switch]$JSON
)

# Проверка статуса сервисов
Test-NetConnection -ComputerName localhost -Port 50477
Test-NetConnection -ComputerName localhost -Port 9696
```

## ⚙️ Конфигурация

### 🔧 Параметры по умолчанию
```powershell
# Настройки в скриптах
$DefaultFoundryPort = 50477
$DefaultFastAPIPort = 9696
$DefaultModelCachePath = "$env:USERPROFILE\.foundry\models"
$DefaultTimeout = 30
```

### 🌐 Переменные окружения
```powershell
# Установка переменных
$env:FOUNDRY_URL = "http://localhost:50477"
$env:FOUNDRY_CACHE_PATH = "C:\foundry\models"
$env:FOUNDRY_LOG_LEVEL = "INFO"
```

## 🧪 Примеры использования

### 🚀 Быстрый старт с моделью
```powershell
# Полный цикл: скачать -> загрузить -> использовать
.\scripts\download-model.ps1 -ModelId "deepseek-r1-distill-qwen-7b"
.\scripts\load-model.ps1 -ModelId "deepseek-r1-distill-qwen-7b"
.\scripts\service-status.ps1 -Service Foundry
```

### 📊 Мониторинг системы
```powershell
# Проверка всех компонентов
.\scripts\service-status.ps1 -Detailed
.\scripts\list-models.ps1 -LoadedOnly
Get-Process | Where-Object {$_.Name -like "*foundry*" -or $_.Name -like "*python*"}
```

### 🔄 Автоматизация
```powershell
# Скрипт автоматической настройки
$RecommendedModels = @(
    "deepseek-r1-distill-qwen-7b",
    "phi-3-mini-4k",
    "llama-3.2-1b"
)

foreach ($model in $RecommendedModels) {
    Write-Host "Загрузка модели: $model"
    .\scripts\download-model.ps1 -ModelId $model
}
```

## 🔍 Отладка и логирование

### 📝 Логирование
```powershell
# Включение подробного логирования
$VerbosePreference = "Continue"
$DebugPreference = "Continue"

# Логирование в файл
Start-Transcript -Path "logs\foundry-management.log"
```

### 🐛 Отладка
```powershell
# Проверка доступности Foundry
Test-NetConnection -ComputerName localhost -Port 50477 -InformationLevel Detailed

# Проверка процессов
Get-Process | Where-Object {$_.Name -like "*foundry*"}

# Проверка портов
netstat -an | findstr ":50477"
```

## 🔗 Интеграция

### 🌐 С веб-интерфейсом
- Скрипты вызываются через FastAPI endpoints
- Результаты отображаются в веб-консоли
- Прогресс операций в реальном времени

### 🤖 С Python приложением
```python
import subprocess

# Вызов PowerShell скрипта из Python
result = subprocess.run([
    "powershell", "-File", "scripts/list-models.ps1", 
    "-Format", "JSON"
], capture_output=True, text=True)

models = json.loads(result.stdout)
```

## 📖 Документация

- **[Foundry Commands](../docs/foundry_commands.md)** - Команды Foundry CLI
- **[Running Guide](../docs/running.md)** - Запуск и управление
- **[Configuration](../docs/configuration.md)** - Настройка системы

---

**📖 Документация:** [Главное README](../README.md) | [Foundry Commands](../docs/foundry_commands.md) | [Running Guide](../docs/running.md)