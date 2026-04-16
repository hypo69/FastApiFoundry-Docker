# 🚀 Запуск и настройка FastAPI Foundry

## 📋 Системные требования

- **Windows 10/11** (основная поддержка)
- **Python 3.11+** (встроенный в проект)
- **Microsoft Foundry** (устанавливается автоматически)
- **8GB RAM** (минимум для AI моделей)

## ⚡ Быстрый запуск

### 1. Клонирование репозитория
```powershell
git clone https://github.com/hypo69/FastApiFoundry-Docker.git
cd FastApiFoundry-Docker
```

### 2. Автоматический запуск (РЕКОМЕНДУЕТСЯ)
```powershell
# Полный запуск с AI моделями
.\start.ps1

# Упрощенный запуск
.\start_simple.ps1
```

### 3. Ручной запуск
```powershell
# 1. Запуск Foundry (первый терминал)
foundry service start

# 2. Запуск FastAPI (второй терминал)
python run.py
```

## 🔧 Embedded Python

Проект включает встроенный Python 3.11 в папке `python-3.11.0-embed-amd64/`

### Создание символических ссылок (один раз)
```powershell
# Запустить PowerShell от имени администратора
New-Item -ItemType SymbolicLink -Path python.exe -Target ".\python-3.11.0-embed-amd64\python.exe"
New-Item -ItemType SymbolicLink -Path py.exe -Target ".\python-3.11.0-embed-amd64\python.exe"
```

### Использование
```powershell
# Использовать встроенный Python
.\python.exe run.py
.\py.exe run.py

# НЕ использовать (запускает системный Python)
python run.py
py run.py
```

## 🌐 Доступ к интерфейсу

После запуска доступны:

- **Веб-интерфейс**: http://localhost:9696
- **API документация**: http://localhost:9696/docs
- **Health check**: http://localhost:9696/api/v1/health
- **Чат**: http://localhost:9696/static/chat.html

## ⚙️ Конфигурация

### config.json - основные настройки
```json
{
  "fastapi_server": {
    "port": 9696,
    "auto_find_free_port": true
  },
  "foundry_ai": {
    "base_url": "http://localhost:50477/v1/",
    "default_model": "qwen2.5-0.5b-instruct-generic-cpu:4",
    "auto_load_default": false
  }
}
```

### Автозагрузка модели
```json
{
  "foundry_ai": {
    "auto_load_default": true,
    "default_model": "deepseek-r1-distill-qwen-7b-generic-cpu:3"
  }
}
```

## 🔍 Диагностика

### Проверка системы
```powershell
# Диагностика всех компонентов
python diagnose.py

# Проверка конфигурации
python test_config.py

# Проверка порядка запуска
python test_startup_order.py
```

### Остановка процессов
```powershell
# Остановка всех процессов
python stop.py

# Точная остановка
python stop_precise.py
```

## 🛠️ Устранение неполадок

### Проблема: Порт занят
```powershell
# Автоматическое решение
python stop.py
.\start.ps1
```

### Проблема: Foundry не запускается
```powershell
# Проверка статуса
foundry service status

# Перезапуск
foundry service stop
foundry service start
```

### Проблема: Модель не загружается
1. Проверить доступные модели: http://localhost:9696/api/v1/models
2. Установить `auto_load_default: true` в config.json
3. Перезапустить сервер

## 📊 Мониторинг

### Логи
```powershell
# Просмотр логов
Get-Content logs\fastapi-foundry.log -Tail 50

# Анализ логов
python src\utils\log_analyzer.py
```

### Health Check
```powershell
# Проверка здоровья
curl http://localhost:9696/api/v1/health

# Проверка моделей
curl http://localhost:9696/api/v1/models
```

## 🔄 Обновление

```powershell
# Получить обновления
git pull origin main

# Перезапустить
python stop.py
.\start.ps1
```

---

**Следующий шаг**: [Веб-интерфейс](web-interface.md)