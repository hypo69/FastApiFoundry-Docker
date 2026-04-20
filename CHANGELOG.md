# Changelog

All notable changes to FastAPI Foundry are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

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

### Changed
- `src/rag/text_extractor_4_rag/config.py` — интегрирован с проектным синглтоном `Config`: удалён самостоятельный `json.load()`, настройки читаются через `config.get_section("text_extractor")` из `config_manager.py`; `DEBUG` берёт fallback из секции `development.debug`
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
