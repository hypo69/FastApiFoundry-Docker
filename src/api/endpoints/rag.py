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
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
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

RAG_PROFILES_DIR = Path("rag_index/_profiles")


def _profiles_dir() -> Path:
    RAG_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    return RAG_PROFILES_DIR


@router.get("/profiles")
async def list_rag_profiles():
    """List saved RAG profiles."""
    d = _profiles_dir()
    profiles = []
    for meta_file in sorted(d.glob("*.json")):
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            profiles.append(meta)
        except Exception:
            pass
    return {"success": True, "profiles": profiles}


@router.post("/profiles/save")
async def save_rag_profile(request: dict):
    """Save the current RAG index as a named profile.

    Body: { name, description?, source_dir? }
    """
    name = (request.get("name") or "").strip()
    if not name:
        return {"success": False, "error": "name is required"}

    # Read current index_dir from config.json
    config_path = Path("config.json")
    current_index_dir = Path("./rag_index")
    if config_path.exists():
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        current_index_dir = Path(cfg.get("rag_system", {}).get("index_dir", "./rag_index"))

    if not current_index_dir.exists():
        return {"success": False, "error": f"Index directory not found: {current_index_dir}"}

    import shutil
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    profile_dir = _profiles_dir().parent / safe_name
    try:
        if profile_dir.exists():
            shutil.rmtree(profile_dir)
        shutil.copytree(current_index_dir, profile_dir,
                        ignore=shutil.ignore_patterns("_profiles"))
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Count files
    file_count = sum(1 for _ in profile_dir.rglob("*") if _.is_file())

    meta = {
        "name": name,
        "safe_name": safe_name,
        "description": request.get("description", ""),
        "source_dir": request.get("source_dir", str(current_index_dir)),
        "index_dir": str(profile_dir),
        "files": file_count,
    }
    (_profiles_dir() / f"{safe_name}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"success": True, "profile": meta}


@router.post("/profiles/load")
async def load_rag_profile(request: dict):
    """Load a profile — switch index_dir in config.json.

    Body: { name }
    """
    name = (request.get("name") or "").strip()
    if not name:
        return {"success": False, "error": "name is required"}

    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    meta_file = _profiles_dir() / f"{safe_name}.json"
    if not meta_file.exists():
        return {"success": False, "error": f"Profile '{name}' not found"}

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    profile_dir = Path(meta["index_dir"])
    if not profile_dir.exists():
        return {"success": False, "error": f"Profile index directory missing: {profile_dir}"}

    # Update config.json
    config_path = Path("config.json")
    cfg = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    cfg.setdefault("rag_system", {})["index_dir"] = str(profile_dir)
    config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"success": True, "message": f"Profile '{name}' loaded", "index_dir": str(profile_dir)}


@router.delete("/profiles/{name}")
async def delete_rag_profile(name: str):
    """Delete profile (metadata and index only, not the current active one)."""
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    meta_file = _profiles_dir() / f"{safe_name}.json"
    if not meta_file.exists():
        return {"success": False, "error": f"Profile '{name}' not found"}

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    profile_dir = Path(meta["index_dir"])

    import shutil
    if profile_dir.exists() and profile_dir != Path("./rag_index").resolve():
        shutil.rmtree(profile_dir, ignore_errors=True)
    meta_file.unlink(missing_ok=True)
    return {"success": True, "message": f"Profile '{name}' deleted"}


@router.post("/build")
async def build_rag_index(request: RAGBuildRequest):
    """Build RAG index from specified directory"""
    docs_dir = Path(request.docs_dir)
    if not docs_dir.exists():
        return {"success": False, "error": f"Directory not found: {request.docs_dir}"}

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
                raise ValueError("No indexable documents found in the selected directory")
            indexer.create_embeddings()
            indexer.save_index(Path(request.output_dir))
            return len(indexer.chunks)

        chunks_count = await loop.run_in_executor(None, _run)
        return {
            "success": True,
            "message": f"Index built successfully",
            "chunks": chunks_count,
            "docs_dir": request.docs_dir,
            "output_dir": request.output_dir
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
