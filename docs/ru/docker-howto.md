
# Docker Compose — запуск и работа с проектом

## Требования
- Установлен Docker
- Docker Compose (входит в Docker Desktop)

Проверка:
```bash
docker --version
docker compose version
````

---

## Первый запуск проекта

Перейти в директорию с `docker-compose.yml`:

```bash
cd path/to/project
```

Первый запуск с пересборкой образов:

```bash
docker compose up -d --build
```

---

## Повторный запуск (без пересборки)

Если код не менялся или используется volume:

```bash
docker compose up -d
```

---

## Перезапуск контейнеров

Перезапуск всех сервисов:

```bash
docker compose restart
```

Перезапуск конкретного сервиса:

```bash
docker compose restart app
```

---

## Изменение кода

### 1. Код прокинут через volume

Если код монтируется как volume (например, backend / frontend):

```yaml
volumes:
  - .:/app
```

➡️ **Ничего пересобирать не нужно**, просто обнови страницу или перезапусти сервис:

```bash
docker compose restart app
```

---

### 2. Код внутри Docker-образа

Если код копируется через `Dockerfile` (`COPY . /app`):

После изменений **обязательно пересобрать**:

```bash
docker compose up -d --build
```

---

## Просмотр статуса и логов

Список контейнеров:

```bash
docker compose ps
```

Логи всех сервисов:

```bash
docker compose logs
```

Логи конкретного сервиса:

```bash
docker compose logs -f app
```

---

## Вход в контейнер

```bash
docker compose exec app sh
```

или

```bash
docker compose exec app bash
```

---

## Остановка проекта

Остановить контейнеры:

```bash
docker compose down
```

Остановить и удалить volumes (⚠️ удалит данные БД):

```bash
docker compose down -v
```

---

## Полная очистка (если что-то сломалось)

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## Полезные команды

```bash
docker compose pull        # обновить образы
docker compose config      # проверить docker-compose.yml
docker system prune        # очистка неиспользуемых ресурсов
```

---

## Типовой workflow

```bash
# первый запуск
docker compose up -d --build

# разработка
изменил код → refresh / restart

# если менялся Dockerfile или зависимости
docker compose up -d --build

# остановка
docker compose down
```

```

---
