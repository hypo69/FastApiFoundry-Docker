# 🚀 FastAPI Foundry - Руководство по развертыванию

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
FOUNDRY_TEMPERATURE=0.6
FOUNDRY_MAX_TOKENS=2048
FOUNDRY_TIMEOUT=300

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
RAG_INDEX_DIR=/opt/fastapi-foundry/rag_index
RAG_MODEL=sentence-transformers/all-MiniLM-L6-v2

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

# Логирование
StandardOutput=journal
StandardError=journal
SyslogIdentifier=fastapi-foundry

# Безопасность
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/fastapi-foundry/logs /opt/fastapi-foundry/rag_index

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

### 1. Docker Compose (рекомендуется)

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  fastapi-foundry:
    build: .
    container_name: fastapi-foundry-prod
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - API_WORKERS=4
      - LOG_LEVEL=INFO
      - FOUNDRY_BASE_URL=http://foundry:5272/v1/
    volumes:
      - ./logs:/app/logs
      - ./rag_index:/app/rag_index
      - ./prod.env:/app/.env
    depends_on:
      - foundry
    networks:
      - foundry-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  foundry:
    image: foundryai/foundry:latest
    container_name: foundry-prod
    restart: unless-stopped
    ports:
      - "5272:5272"
    volumes:
      - foundry-models:/app/models
    networks:
      - foundry-network

  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - fastapi-foundry
    networks:
      - foundry-network

volumes:
  foundry-models:

networks:
  foundry-network:
    driver: bridge
```

Запуск:

```bash
# Продакшн развертывание
docker-compose -f docker-compose.prod.yml up -d

# Мониторинг логов
docker-compose -f docker-compose.prod.yml logs -f

# Обновление
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Nginx конфигурация

Создать файл `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream fastapi_foundry {
        server fastapi-foundry:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name api.yourdomain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # API proxy
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://fastapi_foundry;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 300s;
        }

        # Health check
        location /health {
            proxy_pass http://fastapi_foundry/api/v1/health;
        }

        # Documentation
        location /docs {
            proxy_pass http://fastapi_foundry/docs;
        }
    }
}
```

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
sudo ufw deny 5272/tcp   # Блокировать прямой доступ к Foundry
sudo ufw enable
```

### 3. SSL сертификаты

```bash
# Let's Encrypt с Certbot
sudo apt install certbot
sudo certbot certonly --standalone -d api.yourdomain.com

# Копировать сертификаты для Nginx
sudo cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/key.pem
```

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

HEALTH_URL="http://localhost:8000/api/v1/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ FastAPI Foundry is healthy"
    exit 0
else
    echo "❌ FastAPI Foundry is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

### 3. Автоматический перезапуск

```bash
# Cron job для проверки и перезапуска
# Добавить в crontab: crontab -e
*/5 * * * * /opt/fastapi-foundry/health_check.sh || systemctl restart fastapi-foundry
```

## 🔄 Обновление и обслуживание

### 1. Обновление кода

```bash
# Остановить сервис
sudo systemctl stop fastapi-foundry

# Обновить код
cd /opt/fastapi-foundry
git pull origin main

# Обновить зависимости
source venv/bin/activate
pip install -r requirements.txt

# Запустить сервис
sudo systemctl start fastapi-foundry
```

### 2. Обновление RAG индекса

```bash
# Переиндексировать документы
python rag_indexer.py --docs-dir /path/to/docs --output-dir rag_index

# Перезагрузить RAG через API
curl -X POST http://localhost:8000/api/v1/rag/reload \
  -H "Authorization: Bearer your-api-key"
```

### 3. Резервное копирование

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/fastapi-foundry"
DATE=$(date +%Y%m%d_%H%M%S)

# Создать директорию
mkdir -p $BACKUP_DIR

# Бэкап конфигурации
tar -czf $BACKUP_DIR/config_$DATE.tar.gz .env nginx/

# Бэкап RAG индекса
tar -czf $BACKUP_DIR/rag_index_$DATE.tar.gz rag_index/

# Бэкап логов (последние 7 дней)
find logs/ -name "*.log" -mtime -7 | tar -czf $BACKUP_DIR/logs_$DATE.tar.gz -T -

echo "Backup completed: $BACKUP_DIR"
```

## 🚨 Устранение проблем

### 1. Сервис не запускается

```bash
# Проверить статус
sudo systemctl status fastapi-foundry

# Проверить логи
sudo journalctl -u fastapi-foundry --no-pager

# Проверить конфигурацию
python -c "from config import settings; print(settings)"
```

### 2. Foundry недоступен

```bash
# Проверить Foundry
curl http://localhost:5272/v1/models

# Проверить Docker контейнер
docker ps | grep foundry
docker logs foundry-container-name
```

### 3. RAG не работает

```bash
# Проверить индекс
ls -la rag_index/

# Проверить зависимости
pip list | grep -E "(sentence-transformers|faiss)"

# Переиндексировать
python rag_indexer.py --docs-dir docs/ --output-dir rag_index/
```

### 4. Высокая нагрузка

```bash
# Мониторинг ресурсов
htop
docker stats

# Увеличить количество workers
# В .env: API_WORKERS=8

# Настроить rate limiting в Nginx
# limit_req zone=api burst=50 nodelay;
```

## 📈 Масштабирование

### 1. Горизонтальное масштабирование

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  fastapi-foundry:
    build: .
    deploy:
      replicas: 4
    environment:
      - API_WORKERS=2
    # ... остальная конфигурация

  nginx:
    # Load balancer конфигурация
    volumes:
      - ./nginx/nginx-lb.conf:/etc/nginx/nginx.conf
```

### 2. Кэширование

```python
# Добавить Redis для кэширования
# requirements.txt
redis>=4.5.0

# В main.py
import redis
redis_client = redis.Redis(host='redis', port=6379, db=0)
```

### 3. Мониторинг производительности

```bash
# Установить Prometheus + Grafana
# Добавить метрики в FastAPI
pip install prometheus-fastapi-instrumentator
```

## 📞 Поддержка

### Полезные команды

```bash
# Проверка всех сервисов
curl http://localhost:8000/api/v1/health
curl http://localhost:5272/v1/models

# Тестирование API
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{"prompt": "Test prompt"}'

# Просмотр метрик
docker stats
systemctl status fastapi-foundry
```

### 📚 Документация и ресурсы

- **[📂 Индекс документации](DOCS_INDEX.md)** - Полный каталог всех документов
- **[🚀 Быстрый старт](README.md)** - Основная документация
- **[🏗️ Архитектура](howto.md)** - Подробное руководство по компонентам
- **[🌐 Туннели](TUNNEL_GUIDE.md)** - Публичный доступ к API
- **API Docs**: http://localhost:8000/docs - Автоматическая документация
- **Health Check**: http://localhost:8000/api/v1/health - Мониторинг
- **Конфигурация**: http://localhost:8000/api/v1/config - Текущие настройки

### 🐛 Поддержка и обратная связь

- **GitHub Issues**: https://github.com/hypo69/aistros/issues
- **Email**: support@aistros.com
- **Website**: https://aistros.com

---

**FastAPI Foundry Deployment Guide v1.0.0**  
📚 [Полная документация](DOCS_INDEX.md) | 🚀 [Быстрый старт](README.md) | 🏗️ [Архитектура](howto.md)  
© 2025 AiStros Team | Часть экосистемы AiStros