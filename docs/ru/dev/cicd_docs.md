# CI/CD: Автоматическая сборка документации

Документация FastAPI Foundry собирается и публикуется автоматически при каждом пуше в ветки `main` или `master` через GitHub Actions.

## Обзор

Система состоит из трёх параллельных job'ов, которые генерируют документацию из исходного кода на разных языках, и одного финального job'а, который публикует всё на GitHub Pages.

```
push → [docs-js]          ──┐
     → [docs-powershell]  ──┼──→ [deploy] → GitHub Pages
     → (Python inline)    ──┘
```

| Job | Runner | Инструмент | Покрывает |
|---|---|---|---|
| `docs-js` | ubuntu-latest | TypeDoc + typedoc-plugin-markdown | JSDoc в `.js` файлах расширения |
| `docs-powershell` | windows-latest | PlatyPS (PowerShell) | Comment-based help в `.ps1` файлах |
| `deploy` | ubuntu-latest | MkDocs Material + mkdocstrings | Python docstrings + все `.md` файлы |

Workflow файл: `.github/workflows/deploy-docs.yml`

---

## Триггеры

Сборка запускается при изменении файлов в следующих путях:

```yaml
paths:
  - 'src/**'                        # Python исходники
  - 'docs/**'                       # Markdown документация
  - 'mkdocs.yml'                    # Конфиг MkDocs
  - 'extensions/**'                 # JS браузерное расширение
  - 'mcp-powershell-servers/**'     # PowerShell MCP серверы
  - 'scripts/**'                    # PowerShell операционные скрипты
  - 'install/**'                    # Скрипты установки
  - 'utils/**'                      # Вспомогательные утилиты
  - 'static/**'                     # Веб-интерфейс
  - 'check_engine/**'               # Диагностические тесты
  - 'SANDBOX/**'                    # SDK и эксперименты
  - 'config.json'                   # Основная конфигурация
  - 'config_manager.py'             # Класс Config
  - 'run.py'                        # Точка входа
  - '.github/workflows/deploy-docs.yml'
```

---

## Job 1: docs-js (TypeDoc)

Генерирует документацию из JSDoc аннотаций в JavaScript файлах браузерного расширения.

**Исходники:** `extensions/browser-extension-summarizer/`

**Инструменты:**
- [TypeDoc](https://typedoc.org/) — парсит JSDoc и генерирует документацию
- [typedoc-plugin-markdown](https://typedoc-plugin-markdown.org/) — выводит в формате Markdown вместо HTML

**Конфигурация:** `extensions/browser-extension-summarizer/typedoc.json`

**Вывод:** `docs/ru/dev/js/` — передаётся в job `deploy` через GitHub Actions artifact

**Покрываемые файлы:**

| Файл | Описание |
|---|---|
| `summarizer.js` | Логика суммаризации страниц, маршрутизация к провайдерам |
| `connectors/gemini.js` | Коннектор к Google Gemini |
| `connectors/openai-compat.js` | OpenAI-совместимый коннектор |
| `connectors/openrouter.js` | Коннектор к OpenRouter |
| `logger.js` | Логирование в расширении |
| `ui-manager.js` | Управление UI компонентами |

**Формат JSDoc** (используется в проекте):

```javascript
/**
 * Суммаризация текста одной страницы.
 *
 * @param {string} pageText - Текст страницы для суммаризации
 * @param {string} provider - ID провайдера ('gemini', 'foundry', ...)
 * @param {string} apiKey   - API ключ провайдера
 * @param {string} model    - Название модели
 * @param {string} [customUrl] - Кастомный URL (опционально)
 * @param {string} [lang]   - Код языка, по умолчанию 'auto'
 * @returns {Promise<string>} Текст суммаризации
 */
export async function summarizePage(pageText, provider, apiKey, model, customUrl = '', lang = 'auto') {
```

---

## Job 2: docs-powershell (PlatyPS)

Генерирует документацию из comment-based help в PowerShell скриптах MCP серверов.

**Исходники:** `mcp-powershell-servers/src/servers/*.ps1`

**Инструменты:**
- [PlatyPS](https://github.com/PowerShell/platyPS) — стандартный инструмент Microsoft для генерации `.md` из PowerShell help

**Вывод:** `docs/ru/dev/powershell/` — передаётся в job `deploy` через GitHub Actions artifact

**Покрываемые файлы:**

| Файл | Описание |
|---|---|
| `McpSTDIOServer.ps1` | MCP сервер через STDIO (JSON-RPC 2.0) |
| `McpHttpsServer.ps1` | MCP сервер через HTTPS |
| `McpWPCLIServer.ps1` | MCP сервер для WordPress CLI |
| `McpWpServer.ps1` | MCP сервер для WordPress |
| `McpHuggingFaceServer.ps1` | MCP сервер для HuggingFace |

**Формат comment-based help** (используется в проекте):

```powershell
<#
.SYNOPSIS
    MCP PowerShell Server (STDIO версия)
.DESCRIPTION
    Сервер MCP для выполнения PowerShell скриптов через протокол JSON-RPC
    с использованием стандартных потоков ввода-вывода.
.NOTES
    Version: 1.1.5
    Author: hypo69
#>
```

---

## Job 3: deploy (MkDocs + mkdocstrings)

Финальный job. Скачивает артефакты из `docs-js` и `docs-powershell`, затем собирает и публикует весь сайт.

**Инструменты:**

| Пакет | Назначение |
|---|---|
| `mkdocs-material` | Тема и движок MkDocs |
| `mkdocs-static-i18n` | Поддержка русского и английского языков |
| `mkdocstrings[python]` | Авто-генерация из Python docstrings |
| `griffe` | Парсер Python AST для mkdocstrings |

**Зависимости:** `docs/requirements.txt`

**Конфигурация:** `mkdocs.yml`

**Python docstrings** — используется Google style, который mkdocstrings понимает нативно:

```python
async def health_check(self):
    """Проверка состояния Foundry.

    Returns:
        dict: Словарь со статусом, URL и timestamp.
            Ключ ``status`` может быть ``healthy``, ``unhealthy`` или ``disconnected``.

    Example:
        >>> result = await client.health_check()
        >>> print(result["status"])
        healthy
    """
```

**Синтаксис вставки в `.md` файлы:**

```markdown
::: src.models.foundry_client.FoundryClient
::: src.rag.rag_system
::: config_manager.Config
```

---

## Структура вывода

После успешного деплоя документация доступна по адресу:
`https://hypo69.github.io/FastApiFoundry-Docker/`

Структура разделов:

```
/                           ← Главная (docs/ru/index.md)
/user/getting_started/      ← Быстрый старт
/user/installation/         ← Установка
/dev/architecture/          ← Архитектура
/dev/api_reference/         ← REST API справочник
/dev/code/foundry_client/   ← Python: FoundryClient (mkdocstrings)
/dev/code/config/           ← Python: Config (mkdocstrings)
/dev/code/rag_system/       ← Python: RAG System (mkdocstrings)
/dev/code/app/              ← Python: App Factory (mkdocstrings)
/dev/js/                    ← JS: Browser Extension (TypeDoc)
/dev/powershell/            ← PowerShell: MCP Servers (PlatyPS)
```

---

## Первоначальная настройка

Для активации публикации на GitHub Pages выполните один раз:

1. Перейдите в **Settings → Pages** репозитория
2. В поле **Source** выберите ветку `gh-pages`
3. Сохраните

После первого успешного запуска workflow ветка `gh-pages` создаётся автоматически командой `mkdocs gh-deploy --force`.

---

## Локальная сборка

Для предпросмотра документации локально:

```bash
# Установить зависимости
pip install -r docs/requirements.txt

# Запустить dev-сервер с hot reload
mkdocs serve

# Или собрать статику в папку site/
mkdocs build
```

Сервер будет доступен по адресу `http://127.0.0.1:8000`.

!!! note "JS и PowerShell docs локально"
    При локальной сборке разделы `/dev/js/` и `/dev/powershell/` показывают заглушки.
    Полная документация генерируется только в CI. Для локальной генерации JS docs:
    ```bash
    cd extentions/browser-extention-summarizer
    npx typedoc --plugin typedoc-plugin-markdown
    ```

---

## Добавление новых модулей в документацию

### Python модуль

1. Создайте файл `docs/ru/dev/code/my_module.md`:
    ```markdown
    # My Module
    ::: src.my_package.my_module
    ```
2. Добавьте в `mkdocs.yml` в секцию `nav`:
    ```yaml
    - My Module: dev/code/my_module.md
    ```

### JavaScript файл

Добавьте путь к файлу в `extensions/browser-extension-summarizer/typedoc.json`:

```json
{
  "entryPoints": [
    "summarizer.js",
    "my-new-module.js"
  ]
}
```

### PowerShell скрипт

Добавьте `.ps1` файл в `mcp-powershell-servers/src/servers/` с comment-based help блоком (`.SYNOPSIS`, `.DESCRIPTION`). Job `docs-powershell` подхватит его автоматически через `Get-ChildItem -Filter "*.ps1"`.
