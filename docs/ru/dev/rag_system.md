# 📚 RAG Система (Retrieval-Augmented Generation)

!!! info "См. также"
    Краткий технический справочник по всем классам и файлам модуля: [`src/rag/README.md`](https://github.com/hypo69/FastApiFoundry-Docker/blob/master/src/rag/README.md)

Модуль `src/rag/rag_system.py` является ядром системы RAG, отвечающим за управление векторными индексами FAISS, поиск релевантных фрагментов текста и их подготовку для передачи в LLM.

---

## Как работает RAG — полный цикл

```
ИНДЕКСАЦИЯ (один раз / при обновлении документов)
  │
  ├─ RAGIndexer.index_directory(docs/)
  │     └─ читает .md, .txt, .html, .rst
  │         └─ chunk_text() — нарезает на куски ~1000 символов
  │             с перекрытием 50 символов
  │
  ├─ RAGIndexer.create_embeddings()
  │     └─ SentenceTransformer.encode(chunks)
  │         → float32 векторы размерностью 384 или 768
  │
  └─ RAGIndexer.save_index(rag_index/)
        ├─ faiss.normalize_L2(embeddings)   ← нормализация для cosine similarity
        ├─ faiss.IndexFlatIP(dim)           ← Inner Product = cosine после нормализации
        ├─ faiss.index → faiss.index
        └─ chunks → chunks.json

ПОИСК (при каждом запросе)
  │
  ├─ RAGSystem.search(query, top_k=5)
  │     ├─ проверка кэша (query, top_k) → если есть, вернуть сразу
  │     ├─ SentenceTransformer.encode([query]) → вектор запроса
  │     ├─ faiss.index.search(query_vector, top_k)
  │     │     → distances[], indices[]
  │     └─ собрать chunks[indices] + score = distance
  │
  └─ результат: [{content, score, source, section, ...}, ...]

ИСПОЛЬЗОВАНИЕ В ГЕНЕРАЦИИ
  │
  POST /api/v1/ai/generate  (use_rag=true)
    ├─ rag_system.search(prompt)
    ├─ format_context(results)
    └─ prompt = "Context:\n{rag}\n\nUser: {prompt}"
         → foundry_client.generate_text(prompt)
```

---

## Модели эмбеддингов

Используются модели из библиотеки **SentenceTransformers**. Выбор модели задаётся в `config.json`:

```json
"rag_system": {
  "model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

| Модель | Размерность | Размер | Скорость | Качество | Рекомендация |
|---|---|---|---|---|---|
| `all-MiniLM-L6-v2` | 384 | ~80 MB | быстрая | хорошее | по умолчанию, большие корпуса |
| `all-mpnet-base-v2` | 768 | ~420 MB | медленнее | лучшее | высокое качество поиска |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | ~120 MB | средняя | хорошее | мультиязычные тексты |

!!! warning "Модель при индексации и поиске должна совпадать"
    При загрузке индекса `reload_index()` сравнивает размерность вектора индекса
    с размерностью текущей модели. Если не совпадают — индекс отклоняется с ошибкой.
    Индекс нужно пересобрать с новой моделью.

---

## Ключевые детали реализации

**Нарезка текста** — умная: ищет ближайшую точку/восклицательный/вопросительный знак перед границей чанка, чтобы не резать на середине предложения. Для Markdown — учитывает заголовки `#` как границы разделов.

**Инкрементальная индексация** — при повторной индексации сравнивает MD5 чексумму файла. Если файл не изменился — переиспользует старые векторы без повторного кодирования.

**Кэш поиска** — результаты кэшируются по ключу `(query, top_k)`. Сбрасывается при `reload_index()`.

**Дедупликация чанков** — при загрузке индекса удаляются дублирующиеся фрагменты по тексту.

**Профили RAG** — несколько независимых индексов в `~/.rag/<name>/`. Переключение через `POST /api/v1/rag/profiles/load` без перезапуска сервера.

---


### `RAGSystem`

Класс `RAGSystem` управляет жизненным циклом RAG-индекса. Реализован как модульный синглтон (`rag_system = RAGSystem()` в конце файла).

#### `initialize()`
Асинхронный метод, вызываемый при старте приложения (`app.py` lifespan). Загружает индекс из директории, указанной в `config.rag_index_dir`. Если индекс не найден — возвращает `False` без ошибки, RAG-функциональность остаётся отключённой.

#### `reload_index(index_dir: str)`

**Назначение:** Динамическая перезагрузка индекса RAG. Позволяет переключать активные профили (базы знаний) без перезапуска FastAPI сервера.

**Логика:**
1. Проверяет существование директории `index_dir`.
2. **Проверка целостности индекса (`_check_index_integrity`)**: Перед загрузкой `faiss.index` выполняется базовая проверка файла (существование, тип, минимальный размер ~100 байт). Предотвращает загрузку повреждённых файлов.
3. **Проверка совместимости размерности векторов**: Сравнивает размерность (`.d`) загруженного FAISS индекса с размерностью эмбеддингов текущей `SentenceTransformer` модели. Если не совпадают — загрузка прерывается с ошибкой.
4. Загружает `faiss.index` (векторная база) и `chunks.json` (метаданные текстовых фрагментов).
5. **Удаление дубликатов (`_remove_duplicate_chunks`)**: Фильтрует чанки по уникальности текста. Оптимизирует память и предотвращает повторяющиеся результаты.
6. Атомарно обновляет `self.index` и `self.chunks`.
7. Очищает кеш поиска (`_search_cache`).
8. **Обновление `meta.json`**: Сохраняет/обновляет файл метаданных в директории индекса (количество чанков, модель, время обновления).

#### `search(query: str, top_k: int)`

Выполняет векторный поиск по индексу.
1. **Кеширование**: Проверяет `_search_cache` по ключу `(query, top_k)`.
2. **Генерация эмбеддингов**: Использует `SentenceTransformer` (`_get_model()`) — ленивая загрузка при первом вызове.
3. **Поиск в FAISS**: `self.index.search(query_vector, top_k)`.
4. **Форматирование результатов**: Связывает индексы с чанками из `self.chunks`, добавляет поле `score` (расстояние FAISS).

#### `filter_by_source(results, sources)`

Фильтрует результаты поиска, оставляя только те, чьё поле `source` входит в список `sources`.

#### `filter_by_score(results, min_score)`

Отсекает результаты с оценкой схожести (`score`) ниже порога `min_score`.

#### `format_context(results)`

Объединяет текстовые фрагменты через двойной перенос строки для передачи в LLM.

#### `index_directories(source_dirs)`

Индексирует несколько директорий. Список берётся из аргумента или из `config.get_section("rag_system").get("source_dirs", [])`.

---

## 📁 RAGProfileManager

**Файл:** `src/rag/rag_profile_manager.py`  
**Синглтон:** `rag_profile_manager`

Управляет именованными RAG индексами в директории `config.dir_rag` (по умолчанию `~/.rag/<profile>/`).

### Методы

| Метод | Описание |
|---|---|
| `list_profiles()` | Список всех профилей с флагами `has_index`, `description` |
| `get_profile_path(name)` | Путь к профилю или `None` |
| `create_profile(name, description)` | Создать директорию профиля, сохранить `description.txt` |
| `delete_profile(name)` | Переименовать в `<name>~` (soft delete) |

### Структура профиля

```
~/.rag/
├── support/
│   ├── faiss.index       # FAISS векторный индекс
│   ├── chunks.json       # Текстовые чанки с метаданными
│   ├── meta.json         # Статистика: chunks, model, updated_at
│   └── description.txt   # Описание профиля (опционально)
├── code/
│   └── ...
└── support~              # Удалённый профиль (soft delete)
```

`list_profiles()` проверяет наличие как `faiss.index`, так и `index.faiss` (оба варианта имени).

---

## ☁️ Построение индекса в Google Colab

Построение RAG-индекса — вычислительно затратная операция: модель `all-mpnet-base-v2` кодирует тысячи текстовых фрагментов в векторы. На слабом CPU это может занять десятки минут. Google Colab предоставляет **бесплатный GPU (T4)**, который ускоряет процесс в 10–30 раз.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hypo69/FastApiFoundry-Docker/blob/master/notebooks%5Crag_colab.ipynb)

### Зачем использовать Colab

| Ситуация | Локально | Colab (T4 GPU) |
|---|---|---|
| 1 000 чанков | ~2–5 мин | ~10–20 сек |
| 10 000 чанков | ~20–50 мин | ~2–5 мин |
| Большая документация (50+ файлов) | медленно | быстро |
| Нет GPU на машине | единственный вариант | ✅ |

### Как пользоваться

```
Colab notebook (rag_colab.ipynb)
  │
  ├─ [1] Установка зависимостей
  │     └─ pip install faiss-cpu sentence-transformers
  │
  ├─ [2] Загрузка документов (выбрать один вариант)
  │     ├─ A: Upload files вручную
  │     ├─ B: Mount Google Drive
  │     └─ C: git clone репозитория
  │
  ├─ [3] Конфигурация
  │     ├─ MODEL_NAME — модель эмбеддингов
  │     ├─ CHUNK_SIZE — размер фрагмента (default: 1000)
  │     └─ OVERLAP — перекрытие (default: 50)
  │
  ├─ [4] Построение индекса
  │     └─ RAGIndexer → FAISS index + chunks.json
  │
  ├─ [5] Тест поиска
  │     └─ проверить качество до скачивания
  │
  └─ [6] Скачать rag_index.zip
        └─ распаковать в ~/.rag/<profile>/
```

### Настройка на максимальную производительность

**1. Включить GPU:**
> Runtime → Change runtime type → Hardware accelerator → **GPU (T4)**

**2. Выбрать модель под задачу:**

| Модель | Размерность | Скорость | Качество | Рекомендация |
|---|---|---|---|---|
| `all-mpnet-base-v2` | 768 | средняя | ⭐⭐⭐ лучшее | по умолчанию |
| `all-MiniLM-L6-v2` | 384 | быстрая | ⭐⭐ хорошее | большие корпусы |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | средняя | ⭐⭐ | мультиязычные тексты |

**3. Увеличить `batch_size`** в ячейке `create_embeddings` (по умолчанию 64):
- T4 GPU: `batch_size=128` или `256`
- Если `CUDA out of memory` — уменьшить до `32`

**4. Использовать Google Drive** для хранения документов — быстрее, чем загружать каждый раз вручную.

### Использование готового индекса

После скачивания `rag_index.zip`:

```powershell
# Распаковать в профиль RAG
Expand-Archive rag_index.zip -DestinationPath "$env:USERPROFILE\.rag\my_docs"
```

Затем в веб-интерфейсе: вкладка **RAG** → **RAG Bases** → выбрать профиль `my_docs` → **Load**.

---

## 🔌 RAG API Endpoints

**Файл:** `src/api/endpoints/rag.py`  
**Prefix:** `/api/v1/rag`

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/rag/status` | Статус системы: enabled, index_dir, model, chunk_size |
| `PUT` | `/rag/config` | Обновить секцию `rag_system` в config.json |
| `POST` | `/rag/search` | Поиск: `{query, top_k, min_score}` |
| `POST` | `/rag/rebuild` | Запустить пересборку индекса |
| `POST` | `/rag/clear` | Удалить файлы `.index` и `.json` из index_dir |
| `GET` | `/rag/dirs` | Список директорий с текстовыми файлами |
| `GET` | `/rag/cwd` | Текущая рабочая директория сервера |
| `GET` | `/rag/browse` | Обзор файловой системы (для выбора папок) |
| `GET` | `/rag/profiles` | Список профилей из `~/.rag/` |
| `POST` | `/rag/profiles/load` | Переключить активный профиль |
| `DELETE` | `/rag/profiles/{name}` | Удалить профиль (soft delete) |
| `POST` | `/rag/build` | Создать индекс из директории |
| `POST` | `/rag/extract/file` | Извлечь текст из загруженного файла |
| `POST` | `/rag/extract/url` | Извлечь текст с веб-страницы |
| `GET` | `/rag/extract/formats` | Список поддерживаемых форматов |
