# Changelog

All notable changes to FastAPI Foundry are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [0.6.1] - 2025

### Added
- Добавлен механизм автоматической очистки временных файлов логов (`.tmp`) старше заданного времени (настраивается в `config.json`).
- Добавлены интерактивные кнопки подтверждения (Да/Нет) для команды `/restart_server` в Telegram-боте.
- Реализована автоматическая система оповещения о критическом заполнении диска (>95%) в Telegram.
- Реализован полноценный векторный поиск в `RAGSystem` с использованием `SentenceTransformers`.
- Добавлено кеширование результатов поиска в `RAGSystem` для оптимизации повторных запросов.
- Реализована автоматическая проверка совместимости размерности векторов модели и индекса при загрузке.
- Реализовано автоматическое обновление метаданных (`meta.json`) при каждой активации/перезагрузке профиля RAG.
- Добавлен метод `_remove_duplicate_chunks` в `RAGSystem` для удаления дубликатов чанков при загрузке индекса и сохранении метаданных.
- Добавлена отправка уведомлений через WebSocket при изменении статуса Foundry в процессе опроса.
- Реализован автоматический сброс всех предохранителей в `CommandAgent` при обнаружении изменений в `PATH`.
- Добавлены команды `/stats` (графики ресурсов, включая диск), `/get_logs` (отправка файла логов) и `/restart_server` в Telegram-бота.
- Реализована фоновая проверка состояния Foundry с оповещением в Telegram при падении сервиса.
- Добавлен метод `test_command_available` в `CommandAgent` для предварительной проверки наличия утилит в системном окружении.
- Реализована проверка целостности файлов индекса (faiss.index) перед загрузкой в `RAGSystem`.
- Добавлен метод `filter_by_source` в `RAGSystem` для фильтрации результатов поиска по источнику.
- Добавлен метод `filter_by_score` в `RAGSystem` для фильтрации результатов по порогу схожести.
- Обновлён эндпоинт `/search` в `rag.py`: добавлен параметр `min_score` и интеграция с реальным поиском `RAGSystem.search`.
- Обновлён эндпоинт `/ai/generate` в `ai_endpoints.py`: добавлена поддержка параметра `min_score` для RAG.
- Обновлён эндпоинт `/ai/chat` в `ai_endpoints.py`: добавлена поддержка параметра `min_score` и интеграция RAG контекста.
- Добавлена поддержка параметра `system_prompt` в эндпоинте `/ai/chat` для переопределения поведения ассистента.
- Реализована поддержка стриминга для чата через эндпоинт `/ai/chat/stream` с сохранением истории сессии.
- Добавлена отправка заголовка `X-Session-Id` в эндпоинте `/ai/chat/stream` для отслеживания сессий в логах.
- Реализовано автоматическое сохранение истории чата в файл `session_history.json` при каждом запросе в `ai_endpoints.py`.
- Добавлена автоматическая очистка файла `session_history.json` при старте приложения, если он старше 7 дней.
- Реализована автоматическая очистка папки `archive` при достижении размера 2 ГБ (FIFO удаление старых файлов).
- Добавлена возможность исключать определенные файлы из удаления в `cleanup_archive_size` через параметр `logging.archive_keep_files` в `config.json`.
- Добавлен метод `execute_command_lines` в `CommandAgent` для асинхронного получения текстового вывода команд.
- Обновлён эндпоинт `/foundry/status` в `foundry_management.py` для интеграции с парсером `CommandAgent`.
- Реализован метод `parse_foundry_status` в `CommandAgent` для структурированного парсинга вывода `foundry service status`.
- Интегрирован асинхронный `CommandAgent` и PowerShell wrapper для безопасного выполнения CLI команд с JSONL-логированием.
- Реализован метод `reset_circuit_breaker` в `CommandAgent` и соответствующий эндпоинт в API.
- Добавлен фоновый опрос статуса Foundry через `BackgroundTasks` после вызова команды старта.
- Реализована ротация файлов истории чата: устаревшие файлы перемещаются в папку `archive/` перед "удалением" из корня.
- Добавлен параметр `logging.history_retention_days` в `config.json` для настройки срока хранения истории.

### Changed
- Выполнен рефакторинг и приведение к стандартам AiStros файлов `run.py`, `config_manager.py`, `start.ps1`, `autostart.ps1`.
- Параметр `logging.retention_hours` добавлен в `config.json`.
- Версии проекта во всех заголовках обновлены до 0.6.1.
- Исправлена ошибка синтаксиса в эндпоинтах RAG.

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
