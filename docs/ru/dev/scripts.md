# Операционные скрипты

Все скрипты находятся в `scripts/` и запускаются из корня проекта.

## Список скриптов

| Скрипт | Назначение |
|---|---|
| `restart-mkdocs.ps1` | Перезапуск сервера документации MkDocs |
| `llama-start.ps1` | Запуск `llama-server.exe` с выбранной GGUF моделью |
| `load-model.ps1` | Загрузка модели в Foundry через CLI |
| `unload-model.ps1` | Выгрузка модели из Foundry |
| `list-models.ps1` | Список доступных и загруженных моделей Foundry |
| `download-model.ps1` | Скачивание модели через Foundry CLI |
| `hf-download-model.ps1` | Скачивание модели с HuggingFace Hub |
| `hf-models.ps1` | Поиск и просмотр моделей на HuggingFace |
| `service-status.ps1` | Проверка статуса Foundry и FastAPI |
| `build_exes.ps1` | Сборка `install.exe` и `launcher.exe` |

---

## restart-mkdocs.ps1

Останавливает текущий процесс MkDocs и запускает новый.

Порт читается из `config.json → docs_server.port` (по умолчанию `9697`).

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\restart-mkdocs.ps1
```

**Что делает:**

1. Читает порт из `config.json`
2. Находит процесс на этом порту через `netstat` и убивает его
3. Ждёт 800 мс (освобождение порта)
4. Запускает `mkdocs serve` в новом окне через `venv\Scripts\python.exe`

---

## llama-start.ps1

Запускает `llama-server.exe` из `bin/` с моделью, указанной в `.env`.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\llama-start.ps1
```

Переменные `.env`:

```env
LLAMA_MODEL_PATH=D:\models\qwen2.5-0.5b-q4_k_m.gguf
LLAMA_SERVER_PATH=.\bin\llama-b8802-bin-win-cpu-x64\llama-server.exe
```

---

## load-model.ps1 / unload-model.ps1

Загрузка и выгрузка модели в Microsoft Foundry Local через CLI.

```powershell
.\scripts\load-model.ps1 -ModelId "qwen2.5-0.5b-instruct-generic-cpu:4"
.\scripts\unload-model.ps1 -ModelId "qwen2.5-0.5b-instruct-generic-cpu:4"
```

---

## hf-download-model.ps1

Скачивание GGUF модели с HuggingFace Hub.

```powershell
.\scripts\hf-download-model.ps1 -Repo "bartowski/gemma-7b-it-GGUF" -LocalDir "D:\models"
```

Требует `HF_TOKEN` в `.env` для закрытых моделей (Gemma, Llama).

---

## service-status.ps1

Проверяет статус Foundry и FastAPI, выводит порты и состояние процессов.

```powershell
.\scripts\service-status.ps1
```
