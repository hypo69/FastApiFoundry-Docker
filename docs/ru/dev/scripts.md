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
| `Update-Project.ps1` | Проверка обновлений из GitHub и переключение на новый тег |
| `generate-ps-docs.ps1` | Генерация Markdown-документации из PowerShell comment-based help |
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
2. Находит процесс на этом порту через `Get-NetTCPConnection` и убивает его
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

---

## Update-Project.ps1

Проверяет GitHub на наличие нового релиза и предлагает обновиться. Автоматически запускается из `start.ps1`.

```powershell
# Интерактивный режим
powershell -ExecutionPolicy Bypass -File .\scripts\Update-Project.ps1

# Без подтверждения (авто-принятие)
powershell -ExecutionPolicy Bypass -File .\scripts\Update-Project.ps1 -Silent

# Принудительное обновление даже если версия актуальна
powershell -ExecutionPolicy Bypass -File .\scripts\Update-Project.ps1 -Force
```

**Что делает:**

1. Читает текущую версию из файла `VERSION` или `git describe --tags`
2. Делает `git fetch --tags` и находит последний тег на remote
3. Если есть обновление — предлагает переключиться (`git checkout <tag>`)
4. Запускает `install.ps1` для обновления зависимостей

| Параметр | Описание |
|---|---|
| `-Silent` | Авто-принятие обновления без вопроса |
| `-Force` | Обновить даже если версия уже актуальна |

!!! note
    Требует `git` в `PATH`. Если проект запущен не из git-репозитория, проверка пропускается автоматически.

---

## generate-ps-docs.ps1

Генерирует Markdown-документацию из PowerShell comment-based help (блоки `<# .SYNOPSIS .DESCRIPTION #>`). Используется в GitHub Actions workflow `deploy-docs.yml`.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\generate-ps-docs.ps1
```

**Что делает:**

1. Сканирует `mcp-powershell-servers/src/servers/` и `scripts/` на все `.ps1` файлы
2. Извлекает `.SYNOPSIS`, `.DESCRIPTION`, `.NOTES` из comment-based help
3. Генерирует `docs/ru/dev/powershell/<name>.md` для каждого скрипта
4. Создаёт `docs/ru/dev/powershell/index.md` со ссылками на все страницы

!!! note
    Чтобы скрипт попал в документацию, добавьте в него блок `<# .SYNOPSIS ... #>`.

---

## build_exes.ps1

Собирает `install.exe` и `launcher.exe` — обёртки над PowerShell скриптами для запуска двойным кликом. Использует встроенный компилятор `csc.exe` (.NET Framework 4), внешние инструменты не нужны.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_exes.ps1
```

**Что делает:**

1. Находит `csc.exe` в `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\`
2. Генерирует C# обёртку, которая находит `.ps1` рядом с `.exe` и запускает его через `powershell.exe -ExecutionPolicy Bypass`
3. Компилирует `install.exe` (обёртка `install.ps1`) и `launcher.exe` (обёртка `launcher.ps1`)
4. Кладёт файлы в корень проекта

!!! warning
    Требует .NET Framework 4 (есть на любом Windows 7+). Не требует Visual Studio или MSBuild.
