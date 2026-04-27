# Changelog

All notable changes to AI Assistant (ai_assist) are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)



---

## [0.7.1] - 2025

### Changed
- `install/install-autostart.ps1` → `install/Install-Autostart.ps1` — переименован в CamelCase
- `install/install-foundry.ps1` → `install/Install-Foundry.ps1` — переименован в CamelCase
- `install/install-huggingface-cli.ps1` → `install/Install-HuggingFaceCli.ps1` — переименован в CamelCase
- `install/install-llama.ps1` → `install/Install-Llama.ps1` — переименован в CamelCase
- `install/install-models.ps1` → `install/Install-Models.ps1` — переименован в CamelCase
- `install/install-shortcuts.ps1` → `install/Install-Shortcuts.ps1` — переименован в CamelCase
- `install/install-tesseract.ps1` → `install/Install-Tesseract.ps1` — переименован в CamelCase
- `install/make-ico.ps1` → `install/Make-Ico.ps1` — переименован в CamelCase
- `install/setup-env.ps1` → `install/Setup-Env.ps1` — переименован в CamelCase
- `scripts/build_exes.ps1` → `scripts/Build-Exes.ps1` — переименован в CamelCase
- `scripts/clear-reports.ps1` → `scripts/Clear-Reports.ps1` — переименован в CamelCase
- `scripts/create_requirements.ps1` → `scripts/Create-Requirements.ps1` — переименован в CamelCase
- `scripts/download-model.ps1` → `scripts/Download-Model.ps1` — переименован в CamelCase
- `scripts/generate-ps-docs.ps1` → `scripts/Generate-PsDocs.ps1` — переименован в CamelCase
- `scripts/hf-download-model.ps1` → `scripts/Hf-DownloadModel.ps1` — переименован в CamelCase
- `scripts/hf-models.ps1` → `scripts/Hf-Models.ps1` — переименован в CamelCase
- `scripts/list-models.ps1` → `scripts/List-Models.ps1` — переименован в CamelCase
- `scripts/llama-start.ps1` → `scripts/Start-Llama.ps1` — переименован в CamelCase (Verb-Noun)
- `scripts/load-model.ps1` → `scripts/Load-Model.ps1` — переименован в CamelCase
- `scripts/restart-mkdocs.ps1` → `scripts/Restart-MkDocs.ps1` — переименован в CamelCase
- `scripts/run-qa.ps1` → `scripts/Run-Qa.ps1` — переименован в CamelCase
- `scripts/service-status.ps1` → `scripts/Get-ServiceStatus.ps1` — переименован в CamelCase (Verb-Noun)
- `scripts/unload-model.ps1` → `scripts/Unload-Model.ps1` — переименован в CamelCase
- `scripts/watch_tests.ps1` → `scripts/Watch-Tests.ps1` — переименован в CamelCase
- `check_engine/check_port.ps1` → `check_engine/Check-Port.ps1` — переименован в CamelCase
- `src/utils/invoke-command-logged-lite.ps1` → `src/utils/Invoke-CommandLoggedLite.ps1` — переименован в CamelCase
- `tests/qa-install.ps1` → `tests/Invoke-QaInstall.ps1` — переименован в CamelCase (Verb-Noun)
- `tests/qa-start.ps1` → `tests/Invoke-QaStart.ps1` — переименован в CamelCase (Verb-Noun)
- `mcp/src/clients/powershell.ps1` → `mcp/src/clients/Invoke-PowerShell.ps1` — переименован в CamelCase
- `mcp/src/clients/wpcli.ps1` → `mcp/src/clients/Invoke-WpCli.ps1` — переименован в CamelCase
- `install/ReinstallFoundry.ps1` — создан: полная переустановка Foundry Local (CI/QA); восстановлены потерянные блоки кода
- `scripts/README.md` — создан: таблица всех скриптов с новыми CamelCase именами
- `SECURITY.md` — переписан под версию 0.7.1: таблица поддерживаемых версий, инструкция по репортингу уязвимостей, security considerations
- Все ссылки на переименованные скрипты обновлены в: `install.ps1`, `start.ps1`, `autostart.ps1`, `install/README.md`, `INSTALL.md`, `.github/workflows/`, `docs/ru/`

### Added
- `docs/ru/user/installation.md` — раздел «Скрипты директории install/»: таблица всех скриптов, примеры запуска, таблицы параметров
- `docs/ru/dev/scripts.md` — раздел «Разбор кода install/»: структура скриптов, стандарт docstring, примеры функций, диаграмма связей

---

## [0.7.1] - 2025

### Added
- `config.json` — секция `dialogs`: единое место хранения диалогов для всех клиентов (`dir`, `retention_days`, `max_size_mb`)
- `config_manager.py` — свойства `dir_dialogs`, `dialogs_retention_days`, `dialogs_max_size_mb`
- `src/api/endpoints/chat_endpoints.py` — `GET /chat/history/list`: список сохранённых диалогов с диска (пагинация, метаданные)
- `src/api/endpoints/chat_endpoints.py` — `GET /chat/history/file/{filename}`: загрузка одного диалога с диска (с защитой от path traversal)
- `src/api/endpoints/chat_endpoints.py` — `POST /chat/history/cleanup`: удаление устаревших/превышающих лимит диалогов (по `retention_days` и `max_size_mb`)
- `src/agents/qa_agent.py` — новый `QAAgent`: запуск тестов, покрытие, список тестовых файлов
- `scripts/watch_tests.ps1` — вотчер: автозапуск связанных тестов при изменении `*.py` в `src/`, debounce 1500ms
- `docs/ru/dev/api_reference.md` — добавлены `GET /chat/history/list`, `GET /chat/history/file/{fn}`, `POST /chat/history/cleanup`
- `docs/ru/dev/agents.md` — добавлены `QAAgent` и раздел про `watch_tests.ps1`
- `docs/ru/dev/rag_system.md` — добавлены: полный цикл индексации/поиска (ASCII-диаграмма), таблица моделей эмбеддингов, ключевые детали реализации
- `docs/ru/dev/utils.md` — добавлены `command_agent`, `process_utils`, `text_utils`: описание, методы, примеры
- `docs/ru/user/configuration.md` — добавлена секция `dialogs` в пример `config.json` и таблицу параметров
- `docs/ru/dev/architecture.md` — раздел «Хранилище диалогов»: структура, формат файла, пример кода, таблица клиентов
- `docs/ru/dev/architecture.md` — добавлены таблицы модулей `src/training/`, `telegram/`; `requirements-google.txt` в таблицу зависимостей
- `mkdocs.yml` — добавлено расширение `md_in_html` (рендеринг inline HTML в Markdown)

### Changed
- `src/api/endpoints/chat_endpoints.py` — `save_chat_history()`: путь читается из `config.dir_dialogs` (был хардкод `~/.ai-assistant-chat-history`)
- `src/api/endpoints/helpdesk.py` — `_DIALOGS_FILE` заменён на `_dialogs_file()` — пишет в `config.dir_dialogs/helpdesk_dialogs.jsonl`
- `telegram/helpdesk_bot.py` — `_DIALOGS_FILE` исправлен: хардкод `logs/helpdesk_dialogs.jsonl` заменён на `config.dir_dialogs`

### Fixed
- `src/models/foundry_client.py` — добавлены аннотации типов ко всем методам; удалён дублирующий старый класс без аннотаций; устранены griffe warnings
- `config_manager.py` — `reload_config()`: заменено `Raises: Same as _load_config()` на явные типы исключений; устранён griffe warning

### Changed
- `src/models/router.py` — добавлены workflow-диаграммы, примеры всех вариантов вызова, аннотации приватных функций
- `src/utils/api_utils.py` — добавлены workflow, примеры всех сценариев декоратора, аннотация возврата

### Removed
- `src/api/endpoints/chat_endpoints_new.py` — мёртвый код (mock-заглушка, не подключен в app.py); помечен `~`
- `src/api/endpoints/logging_endpoints.py` — мёртвый код (дублирует `logs.py`); помечен `~`
- `src/api/endpoints/models_extra.py` — мёртвый код (mock-заглушки); помечен `~`
- `src/api/endpoints/examples_endpoints.py` — мёртвый код (не подключен в app.py); помечен `~`

### Added
- `.amazonq/rules/CODE_REVISION.md` — чеклист и правила периодической ревизии кода

### Added
- `src/agents/windows_os_agent.py` — новый агент `windows_os`: специалист по Windows OS; сценарий `prompt → RAG → model → MCP tools → ответ`; инструменты: `rag_search`, `get_processes`, `get_services`, `get_disk_info`, `get_network_stats`, `get_system_info`, `get_startup_items`, `kill_process`
- `mcp/src/servers/windows_os_mcp.py` — MCP STDIO сервер с типизированными инструментами для Windows OS диагностики (без сырого PS кода)
- `mcp/settings.json` — зарегистрирован сервер `windows-os`
- `src/api/endpoints/agent.py` — `WindowsOsAgent` добавлен в реестр агентов
- `docs/ru/dev/agents.md` — документация `WindowsOsAgent`: инструменты, сценарий выполнения, пример запроса

- `mkdocs.yml` — добавлены все страницы в `nav`: `dev/utils.md`, `user/cicd_docs.md`, все страницы `dev/extensions/browser-extension-summarizer/`
- `mkdocs.yml` — добавлены `site_dir: site` и `docs_dir: docs`; гарантированная сборка в `site/` внутри проекта
- `docs/assets/icons/` — создана директория, скопированы `icon16.png`, `icon48.png`, `icon128.png` из `static/assets/icons/`; устранены 404 на логотип и favicon MkDocs
- `doc.ps1` — добавлен шаг `Build-MkDocs` (вызов `mkdocs build`) перед `mkdocs serve`; теперь `site/` всегда создаётся при запуске документации
- `doc.ps1` — перед сборкой всегда удаляется `site/` (полная пересборка)
- `start.ps1` — этап 5: если `site/` есть — сразу `serve`; если `site/` нет — сначала `build`, затем `serve`

### Added
- `docs/ru/dev/extensions/browser-extension-summarizer/i18n.md` — документация механизма переводов UI расширения
- `docs/ru/dev/extensions/browser-extension-summarizer/styles.md` — документация стилей и UI страниц расширения
- `docs/ru/dev/extensions/browser-extension-summarizer/storage.md` — схема данных `chrome.storage` расширения
- `docs/ru/dev/extensions/browser-extension-summarizer/api_reference.md` — справочник JS модулей расширения
- `docs/ru/index.md` — бейджи version/python/license/platform
- `docs/en/index.md` — создана главная страница английской документации с бейджами
- `mkdocs.yml` — `extra.ai_assist_version: "0.7.1"`, `extra.social` (GitHub); `en` стал языком по умолчанию (site/ корень), `ru` в site/ru/
- `mkdocs.yml` — отключён плагин `i18n`; `docs_dir: docs/ru`; `theme.language: ru`; чистая сборка без warnings о ненайденных файлах
- `docs/ru/assets/icons/` — скопированы иконки для правильного разрешения при `docs_dir: docs/ru`
- `docs/ru/stylesheets/extra.css`, `docs/ru/javascripts/extra.js` — скопированы из `docs/`; устранены 404
- `mkdocs.yml` — удалён `extra.version.provider: mike`; устранён 404 на `versions.json`
- `VERSION` — обновлён до `v0.7.1`
- `.amazonq/rules/VERSION.md` — текущая версия 0.7.1, формат бейджа и CHANGELOG

---

## [0.7.0] - 2025 (orchestrator)

### Changed
- Project renamed: **FastAPI Foundry** → **AI Assistant** (`ai_assist`)
- Concept shift: from "FastAPI server for Foundry" to **local AI model orchestrator**
- `src/models/router.py` — создан: центральный модуль маршрутизации оркестратора; `detect_backend()` + `route_generate()`
- `src/api/endpoints/generate.py` — заменён ручной if/elif диспатч на `router.route_generate()`
- `src/api/endpoints/ai_endpoints.py` — `/ai/generate` и `/ai/chat` теперь используют `route_generate()` вместо прямого вызова `foundry_client`
- `README.md` — таблица маршрутизации: `foundry::` теперь явный префикс; bare ID — legacy с предупреждением
- `VERSION` — обновлена до `v0.7.0`
- `src/api/app.py` — обновлены `title`, `description`, `version` до 0.7.0
- `.amazonq/rules/VERSION.md` — текущая версия обновлена до 0.7.0
- `.amazonq/rules/memory-bank/product.md` — обновлено название и версия
- `.amazonq/rules/memory-bank/guidelines.md` — обновлена версия до 0.7.0

---

## [0.6.1] - 2025 (refactored)

### Changed
- `pc_component_processor.py` — перемещён из корня проекта в `utils/pc_component_processor.py`; обновлён заголовок файла
- `utils/README.md` — добавлен `pc_component_processor.py` в таблицу утилит
- `docs/ru/dev/utils.md` — добавлен раздел `utils/` (standalone-утилиты) с документацией `pc_component_processor`
- `docs/ru/user/getting_started.md` — добавлен раздел «Остановка системы» с командами для всех сервисов

### Removed
- `install/server.py` — GUI-установщик (веб-интерфейс на порту 9698) удалён; помечен `server.py~`
- `install/static/` — SPA установщика удалёна; папка помечена `static~`

### Added
- `stop.ps1` — скрипт остановки всех сервисов (FastAPI, llama.cpp, MkDocs) для silent mode; опциональная остановка Foundry через `-StopFoundry`
- `docs/ru/user/installation.md` — добавлен раздел **Автозапуск при входе в Windows**: `autostart.ps1`, Task Scheduler, ярлыки, `stop.ps1`

### Changed
- `install.ps1` — удалён шаг 3.5 (запуск `server.py`), удалён параметр `-NoGui`; вся установка теперь только через терминал
- `docs/ru/user/installation.md` — переписана: убраны все упоминания GUI, остались только `install.bat` и `install.ps1`

### Fixed
- `src/api/main.py` — удалён дублирующий `app.include_router(rag_router)`; исправлен импорт логгера (`logging.getLogger` вместо `src.logger`); исправлен `__main__` блок — использует `config.api_*` вместо несуществующего `settings`
- `src/api/app.py` — удалён дублирующий импорт `ai_endpoints`; версия обновлена до 0.6.1
- `src/core/config.py` — удалён устаревший алиас `settings = config`; добавлен `__all__ = ["config"]`
- `src/rag/rag_system.py` — `index_directories()`: исправлен вызов `config.rag_system.get(...)` → `config.get_section("rag_system").get(...)`
- `src/api/endpoints/ai_endpoints.py` — исправлен дублированный блок `Args:` в docstring; исправлены escape-последовательности в SSE (`\\n` → `\n`)
- `src/models/foundry_client.py` — `generate_text()`: удалён inline subprocess retry при HTTP 400; возвращается `error_code: model_not_loaded` с инструкцией пользователю
- `src/api/endpoints/foundry_models.py` — `list_loaded_models()` использует динамический URL из `foundry_client` вместо хардкода
- `src/api/endpoints/generate.py` — `error_code: model_not_loaded` пробрасывается к клиенту
- `static/js/foundry.js` — метки «In RAM» / «On disk» заменены на «Loaded» / «Cached»
- `docs/ru/dev/rag_system.md` — переписана: добавлены `RAGProfileManager`, таблица всех RAG API endpoints, исправлена ссылка на `config.get_section()`
- `docs/ru/user/telegram_bots.md` — исправлены: поток HelpDesk (top-5 чанков, `/api/v1/ai/generate`), добавлены HelpDesk API endpoints, исправлен путь ZIP-архивов
- `docs/ru/dev/telegram_bots.md` — исправлен поток HelpDesk (top-5 чанков вместо top-3)

### Added
- `install/make-ico.ps1` — конвертер PNG → ICO
- `install/install-models.ps1` — раздел llama.cpp: создаёт `~/.models`, определяет найденные `.gguf` и автопрописывает первый в `config.json`; если моделей нет — показывает инструкцию с рекомендуемыми моделями (Mega.nz не поддерживает прямое скачивание): собирает `assets/icons/icon16.png` + `icon48.png` + `icon128.png` в `icon.ico` через `System.Drawing` (без внешних инструментов)
- `static/assets/icons/` — иконки скопированы в `static/` для раздачи через FastAPI StaticFiles
- `docs/assets/icons/` — иконки скопированы в `docs/` для MkDocs (`logo` + `favicon`)
- `config.json` — секция `model_manager` с параметрами `max_loaded_models`, `ttl_seconds`, `max_ram_percent`
- `config_manager.py` — свойства `model_manager_max_loaded`, `model_manager_ttl_seconds`, `model_manager_max_ram_percent`
- `docs/ru/dev/code/foundry_client.md` — таблица статусов модели, модель памяти Foundry, `error_code: model_not_loaded`
- `scripts/create_requirements.ps1` — генерация `requirements.txt` в режимах `freeze` / `pipreqs` / `clean`

### Changed
- `requirements.txt` — объединён с `requirements-rag.txt`, `requirements-extras.txt`, `requirements-dev.txt`
- `install/server.py` — шаги `rag`, `extras`, `dev` удалены; остался один шаг `requirements`
- `.env.example` — синхронизирован с `.env`: добавлены `SECRET_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `GITHUB_PAT`, `LLAMA_SERVER_PATH`; все ключи присутствуют в файле (пустыми или закомментированы) чтобы `setup-env.ps1` мог их заменять
- `install/setup-env.ps1` — исправлена ошибка `❌ .env.example not found`: `$Root` указывал на `install\` вместо корня проекта; добавлен `$Project = Split-Path -Parent $PSScriptRoot`
- `install/install-shortcuts.ps1` — ищет `icon.ico` в корне проекта, автозапуск `make-ico.ps1` если `icon.ico` отсутствует, `WorkingDirectory` исправлен на корень проекта; добавлен ярлык «AI Assistant Docs» на рабочем столе (открывает браузер на порте документации из `config.json`)
- `install.ps1` — шаг 11: перед созданием ярлыков вызывается `make-ico.ps1`; в summary добавлены ссылки на приложение, документацию и Swagger UI (порты читаются из `config.json`)
- `start.ps1` — после запуска FastAPI автоматически открывается браузер на порте приложения (опрос TCP до 15с); если `docs_server.enabled=true` — также открывает браузер на порте документации (опрос HTTP до 20с); llama.cpp запускается автоматически если задан `llama_cpp.model_path` (без необходимости `auto_start=true`); отключить можно явным `auto_start=false`
- `install/install-models.ps1` — раздел llama.cpp: создаёт `~/.models`, интерактивный выбор модели из найденных `.gguf`; если моделей нет — инструкция с `huggingface-cli` примером и подсказкой про веб-интерфейс
- `mkdocs.yml` — добавлены `logo: assets/icons/icon128.png` и `favicon: assets/icons/icon48.png`
- `static/index.html`, `static/chat.html`, `static/simple.html`, `static/partials/_head.html` — добавлены `<link rel="icon">` для 16/48/128px + `apple-touch-icon`
- Все заголовки файлов приведены к версии 0.6.1

## [0.6.0] - 2025-12-10 (updated)

### Fixed
- `start.ps1` — MkDocs и llama.cpp теперь останавливаются при выходе (Ctrl+C): PID сохраняется в `$script:MkDocsPid` / `$script:LlamaPid`, блок `finally` вызывает `Stop-Process`; Foundry намеренно не останавливается — это системный сервис

### Added
- `docs/ru/user/cli_reference.md` — новый раздел CLI Reference: справочник команд Foundry Local CLI, llama.cpp, HuggingFace CLI, диагностика FastAPI Foundry, RAG API
- `mkdocs.yml` — страница CLI Reference добавлена в навигацию раздела «Руководство пользователя»

### Fixed
- `src/api/endpoints/health.py` — `Config` object has no attribute `get`: заменены все вызовы `config.get(section, {})` на `config.get_section(section)` и `config.rag_enabled` / `config.rag_index_dir`; это было корневой причиной того, что `/health` возвращал `foundry_status: error` и бейдж и индикатор Foundry показывали offline
- `src/models/foundry_client.py` — `_find_foundry_port()` переписан: теперь парсит `foundry service status` вместо сканирования только 3 захардкоденных портов; добавлен порт 52632 в fallback-список
- `static/js/foundry.js` — `waitForFoundryModelLoaded()` показывает живой счётчик с спиннером во время загрузки модели
- `static/partials/_tab_foundry.html` — добавлен `#foundry-load-status` для отображения статуса загрузки
 теперь читает статическое значение из `config.json → foundry_ai.base_url` когда runtime override не задан; ранее возвращал `None` и всегда запускал автообнаружение
- `src/utils/foundry_utils.py` — `find_foundry_port()` переписан: вместо ненадёжного `tasklist + netstat` теперь парсит вывод `foundry service status` (содержит точный URL `http://127.0.0.1:PORT`)
- `run.py` — `find_foundry_port()` делегирует в `foundry_utils.py`; убрана дублирующая реализация со старой логикой
- `src/api/endpoints/foundry_models.py` — `list_loaded_models()` оборачивает HTTP-запрос в `try/except`; `TimeoutError`/`CancelledError` при недоступном Foundry возвращают `{success: false, models: []}` вместо исключения
- `src/api/endpoints/foundry_management.py` — `start_foundry()` заменён с блокирующего `run_command` на неблокирующий `Popen`; добавлена обработка `FileNotFoundError`
- `static/js/model-badge.js` — `refreshModelBanner()` принимает опциональный `modelInfo` для немедленного рендера без ожидания poll
- `static/js/models.js` — `syncChatModelToActive()` при llama.cpp теперь сверяется с `/v1/models` для точного совпадения пути модели

: сравнивает локальную версию с последним тегом remote, предлагает обновление, выполняет `git checkout <tag>` и перезапускает `install.ps1`
- `VERSION` — файл с текущей установленной версией (`v0.6.0`); читается `Update-Project.ps1` как fallback при отсутствии git
- `docs/ru/dev/versioning.md` — новая глава документации: схема semver, файл VERSION, механизм автообновления, выпуск релиза, ручное обновление, откат
- `mkdocs.yml` — страница «Управление версиями» добавлена в раздел «Для разработчиков»

### Changed
- `start.ps1` — добавлен Этап 0: вызов `scripts/Update-Project.ps1` перед проверкой venv; обновлена версия заголовка до 0.6.0

---

## [0.6.0] - 2025-12-09

### Added
- `src/rag/text_extractor_4_rag/` — новый модуль извлечения текста из 40+ форматов (PDF, DOCX, XLSX, PPTX, изображения OCR, HTML, архивы, исходный код и др.)
- `src/api/endpoints/rag.py` — три новых endpoint: `POST /api/v1/rag/extract/file`, `POST /api/v1/rag/extract/url`, `GET /api/v1/rag/extract/formats`
- `static/partials/_tab_rag.html` — секция **Text Extractor** с вкладками File/URL, предпросмотром результата и кнопкой копирования
- `static/partials/_tab_settings.html` — секция **Text Extractor** с 7 настраиваемыми параметрами
- `static/js/rag.js` — функции `extractFromFile()`, `extractFromURL()`, `copyExtractedText()`
- `static/js/config.js` — загрузка и сохранение полей `text_extractor` в Settings
- `config.json` — секция `text_extractor` с 7 настройками с значениями по умолчанию
- `docs/ru/user/text_extraction.md` — руководство пользователя: форматы, веб-интерфейс, API, OCR, настройки
- `docs/ru/dev/text_extractor.md` — техническая документация: архитектура, классы, API, безопасность, зависимости
- `mkdocs.yml` — обе страницы добавлены в навигацию
- `static/locales/ru.json` — переводы для всех новых элементов интерфейса (RAG + Settings)
- `src/utils/translator.py` — утилита перевода через бесплатные онлайн-сервисы (MyMemory, LibreTranslate)
- `config.json` — секция `translator` (default_provider, mymemory_email, libretranslate_url, libretranslate_fallback_url, libretranslate_api_key, request_timeout_sec)
- `static/partials/_tab_settings.html` — секция Translator в вкладке Settings
- `docs/ru/dev/utils.md` — документация разработчика для `src/utils/`
- `examples/translator_example.py` — пример использования переводчика

### Added
- `LICENSE` — замена CC BY-NC-SA 4.0 на MIT License
- `README.md` — обновлена ссылка на лицензию (порт из `config.json → docs_server.port`)
- `scripts/restart-mkdocs.ps1` — скрипт перезапуска MkDocs: читает порт из `config.json`, убивает процесс через `netstat`, запускает новый в отдельном окне
- `docs/ru/dev/scripts.md` — новая страница документации с описанием всех операционных скриптов

### Changed
- `scripts/README.md` — добавлен `restart-mkdocs.ps1` в таблицу и примеры использования
- `mkdocs.yml` — добавлен раздел «Скрипты» в навигацию для разработчиков: удалён самостоятельный `json.load()`, настройки читаются через `config.get_section("text_extractor")` из `config_manager.py`; `DEBUG` берёт fallback из секции `development.debug`
- `docs/ru/dev/code/config.md` — расширена документация: добавлена полная глава по конфигурации (синглтон, структура `config.json`, секция `text_extractor`, приоритет env vars, рантаймовое обновление)
- `src/rag/text_extractor_4_rag/extractors.py` — исправлены импорты (`from app.*` → относительные), добавлен заголовок
- `src/rag/text_extractor_4_rag/main.py` — исправлены импорты, добавлен заголовок
- `src/rag/text_extractor_4_rag/utils.py` — `resource` и `magic` стали опциональными (совместимость с Windows), добавлен заголовок
- `src/rag/text_extractor_4_rag/__init__.py` — добавлен публичный API (`TextExtractor`, `settings`)
- `src/utils/__init__.py` — добавлен экспорт `Translator`, `translator`
- `src/utils/README.md` — переписан, добавлено описание translator
- `static/js/config.js` — `loadConfigFields()` и `saveConfigFields()` дополнены полями секции `translator`
- `docs/ru/user/installation.md` — убран раздел «Настройка конфигурации»; заменён на tip-блок со ссылкой на `configuration.md`
- `docs/ru/user/configuration.md` — добавлен раздел «Первый запуск» с командами создания `.env`

### Removed
- `src/models/translator/` — перемещён в `src/utils/translator.py`. Старая директория переименована в `src/models/translator~`

---
