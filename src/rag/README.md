# RAG System

Модуль поиска и извлечения контекста (Retrieval-Augmented Generation) для FastAPI Foundry.

---

## Файлы

| Файл | Назначение |
|------|-----------|
| `rag_system.py` | Основной класс `RAGSystem` — загрузка индекса, поиск, управление |
| `__init__.py` | Экспорт глобального экземпляра `rag_system` |

Индексатор для построения индекса находится в корне проекта: `rag_indexer.py`

---

## Как это работает

```
Документы (docs/, .md, .txt, .html)
        ↓
  rag_indexer.py          ← запускается вручную один раз
        ↓
  rag_index/
    ├── faiss.index       ← векторный индекс FAISS
    ├── chunks.json       ← текст и метаданные чанков
    └── index_info.json   ← модель, размерность, дата создания
        ↓
  rag_system.py           ← загружает индекс при старте сервера
        ↓
  search(query) → релевантные чанки → контекст для AI
```

---

## Класс RAGSystem

Глобальный экземпляр: `from src.rag.rag_system import rag_system`

### Методы

| Метод | Описание |
|-------|---------|
| `await initialize()` | Загрузить индекс и модель эмбеддингов. Вызывается при старте в lifespan |
| `await search(query, top_k)` | Найти top_k релевантных чанков по запросу |
| `format_context(results)` | Отформатировать результаты поиска как строку контекста для промпта |
| `await get_status()` | Вернуть статус: загружен ли индекс, количество чанков и векторов |
| `await reload_index()` | Сбросить и перезагрузить индекс с диска |
| `await clear_index()` | Удалить файлы индекса и сбросить состояние |
| `await get_all_chunks()` | Вернуть все чанки с метаданными |

### Формат результата поиска

```python
[
    {
        "source": "installation.md",   # имя файла-источника
        "section": "Быстрый старт",    # заголовок секции
        "text": "...",                  # текст чанка
        "score": 0.91                  # косинусное сходство (0–1)
    },
    ...
]
```

---

## Конфигурация

Читается из `config.json`, секция `rag_system`:

```json
{
  "rag_system": {
    "enabled": true,
    "index_dir": "rag_index",
    "model": "sentence-transformers/all-mpnet-base-v2",
    "chunk_size": 1000,
    "top_k": 5
  }
}
```

| Параметр | Описание |
|----------|---------|
| `enabled` | Включить RAG. Если `false` — `initialize()` сразу возвращает `False` |
| `index_dir` | Директория с файлами индекса |
| `model` | Модель эмбеддингов. **Должна совпадать** с моделью, использованной при индексации |
| `chunk_size` | Размер чанка в символах. Должен совпадать с `--chunk-size` при запуске `rag_indexer.py` |
| `top_k` | Количество результатов поиска по умолчанию |

---

## Построение индекса

Перед первым запуском нужно проиндексировать документы:

```powershell
# Индексировать директорию docs/
python rag_indexer.py --docs-dir docs --output-dir rag_index

# Явно указать параметры, совпадающие с config.json
python rag_indexer.py `
  --docs-dir docs `
  --output-dir rag_index `
  --model sentence-transformers/all-mpnet-base-v2 `
  --chunk-size 1000 `
  --overlap 50
```

> ⚠️ Модель (`--model`) и размер чанка (`--chunk-size`) должны совпадать со значениями в `config.json`. Несовпадение модели делает результаты поиска некорректными.

---

## API Endpoints

Эндпоинты в `src/api/endpoints/rag.py` (`/api/v1/rag/`):

| Метод | Путь | Описание | Статус |
|-------|------|---------|--------|
| GET | `/rag/status` | Статус RAG: включён, модель, количество чанков | ✅ реализован |
| PUT | `/rag/config` | Обновить секцию `rag_system` в `config.json` | ✅ реализован |
| POST | `/rag/clear` | Удалить все файлы индекса | ✅ реализован |
| POST | `/rag/search` | Поиск по запросу | ⚠️ заглушка (mock) |
| POST | `/rag/rebuild` | Перестроить индекс | ⚠️ заглушка (mock) |

> `/rag/search` и `/rag/rebuild` возвращают mock-данные и не используют `RAGSystem`. Реальный поиск выполняется через `rag_system.search()` напрямую из эндпоинта генерации (`/api/v1/generate`).

---

## Зависимости

```
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
numpy>=1.24.0
torch>=2.0.0
```

Установка:

```powershell
pip install sentence-transformers faiss-cpu numpy torch
# или через скрипт проекта
python install_rag_deps.py
```

Если зависимости не установлены — `RAGSystem` логирует предупреждение и отключается, сервер продолжает работу без RAG.
