# 📜 Операционные скрипты (scripts/)

Служебные PowerShell скрипты для управления runtime-компонентами системы.

## Файлы

| Скрипт | Описание |
|---|---|
| `llama-start.ps1` | Запуск `llama-server.exe` с выбранной GGUF моделью |
| `load-model.ps1` | Загрузка модели в Foundry через CLI |
| `unload-model.ps1` | Выгрузка модели из Foundry |
| `list-models.ps1` | Список доступных и загруженных моделей Foundry |
| `download-model.ps1` | Скачивание модели через Foundry CLI |
| `hf-download-model.ps1` | Скачивание модели с HuggingFace Hub |
| `hf-models.ps1` | Поиск и просмотр моделей на HuggingFace |
| `service-status.ps1` | Проверка статуса Foundry и FastAPI сервисов |
| `build_exes.ps1` | Сборка `install.exe` и `launcher.exe` из PowerShell скриптов |
| `restart-mkdocs.ps1` | Перезапуск сервера документации MkDocs |
| `create_requirements.ps1` | Генерация `requirements.txt` (режимы: `freeze`, `pipreqs`, `clean`) |

## Использование

```powershell
# Запуск llama.cpp с моделью
.\scripts\llama-start.ps1

# Загрузить модель в Foundry
.\scripts\load-model.ps1 -ModelId "qwen2.5-0.5b-instruct-generic-cpu"

# Скачать модель с HuggingFace
.\scripts\hf-download-model.ps1 -Repo "bartowski/gemma-7b-it-GGUF" -LocalDir "~\hf_models"

# Проверить статус сервисов
.\scripts\service-status.ps1

# Перезапустить сервер документации
.\scripts\restart-mkdocs.ps1

# Создать requirements.txt из импортов в коде
.\scripts\create_requirements.ps1 -Mode pipreqs

# Создать requirements.txt из текущего venv
.\scripts\create_requirements.ps1 -Mode freeze

# Пересоздать venv с нуля
.\scripts\create_requirements.ps1 -Mode clean
```

## Правила

Любые изменения в параметрах запуска моделей должны отражаться в конфигурации `.env` и `config.json`.

Путь к `llama-server.exe` задаётся через переменную `LLAMA_SERVER_PATH` в `.env`.
