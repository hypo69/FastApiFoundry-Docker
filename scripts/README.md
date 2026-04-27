# ⚙️ Операционные скрипты (scripts/)

Вспомогательные PowerShell скрипты для управления сервисами, моделями и документацией.
Запускаются из корня проекта.

## Список скриптов

| Скрипт | Назначение |
|---|---|
| `Create-Requirements.ps1` | Обновление `requirements.txt` (режимы: pipreqs, freeze) |
| `Restart-MkDocs.ps1` | Перезапуск сервера документации MkDocs |
| `Start-Llama.ps1` | Запуск `llama-server.exe` с выбранной GGUF моделью |
| `Load-Model.ps1` | Загрузка модели в Foundry через CLI |
| `Unload-Model.ps1` | Выгрузка модели из Foundry |
| `List-Models.ps1` | Список доступных и загруженных моделей Foundry |
| `Download-Model.ps1` | Скачивание модели через Foundry CLI |
| `Hf-DownloadModel.ps1` | Скачивание модели с HuggingFace Hub |
| `Hf-Models.ps1` | Поиск и просмотр моделей на HuggingFace |
| `Get-ServiceStatus.ps1` | Проверка статуса Foundry и FastAPI |
| `Update-Project.ps1` | Проверка обновлений из GitHub и переключение на новый тег |
| `Generate-PsDocs.ps1` | Генерация Markdown-документации из PowerShell comment-based help |
| `Build-Exes.ps1` | Сборка `install.exe` и `launcher.exe` |
| `Run-Qa.ps1` | Запуск QA-цикла (тесты + покрытие) |
| `Watch-Tests.ps1` | Вотчер: автозапуск тестов при изменении `*.py` |
| `Clear-Reports.ps1` | Очистка директории `tests/reports/` |
| `ReinstallFoundry.ps1` | Полная переустановка Foundry Local (CI/QA) |

## Примеры использования

```powershell
# Обновить requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\Create-Requirements.ps1 -Mode pipreqs

# Перезапустить MkDocs
powershell -ExecutionPolicy Bypass -File .\scripts\Restart-MkDocs.ps1

# Запустить llama.cpp
powershell -ExecutionPolicy Bypass -File .\scripts\Start-Llama.ps1

# Загрузить модель в Foundry
.\scripts\Load-Model.ps1 -ModelId "qwen3-0.6b-generic-cpu:4:4"

# Скачать модель с HuggingFace
.\scripts\Hf-DownloadModel.ps1 -Repo "bartowski/gemma-7b-it-GGUF" -LocalDir "D:\models"

# Проверить статус сервисов
.\scripts\Get-ServiceStatus.ps1

# Запустить QA
powershell -ExecutionPolicy Bypass -File .\scripts\Run-Qa.ps1

# Запустить вотчер тестов
powershell -ExecutionPolicy Bypass -File .\scripts\Watch-Tests.ps1
```

## Примечание

Артефакты QA (отчёты покрытия) сохраняются в `tests/reports/` и генерируются автоматически скриптом `Run-Qa.ps1`.
