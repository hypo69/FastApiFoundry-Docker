# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: API эндпоинты системы RAG
# =============================================================================
# Описание:
#   Управление системой RAG (Retrieval-Augmented Generation).
#   Включает настройку, поиск, управление индексами и профилями.
#
# Примеры:
#   GET /api/v1/rag/status  - Получение статуса системы
#   POST /api/v1/rag/search - Поиск по векторному индексу
#
# File: src/api/endpoints/rag.py
# Project: FastApiFoundry (Docker)
# Package: FastApiFoundry
# Module: api.endpoints.rag
# Version: 0.6.1
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# Date: 2025
# =============================================================================

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
import faiss

from ...rag.rag_system import rag_system
from src.core.config import config as app_config
from src.logger import logger
from ...utils.api_utils import api_response_handler
from ...rag.text_extractor_4_rag.utils import sanitize_filename as sanitize_for_filesystem

router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGConfig(BaseModel):
    enabled: bool = False
    index_dir: str = "./rag_index"
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    top_k: int = 5


class RAGSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    min_score: float = 0.0


class RAGBuildRequest(BaseModel):
    docs_dir: str
    output_dir: str = "./rag_index"
    model: str = "sentence-transformers/all-mpnet-base-v2"
    chunk_size: int = 1000
    overlap: int = 50
    force: bool = False


class ExtractURLRequest(BaseModel):
    url: str
    enable_javascript: bool = False
    process_images: bool = False
    web_page_timeout: int = 30


class RAGSearchResult(BaseModel):
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


@router.get("/status")
@api_response_handler
async def get_rag_status() -> dict:
    """! Получение статуса системы RAG.

    Returns:
        dict: Информация о состоянии: enabled, index_dir, model, chunk_size, total_chunks.

    Example:
        >>> status = await get_rag_status()
        >>> print(status['enabled'])
        True
    """
    total_chunks: int = 0
    index_dir: Path = Path(app_config.rag_index_dir)

    # Подсчет количества сегментов (chunks) в индексе
    # Counting of chunks in the index directory
    if index_dir.exists():
        total_chunks = len(list(index_dir.glob("*.json")))

    return {
        "success": True,
        "enabled": app_config.rag_enabled,
        "index_dir": str(index_dir),
        "model": app_config.rag_model,
        "chunk_size": app_config.rag_chunk_size,
        "total_chunks": total_chunks
    }


@router.put("/config")
@api_response_handler
async def update_rag_config(config: RAGConfig) -> dict:
    """! Обновление конфигурации системы RAG.

    Args:
        config (RAGConfig): Модель данных с новыми настройками.

    Returns:
        dict: Статус выполнения операции.
    """
    config_path: Path = Path("config.json")
    full_config: dict = {}

    # Чтение и обновление секции rag_system
    # Reading and updating the rag_system section
    full_config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    full_config["rag_system"] = config.model_dump() 
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(full_config, f, indent=2, ensure_ascii=False)
    return {"success": True, "message": "RAG configuration updated"}


@router.post("/search")
@api_response_handler
async def search_rag(request: RAGSearchRequest) -> dict:
    """! Выполнение поиска в системе RAG.

    Args:
        request (RAGSearchRequest): Запрос с текстом и параметром top_k.

    Returns:
        dict: Список результатов с контентом и оценками схожести.

    Example:
        >>> res = await search_rag(RAGSearchRequest(query="test", top_k=5, min_score=0.5))
        >>> len(res['results'])
        3
    """
    results: List[Dict[str, Any]] = []
    top_k: int = request.top_k or 5

    # Выполнение поиска через ядро системы
    # Execution of the search through the system core
    results = await rag_system.search(request.query, top_k=top_k)

    # Фильтрация результатов по порогу схожести
    # Filtration of results by the similarity threshold
    if request.min_score > 0:
        # ПОЧЕМУ ВЫБРАН ЭТОТ МЕТОД:
        #   Использование централизованной логики фильтрации из RAGSystem гарантирует 
        #   одинаковое поведение API и внутренних модулей генерации.
        results = rag_system.filter_by_score(results, request.min_score)

    return {"success": True, "results": results[: request.top_k], "total": len(results)}


@router.post("/rebuild")
@api_response_handler
async def rebuild_rag_index() -> dict:
    """! Пересборка векторного индекса.

    Returns:
        dict: Статус запуска процесса пересборки.
    """
    return {"success": True, "message": "RAG index rebuild started (mock)", "chunks_processed": 42}


@router.post("/clear")
@api_response_handler
async def clear_rag_chunks() -> dict:
    """! Очистка файлов индекса в настроенной директории.

    Returns:
        dict: Количество удаленных файлов.
    """
    index_dir: Path = Path(app_config.rag_index_dir)
    deleted_count: int = 0
    file: Path = None

    if index_dir.exists():
        # Удаление файлов .index и .json
        for file in index_dir.glob("*"):
            if file.is_file() and file.suffix in (".index", ".json"):
                file.unlink()
                deleted_count += 1

    return {"success": True, "message": f"Cleared {deleted_count} index files", "deleted_count": deleted_count}


@router.get("/dirs")
@api_response_handler
async def list_indexable_dirs() -> dict:
    """! Получение списка директорий, доступных для индексации.

    Returns:
        dict: Список путей с количеством найденных текстовых файлов.
    """
    root: Path = Path(".")
    candidates: list = []
    p: Path = None
    count: int = 0

    skip = {"venv", ".git", "__pycache__", "node_modules", "rag_index", ".amazonq"}
    for p in sorted(root.iterdir()):
        if p.is_dir() and p.name not in skip and not p.name.startswith("."):
            count = sum(1 for _ in p.rglob("*") if _.is_file() and _.suffix.lower() in {".md", ".txt", ".html", ".rst"})
            if count > 0:
                candidates.append({"path": str(p), "name": p.name, "files": count})
    return {"success": True, "dirs": candidates}


# ── RAG Profiles ──────────────────────────────────────────────────────────────

RAG_HOME = Path.home() / ".rag"


def _rag_home() -> Path:
    """! Получение домашней директории RAG (~/.rag)."""
    RAG_HOME.mkdir(parents=True, exist_ok=True)
    return RAG_HOME


def _profile_index_dir(safe_name: str) -> Path:
    """! Получение пути к директории профиля."""
    return _rag_home() / safe_name


@router.get("/cwd")
async def get_cwd() -> dict:
    """! Получение текущей рабочей директории сервера."""
    return {"success": True, "cwd": str(Path.cwd())}


@router.get("/browse")
async def browse_filesystem(path: str = "") -> dict:
    """! Просмотр файловой системы для выбора папок.

    Args:
        path (str): Абсолютный путь для обзора. По умолчанию домашняя папка.

    Returns:
        dict: Список вложенных папок и информация о текущем пути.

    Raises:
        HTTPException: Если путь не существует или не является директорией.
    """
    base = Path(path).expanduser() if path else Path.home()
    if not base.exists() or not base.is_dir():
        return {"success": False, "error": f"Directory not found: {base}"}

    skip = {"__pycache__", "node_modules", ".git", "venv", ".venv"}
    dirs = [{"name": p.name, "path": str(p)} for p in sorted(base.iterdir()) if p.is_dir() and p.name not in skip]

    return {
        "success": True,
        "current": str(base),
        "parent": str(base.parent) if base.parent != base else None,
        "dirs": dirs,
    }


@router.get("/profiles")
async def list_rag_profiles() -> dict:
    """! Получение списка всех профилей RAG в директории ~/.rag/.

    Returns:
        dict: success, profiles.
    """
    profiles: list = []
    d: Path = None

    for d in sorted(_rag_home().iterdir()):
        if not d.is_dir():
            continue
        meta_file = d / "meta.json"
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                meta["has_index"] = (d / "faiss.index").exists()
                profiles.append(meta)
            except Exception:
                pass
        else:
            profiles.append({"name": d.name, "safe_name": d.name, "index_dir": str(d), "has_index": (d / "faiss.index").exists()})
    return {"success": True, "profiles": profiles}


@router.post("/profiles/load")
async def load_rag_profile(request: dict) -> dict:
    """! Переключение активного профиля RAG.

    Args:
        request (dict): Тело запроса с полем 'name'.

    Returns:
        dict: Результат загрузки и путь к новому индексу.
    """
    config_path: Path = Path("config.json")
    name = (request.get("name") or "").strip()

    if not name:
        return {"success": False, "error": "name is required"}

    profile_dir = _profile_index_dir(sanitize_for_filesystem(name))
    if not profile_dir.exists():
        return {"success": False, "error": f"Profile '{name}' not found"}
    if not (profile_dir / "faiss.index").exists():
        return {"success": False, "error": f"Profile '{name}' has no index yet"}

    cfg = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    cfg.setdefault("rag_system", {})["index_dir"] = str(profile_dir)
    config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    await rag_system.reload_index(index_dir=str(profile_dir))

    return {"success": True, "message": f"Loaded profile '{name}'", "index_dir": str(profile_dir)}


@router.delete("/profiles/{name}")
async def delete_rag_profile(name: str) -> dict:
    """! Удаление профиля RAG с диска.

    Args:
        name (str): Имя профиля.

    Returns:
        dict: Статус удаления.
    """
    import shutil
    profile_dir: Path = None
    profile_dir = _profile_index_dir(sanitize_for_filesystem(name))
    if not profile_dir.exists():
        return {"success": False, "error": f"Profile '{name}' not found"}
    shutil.rmtree(profile_dir, ignore_errors=True)
    return {"success": True, "message": f"Profile '{name}' deleted"}


@router.post("/build")
async def build_rag_index(request: RAGBuildRequest) -> dict:
    """! Создание векторного индекса из локальной директории.

    Args:
        request (RAGBuildRequest): Параметры сборки (путь, модель, размер чанка).

    Returns:
        dict: Статистика сборки: количество сегментов, признак пересборки.
    """
    docs_dir: Path = Path(request.docs_dir).expanduser()

    if not docs_dir.is_absolute():
        docs_dir = Path.cwd() / docs_dir
    docs_dir = docs_dir.resolve()
    if not docs_dir.exists():
        return {"success": False, "error": f"Directory not found: {docs_dir}"}

    safe_name = sanitize_for_filesystem(docs_dir.name)
    output_dir: Path = rag_system._profile_index_dir(safe_name) # type: ignore
    output_dir.mkdir(parents=True, exist_ok=True)

    index_path = output_dir / "faiss.index"
    index_exists = index_path.exists()

    try:
        from ...rag.indexer import RAGIndexer
    except ImportError as e:
        return {"success": False, "error": f"RAG indexer not available: {e}"}

    try:
        loop = asyncio.get_event_loop()

        def _run() -> tuple[int, bool]:
            indexer = RAGIndexer(model_name=request.model)
            
            # Load existing chunks for incremental check
            existing_chunks = None
            chunks_path = output_dir / "chunks.json"
            if chunks_path.exists() and not request.force:
                try:
                    existing_chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

            indexer.load_model()
            indexer.index_directory(
                docs_dir, 
                chunk_size=request.chunk_size, 
                overlap=request.overlap,
                existing_chunks=existing_chunks
            )
            
            if not indexer.chunks:
                raise ValueError("No indexable documents found")

            # Only rebuild if files changed, force is true, or index missing
            rebuilt = False
            if indexer.has_changes or request.force or not index_exists:
                # Attempt to load existing index to reuse vectors for unchanged chunks
                existing_index = None
                if index_exists and not request.force:
                    try:
                        existing_index = faiss.read_index(str(index_path))
                    except Exception:
                        pass
                
                indexer.create_embeddings(existing_index=existing_index)
                indexer.save_index(output_dir)
                rebuilt = True
            
            return len(indexer.chunks), rebuilt

        chunks_count, was_rebuilt = await loop.run_in_executor(None, _run)

        meta = {
            "name": docs_dir.name, 
            "safe_name": safe_name, 
            "source_dir": str(docs_dir), 
            "index_dir": str(output_dir), 
            "chunks": chunks_count, 
            "model": request.model, 
            "updated_at": datetime.now().isoformat()
        }
        (output_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "success": True, 
            "chunks": chunks_count, 
            "rebuilt": was_rebuilt,
            "index_dir": str(output_dir), 
            "name": safe_name,
            "message": "Index rebuilt" if was_rebuilt else "Index is up to date"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Text Extraction endpoints ─────────────────────────────────────────────────

@router.post("/extract/file")
async def extract_text_from_file(file: UploadFile = File(...)) -> dict:
    """! Извлечение текста из загруженного файла.

    Args:
        file (UploadFile): Файл для обработки.

    Returns:
        dict: Извлеченный текст и метаданные.
    """
    try:
        extractor: Any = None
        results: list = []
        from ...rag.text_extractor_4_rag import TextExtractor
    except ImportError as e:
        return {"success": False, "error": f"TextExtractor not available: {e}"}

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    safe_name = sanitize_for_filesystem(file.filename)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="File is empty")

    try:
        extractor = TextExtractor()
        loop = asyncio.get_event_loop()
        results = await asyncio.wait_for(loop.run_in_executor(None, extractor.extract_text, content, safe_name), timeout=300)
        total_chars = sum(len(r.get("text", "")) for r in results)
        return {"success": True, "filename": file.filename, "count": len(results), "total_chars": total_chars, "files": results}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Processing timeout (300s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/extract/url")
async def extract_text_from_url(request: ExtractURLRequest) -> dict:
    """! Извлечение контента с веб-страницы.

    Args:
        request (ExtractURLRequest): URL и параметры парсинга (JS, изображения).

    Returns:
        dict: Текстовое содержимое страницы.
    """
    try:
        extractor: Any = None
        results: list = []
        from ...rag.text_extractor_4_rag import TextExtractor
        from ...rag.text_extractor_4_rag.main import ExtractionOptions
    except ImportError as e:
        return {"success": False, "error": f"TextExtractor not available: {e}"}

    url = request.url.strip()
    if not url.startswith(("http://", "https://")):
        return {"success": False, "error": "URL must start with http:// or https://"}

    options = ExtractionOptions(enable_javascript=request.enable_javascript, process_images=request.process_images, web_page_timeout=request.web_page_timeout)

    try:
        extractor = TextExtractor()
        loop = asyncio.get_event_loop()
        results = await asyncio.wait_for(loop.run_in_executor(None, extractor.extract_from_url, url, None, options), timeout=300)
        total_chars = sum(len(r.get("text", "")) for r in results)
        return {"success": True, "url": url, "count": len(results), "total_chars": total_chars, "files": results}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Processing timeout (300s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/extract/formats")
async def get_supported_formats() -> dict:
    """! Получение списка поддерживаемых форматов для извлечения текста.

    Returns:
        dict: Список расширений.
    """
    try:
        from ...rag.text_extractor_4_rag.config import settings as ext_settings
        return {"success": True, "formats": ext_settings.SUPPORTED_FORMATS}
    except ImportError:
        return {"success": False, "error": "TextExtractor not available"}
