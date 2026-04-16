# 🛠️ Устранение неполадок - FastAPI Foundry

## 🚨 Частые проблемы и решения

### 1. Foundry не запускается

**Симптомы:**
- Ошибка "Connection refused to http://localhost:50477"
- Сообщение "Foundry service unavailable"

**Решения:**

```powershell
# Проверить статус Foundry
foundry service status

# Остановить и запустить заново
foundry service stop
foundry service start

# Проверить процессы
Get-Process -Name "foundry" -ErrorAction SilentlyContinue

# Проверить порты
netstat -ano | findstr ":50477"
```

**Если не помогает:**
```powershell
# Полная переустановка Foundry
foundry service uninstall
foundry service install
foundry service start
```

### 2. Порт 9696 занят

**Симптомы:**
- Ошибка "Address already in use"
- FastAPI не запускается

**Автоматическое решение:**
```powershell
# Остановить все процессы
python stop.py

# Запустить заново
.\start.ps1
```

**Ручное решение:**
```powershell
# Найти процесс на порту
netstat -ano | findstr ":9696"

# Завершить процесс (замените PID)
taskkill /PID <PID> /F

# Или изменить порт в config.json
{
  "fastapi_server": {
    "port": 9697
  }
}
```

### 3. Модель не загружается

**Симптомы:**
- "Model not available"
- "Model loading failed"

**Решения:**

```powershell
# Проверить доступные модели
curl http://localhost:50477/v1/models

# Загрузить модель вручную
curl -X POST http://localhost:9696/api/v1/models/load \
  -H "Content-Type: application/json" \
  -d '{"model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"}'

# Проверить статус модели
curl http://localhost:9696/api/v1/models
```

**Автозагрузка модели:**
```json
{
  "foundry_ai": {
    "auto_load_default": true,
    "default_model": "qwen2.5-0.5b-instruct-generic-cpu:4"
  }
}
```

### 4. Веб-интерфейс не открывается

**Симптомы:**
- Страница не загружается
- 404 ошибка

**Решения:**

```powershell
# Проверить статус сервера
curl http://localhost:9696/api/v1/health

# Проверить статические файлы
ls static/

# Открыть правильный URL
# http://localhost:9696 (не https)
# http://localhost:9696/static/chat.html
```

### 5. Медленная генерация текста

**Симптомы:**
- Долгое ожидание ответа
- Таймауты

**Решения:**

```json
// Уменьшить max_tokens
{
  "max_tokens": 100,
  "temperature": 0.7
}

// Увеличить таймаут
{
  "foundry_ai": {
    "timeout": 600
  }
}
```

**Оптимизация:**
- Использовать меньшие модели (0.5B вместо 7B)
- Уменьшить max_tokens
- Увеличить RAM

## 🔍 Диагностические команды

### Полная диагностика
```powershell
# Автоматическая диагностика
python diagnose.py

# Проверка конфигурации
python test_config.py

# Проверка порядка запуска
python test_startup_order.py

# Проверка системы
python test_system.py
```

### Проверка компонентов

```powershell
# 1. Проверка Python
python --version
.\python.exe --version

# 2. Проверка Foundry
foundry --version
foundry service status

# 3. Проверка портов
netstat -ano | findstr ":9696"
netstat -ano | findstr ":50477"

# 4. Проверка процессов
Get-Process -Name "python" -ErrorAction SilentlyContinue
Get-Process -Name "foundry" -ErrorAction SilentlyContinue

# 5. Проверка файлов
Test-Path "config.json"
Test-Path "static/index.html"
Test-Path "src/api/main.py"
```

### Health Checks

```bash
# FastAPI Health
curl http://localhost:9696/api/v1/health

# Foundry Health  
curl http://localhost:50477/v1/models

# Models Status
curl http://localhost:9696/api/v1/models

# Simple Generation Test
curl -X POST http://localhost:9696/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "max_tokens": 10}'
```

## 📊 Логи и мониторинг

### Просмотр логов

```powershell
# Основные логи
Get-Content logs\fastapi-foundry.log -Tail 50

# Логи ошибок
Get-Content logs\fastapi-foundry-errors.log -Tail 20

# Структурированные логи
Get-Content logs\fastapi-foundry-structured.jsonl -Tail 10

# Анализ логов
python src\utils\log_analyzer.py
```

### Мониторинг в реальном времени

```powershell
# Мониторинг логов
Get-Content logs\fastapi-foundry.log -Wait

# Мониторинг процессов
while ($true) {
    Get-Process -Name "python","foundry" -ErrorAction SilentlyContinue | 
    Select-Object Name, Id, CPU, WorkingSet
    Start-Sleep 5
    Clear-Host
}
```

## 🔧 Восстановление системы

### Полный сброс

```powershell
# 1. Остановить все процессы
python stop.py
taskkill /F /IM "python.exe"
taskkill /F /IM "foundry.exe"

# 2. Очистить порты
# (Порты освободятся автоматически)

# 3. Сброс конфигурации
Copy-Item "config.json.backup" "config.json" -Force

# 4. Очистка логов
Remove-Item logs\*.log -Force
Remove-Item logs\*.jsonl -Force

# 5. Перезапуск
.\start.ps1
```

### Переустановка компонентов

```powershell
# Переустановка Foundry
foundry service uninstall
# Скачать новую версию с GitHub
foundry service install

# Обновление FastAPI Foundry
git pull origin main
pip install -r requirements.txt --upgrade
```

## 🐛 Отладка кода

### Debug режим

```json
{
  "development": {
    "debug": true,
    "verbose": true
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

```powershell
# Запуск в debug режиме
python run.py --debug

# Или через переменную окружения
$env:DEBUG = "true"
python run.py
```

### Пошаговая отладка

```python
# Добавить в код для отладки
import pdb; pdb.set_trace()

# Или использовать логирование
from src.utils.logging_system import get_logger
logger = get_logger("debug")
logger.debug(f"Variable value: {variable}")
```

## 🔄 Типичные сценарии восстановления

### Сценарий 1: "Ничего не работает"

```powershell
# Шаг 1: Полная остановка
python stop.py

# Шаг 2: Диагностика
python diagnose.py

# Шаг 3: Перезапуск
.\start.ps1

# Шаг 4: Проверка
curl http://localhost:9696/api/v1/health
```

### Сценарий 2: "Foundry работает, FastAPI нет"

```powershell
# Проверить Foundry
curl http://localhost:50477/v1/models

# Проверить конфигурацию
python test_config.py

# Запустить только FastAPI
python run.py
```

### Сценарий 3: "FastAPI работает, модели нет"

```powershell
# Проверить доступные модели
curl http://localhost:9696/api/v1/models

# Загрузить модель
curl -X POST http://localhost:9696/api/v1/models/load \
  -H "Content-Type: application/json" \
  -d '{"model_id": "qwen2.5-0.5b-instruct-generic-cpu:4"}'

# Включить автозагрузку
# Изменить config.json: "auto_load_default": true
```

## 📞 Получение помощи

### Сбор информации для поддержки

```powershell
# Создать отчет о системе
python diagnose.py > system_report.txt

# Собрать логи
Copy-Item logs\*.log support_logs\
Copy-Item logs\*.jsonl support_logs\

# Экспорт конфигурации
Copy-Item config.json support_logs\

# Информация о системе
systeminfo > support_logs\system_info.txt
```

### Полезные ссылки

- **GitHub Issues**: https://github.com/hypo69/FastApiFoundry-Docker/issues
- **Microsoft Foundry**: https://github.com/microsoft/foundry
- **FastAPI Docs**: https://fastapi.tiangolo.com/

### Контрольный список перед обращением

- [ ] Запустил `python diagnose.py`
- [ ] Проверил логи в папке `logs/`
- [ ] Попробовал перезапуск `.\start.ps1`
- [ ] Проверил конфигурацию `python test_config.py`
- [ ] Собрал системную информацию

---

**Предыдущий шаг**: [Конфигурация](configuration.md) | **Следующий шаг**: [Примеры](examples.md)