# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: RAG System API Endpoints
# =============================================================================
# Description:
#   REST API endpoints for RAG system management
#   Includes configuration, status, search, and index management
#
# Examples:
#   GET /api/v1/rag/status - get RAG status
#   PUT /api/v1/rag/config - update configuration
#   POST /api/v1/rag/search - search in RAG
#
# File: src/api/endpoints/rag.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: December 9, 2025
# =============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
from pathlib import Path

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

class RAGBuildRequest(BaseModel):
    docs_dir: str
    output_dir: str = "./rag_index"
    model: str = "sentence-transformers/all-mpnet-base-v2"
    chunk_size: int = 1000
    overlap: int = 50

class RAGSearchResult(BaseModel):
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

@router.get("/status")
async def get_rag_status():
    """Get RAG system status"""
    try:
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            rag_config = config.get("rag_system", {})
        else:
            rag_config = {}
        
        # Count chunks
        index_dir = Path(rag_config.get("index_dir", "./rag_index"))
        total_chunks = 0
        if index_dir.exists():
            chunk_files = list(index_dir.glob("*.json"))
            total_chunks = len(chunk_files)
        
        return {
            "success": True,
            "enabled": rag_config.get("enabled", False),
            "index_dir": str(index_dir),
            "model": rag_config.get("model", "sentence-transformers/all-MiniLM-L6-v2"),
            "chunk_size": rag_config.get("chunk_size", 1000),
            "top_k": rag_config.get("top_k", 5),
            "total_chunks": total_chunks
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.put("/config")
async def update_rag_config(config: RAGConfig):
    """Update RAG system configuration"""
    try:
        config_path = Path("config.json")
        
        # Load existing configuration
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
        else:
            full_config = {}
        
        # Update RAG section
        full_config["rag_system"] = {
            "enabled": config.enabled,
            "index_dir": config.index_dir,
            "model": config.model,
            "chunk_size": config.chunk_size,
            "top_k": config.top_k
        }
        
        # Save configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2, ensure_ascii=False)
        
        return {"success": True, "message": "RAG configuration updated"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/search")
async def search_rag(request: RAGSearchRequest):
    """Search in RAG system"""
    try:
        # Simple search mock
        results = [
            {
                "content": f"Mock result for query: {request.query}",
                "score": 0.95,
                "metadata": {"source": "mock"}
            },
            {
                "content": f"Another result for: {request.query}",
                "score": 0.87,
                "metadata": {"source": "mock"}
            }
        ]
        
        return {
            "success": True,
            "results": results[:request.top_k],
            "total": len(results)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/rebuild")
async def rebuild_rag_index():
    """Rebuild RAG index"""
    try:
        # Index rebuild mock
        return {
            "success": True,
            "message": "RAG index rebuild started (mock)",
            "chunks_processed": 42
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/clear")
async def clear_rag_chunks():
    """Clear all RAG chunks"""
    try:
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            index_dir = Path(config.get("rag_system", {}).get("index_dir", "./rag_index"))
        else:
            index_dir = Path("./rag_index")

        deleted_count = 0
        if index_dir.exists():
            for file in index_dir.glob("*"):
                if file.is_file() and file.suffix in (".index", ".json"):
                    file.unlink()
                    deleted_count += 1

        return {
            "success": True,
            "message": f"Cleared {deleted_count} index files",
            "deleted_count": deleted_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/dirs")
async def list_indexable_dirs():
    """Return a list of project directories suitable for indexing"""
    root = Path(".")
    candidates = []
    skip = {"venv", ".git", "__pycache__", "node_modules", "rag_index", ".amazonq"}
    for p in sorted(root.iterdir()):
        if p.is_dir() and p.name not in skip and not p.name.startswith("."):
            # Count supported files
            count = sum(1 for _ in p.rglob("*")
                        if _.is_file() and _.suffix.lower() in {".md", ".txt", ".html", ".rst"})
            if count > 0:
                candidates.append({"path": str(p), "name": p.name, "files": count})
    return {"success": True, "dirs": candidates}


# ── RAG Profiles (multiple named index sets) ─────────────────────────────────

RAG_HOME = Path.home() / ".rag"


def _rag_home() -> Path:
    """~/.rag — корневая директория всех RAG баз. Создаётся автоматически."""
    RAG_HOME.mkdir(parents=True, exist_ok=True)
    return RAG_HOME


def _profile_index_dir(safe_name: str) -> Path:
    """Путь к индексу конкретной базы: ~/.rag/<name>/"""
    return _rag_home() / safe_name


def _safe(name: str) -> str:
    """Безопасное имя директории из произвольной строки."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name.strip())


# ── Браузер файловой системы ──────────────────────────────────────────────────

@router.get("/browse")
async def browse_filesystem(path: str = ""):
    """Возвращает содержимое директории для браузера выбора папки.

    Query: path — абсолютный путь (по умолчанию домашняя директория).
    """
    base = Path(path).expanduser() if path else Path.home()
    if not base.exists() or not base.is_dir():
        return {"success": False, "error": f"Directory not found: {base}"}

    skip = {"__pycache__", "node_modules", ".git", "venv", ".venv"}
    dirs = []
    for p in sorted(base.iterdir()):
        if p.is_dir() and p.name not in skip:
            dirs.append({"name": p.name, "path": str(p)})

    return {
        "success": True,
        "current": str(base),
        "parent": str(base.parent) if base.parent != base else None,
        "dirs": dirs,
    }


# ── Профили RAG баз ───────────────────────────────────────────────────────────

@router.get("/profiles")
async def list_rag_profiles():
    """Список всех RAG баз в ~/.rag/."""
    profiles = []
    for d in sorted(_rag_home().iterdir()):
        if not d.is_dir():
            continue
        meta_file = d / "meta.json"
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                # Проверяем наличие индекса
                meta["has_index"] = (d / "faiss.index").exists()
                profiles.append(meta)
            except Exception:
                pass
        else:
            # Директория без мета — показываем как неполный профиль
            profiles.append({
                "name": d.name,
                "safe_name": d.name,
                "index_dir": str(d),
                "has_index": (d / "faiss.index").exists(),
            })
    return {"success": True, "profiles": profiles}


@router.post("/profiles/load")
async def load_rag_profile(request: dict):
    """Переключить активную RAG базу.

    Body: { name }
    Обновляет index_dir в config.json и перезагружает RAG систему.
    """
    name = (request.get("name") or "").strip()
    if not name:
        return {"success": False, "error": "name is required"}

    profile_dir = _profile_index_dir(_safe(name))
    if not profile_dir.exists():
        return {"success": False, "error": f"Profile '{name}' not found"}
    if not (profile_dir / "faiss.index").exists():
        return {"success": False, "error": f"Profile '{name}' has no index yet"}

    # Обновляем config.json
    config_path = Path("config.json")
    cfg = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    cfg.setdefault("rag_system", {})["index_dir"] = str(profile_dir)
    config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    # Перезагружаем RAG систему
    from ...rag.rag_system import rag_system
    await rag_system.reload_index()

    return {"success": True, "message": f"Loaded profile '{name}'", "index_dir": str(profile_dir)}


@router.delete("/profiles/{name}")
async def delete_rag_profile(name: str):
    """Удалить RAG базу из ~/.rag/<name>/."""
    import shutil
    profile_dir = _profile_index_dir(_safe(name))
    if not profile_dir.exists():
        return {"success": False, "error": f"Profile '{name}' not found"}
    shutil.rmtree(profile_dir, ignore_errors=True)
    return {"success": True, "message": f"Profile '{name}' deleted"}


@router.post("/build")
async def build_rag_index(request: RAGBuildRequest):
    """Собрать RAG индекс из указанной директории.

    Сохраняет в ~/.rag/<safe_name>/ где safe_name = имя исходной директории.
    Если индекс уже существует — возвращает has_index=True без пересборки
    (если не передан force=true).
    """
    docs_dir = Path(request.docs_dir).expanduser()
    if not docs_dir.exists():
        return {"success": False, "error": f"Directory not found: {docs_dir}"}

    safe_name = _safe(docs_dir.name)
    output_dir = _profile_index_dir(safe_name)

    # Проверяем существующий индекс
    if (output_dir / "faiss.index").exists() and not getattr(request, "force", False):
        return {
            "success": True,
            "already_indexed": True,
            "message": f"Index for '{docs_dir.name}' already exists",
            "index_dir": str(output_dir),
            "name": safe_name,
        }

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from ...rag.indexer import RAGIndexer
    except ImportError as e:
        return {"success": False, "error": f"RAG indexer not available: {e}"}

    try:
        loop = asyncio.get_event_loop()

        def _run():
            indexer = RAGIndexer(model_name=request.model)
            indexer.load_model()
            indexer.index_directory(docs_dir, chunk_size=request.chunk_size, overlap=request.overlap)
            if not indexer.chunks:
                raise ValueError("No indexable documents found")
            indexer.create_embeddings()
            indexer.save_index(output_dir)
            return len(indexer.chunks)

        chunks = await loop.run_in_executor(None, _run)

        # Сохраняем мета-данные профиля
        meta = {
            "name": docs_dir.name,
            "safe_name": safe_name,
            "source_dir": str(docs_dir),
            "index_dir": str(output_dir),
            "chunks": chunks,
            "model": request.model,
        }
        (output_dir / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        return {"success": True, "chunks": chunks, "index_dir": str(output_dir), "name": safe_name}
    except Exception as e:
        return {"success": False, "error": str(e)}
