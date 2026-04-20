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
# Version: 0.6.3
# Changes in 0.6.3:
#   - MIT License update
#   - Unified headers and return type hints
#   - Added an endpoint to trigger RAG profile cleanup
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
import faiss
from pydantic import BaseModel

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
    """Get RAG system status.

    Returns:
        dict: success, enabled, index_dir, model, chunk_size, top_k, total_chunks.
    """
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        rag_config = cfg.get("rag_system", {})
    else:
        rag_config = {}

    index_dir = Path(rag_config.get("index_dir", "./rag_index"))
    total_chunks = len(list(index_dir.glob("*.json"))) if index_dir.exists() else 0

    return {
        "success": True,
        "enabled": rag_config.get("enabled", False),
        "index_dir": str(index_dir),
        "model": rag_config.get("model", "sentence-transformers/all-MiniLM-L6-v2"),
        "chunk_size": rag_config.get("chunk_size", 1000),
        "top_k": rag_config.get("top_k", 5),
        "total_chunks": total_chunks,
    }


@router.put("/config")
@api_response_handler
async def update_rag_config(config: RAGConfig) -> dict:
    """Update RAG system configuration.

    Args:
        config: RAGConfig Pydantic model.

    Returns:
        dict: success, message.
    """
    config_path = Path("config.json")
    full_config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    full_config["rag_system"] = config.model_dump()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(full_config, f, indent=2, ensure_ascii=False)
    return {"success": True, "message": "RAG configuration updated"}


@router.post("/search")
@api_response_handler
async def search_rag(request: RAGSearchRequest) -> dict:
    """Search in RAG system.

    Args:
        request: RAGSearchRequest with query and top_k.

    Returns:
        dict: success, results, total.
    """
    results = [
        {"content": f"Mock result for query: {request.query}", "score": 0.95, "metadata": {"source": "mock"}},
        {"content": f"Another result for: {request.query}", "score": 0.87, "metadata": {"source": "mock"}},
    ]
    return {"success": True, "results": results[: request.top_k], "total": len(results)}


@router.post("/rebuild")
@api_response_handler
async def rebuild_rag_index() -> dict:
    """Rebuild RAG index.

    Returns:
        dict: success, message, chunks_processed.
    """
    return {"success": True, "message": "RAG index rebuild started (mock)", "chunks_processed": 42}


@router.post("/clear")
@api_response_handler
async def clear_rag_chunks() -> dict:
    """Clear all RAG index files from the configured index directory.

    Returns:
        dict: success, message, deleted_count.
    """
    config_path = Path("config.json")
    if config_path.exists():
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        index_dir = Path(cfg.get("rag_system", {}).get("index_dir", "./rag_index"))
    else:
        index_dir = Path("./rag_index")

    deleted_count = 0
    if index_dir.exists():
        for file in index_dir.glob("*"):
            if file.is_file() and file.suffix in (".index", ".json"):
                file.unlink()
                deleted_count += 1

    return {"success": True, "message": f"Cleared {deleted_count} index files", "deleted_count": deleted_count}


@router.get("/dirs")
@api_response_handler
async def list_indexable_dirs() -> dict:
    """Return a list of project directories suitable for indexing.

    Returns:
        dict: success, dirs.
    """
    root = Path(".")
    candidates = []
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
    """Return ~/.rag, creating it if needed."""
    RAG_HOME.mkdir(parents=True, exist_ok=True)
    return RAG_HOME


def _profile_index_dir(safe_name: str) -> Path:
    """Return ~/.rag/<safe_name>/."""
    return _rag_home() / safe_name


@router.get("/cwd")
async def get_cwd() -> dict:
    """Return server working directory."""
    return {"success": True, "cwd": str(Path.cwd())}


@router.get("/browse")
async def browse_filesystem(path: str = "") -> dict:
    """Return directory listing for folder-picker UI.

    Args:
        path: Absolute path (defaults to home directory).

    Returns:
        dict: success, current, parent, dirs.
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
    """List all RAG profiles in ~/.rag/.

    Returns:
        dict: success, profiles.
    """
    profiles = []
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
    """Switch active RAG profile.

    Args:
        request: JSON body with name (str).

    Returns:
        dict: success, message, index_dir.
    """
    name = (request.get("name") or "").strip()
    if not name:
        return {"success": False, "error": "name is required"}

    profile_dir = _profile_index_dir(sanitize_for_filesystem(name))
    if not profile_dir.exists():
        return {"success": False, "error": f"Profile '{name}' not found"}
    if not (profile_dir / "faiss.index").exists():
        return {"success": False, "error": f"Profile '{name}' has no index yet"}

    config_path = Path("config.json")
    cfg = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    cfg.setdefault("rag_system", {})["index_dir"] = str(profile_dir)
    config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    from ...rag.rag_system import rag_system
    await rag_system.reload_index(index_dir=str(profile_dir))

    return {"success": True, "message": f"Loaded profile '{name}'", "index_dir": str(profile_dir)}


@router.delete("/profiles/{name}")
async def delete_rag_profile(name: str) -> dict:
    """Delete a RAG profile from ~/.rag/<name>/.

    Args:
        name: Profile name (path parameter).

    Returns:
        dict: success, message.
    """
    import shutil
    profile_dir = _profile_index_dir(sanitize_for_filesystem(name))
    if not profile_dir.exists():
        return {"success": False, "error": f"Profile '{name}' not found"}
    shutil.rmtree(profile_dir, ignore_errors=True)
    return {"success": True, "message": f"Profile '{name}' deleted"}


@router.post("/build")
async def build_rag_index(request: RAGBuildRequest) -> dict:
    """Build RAG index from a directory.

    Args:
        request: RAGBuildRequest with docs_dir, model, chunk_size, overlap, force.

    Returns:
        dict: success, chunks, index_dir, name.
    """
    docs_dir = Path(request.docs_dir).expanduser()
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
                        import faiss
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
    """Extract plain text from an uploaded file.

    Args:
        file: Uploaded file (multipart/form-data).

    Returns:
        dict: success, filename, count, total_chars, files.
    """
    try:
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
    """Extract plain text from a URL.

    Args:
        request: ExtractURLRequest with url, enable_javascript, process_images, web_page_timeout.

    Returns:
        dict: success, url, count, total_chars, files.
    """
    try:
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
    """Return all file formats supported by the text extractor.

    Returns:
        dict: success, formats.
    """
    try:
        from ...rag.text_extractor_4_rag.config import settings as ext_settings
        return {"success": True, "formats": ext_settings.SUPPORTED_FORMATS}
    except ImportError:
        return {"success": False, "error": "TextExtractor not available"}
