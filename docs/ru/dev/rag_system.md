# 📚 RAG Система (Retrieval-Augmented Generation)

Модуль `src/rag/rag_system.py` является ядром системы RAG, отвечающим за управление векторными индексами FAISS, поиск релевантных фрагментов текста и их подготовку для передачи в LLM.

## 🧠 Основные компоненты

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
