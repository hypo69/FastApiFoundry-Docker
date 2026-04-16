# 🚀 FastAPI Foundry - Руководство по развертыванию

---
**📚 Навигация:** [🏠 Главная](README.md) | [📦 Установка](installation.md) | [🚀 Запуск](running.md) | [🎯 Лончеры](launchers.md) | [📖 Использование](usage.md) | [⚙️ Настройка](configuration.md) | [📊 Примеры](examples.md) | [🛠️ Рецепты](howto.md) | [🔌 MCP](mcp_integration.md) | [🌍 Туннели](tunnel_guide.md) | [🐳 Docker](docker.md) | [🛠️ Разработка](development.md) | [🚀 Развертывание](deployment.md) | [🔧 cURL](curl_commands.md) | [📋 Проект](project_info.md)
---

**Полное руководство по установке и настройке FastAPI Foundry на сервере**

## 📋 Системные требования

### Минимальные требования
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Python**: 3.8+
- **RAM**: 4GB (8GB+ рекомендуется для RAG)
- **Диск**: 2GB свободного места
- **CPU**: 2+ ядра

### Рекомендуемые требования
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **RAM**: 16GB+
- **Диск**: 10GB+ SSD
- **CPU**: 4+ ядра

## 🛠️ Быстрая установка

### 1. Автоматическая установка

```bash
# Клонировать проект
git clone https://github.com/hypo69/FastApiFoundry.git
cd FastApiFoundry

# Запустить автоматический установщик
python install.py

# Запустить сервер
python run.py --dev
```

### 2. Ручная установка

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить конфигурацию
cp .env.example .env
# Отредактировать .env

# 4. Создать директории
mkdir -p logs rag_index

# 5. Запустить сервер
python run.py
```

## ⚙️ Конфигурация для продакшн

### 1. Настройка .env файла

```env
# Foundry настройки
FOUNDRY_BASE_URL=http://localhost:5272/v1/
FOUNDRY_DEFAULT_MODEL=deepseek-r1-distill-qwen-7b-generic-cpu:3

# API настройки
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
API_WORKERS=4

# Безопасность
API_KEY=your-super-secret-api-key-here
CORS_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]

# RAG настройки
RAG_ENABLED=true

# Логирование
LOG_LEVEL=INFO
LOG_FILE=/var/log/fastapi-foundry/app.log
```

### 2. Системный сервис (Linux)

Создать файл `/etc/systemd/system/fastapi-foundry.service`:

```ini
[Unit]
Description=FastAPI Foundry Server
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/fastapi-foundry
Environment=PATH=/opt/fastapi-foundry/venv/bin
ExecStart=/opt/fastapi-foundry/venv/bin/python run.py --prod
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Активировать сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi-foundry
sudo systemctl start fastapi-foundry
sudo systemctl status fastapi-foundry
```

## 🐳 Docker развертывание

Для развертывания с использованием Docker, см. подробное руководство **[🐳 Docker](docker.md)**.

## 🔐 Безопасность

### 1. API ключи

```bash
# Генерация безопасного API ключа
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Добавить в .env
API_KEY=generated-secure-key-here
```

### 2. Firewall настройки

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # Блокировать прямой доступ к FastAPI
sudo ufw enable
```

### 3. SSL сертификаты

Для production рекомендуется использовать `nginx` в качестве reverse proxy с SSL сертификатами от Let's Encrypt.

## 📊 Мониторинг и логирование

### 1. Логи

```bash
# Системные логи
sudo journalctl -u fastapi-foundry -f

# Docker логи
docker-compose logs -f fastapi-foundry

# Файловые логи
tail -f /var/log/fastapi-foundry/app.log
```

### 2. Мониторинг здоровья

```bash
# Скрипт проверки здоровья
#!/bin/bash
# health_check.sh

HEALTH_URL="http://localhost:9696/api/v1/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ FastAPI Foundry is healthy"
    exit 0
else
    echo "❌ FastAPI Foundry is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

---
## 🚀 Навигация по разделу "Развертывание"

| Документ | Описание |
|----------|----------|
| [🐳 Docker](docker.md) | Контейнеризация и развертывание |
| [🚀 Развертывание](deployment.md) | Production развертывание |

## 🔗 Другие разделы

| Раздел | Документы |
|--------|-----------|
| **📖 Начало работы** | [📦 Установка](installation.md) • [🚀 Запуск](running.md) • [🎯 Лончеры](launchers.md) • [📖 Использование](usage.md) • [⚙️ Настройка](configuration.md) |
| **🛠️ Практика** | [📊 Примеры](examples.md) • [🛠️ Рецепты](howto.md) |
| **🌐 Интеграция** | [🔌 MCP](mcp_integration.md) • [🌍 Туннели](tunnel_guide.md) |
| **👨‍💻 Разработка** | [🛠️ Development](development.md) • [🔧 cURL](curl_commands.md) • [📋 Проект](project_info.md) |

---

**📚 Быстрые ссылки:** [⬅️ Назад к оглавлению](README.md) | [📖 Все документы](README.md#-документация)

**FastAPI Foundry** - часть экосистемы AiStros  
© 2025 AiStros Team