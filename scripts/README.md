<!--
===============================================================================
Название процесса: PowerShell скрипты для управления Foundry
===============================================================================
Описание:
    Скрипты для ручного управления Foundry CLI из терминала.
    Используются разработчиком напрямую — не вызываются из Python кода.

    ПОЧЕМУ СКРИПТЫ ОСТАЛИСЬ, ХОТЯ API ВЫЗЫВАЕТ foundry НАПРЯМУЮ:
      API (foundry_models.py) вызывает foundry CLI через Python subprocess.
      Скрипты здесь — для удобства разработчика в терминале:
      короткие команды вместо длинных foundry model download <id>.

File: scripts/README.md
Project: FastApiFoundry (Docker)
Version: 0.3.4
Author: hypo69
Copyright: © 2026 hypo69
Copyright: © 2026 hypo69
===============================================================================
-->

# scripts/ — Утилиты для управления Foundry

Скрипты для ручного управления Foundry CLI из терминала.

```
scripts/
├── download-model.ps1   # Скачивание модели в кэш
├── load-model.ps1       # Загрузка модели в сервис
├── unload-model.ps1     # Выгрузка модели из сервиса
├── list-models.ps1      # Список моделей
├── service-status.ps1   # Статус Foundry сервиса
└── start/               # Архив устаревших скриптов запуска
```

---

## Скрипты

### download-model.ps1
Скачивание модели в локальный кэш Foundry (`foundry model download`).
Нужно выполнить один раз перед первым использованием модели.

```powershell
.\scripts\download-model.ps1 -ModelId "qwen2.5-0.5b-instruct-generic-cpu:4"
.\scripts\download-model.ps1 -ModelId "deepseek-r1-distill-qwen-7b-generic-cpu:3"
```

### load-model.ps1
Загрузка скачанной модели в Foundry сервис (`foundry model load`).
После загрузки модель доступна через API на `/api/v1/generate`.

```powershell
.\scripts\load-model.ps1 -ModelId "qwen2.5-0.5b-instruct-generic-cpu:4"
```

### unload-model.ps1
Выгрузка модели из памяти (`foundry model unload`).
Освобождает RAM/VRAM.

```powershell
.\scripts\unload-model.ps1 -ModelId "qwen2.5-0.5b-instruct-generic-cpu:4"
```

### list-models.ps1
Список моделей. Параметр `-Type`:
- `available` (по умолчанию) — все доступные модели из каталога Foundry
- `loaded` — только загруженные в сервис

```powershell
.\scripts\list-models.ps1                  # доступные
.\scripts\list-models.ps1 -Type loaded    # загруженные
```

### service-status.ps1
Статус Foundry сервиса (`foundry service status`).

```powershell
.\scripts\service-status.ps1
```

---

## Типичный сценарий первого запуска

```powershell
# 1. Скачать модель (~300 MB, один раз)
.\scripts\download-model.ps1 -ModelId "qwen2.5-0.5b-instruct-generic-cpu:4"

# 2. Запустить сервис
foundry service start

# 3. Загрузить модель в сервис
.\scripts\load-model.ps1 -ModelId "qwen2.5-0.5b-instruct-generic-cpu:4"

# 4. Запустить FastAPI
venv\Scripts\python.exe run.py
```

---

## Связь с API

Те же операции доступны через REST API (вызывают `foundry` CLI напрямую):

| Скрипт | API endpoint |
|--------|-------------|
| `download-model.ps1` | `POST /api/v1/foundry/models/download` |
| `load-model.ps1` | `POST /api/v1/foundry/models/load` |
| `unload-model.ps1` | `POST /api/v1/foundry/models/unload` |
| `list-models.ps1` | `GET /api/v1/foundry/models/loaded` |
| `service-status.ps1` | `GET /api/v1/foundry/status` |
