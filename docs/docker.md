# 🐳 Docker развертывание FastAPI Foundry

**Версия:** 1.0.0  
**Дата:** 20 декабря 2025  

---

## 🎯 Зачем нужен Docker?

Docker позволяет:
- **Упаковать** все приложение с зависимостями в один контейнер
- **Переносить** между машинами без проблем совместимости
- **Изолировать** приложение от системы
- **Масштабировать** и управлять развертыванием

---

## 🚀 Быстрый старт

### 1. Сборка контейнера
```bash
# Linux/Mac
./docker-manager.sh build

# Windows PowerShell
.\docker-manager.ps1 build

# Или напрямую
docker build -t fastapi-foundry .
```

### 2. Запуск контейнера
```bash
# Через docker-compose (рекомендуется)
docker-compose up -d

# Или через скрипт
./docker-manager.sh run      # Linux/Mac
.\docker-manager.ps1 run   # Windows PowerShell
```

### 3. Проверка работы
```bash
# Проверка статуса
curl http://localhost:8000/api/v1/health

# Веб-интерфейс
open http://localhost:8000
```

---

## 📦 Экспорт и перенос контейнера

### Экспорт образа
```bash
# Через скрипт
./docker-manager.sh export

# Или напрямую
docker save -o fastapi-foundry-latest.tar fastapi-foundry:latest
```

### Перенос на другую машину
```bash
# 1. Скопировать файл на целевую машину
scp fastapi-foundry-latest.tar user@target-machine:/path/

# 2. На целевой машине импортировать образ
docker load -i fastapi-foundry-latest.tar

# 3. Скопировать docker-compose.yml и .env
scp docker-compose.yml .env user@target-machine:/path/

# 4. Запустить на целевой машине
docker-compose up -d
```

---

## 🛠️ Управление контейнером

### Основные команды
```bash
# Статус контейнера
docker-compose ps

# Логи
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Вход в контейнер
docker exec -it fastapi-foundry /bin/bash
```

### Через скрипты управления
```bash
# Linux/Mac
./docker-manager.sh status    # Статус
./docker-manager.sh logs      # Логи
./docker-manager.sh stop      # Остановка
./docker-manager.sh restart   # Перезапуск
./docker-manager.sh shell     # Вход в контейнер

# Windows PowerShell
.\docker-manager.ps1 status
.\docker-manager.ps1 logs
.\docker-manager.ps1 stop
.\docker-manager.ps1 restart
.\docker-manager.ps1 shell
```

---

## 📁 Структура контейнера

```
/app/                    # Рабочая директория
├── src/                # Исходный код
├── static/             # Веб-интерфейс
├── docs/               # Документация
├── logs/               # Логи (volume)
├── rag_index/          # RAG индекс (volume)
├── run.py              # Точка входа
└── .env                # Конфигурация
```

### Volumes (постоянные данные)
- `./logs:/app/logs` - Логи приложения
- `./rag_index:/app/rag_index` - RAG индекс
- `./.env:/app/.env` - Конфигурация

---

## ⚙️ Конфигурация

### Переменные окружения
```bash
# В .env файле
HOST=0.0.0.0
PORT=8000
FOUNDRY_HOST=host.docker.internal  # Для доступа к Foundry на хосте
FOUNDRY_PORT=50477
RAG_ENABLED=true
```

### Порты
- **8000** - FastAPI Foundry API и веб-интерфейс
- **50477** - Foundry сервер (должен быть доступен с хоста)

---

## 🔧 Отладка проблем

### Проверка контейнера
```bash
# Статус контейнера
docker ps | grep fastapi-foundry

# Логи контейнера
docker logs fastapi-foundry

# Вход в контейнер для отладки
docker exec -it fastapi-foundry /bin/bash
```

### Проверка сети
```bash
# Проверка портов
netstat -tulpn | grep :8000

# Проверка доступности Foundry из контейнера
docker exec fastapi-foundry curl http://host.docker.internal:50477/v1/models
```

### Проблемы с Foundry
```bash
# Если Foundry на том же хосте, используйте:
FOUNDRY_HOST=host.docker.internal

# Для Linux может потребоваться:
FOUNDRY_HOST=172.17.0.1
```

---

## 🚀 Продакшн развертывание

### С Nginx reverse proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### С SSL сертификатом
```bash
# Добавить в docker-compose.yml
services:
  fastapi-foundry:
    # ... существующая конфигурация
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.fastapi.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.fastapi.tls.certresolver=letsencrypt"
```

---

## 📊 Мониторинг

### Health check
```bash
# Встроенная проверка здоровья
curl http://localhost:8000/api/v1/health

# Docker health check
docker inspect fastapi-foundry | grep Health -A 10
```

### Логи
```bash
# Логи контейнера
docker-compose logs -f

# Логи приложения
tail -f logs/app.log
```

---

## 🧹 Очистка

### Удаление контейнера и образа
```bash
# Через скрипт
./docker-manager.sh clean

# Или напрямую
docker-compose down
docker rmi fastapi-foundry:latest
```

### Очистка Docker системы
```bash
# Удаление неиспользуемых образов
docker image prune

# Полная очистка
docker system prune -a
```

---

## 📝 Примеры использования

### Разработка
```bash
# Сборка и запуск для разработки
docker build -t fastapi-foundry-dev .
docker run -p 8000:8000 -v $(pwd):/app fastapi-foundry-dev
```

### Продакшн
```bash
# Запуск в продакшн режиме
docker-compose -f docker-compose.prod.yml up -d
```

### Масштабирование
```bash
# Запуск нескольких экземпляров
docker-compose up -d --scale fastapi-foundry=3
```

### Тестирование API
```bash
# Запуск контейнера для тестов
docker-compose up -d

# Тестирование через Python клиент
python example_client.py
python example_model_client.py

# Тестирование через cURL
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/models
```

---

**💡 Совет:** Используйте `docker-manager.sh` (Linux/Mac) или `docker-manager.ps1` (Windows PowerShell) для упрощения управления контейнером.

**⚠️ Важно:** Убедитесь, что Foundry сервер доступен из контейнера через `host.docker.internal` или соответствующий IP адрес.

---

## 📁 Файлы проекта

### Основные файлы Docker
- **Dockerfile** - Описание образа контейнера
- **docker-compose.yml** - Оркестрация сервисов
- **.dockerignore** - Исключения при сборке
- **docker-manager.ps1** - Скрипт управления (Windows)
- **docker-manager.sh** - Скрипт управления (Linux/Mac)

### Примеры и тесты
- **example_client.py** - Пример клиента API
- **example_model_client.py** - Пример управления моделями
- **test_system.py** - Системные тесты