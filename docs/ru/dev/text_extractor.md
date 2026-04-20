# Text Extractor — Документация для разработчиков

Модуль `src/rag/text_extractor_4_rag/` — движок извлечения текста из 40+ форматов файлов
и веб-страниц. Используется как библиотека внутри FastAPI Foundry для подготовки данных
перед RAG-индексацией.

## Архитектура модуля

```
src/rag/text_extractor_4_rag/
├── __init__.py      # Публичный API: TextExtractor, settings
├── config.py        # Класс Settings — config.json + env vars
├── extractors.py    # Класс TextExtractor — основная логика извлечения
├── utils.py         # Вспомогательные функции
└── main.py          # Standalone FastAPI приложение (опционально)
```

## Класс `TextExtractor`

```python
from src.rag.text_extractor_4_rag import TextExtractor

extractor = TextExtractor()
```

### Методы

#### `extract_text(file_content: bytes, filename: str) -> List[Dict]`

Извлекает текст из файла. Определяет формат по расширению.
Для архивов возвращает список результатов (по одному на каждый файл внутри).

```python
with open("document.pdf", "rb") as f:
    content = f.read()

results = extractor.extract_text(content, "document.pdf")
# [{"filename": "document.pdf", "path": "document.pdf",
#   "size": 204800, "type": "pdf", "text": "..."}]
```

#### `extract_from_url(url: str, user_agent: Optional[str], extraction_options) -> List[Dict]`

Извлекает текст с веб-страницы или файла по URL.
Автоматически определяет тип контента через HEAD-запрос:
- HTML-страница → парсинг через BeautifulSoup
- Файл → скачивание + `extract_text()`

```python
results = extractor.extract_from_url("https://example.com/doc.pdf")
```

### Формат результата

Каждый элемент возвращаемого списка:

```python
{
    "filename": "document.pdf",   # имя файла
    "path": "document.pdf",       # путь (или URL для веб)
    "size": 204800,               # размер в байтах
    "type": "pdf",                # расширение
    "text": "Извлечённый текст"   # чистый текст
}
```

## Класс `Settings`

Все настройки читаются в следующем порядке приоритета (высший побеждает):

1. **Переменная окружения** (`.env` или системная)
2. **`config.json` → секция `text_extractor`**
3. **Встроенное значение по умолчанию**

```python
from src.rag.text_extractor_4_rag.config import settings

print(settings.MAX_FILE_SIZE)       # 20971520 (20 MB)
print(settings.OCR_LANGUAGES)       # "rus+eng"
print(settings.ENABLE_JAVASCRIPT)   # False
```

### Секция `text_extractor` в `config.json`

```json
{
  "text_extractor": {
    "max_file_size_mb": 20,
    "processing_timeout_seconds": 300,
    "ocr_languages": "rus+eng",
    "enable_javascript": false,
    "max_images_per_page": 20,
    "web_page_timeout": 30,
    "enable_resource_limits": true
  }
}
```

Эти значения редактируются через вкладку **Settings → Text Extractor** в веб-интерфейсе.

### Полная таблица настроек

| Параметр | config.json ключ | Env var | По умолчанию | Описание |
|---|---|---|---|---|
| Макс. размер файла | `max_file_size_mb` | `MAX_FILE_SIZE` | 20 МБ | Максимальный размер загружаемого файла |
| Таймаут обработки | `processing_timeout_seconds` | `PROCESSING_TIMEOUT_SECONDS` | 300 с | Максимальное время обработки файла |
| Языки OCR | `ocr_languages` | `OCR_LANGUAGES` | `rus+eng` | Языки Tesseract через `+` |
| JavaScript | `enable_javascript` | `ENABLE_JAVASCRIPT` | `false` | JS-рендеринг через Playwright |
| Таймаут веб-запроса | `web_page_timeout` | `WEB_PAGE_TIMEOUT` | 30 с | Таймаут загрузки веб-страницы |
| Макс. изображений | `max_images_per_page` | `MAX_IMAGES_PER_PAGE` | 20 | Максимум изображений для OCR на странице |
| Ограничения ресурсов | `enable_resource_limits` | `ENABLE_RESOURCE_LIMITS` | `true` | Лимиты памяти для subprocess (Unix) |
| Вложенность архивов | — | `MAX_ARCHIVE_NESTING` | 3 | Глубина вложенности архивов |
| Макс. распакованный | — | `MAX_EXTRACTED_SIZE` | 100 МБ | Лимит распакованного содержимого |
| Лимит LibreOffice | — | `MAX_LIBREOFFICE_MEMORY` | 1.5 ГБ | Лимит памяти для конвертации DOC/PPT |
| Лимит Tesseract | — | `MAX_TESSERACT_MEMORY` | 512 МБ | Лимит памяти для OCR |

## API Endpoints

Эндпоинты добавлены в `src/api/endpoints/rag.py` с префиксом `/api/v1/rag/`:

### `POST /api/v1/rag/extract/file`

Извлечение текста из загруженного файла.

**Request:** `multipart/form-data`, поле `file`

**Response:**
```json
{
  "success": true,
  "filename": "report.pdf",
  "count": 1,
  "total_chars": 8420,
  "files": [{"filename": "...", "path": "...", "size": 0, "type": "pdf", "text": "..."}]
}
```

### `POST /api/v1/rag/extract/url`

Извлечение текста с веб-страницы или файла по URL.

**Request body:**
```json
{
  "url": "https://example.com/page",
  "enable_javascript": false,
  "process_images": false,
  "web_page_timeout": 30
}
```

### `GET /api/v1/rag/extract/formats`

Возвращает словарь поддерживаемых форматов из `Settings.SUPPORTED_FORMATS`.

## Интеграция с RAG индексатором

Для использования TextExtractor при построении RAG индекса:

```python
from src.rag.text_extractor_4_rag import TextExtractor
from src.rag.indexer import RAGIndexer

extractor = TextExtractor()
indexer = RAGIndexer()

# Извлечь текст из файла
with open("manual.pdf", "rb") as f:
    results = extractor.extract_text(f.read(), "manual.pdf")

# Добавить в индекс
for result in results:
    if result["text"]:
        indexer.add_text(result["text"], metadata={"source": result["filename"]})
```

## Опциональные зависимости

Модуль работает с частично установленными зависимостями — недоступные форматы
просто не поддерживаются, остальные работают нормально.

| Зависимость | Форматы | Установка |
|---|---|---|
| `pdfplumber` | PDF | `pip install pdfplumber` |
| `python-docx` | DOCX, DOC | `pip install python-docx` |
| `pandas` | XLSX, XLS, CSV | `pip install pandas openpyxl` |
| `python-pptx` | PPTX, PPT | `pip install python-pptx` |
| `pytesseract` + Tesseract | Изображения OCR | `pip install pytesseract` + Tesseract |
| `beautifulsoup4` | HTML, EPUB | `pip install beautifulsoup4 lxml` |
| `odfpy` | ODT | `pip install odfpy` |
| `striprtf` | RTF | `pip install striprtf` |
| `PyYAML` | YAML | `pip install pyyaml` |
| `requests` | URL извлечение | `pip install requests` |
| `playwright` | JS-рендеринг | `pip install playwright && playwright install chromium` |
| `rarfile` | RAR архивы | `pip install rarfile` |
| `py7zr` | 7Z архивы | `pip install py7zr` |
| `python-magic` | MIME валидация | `pip install python-magic` |

## Безопасность

### SSRF защита

`extract_from_url()` проверяет URL перед запросом:
- Блокирует `localhost`, `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
- Блокирует metadata service `169.254.169.254`
- Блокирует Docker bridge gateway
- Настраивается через `BLOCKED_IP_RANGES` и `BLOCKED_HOSTNAMES`

### Zip Bomb защита

При обработке архивов:
- Проверяется суммарный размер распакованных файлов до извлечения
- Ограничение: `MAX_EXTRACTED_SIZE` (100 МБ по умолчанию)
- Ограничение глубины вложенности: `MAX_ARCHIVE_NESTING` (3)

### MIME валидация

Расширение файла проверяется на соответствие реальному содержимому через `python-magic`.
При несоответствии файл отклоняется.

## Ограничения на Windows

Модуль `resource` (Unix) недоступен на Windows — ограничения памяти для subprocess
автоматически отключаются. Функциональность извлечения текста при этом не затрагивается.

LibreOffice (для DOC/PPT конвертации) должен быть установлен отдельно.
