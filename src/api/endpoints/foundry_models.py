# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Foundry Models Management API
# =============================================================================
# Description:
#   API endpoints for Foundry models.
#   Keep lifecycle semantics simple:
#     - GET /v1/models lists models known to the running Foundry service.
#     - "load" is a warm-up inference request.
#     - "unload" is best-effort via foundry_client.
#
#   Foundry Local API endpoints used:
#     GET    /v1/models              — list available/registered models
#     POST   /v1/chat/completions    — inference (via foundry_client)
#     POST   /v1/completions         — text completion (via foundry_client)
#     POST   /v1/embeddings          — embeddings (via foundry_client)
#
#   CLI used only for:
#     foundry model download <id>    — no HTTP API alternative
#
# Примеры:
#   GET  /api/v1/foundry/models/catalog        — полный каталог Foundry (foundry model list CLI)
#   GET  /api/v1/foundry/models/available
#   GET  /api/v1/foundry/models/loaded
#   GET  /api/v1/foundry/models/cached
#   POST /api/v1/foundry/models/completions   {"prompt": "...", "model": "..."}
#   POST /api/v1/foundry/models/embeddings    {"input": "...", "model": "..."}
#   POST /api/v1/foundry/models/download      {"model_id": "qwen2.5-0.5b-..."}
#   GET  /api/v1/foundry/models/download/status/{pid}
#   POST /api/v1/foundry/models/load          {"model_id": "qwen2.5-0.5b-..."}
#   POST /api/v1/foundry/models/unload        {"model_id": "qwen2.5-0.5b-..."}
#
# File: src/api/endpoints/foundry_models.py
# Project: AI Assistant (ai_assist)
# Version: 0.7.1
# Changes in 0.7.1:
#   - Added /completions proxy (Foundry /v1/completions)
#   - Added /embeddings proxy (Foundry /v1/embeddings)
#   - Replaced CLI subprocess calls with Foundry HTTP API (load, list_available)
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import subprocess
import logging
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from ...utils.foundry_utils import is_foundry_model_cached, _get_foundry_cache_dir
from ...utils.process_utils import run_command, DEFAULT_SUBPROCESS_KWARGS
from ...utils.api_utils import api_response_handler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/foundry/models", tags=["foundry-models"])

# Hardcoded fallback catalog — shown when Foundry service is unreachable.
# Used by list_available_models() as last resort so the UI always has something.
AVAILABLE_MODELS: list = [
    {
        "id": "qwen3-0.6b-generic-cpu:4",
        "name": "Qwen3 0.6B (CPU)",
        "size": "0.8 GB",
        "type": "cpu",
        "description": "Самая лёгкая CPU модель",
    },
    {
        "id": "qwen2.5-0.5b-instruct-generic-cpu:4",
        "name": "Qwen 2.5 0.5B (CPU)",
        "size": "0.8 GB",
        "type": "cpu",
        "description": "Лёгкая CPU модель",
    },
    {
        "id": "qwen2.5-1.5b-instruct-generic-cpu:4",
        "name": "Qwen 2.5 1.5B (CPU)",
        "size": "1.78 GB",
        "type": "cpu",
        "description": "Средняя CPU модель",
    },
    {
        "id": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
        "name": "DeepSeek R1 Distill 7B (CPU)",
        "size": "6.43 GB",
        "type": "cpu",
        "description": "Продвинутая CPU модель с рассуждениями",
    },
    {
        "id": "phi-3-mini-4k-instruct-openvino-gpu:1",
        "name": "Phi-3 Mini 4K (GPU)",
        "size": "2.4 GB",
        "type": "gpu",
        "description": "GPU модель",
    },
]

# Background download processes: {pid: {"model_id": str, "process": Popen}}
_download_processes: dict = {}


def _get_foundry_base_url() -> str:
    """Return Foundry service base URL from environment or config."""
    return os.getenv("FOUNDRY_BASE_URL", "http://localhost:63995/v1/")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/auto-load-default")
@api_response_handler
async def auto_load_default_model() -> dict:
    """Warm up the default model from config.json.

    For Foundry, "load" means a tiny inference request that makes the model
    ready for normal requests. Foundry Local does not expose a reliable HTTP
    load-into-RAM endpoint.

    Returns:
        dict: success, model_id, message on success; success=False on failure.
    """
    from ...core.config import config as app_config
    from ...models.foundry_client import foundry_client

    model_id: str = app_config.foundry_default_model
    if not model_id:
        return {"success": False, "message": "default_model not set in config"}

    if not app_config.foundry_auto_load_default:
        return {"success": False, "message": "auto_load_default is disabled in config"}

    logger.info("Loading default model via Foundry API: %s", model_id)
    result = await foundry_client.load_model(model_id)
    if result.get("success"):
        return {"success": True, "model_id": model_id, "message": result.get("message", f"Loading {model_id}")}
    return {"success": False, "model_id": model_id, "error": result.get("error", "Load failed")}


@router.get("")
@router.get("/")
async def list_models_root() -> dict:
    """Alias for /available."""
    return await list_available_models()


@router.get("/catalog")
@api_response_handler
async def list_catalog_models() -> dict:
    """List the full Foundry model catalog via CLI (foundry model list).

    This is the catalog of ALL models available for download from Foundry,
    not just the ones already cached or loaded.
    Uses CLI because Foundry has no HTTP API for the catalog.

    Returns:
        dict: success, models (list with id, alias, device, task, size, license, cached),
              count, source.
    """
    import re
    try:
        result = run_command(["foundry", "model", "list"], timeout=15)
    except FileNotFoundError:
        logger.warning("foundry CLI not found — returning hardcoded catalog")
        models = [{**m, "cached": is_foundry_model_cached(m["id"]), "loaded": False} for m in AVAILABLE_MODELS]
        return {"success": True, "models": models, "count": len(models), "source": "hardcoded"}
    except Exception as e:
        logger.warning("foundry model list failed: %s — returning hardcoded catalog", e)
        models = [{**m, "cached": is_foundry_model_cached(m["id"]), "loaded": False} for m in AVAILABLE_MODELS]
        return {"success": True, "models": models, "count": len(models), "source": "hardcoded"}

    output = (result.stdout or "").strip()
    if result.returncode != 0 or not output:
        logger.warning("foundry model list returned no output — returning hardcoded catalog")
        models = [{**m, "cached": is_foundry_model_cached(m["id"]), "loaded": False} for m in AVAILABLE_MODELS]
        return {"success": True, "models": models, "count": len(models), "source": "hardcoded"}

    # Parse CLI table output:
    # Alias          | Device | Task | File Size | License | Model ID
    # Lines starting with dashes or empty are separators.
    parsed: list[dict] = []
    current_alias = ""
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("-") or line.lower().startswith("alias"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            continue
        alias, device, task, size, license_, model_id = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        if alias:
            current_alias = alias
        parsed.append({
            "id":      model_id,
            "alias":   current_alias,
            "name":    current_alias or model_id,
            "device":  device,
            "task":    task,
            "size":    size,
            "license": license_,
            "cached":  is_foundry_model_cached(model_id),
            "loaded":  False,
        })

    if not parsed:
        # CLI ran but output unparseable — return hardcoded
        models = [{**m, "cached": is_foundry_model_cached(m["id"]), "loaded": False} for m in AVAILABLE_MODELS]
        return {"success": True, "models": models, "count": len(models), "source": "hardcoded"}

    logger.info("Foundry catalog: %d models from CLI", len(parsed))
    return {"success": True, "models": parsed, "count": len(parsed), "source": "foundry-cli"}


@router.get("/available")
@api_response_handler
async def list_available_models() -> dict:
    """List models reported by the running Foundry service.

    Uses Foundry HTTP API (GET /v1/models).
    Falls back to hardcoded AVAILABLE_MODELS when Foundry is unreachable.

    NOTE: Foundry Local does not expose a reliable separate "loaded in RAM"
    list here. Treat these as available/registered models.

    Returns:
        dict: success, models, count, source ('foundry-api' or 'hardcoded').
    """
    from ...models.foundry_client import foundry_client

    result = await foundry_client.list_available_models()
    if result.get("success"):
        models = result.get("models", [])
        # Normalize to consistent shape: ensure id, name, cached fields
        normalized = []
        for m in models:
            mid = m.get("id", "")
            normalized.append({
                "id":      mid,
                "name":    m.get("name") or mid,
                "alias":   m.get("alias", ""),
                "device":  m.get("device") or m.get("type", ""),
                "size":    m.get("size", ""),
                "cached":  True,
                "loaded":  False,
                "status":  "available",
            })
        logger.info("Foundry API returned %d models", len(normalized))
        return {"success": True, "models": normalized, "count": len(normalized), "source": "foundry-api"}

    # Fallback: hardcoded catalog with cache status from filesystem
    logger.warning("Foundry API unavailable, falling back to hardcoded model list")
    models = [{**m, "cached": is_foundry_model_cached(m["id"]), "loaded": False} for m in AVAILABLE_MODELS]
    return {"success": True, "models": models, "count": len(models), "source": "hardcoded"}


@router.get("/cached")
@api_response_handler
async def list_cached_models() -> dict:
    """List models downloaded to the local Foundry cache on disk.

    Foundry has no HTTP API for listing cached (not-yet-loaded) models,
    so this endpoint scans the filesystem directly.

    Cache structure: <cache_dir>/Microsoft/<model-dir>/v<version>/

    Returns:
        dict: success, models (list of model_id strings), items (full model dicts),
              count, cache_dir.
    """
    cache_dir = _get_foundry_cache_dir()
    microsoft_dir = cache_dir / "Microsoft"

    # Try Microsoft subdir first, fall back to cache root
    scan_dir = microsoft_dir if microsoft_dir.exists() else cache_dir

    if not scan_dir.exists():
        return {
            "success":   True,
            "models":    [],
            "items":     [],
            "count":     0,
            "cache_dir": str(cache_dir),
        }

    # Scan filesystem — reconstruct model IDs from directory names
    # Directory name format: "qwen3-0.6b-generic-cpu-4" (all colons replaced with dashes)
    # Version subdir format: "v4"
    # Skip empty directories — incomplete/failed downloads
    found_ids: list[str] = []
    for model_dir in sorted(scan_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        dir_name = model_dir.name

        version_dirs = [d for d in model_dir.iterdir() if d.is_dir() and d.name.startswith("v")]
        if version_dirs:
            for vdir in sorted(version_dirs):
                version = vdir.name[1:]  # strip leading "v"
                # Reconstruct: "qwen3-0.6b-generic-cpu-4" + "4" → "qwen3-0.6b-generic-cpu:4"
                if dir_name.endswith(f"-{version}"):
                    base = dir_name[: -(len(version) + 1)]
                    found_ids.append(f"{base}:{version}")
                else:
                    found_ids.append(dir_name)
        # Skip directories with no version subdirs — incomplete downloads

    items = []
    for mid in found_ids:
        items.append({
            "id":     mid,
            "name":   mid,
            "alias":  "",
            "device": "CPU",
            "size":   "",
            "cached": True,
            "loaded": False,
        })

    logger.info("Found %d cached Foundry models in %s", len(items), scan_dir)
    return {
        "success":   True,
        "models":    found_ids,
        "items":     items,
        "count":     len(items),
        "cache_dir": str(scan_dir),
    }


@router.get("/loaded")
@api_response_handler
async def list_loaded_models() -> dict:
    """Compatibility alias for models reported by Foundry.

    Foundry Local does not reliably separate available from loaded in this API.

    Returns:
        dict: success, models (list of {id, name, status}), count.
    """
    from ...models.foundry_client import foundry_client

    result = await foundry_client.list_available_models()
    if not result.get("success"):
        return {"success": False, "models": [], "count": 0, "error": result.get("error", "Foundry unavailable")}

    models = [
        {"id": m.get("id", ""), "name": m.get("id", ""), "status": "available"}
        for m in result.get("models", [])
    ]
    return {"success": True, "models": models, "count": len(models)}


@router.post("/download")
@api_response_handler
async def download_model(request: dict) -> dict:
    """Download a model to the Foundry cache via CLI.

    Foundry has no HTTP API for downloading models — CLI is the only option.
    Launches download in background and returns PID immediately.

    Args:
        request: {"model_id": "qwen3-0.6b-generic-cpu:4"}

    Returns:
        dict: success, model_id, status ('downloading'/'already_cached'), pid.
    """
    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    if is_foundry_model_cached(model_id):
        return {"success": True, "model_id": model_id, "status": "already_cached"}

    process = subprocess.Popen(
        ["foundry", "model", "download", model_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **DEFAULT_SUBPROCESS_KWARGS,
    )
    _download_processes[process.pid] = {"model_id": model_id, "process": process}
    logger.info("Downloading model %s (PID: %d)", model_id, process.pid)
    return {"success": True, "model_id": model_id, "status": "downloading", "pid": process.pid}


@router.get("/download/status/{pid}")
@api_response_handler
async def get_download_status(pid: int) -> dict:
    """Check status of a background download process.

    Args:
        pid: PID returned by /download.

    Returns:
        dict: success, pid, model_id, status ('downloading'/'done'/'error').
    """
    entry = _download_processes.get(pid)
    if not entry:
        return {"success": False, "error": f"PID {pid} not found"}

    process = entry["process"]
    model_id = entry["model_id"]
    retcode = process.poll()

    if retcode is None:
        return {"success": True, "pid": pid, "model_id": model_id, "status": "downloading"}

    stdout = (process.stdout.read() or b"").decode("utf-8", errors="replace") if process.stdout else ""
    stderr = (process.stderr.read() or b"").decode("utf-8", errors="replace") if process.stderr else ""
    del _download_processes[pid]

    cached = is_foundry_model_cached(model_id)
    if retcode == 0 or cached:
        logger.info("Download complete: %s", model_id)
        return {"success": True, "pid": pid, "model_id": model_id, "status": "done", "cached": cached}

    logger.error("Download failed: %s — %s", model_id, stderr)
    return {
        "success": False,
        "pid":      pid,
        "model_id": model_id,
        "status":   "error",
        "error":    stderr.strip() or stdout.strip() or "Foundry download failed",
    }


@router.post("/load")
@api_response_handler
async def load_model(request: dict) -> dict:
    """Warm up a model in Foundry.

    The client sends a short chat completion request. This is intentionally
    simpler and more reliable than trying to track an internal loaded state.

    Args:
        request: {"model_id": "qwen3-0.6b-generic-cpu:4"}

    Returns:
        dict: success, model_id, message on success; success=False, error on failure.
    """
    from ...models.foundry_client import foundry_client

    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    logger.info("Warming up Foundry model: %s", model_id)
    result = await foundry_client.load_model(model_id)
    if result.get("success"):
        return {"success": True, "model_id": model_id, "message": result.get("message", f"Ready {model_id}"), "status": "ready"}
    return {"success": False, "model_id": model_id, "error": result.get("error", "Load failed")}


@router.post("/unload")
@api_response_handler
async def unload_model(request: dict) -> dict:
    """Best-effort unload of a Foundry model.

    Args:
        request: {"model_id": "qwen3-0.6b-generic-cpu:4"}

    Returns:
        dict: success, model_id, message on success; success=False, error on failure.
    """
    from ...models.foundry_client import foundry_client

    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    result = await foundry_client.unload_model(model_id)
    if result.get("success"):
        return {"success": True, "model_id": model_id, "message": result.get("message", f"Unloaded {model_id}")}
    return {"success": False, "model_id": model_id, "error": result.get("error", "Unload failed")}


@router.get("/status/{model_id:path}")
@api_response_handler
async def get_model_status(model_id: str) -> dict:
    """Get model status: available in service and/or cached on disk.

    Args:
        model_id: Model identifier (path parameter).

    Returns:
        dict: success, model_id, available (bool), cached (bool), status.
    """
    available_result = await list_loaded_models()
    is_available = available_result.get("success") and any(
        m["id"] == model_id for m in available_result.get("models", [])
    )
    is_cached = is_foundry_model_cached(model_id)
    return {
        "success":  True,
        "model_id": model_id,
        "available": is_available,
        "loaded":   False,
        "cached":   is_cached,
        "status":   "available" if is_available else ("cached" if is_cached else "not_downloaded"),
    }


# ── Foundry API proxy: completions + embeddings ────────────────────────────────

@router.post("/completions")
@api_response_handler
async def foundry_completions(request: dict) -> dict:
    """Text completion через Foundry /v1/completions.

    Args:
        request: {"prompt": str, "model": str (optional),
                  "temperature": float, "max_tokens": int, ...}

    Returns:
        dict: OpenAI-совместимый ответ или success=False.
    """
    from ...models.foundry_client import foundry_client
    prompt: str = request.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    return await foundry_client.completions(
        prompt=prompt,
        model=request.get("model"),
        temperature=float(request.get("temperature", 0.7)),
        max_tokens=int(request.get("max_tokens", 512)),
    )


@router.post("/embeddings")
@api_response_handler
async def foundry_embeddings(request: dict) -> dict:
    """Эмбеддинги через Foundry /v1/embeddings.

    Args:
        request: {"input": str | list[str], "model": str (optional)}

    Returns:
        dict: success, data (list of embedding vectors), usage.
    """
    from ...models.foundry_client import foundry_client
    inp = request.get("input")
    if not inp:
        raise HTTPException(status_code=400, detail="input is required")
    return await foundry_client.embeddings(input=inp, model=request.get("model"))
