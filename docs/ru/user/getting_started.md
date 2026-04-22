# Быстрый старт

## Первый запуск — установка + старт

Если `venv\` ещё не создан, `start.ps1` автоматически запустит `install.ps1`.
`install.ps1` после установки базовых пакетов откроет браузер с GUI-установщиком на **http://localhost:9698**.

После завершения установки в браузере — запустите сервер:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

После запуска веб-интерфейс доступен по адресу **http://localhost:9696**

!!! tip "Только установка (без запуска сервера)"
    ```powershell
    powershell -ExecutionPolicy Bypass -File .\install.ps1
    ```
    Подробнее: [Установка](installation.md)

---

## Что происходит при запуске

`start.ps1` — единственная точка входа. Он последовательно проходит 8 этапов,
затем передаёт управление `run.py`, который запускает FastAPI через Uvicorn.

=== "Для пользователя"

    1. **Проверка окружения** — если `venv\` нет, автоматически запускается установка
    2. **Загрузка настроек** — переменные из `.env` попадают в окружение процесса
    3. **Foundry AI** — ищет запущенный Foundry, при необходимости запускает его
    4. **Документация** — опционально собирает и запускает локальный сервер MkDocs
    5. **llama.cpp** — опционально запускает локальный inference сервер
    6. **Installer** — останавливает GUI-установщик (если ещё работает)
    7. **Очистка** — останавливает предыдущий экземпляр FastAPI (если был)
    8. **Запуск** — стартует FastAPI сервер, открывается http://localhost:9696

=== "Для разработчика"

    ```
    start.ps1
      │
      ├─[1] Test-Path venv\Scripts\python.exe
      │      ├─ найден → . venv\Scripts\Activate.ps1
      │      └─ не найден → .\install.ps1 → создать venv
      │
      ├─[2] Load-EnvFile ".env"
      │      └─ SetEnvironmentVariable KEY=VALUE (секреты маскируются ***)
      │
      ├─[3] объявление функций Test-FoundryCli, Get-FoundryPort
      │
      ├─[4] Get-FoundryPort()
      │      ├─ Get-Process "Inference.Service.Agent*" → найден?
      │      │   ├─ да  → netstat -ano | grep PID | grep LISTENING
      │      │   │         → GET /v1/models → HTTP 200
      │      │   │         → FOUNDRY_DYNAMIC_PORT=<port>
      │      │   │         → FOUNDRY_BASE_URL=http://localhost:<port>/v1/
      │      │   └─ нет → Test-FoundryCli?
      │      │             ├─ да  → foundry service start (свёрнутое окно)
      │      │             │         → опрос 10×2 сек → FOUNDRY_DYNAMIC_PORT=<port>
      │      │             └─ нет → предупреждение, продолжить без Foundry
      │
      ├─[5] config.json → docs_server.enabled?
      │      └─ true →
      │          ├─ python -m mkdocs build --quiet  (синхронно, обновляет site/)
      │          └─ mkdocs serve -a 0.0.0.0:<port>  (фоновое окно, hot-reload)
      │
      ├─[6] LLAMA_MODEL_PATH + LLAMA_AUTO_START=true?
      │      └─ true → scripts\llama-start.ps1 -ModelPath ... -Port ...
      │                 → LLAMA_BASE_URL=http://127.0.0.1:<port>/v1
      │
      ├─[6.5] install\.installer.pid → Kill installer-сервер (если жив)
      │        └─ удалить install\.installer.pid
      │
      ├─[7] %TEMP%\fastapi-foundry.pid → Kill предыдущий процесс FastAPI
      │
      └─[8] Start-Process $venvPath run.py  ← блокирует до завершения
             └─ PID сохраняется в %TEMP%\fastapi-foundry.pid
    ```

---

## Этапы подробно

??? note "Этап 1 — Проверка venv"

    `start.ps1` ищет `venv\Scripts\python.exe` (или `python311.exe`).

    - **Найден** → активирует `venv\Scripts\Activate.ps1` и продолжает
    - **Не найден** → запускает `install.ps1` автоматически

    `install.ps1` создаёт venv, устанавливает `requirements.txt`, опционально
    устанавливает RAG-зависимости и Foundry CLI.

??? note "Этап 2 — Загрузка .env"

    Функция `Load-EnvFile` читает `.env` построчно и экспортирует каждую пару
    `КЛЮЧ=ЗНАЧЕНИЕ` через `[System.Environment]::SetEnvironmentVariable`.

    Секретные переменные (`PASSWORD`, `SECRET`, `KEY`, `TOKEN`, `PAT`) маскируются
    в выводе как `***`.

    Если `.env` не найден — выводится подсказка создать его из `.env.example`:

    ```powershell
    Copy-Item .env.example .env
    notepad .env
    ```

??? note "Этап 3 — Foundry AI"

    Алгоритм поиска запущенного Foundry:

    ```
    Get-Process | Where ProcessName -like "Inference.Service.Agent*"
      └─ найден → netstat -ano | grep PID | grep LISTENING
          └─ для каждого порта → GET http://127.0.0.1:<port>/v1/models
              └─ HTTP 200 → вернуть порт
    ```

    Если Foundry не запущен, но `foundry` есть в PATH:

    ```powershell
    Start-Process foundry -ArgumentList "service", "start" -WindowStyle Minimized
    # Опрос каждые 2 сек, максимум 10 попыток (20 сек)
    ```

    !!! warning "Foundry недоступен"
        Если Foundry не найден и не установлен — сервер всё равно запустится.
        HuggingFace и llama.cpp продолжат работать. Foundry-модели будут недоступны.

??? note "Этап 4 — MkDocs (опционально)"

    Управляется через `config.json`:

    ```json
    {
      "docs_server": {
        "enabled": true,
        "port": 9697
      }
    }
    ```

    Последовательность действий:

    1. `Get-NetTCPConnection -LocalPort 9697` — если порт занят, убивает процесс (`Stop-Process`)
    2. `mkdocs build` — пересобирает `site/` из актуальных `docs/`
    3. `mkdocs serve` — запускает live-сервер с hot-reload в фоновом окне

    Документация доступна на **http://localhost:9697**

    !!! info "Почему нужна пересборка"
        `mkdocs serve` отдаёт страницы из `docs/` напрямую (hot-reload),
        но `site/` — статика для GitHub Pages — обновляется только через `mkdocs build`.
        `start.ps1` запускает оба шага, поэтому `site/` всегда актуален.

??? note "Этап 5 — llama.cpp (опционально)"

    ### Проверка и установка бинарника

    При каждом запуске `start.ps1` вызывает `Ensure-LlamaBin`:

    1. Ищет файлы `llama-*-bin-win-*.zip` в директории `bin/`
    2. Берёт последний по имени (номер сборки растёт лексикографически)
    3. Читает установленную версию из `config.json` → `llama_cpp.bin_version`
    4. Если версия совпадает и `llama-server.exe` существует — пропускает
    5. Если найдена **новая версия** — спрашивает:

    ```
    📦 New llama.cpp version available!
       Installed : llama-b8000-bin-win-cpu-x64
       Available : llama-b8802-bin-win-cpu-x64
       Install now? [Y/n]
    ```

    При согласии (`Y` или Enter):
    - Удаляет старую директорию
    - Распаковывает zip в `bin/<version>/` (файлы из zip без корневой папки)
    - Обновляет `config.json` → `llama_cpp.bin_version`

    При отказе (`n`) — продолжает с уже установленным бинарником.

    ### Поиск llama-server.exe

    `_find_llama_server()` в Python ищет в следующем порядке:

    1. `LLAMA_SERVER_PATH` из `.env` (явный путь)
    2. `PATH` системы (`shutil.which`)
    3. `bin/<bin_version>/llama-server.exe` — **основной путь**, версия из `config.json`
    4. Любая поддиректория `bin/` (fallback, по убыванию имени)
    5. Стандартные места Windows (`C:/llama.cpp/`, `%LOCALAPPDATA%/llama.cpp/`)

    ### Автозапуск сервера

    Управляется через `config.json`:

    ```json
    {
      "llama_cpp": {
        "model_path": "D:\\models\\qwen2.5-0.5b-q4_k_m.gguf",
        "auto_start": true,
        "port": 9780
      }
    }
    ```

    При `auto_start: true`:

    1. Останавливает предыдущий процесс на порту
    2. Запускает `llama-server.exe` напрямую из `bin/<bin_version>/`
    3. Ждёт до 10 сек пока `/health` ответит 200
    4. При немедленном падении процесса — переизвлекает бинарник и повторяет (max 2 попытки)
    5. Экспортирует `LLAMA_BASE_URL=http://127.0.0.1:<port>/v1`

    !!! info "Версия бинарника в config.json"
        ```json
        {
          "llama_cpp": {
            "port": 9780,
            "host": "127.0.0.1",
            "bin_version": "llama-b8802-bin-win-cpu-x64"
          }
        }
        ```
        Поле `bin_version` обновляется автоматически при установке новой версии.
        Чтобы добавить новую версию — положите zip в `bin/` и перезапустите `start.ps1`.

??? note "Этап 6.5 — Остановка installer-сервера"

    При первой установке `install.ps1` запускает `install/server.py` — временный
    FastAPI-сервер с GUI-установщиком на порту 9698. Сервер записывает свой PID
    в `install/.installer.pid`.

    `start.ps1` проверяет этот файл и завершает процесс если он ещё жив:

    ```powershell
    $InstallerPidFile = Join-Path $Root 'install\.installer.pid'
    if (Test-Path $InstallerPidFile) {
        $installerPid = Get-Content $InstallerPidFile
        Get-Process -Id $installerPid | Kill()   # игнорирует ошибку если уже завершён
        Remove-Item $InstallerPidFile
    }
    ```

    Installer-сервер также завершается сам при нажатии **Finish** в браузере
    (UI вызывает `POST /api/shutdown` → сервер удаляет PID-файл и посылает `SIGTERM`).

    | Сценарий | Что происходит |
    |---|---|
    | Пользователь нажал Finish | Сервер завершается сам, PID-файл удаляется |
    | Пользователь закрыл браузер | Сервер продолжает работать до `start.ps1` |
    | Перезагрузка ПК | PID-файл остался, `start.ps1` пробует Kill (процесс мёртв — игнорирует) |

??? note "Этап 7 — Остановка предыдущего экземпляра FastAPI"

    PID запущенного FastAPI сохраняется в `%TEMP%\fastapi-foundry.pid`.
    При следующем запуске `start.ps1` читает этот файл и завершает старый процесс
    перед стартом нового — порт не будет занят.

??? note "Этап 7 — run.py и FastAPI lifespan"

    `start.ps1` запускает `venv\Scripts\python.exe run.py` и ждёт завершения.

    `run.py` выполняет:

    1. Форсирует UTF-8 для stdout/stderr (важно на Windows)
    2. Загружает `.env` через `src/utils/env_processor`
    3. Импортирует `Config` singleton — читает `config.json` один раз
    4. Определяет порт FastAPI (фиксированный или автопоиск в диапазоне 9696–9796)
    5. Повторно ищет Foundry (на случай прямого запуска без `start.ps1`)
    6. Запускает Uvicorn

    После старта Uvicorn выполняется `lifespan` в `app.py`:

    ```python
    async with lifespan(app):
        await rag_system.initialize()          # загружает FAISS индекс
        if auto_load_default and default_model:
            subprocess foundry model load ...  # автозагрузка модели
        yield
        await foundry_client.close()           # закрытие aiohttp сессии
    ```

    ### Reloader (WatchFiles)

    В режиме `mode: dev` Uvicorn запускает **два процесса**:

    ```
    reloader process [33548] using WatchFiles   ← следит за изменениями *.py
    Started server process [33612]              ← фактический FastAPI сервер
    ```

    Это нормальное поведение. При сохранении любого `.py` файла worker перезапускается автоматически.

    Чтобы стартовые сообщения не печатались дважды, `run.py` использует флаг `_UVICORN_CHILD`.

    Для отключения reloader установите `mode: prod` в `config.json`.

---

## Повторный запуск (restart)

Команда та же самая:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

`start.ps1` сам разберётся что остановить, что оставить и что запустить заново:

| Сервис | Уже запущен? | Действие |
|---|---|---|
| **Installer** (порт 9698) | жив | убивает по `install/.installer.pid` → удаляет файл |
| **FastAPI** (порт 9696) | да | убивает по `%TEMP%/fastapi-foundry.pid` → запускает новый |
| **MkDocs** (порт 9697) | да | убивает по порту → `mkdocs build` → `mkdocs serve` |
| **llama.cpp** (порт 9780) | да | убивает по порту → запускает новый |
| **Foundry** | да | не трогает — только читает порт |
| **Foundry** | нет | запускает `foundry service start`, ждёт 20 сек |

!!! info "Foundry не перезапускается намеренно"
    Foundry — внешний системный сервис Microsoft. Его перезапуск выгрузил бы загруженную модель из памяти.
    `start.ps1` никогда не останавливает Foundry самостоятельно.

---

## Прямой запуск без start.ps1

!!! tip "Если Foundry уже запущен"
    ```powershell
    venv\Scripts\python.exe run.py
    ```
    `run.py` сам найдёт Foundry через `tasklist` + `netstat`.

---

## Параметры start.ps1

| Параметр | По умолчанию | Описание |
|---|---|---|
| `-Config` | `config.json` | Путь к файлу конфигурации |

```powershell
.\start.ps1 -Config config.prod.json
```

---

## Ключевые переменные окружения

!!! info "Актуальность"
    Таблица отражает текущее состояние. Правило проекта: **`.env` хранит только секреты**.
    Все пути, порты, флаги и настройки поведения — в `config.json`.
    Состав может меняться по мере развития проекта. Актуальный эталон — в [`.env.example`](https://github.com/hypo69/FastApiFoundry-Docker/blob/main/.env.example).

### Секреты — хранятся в `.env`

| Переменная | Описание |
|---|---|
| `HF_TOKEN` | Токен HuggingFace для закрытых моделей (Gemma, Llama, Mistral) |
| `API_KEY` | Ключ для защиты FastAPI эндпоинтов (optional) |
| `SECRET_KEY` | JWT секрет (optional) |
| `FOUNDRY_API_KEY` | Ключ Foundry API (optional) |
| `OPENAI_API_KEY` | Ключ OpenAI |
| `ANTHROPIC_API_KEY` | Ключ Anthropic |
| `GEMINI_API_KEY` | Ключ Google Gemini |
| `OPENROUTER_API_KEY` | Ключ OpenRouter |
| `MISTRAL_API_KEY` | Ключ Mistral |
| `GROQ_API_KEY` | Ключ Groq |
| `DEEPSEEK_API_KEY` | Ключ DeepSeek |
| `XAI_API_KEY` | Ключ xAI (Grok) |
| `GITHUB_PAT` | GitHub Personal Access Token |
| `SMTP_PASSWORD` | Пароль SMTP сервера |
| `REDIS_PASSWORD` | Пароль Redis |

### Служебные — выставляются `start.ps1` автоматически

Эти переменные **не нужно задавать вручную** — `start.ps1` выставляет их сам в процесс после обнаружения сервисов:

| Переменная | Кто выставляет | Описание |
|---|---|---|
| `FOUNDRY_BASE_URL` | `start.ps1` | Полный URL Foundry API |
| `FOUNDRY_DYNAMIC_PORT` | `start.ps1` | Порт, найденный автоматически |
| `LLAMA_BASE_URL` | `start.ps1` | URL llama.cpp после запуска |
| `LLAMA_SERVER_PATH` | `.env` (optional) | Явный путь к `llama-server.exe` |

### Настройки поведения — хранятся в `config.json`

| Параметр | Секция | Описание |
|---|---|---|
| `port`, `host` | `fastapi_server` | Порт и хост FastAPI |
| `default_model`, `auto_load_default` | `foundry_ai` | Модель по умолчанию и автозагрузка |
| `port`, `host`, `model_path`, `auto_start` | `llama_cpp` | Настройки llama.cpp |
| `hf_models` | `directories` | Директория HuggingFace моделей |
| `models`, `rag` | `directories` | Директории GGUF и RAG индексов |
| `enabled`, `index_dir`, `chunk_size` | `rag_system` | Настройки RAG |
| `level`, `file` | `logging` | Уровень и файл логов |

---

## Что дальше

- [Установка](installation.md) — первичная настройка, install.ps1
- [Работа с моделями](models_guide.md) — Foundry, HuggingFace, llama.cpp
- [Веб-интерфейс](web_interface.md) — описание всех вкладок
