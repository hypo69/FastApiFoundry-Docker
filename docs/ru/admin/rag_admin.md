# RAG — управление индексами

Администратор управляет RAG-профилями: создаёт, загружает документы, переключает активный профиль.

---

## Где хранятся индексы

```
~/.ai-assist/rag/
├── train_data/           ← активный профиль (задан в config.json)
│   ├── faiss.index       ← FAISS IndexIDMap
│   ├── documents.db      ← SQLite: документы и чанки
│   ├── meta.json         ← chunks, model, updated_at
│   └── README.md         ← описание (отображается в UI)
├── project_docs/
│   └── ...
└── legal/
    └── ...
```

Активный профиль задаётся в `config.json`:

```json
{
  "rag_system": {
    "index_dir": "~/.ai-assist/rag/train_data",
    "enabled": true
  }
}
```

---

## Загрузка документов через веб-интерфейс

Вкладка **RAG → Index Documents** содержит две вкладки.

### ZIP / Files

Загрузка одного или нескольких файлов/архивов из браузера.

- Поддерживаемые форматы: `zip`, `7z`, `rar`, `tar`, `tar.gz`, `tgz`, `pdf`, `docx`, `md`, `txt`, `html`, `xlsx`, `pptx`
- Содержимое архивов рекурсивно извлекается и индексируется как единый документ
- Прогресс отображается пофайлово: extract → chunk → embed → index
- Endpoint: `POST /api/v1/rag/index/stream` (SSE)

### Directory

Загрузка всех файлов из локальной папки через нативный диалог браузера.

- Используется `<input webkitdirectory>` — браузер открывает системный диалог выбора папки
- Все файлы внутри папки (включая подпапки) передаются на сервер
- Каждый файл индексируется отдельно через тот же SSE endpoint
- Относительный путь (`ru/about.md`) сохраняется как `source_name` в метаданных

!!! warning "Временные файлы при загрузке"
    Все загружаемые файлы временно сохраняются на диск сервера перед обработкой.
    Это архитектурное ограничение: MarkItDown, zipfile, tarfile, py7zr и rarfile
    работают с путями к файлам, а не с байтами в памяти.
    Временные файлы создаются через `tempfile.mkstemp()` в %TEMP% или /tmp
    и удаляются сразу после обработки.

!!! info "Имена файлов с путями (webkitdirectory)"
    При загрузке директории браузер передаёт `filename` как относительный путь
    (например `ru/about.md`). Сервер использует его только как метку источника
    в индексе — для создания временного файла берётся только расширение из `basename`.

---

## Построить индекс из серверной директории

Если документы уже находятся на сервере — используйте `POST /api/v1/rag/build`:

```bash
POST /api/v1/rag/build
{
  "docs_dir": "C:/Documents/MyProject",
  "model": "sentence-transformers/all-mpnet-base-v2",
  "chunk_size": 1000,
  "overlap": 50,
  "force": false
}
```

Ответ:

```json
{
  "success": true,
  "chunks": 342,
  "rebuilt": true,
  "index_dir": "~/.ai-assist/rag/MyProject",
  "message": "Index rebuilt"
}
```

---

## Переключить активный профиль

```bash
# Активировать профиль
POST /api/v1/rag/profiles/project_docs/activate

# Отключить RAG (без удаления индексов)
POST /api/v1/rag/profiles/deactivate
```

В веб-интерфейсе: **RAG → RAG Bases** → кнопка ▶ рядом с профилем.

---

## Document Manager

Вкладка **RAG → Document Manager** позволяет управлять документами инкрементально:

- Добавить документ вручную (текст + заголовок)
- Редактировать — переиндексируются только изменённые чанки
- Удалить — soft-delete, векторы остаются в FAISS до Compact
- **Compact** — перестроить FAISS из активных чанков (появляется когда >20% неактивных)

---

## README.md для профиля

Каждый профиль может содержать `README.md` с описанием:

```markdown
# Документация проекта

Техническая документация по проекту XYZ.
Содержит: архитектурные решения, API описания, инструкции по развёртыванию.
```

API возвращает это описание при `GET /api/v1/rag/profiles`.

---

## Миграция legacy-индекса

Старые профили с `chunks.json` (без SQLite) нужно мигрировать:

```bash
POST /api/v1/rag/migrate/index-id-map
```

Миграция импортирует чанки в `documents.db` и перестраивает `faiss.index` как `IndexIDMap`.

---

## Размер индекса и требования к RAM

| Документов | RAM под индекс | Время построения (CPU) |
|---|---|---|
| 5 000 | ~200 MB | 10–30 мин |
| 50 000 | ~2 GB | 2–5 часов |
| 100 000 | ~4 GB | 5–12 часов |

!!! tip "Большие корпусы — строить в Google Colab"
    При 50 000+ документов используйте [Colab notebook](https://colab.research.google.com/github/hypo69/FastApiFoundry-Docker/blob/master/notebooks/rag_colab.ipynb) с GPU T4.
    Готовый индекс распакуйте в `~/.ai-assist/rag/<profile>/`.
