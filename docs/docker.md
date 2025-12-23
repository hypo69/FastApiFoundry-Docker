# 🐳 Docker запуск

**Быстрый старт с Docker для FastAPI Foundry**

## 🚀 Первый запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/hypo69/FastApiFoundry-Docker.git
cd FastApiFoundry-Docker

# 2. Настроить конфигурацию
cp .env.example .env

# 3. Первый запуск (с сборкой)
docker-compose up --build -d
```

## ⚡ Ежедневное использование

**Сборка нужна только при первом запуске или изменении кода!**

### Запуск
```bash
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

## 🔄 При изменении кода

```bash
# Пересборка и запуск
docker-compose up --build -d

# Или отдельно
docker-compose build
docker-compose up -d
```

## 📊 Управление контейнерами

### Статус
```bash
docker-compose ps
```

### Логи
```bash
# Все логи
docker-compose logs -f

# Только последние
docker-compose logs --tail=50 -f
```

### Вход в контейнер
```bash
docker-compose exec fastapi-foundry bash
```

### Проверка здоровья
```bash
curl http://localhost:8000/api/v1/health
```

## 🔧 Полезные команды

### Очистка
```bash
# Удалить контейнеры и образы
docker-compose down --rmi all

# Очистить volumes
docker-compose down -v

# Полная очистка Docker
docker system prune -a
```

### Обновление
```bash
# Обновить код
git pull

# Пересобрать и запустить
docker-compose up --build -d
```

## 📁 Структура volumes

```
./logs:/app/logs              # Логи приложения
./rag_index:/app/rag_index    # RAG индекс
./.env:/app/.env:ro           # Конфигурация (только чтение)
./src/config.json:/app/src/config.json:ro  # Настройки приложения
```

## 🌐 Доступ к приложению

- **API**: http://localhost:8000
- **Документация**: http://localhost:8000/docs
- **Веб-интерфейс**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/v1/health

## ⚠️ Важные моменты

1. **Первый запуск**: всегда используйте `--build`
2. **Ежедневно**: просто `docker-compose up -d`
3. **После изменений**: `docker-compose up --build -d`
4. **Логи**: `docker-compose logs -f` для отладки
5. **Остановка**: `docker-compose down` сохраняет данные

## 🔍 Troubleshooting

### Контейнер не запускается
```bash
# Проверить логи
docker-compose logs

# Проверить статус
docker-compose ps

# Пересобрать с нуля
docker-compose down
docker-compose up --build -d
```

### Порт занят
```bash
# Изменить порт в .env
echo "PORT=8001" >> .env

# Или в docker-compose.yml
# ports:
#   - "8001:8000"
```

### Проблемы с volumes
```bash
# Пересоздать volumes
docker-compose down -v
docker-compose up -d
```

---

**Готово!** Теперь FastAPI Foundry работает в Docker контейнере.