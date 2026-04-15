# 🔐 Environment Variables Setup - Complete Guide

**Версия:** 0.2.1  
**Проект:** FastApiFoundry (Docker)  
**Дата:** 9 декабря 2025  

---

## 📋 Созданные файлы

### 🔧 Основные файлы:
- **`.env.example`** - Пример файла с переменными окружения
- **`.env`** - Реальный файл с вашими данными (не коммитится в Git)
- **`config.json`** - Переменные окружения 

### 🛠️ Утилиты:
- **`check_env.py`** - Проверка и валидация переменных окружения
- **`setup-env.ps1`** - Интерактивная настройка переменных (PowerShell)
- **`src/utils/env_processor.py`** - Обработчик переменных в config.json

### 📚 Документация:
- **`docs/environment.md`** - Подробная документация по настройке

---

## 🚀 Быстрый старт

### 1. Настройка переменных окружения:

```powershell
# Интерактивная настройка (Windows)
.\setup-env.ps1

# Или вручную
cp .env.example .env
# Отредактируйте .env файл
```

### 2. Проверка конфигурации:

```bash
# Проверка переменных окружения
python check_env.py

# Проверка с показом секретов (осторожно!)
python check_env.py --show-secrets
```

### 3. Запуск приложения:

```bash
# Обычный запуск
python run.py

# Или полный запуск с Foundry (Windows)
.\start.ps1
```

---

## 🔑 Основные переменные

### GitHub Configuration:
```env
GITHUB_USER=your_username
GITHUB_PASSWORD=your_password_or_token
GITHUB_PAT=ghp_your_personal_access_token_here
```

### API Configuration:
```env
API_KEY=your_secret_api_key_here
SECRET_KEY=your_jwt_secret_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Foundry AI Configuration:
```env
FOUNDRY_BASE_URL=http://localhost:50477/v1
FOUNDRY_API_KEY=optional_foundry_api_key
FOUNDRY_TIMEOUT=30
```

---

## 🔧 Поддержка в config.json

Файл `config.json` поддерживает переменные окружения:

```json
{
  "security": {
    "api_key": "${API_KEY}",
    "secret_key": "${SECRET_KEY}",
    "cors_origins": "${CORS_ORIGINS:*}"
  },
  "foundry_ai": {
    "base_url": "${FOUNDRY_BASE_URL:http://localhost:50477/v1}",
    "timeout": "${FOUNDRY_TIMEOUT:300}"
  },
  "logging": {
    "level": "${LOG_LEVEL:INFO}"
  }
}
```

**Синтаксис:**
- `${VAR_NAME}` - обязательная переменная
- `${VAR_NAME:default}` - с значением по умолчанию

---

## 🛠️ Утилиты

### check_env.py
```bash
# Основная проверка
python check_env.py

# Показать реальные значения секретов
python check_env.py --show-secrets

# Показать команды для генерации ключей
python check_env.py --generate-keys
```

### setup-env.ps1 (PowerShell)
```powershell
# Интерактивная настройка
.\setup-env.ps1

# Принудительная перезапись
.\setup-env.ps1 -Force

# Автогенерация ключей
.\setup-env.ps1 -GenerateKeys
```

---

## 🔒 Безопасность

### ✅ Что сделано для везопасности:
- `.env` файл исключен из Git (.gitignore)
- Создан `.env.example` для примера
- Секретные значения маскируются при выводе
- Поддержка автогенерации безопасных ключей

### ⚠️ Важно:
- Никогда не коммитьте реальный `.env` файл
- Используйте сильные пароли и токены
- Регулярно обновляйте API ключи
- Не передавайте `.env` файл другим людям

---

## 🔄 Интеграция с приложением

### Автоматическая загрузка:
- `start.ps1` автоматически загружает переменные из `.env`
- `run.py` использует `env_processor` для обработки config.json
- Все переменные доступны через `os.getenv()`

### Обработка в коде:
```python
from src.utils.env_processor import process_config

# Загрузка конфигурации с переменными окружения
config = process_config('config.json')
```

---

## 🎯 Примеры использования

### 1. GitHub API:
```python
import os
github_token = os.getenv('GITHUB_PAT')
github_user = os.getenv('GITHUB_USER')
```

### 2. API Security:
```python
api_key = os.getenv('API_KEY')
secret_key = os.getenv('SECRET_KEY')
```

### 3. Foundry Connection:
```python
foundry_url = os.getenv('FOUNDRY_BASE_URL', 'http://localhost:50477/v1')
```

---

## 🚨 Troubleshooting

### Проблема: Переменные не загружаются
```bash
# Проверьте формат .env файла
python check_env.py

# Проверьте права доступа
ls -la .env  # Linux/Mac
dir .env     # Windows
```

### Проблема: Неверный формат переменных
```bash
# Проверьте синтаксис
cat .env | grep -v '^#' | grep '='
```

### Проблема: Config.json не обрабатывается
```bash
# Проверьте обработчик
python src/utils/env_processor.py config.json
```

---

## 📞 Поддержка

- **Документация**: [docs/environment.md](docs/environment.md)
- **Проверка**: `python check_env.py`
- **Настройка**: `.\setup-env.ps1`
- **GitHub**: https://github.com/hypo69/FastApiFoundry-Docker

---

**✅ Настройка переменных окружения завершена!**

Теперь ваше приложение поддерживает безопасное хранение чувствительных данных через `.env` файл.