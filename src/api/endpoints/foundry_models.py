# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Foundry Models Management API
# =============================================================================
# Description:
#   API endpoints for managing Foundry models:
#   список доступных, загруженных, скачанных, загрузка, выгрузка, статус.
#
# Примеры:
#   GET  /api/v1/foundry/models/available
#   GET  /api/v1/foundry/models/loaded
#   GET  /api/v1/foundry/models/cached
#   POST /api/v1/foundry/models/download        {\"model_id\": \"qwen2.5-0.5b-...\"}
#   GET  /api/v1/foundry/models/download/status/{pid}
#   POST /api/v1/foundry/models/load            {\"model_id\": \"qwen2.5-0.5b-...\"}
#   POST /api/v1/foundry/models/unload          {\"model_id\": \"qwen2.5-0.5b-...\"}
#
# File: src/api/endpoints/foundry_models.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Changes in 0.6.0:
#   - MIT License update
#   - Unified headers and return type hints
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================

import subprocess
import logging
import os
import re
import aiohttp
from pathlib import Path
from fastapi import APIRouter, HTTPException
from ...utils.foundry_utils import is_foundry_model_cached, FOUNDRY_CACHE_DIR
from ...utils.process_utils import run_command, DEFAULT_SUBPROCESS_KWARGS
from ...utils.api_utils import api_response_handler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/foundry/models", tags=["foundry-models"])

AVAILABLE_MODELS: list = [
    {
        "id": "qwen2.5-0.5b-instruct-generic-cpu:4",
        "name": "Qwen 2.5 0.5B (CPU)",
        "size": "0.8 GB",
        "type": "cpu",
        "description": "Самая лёгкая CPU модель"
    },
    {
        "id": "qwen2.5-1.5b-instruct-generic-cpu:4",
        "name": "Qwen 2.5 1.5B (CPU)",
        "size": "1.78 GB",
        "type": "cpu",
        "description": "Средняя CPU модель"
    },
    {
        "id": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
        "name": "DeepSeek R1 Distill 7B (CPU)",
        "size": "6.43 GB",
        "type": "cpu",
        "description": "Продвинутая CPU модель с рассуждениями"
    },
    {
        "id": "phi-3-mini-4k-instruct-openvino-gpu:1",
        "name": "Phi-3 Mini 4K (GPU)",
        "size": "2.4 GB",
        "type": "gpu",
        "description": "GPU модель"
    },
]

# Активные фоновые процессы скачивания: {pid: {"model_id": str, "process": Popen}}
_download_processes: dict = {}

def _get_foundry_base_url() -> str:
    """! Получить base URL Foundry сервиса.

    Читает FOUNDRY_BASE_URL из окружения, установленного динамически в start.ps1.

    Returns:
        str: URL вида http://localhost:PORT/v1/
    """
    return os.getenv("FOUNDRY_BASE_URL", "http://localhost:50477/v1/")


def _run_foundry(args: list, timeout: int = 30) -> subprocess.CompletedProcess:
    """! Запустить команду foundry CLI через subprocess.

    Args:
        args:    Аргументы после 'foundry', например ['model', 'ls'].
        timeout: Таймаут в секундах.

    Returns:
        subprocess.CompletedProcess

    Raises:
        FileNotFoundError: Если foundry CLI не установлен.
        subprocess.TimeoutExpired: При превышении таймаута.
    """
    return run_command(["foundry"] + args, timeout=timeout)


@router.post("/auto-load-default")
@api_response_handler
async def auto_load_default_model() -> dict:
    """! Загрузить модель по умолчанию из config.json (foundry_ai.default_model).

    Returns:
        dict: success, model_id, message, pid on success;
              success=False, message/error on failure.
    """
    import os
    from ...core.config import config as app_config

    model_id: str = app_config.foundry_default_model
    if not model_id:
        return {"success": False, "message": "default_model not set in config"}

    if not app_config.foundry_auto_load_default:
        return {"success": False, "message": "auto_load_default is disabled in config"}

    process = subprocess.Popen(
        ["foundry", "model", "load", model_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **DEFAULT_SUBPROCESS_KWARGS,
    )
    logger.info(f"Загрузка модели по умолчанию {model_id} (PID: {process.pid})")
    return {"success": True, "model_id": model_id, "message": f"Загрузка {model_id} запущена", "pid": process.pid}


@router.get("")
@router.get("/")
async def list_models_root() -> dict:
    """! Алиас для /available — список моделей из каталога Foundry.

    Returns:
        dict: Same as list_available_models().
    """
    return await list_available_models()


@router.get("/available")
@api_response_handler
async def list_available_models() -> dict:
    """! Список моделей из каталога Foundry (foundry model ls).

    Если CLI недоступен — возвращает хардкод из AVAILABLE_MODELS.

    Returns:
        dict: success, models (list with id/name/alias/device/type/size/cached),
              count, source ('foundry-cli' or 'hardcoded').
    """
    try:
        result = _run_foundry(["model", "ls"], timeout=15)
        if result.returncode == 0 and result.stdout.strip():
            models = _parse_foundry_ls(result.stdout)
            if models:
                return {"success": True, "models": [
                    {**m, "cached": is_foundry_model_cached(m["id"])} for m in models
                ], "count": len(models), "source": "foundry-cli"}
    except Exception as e:
        logger.warning(f"foundry model ls недоступен: {e}")

    # Fallback на хардкод
    models = [{**m, "cached": is_foundry_model_cached(m["id"])} for m in AVAILABLE_MODELS]
    return {"success": True, "models": models, "count": len(models), "source": "hardcoded"}


@router.get("/cached")
@api_response_handler
async def list_cached_models() -> dict:
    """! Список моделей скачанных в кэш Foundry на диске.

    Returns:
        dict: success, models (list of model_id strings), items (full model dicts),
              count, cache_dir.
    """
    if not FOUNDRY_CACHE_DIR.exists():
        return {
            "success": True,
            "models": [],
            "cache_dir": str(FOUNDRY_CACHE_DIR),
            "message": "Директория кэша не найдена"
        }

    available = await list_available_models()
    all_models = available.get("models", []) if available.get("success") else []
    cached_models = [m for m in all_models if is_foundry_model_cached(m["id"])]

    logger.info(f"Найдено {len(cached_models)} моделей в кэше: {FOUNDRY_CACHE_DIR}")
    return {
        "success": True,
        "models": [m["id"] for m in cached_models],
        "items": cached_models,
        "count": len(cached_models),
        "cache_dir": str(FOUNDRY_CACHE_DIR)
    }


@router.get("/loaded")
@api_response_handler
async def list_loaded_models() -> dict:
    """! Список моделей загруженных в Foundry сервис.

    Returns:
        dict: success, models (list of {id, name, status}), count;
              success=False, error on failure.
    """
    base_url: str = _get_foundry_base_url().rstrip("/")
    url: str = f"{base_url}/models"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    return {"success": False, "models": [], "error": f"HTTP {response.status}"}
                data: dict = await response.json()
                models: list = [
                    {"id": m.get("id", ""), "name": m.get("id", ""), "status": "loaded"}
                    for m in data.get("data", [])
                ]
                return {"success": True, "models": models, "count": len(models)}
    except Exception as e:
        logger.debug(f"Foundry service unavailable at {url}: {e}")
        return {"success": False, "models": [], "count": 0, "error": "Foundry service unavailable"}


@router.post("/download")
@api_response_handler
async def download_model(request: dict) -> dict:
    """! Скачивание модели в кэш Foundry (foundry model download).

    Запускает загрузку в фоне — возвращает PID не дожидаясь завершения.

    Args:
        request: JSON body с полями:
            model_id (str): Идентификатор модели (обязательно).

    Returns:
        dict: success, model_id, status ('downloading'/'already_cached'), pid.

    Raises:
        HTTPException 400: model_id не передан.
    """
    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    # Проверить — уже скачана?
    if is_foundry_model_cached(model_id):
        return {"success": True, "model_id": model_id, "status": "already_cached"}

    process = subprocess.Popen(
        ["foundry", "model", "download", model_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **DEFAULT_SUBPROCESS_KWARGS,
    )
    _download_processes[process.pid] = {"model_id": model_id, "process": process}
    logger.info(f"Скачивание модели {model_id} запущено (PID: {process.pid})")
    return {"success": True, "model_id": model_id, "status": "downloading", "pid": process.pid}


@router.get("/download/status/{pid}")
@api_response_handler
async def get_download_status(pid: int) -> dict:
    """! Статус процесса скачивания по PID.

    Args:
        pid: PID процесса скачивания, полученный из /download.

    Returns:
        dict: success, pid, model_id, status ('downloading'/'done'/'error'),
              cached (bool) on done; success=False, error if PID not found.
    """
    entry = _download_processes.get(pid)
    if not entry:
        return {"success": False, "error": f"PID {pid} не найден"}

    process = entry["process"]
    model_id = entry["model_id"]
    retcode = process.poll()

    if retcode is None:
        return {"success": True, "pid": pid, "model_id": model_id, "status": "downloading"}

    # Процесс завершён
    stdout, stderr = process.communicate() if retcode is not None else ("", "")
    stdout = stdout or ""
    stderr = stderr or ""
    del _download_processes[pid]

    cached = is_foundry_model_cached(model_id)
    if retcode == 0 or cached:
        logger.info(f"Скачивание {model_id} завершено успешно")
        return {"success": True, "pid": pid, "model_id": model_id, "status": "done", "cached": cached}
    else:
        logger.error(f"Скачивание {model_id} завершено с ошибкой: {stderr}")
        return {
            "success": False,
            "pid": pid,
            "model_id": model_id,
            "status": "error",
            "error": stderr.strip() or stdout.strip() or "Foundry download failed",
        }


@router.post("/load")
@api_response_handler
async def load_model(request: dict) -> dict:
    """! Загрузка модели в Foundry сервис (foundry model load).

    Args:
        request: JSON body с полями:
            model_id (str): Идентификатор модели (обязательно).

    Returns:
        dict: success, model_id, status ('loading'), pid.

    Raises:
        HTTPException 400: model_id не передан.
    """
    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    process = subprocess.Popen(
        ["foundry", "model", "load", model_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **DEFAULT_SUBPROCESS_KWARGS,
    )
    logger.info(f"Загрузка модели {model_id} в сервис запущена (PID: {process.pid})")
    return {"success": True, "model_id": model_id, "status": "loading", "pid": process.pid}


@router.post("/unload")
@api_response_handler
async def unload_model(request: dict) -> dict:
    """! Выгрузка модели из Foundry сервиса.

    Сначала пробует CLI (foundry model unload), при ошибке — REST API DELETE.

    Args:
        request: JSON body с полями:
            model_id (str): Идентификатор модели (обязательно).

    Returns:
        dict: success, model_id, message on success; success=False, error on failure.

    Raises:
        HTTPException 400: model_id не передан.
    """
    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    # Try CLI first
    try:
        result = _run_foundry(["model", "unload", model_id])
        output = (result.stdout or "").strip()
        error_keywords = ("exception", "denied", "failed", "unexpected error")
        cli_ok = result.returncode == 0 and not any(k in output.lower() for k in error_keywords)
        if cli_ok:
            logger.info(f"Модель {model_id} выгружена через CLI")
            return {"success": True, "model_id": model_id, "message": f"Модель {model_id} выгружена"}
        logger.warning(f"CLI unload failed for {model_id}: {output} — falling back to REST API")
    except Exception as e:
        logger.warning(f"CLI unload exception for {model_id}: {e} — falling back to REST API")

    # Fallback: REST API DELETE /v1/models/{id}
    base_url: str = _get_foundry_base_url().rstrip("/")
    url: str = f"{base_url}/models/{model_id}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                data: dict = {}
                try:
                    data = await response.json()
                except Exception:
                    pass
                if response.status == 200 and data.get("deleted"):
                    logger.info(f"Модель {model_id} выгружена через REST API")
                    return {"success": True, "model_id": model_id, "message": f"Модель {model_id} выгружена"}
                # 400/404 — model already not loaded
                if response.status in (400, 404):
                    return {"success": True, "model_id": model_id, "message": f"Модель {model_id} не загружена"}
                error_msg = data.get("error") or f"HTTP {response.status}"
                return {"success": False, "error": error_msg}
    except Exception as e:
        logger.error(f"REST unload exception for {model_id}: {e}")
        return {"success": False, "error": str(e)}


@router.get("/status/{model_id:path}")
@api_response_handler
async def get_model_status(model_id: str) -> dict:
    """! Статус модели: загружена в сервис и/или скачана в кэш.

    Args:
        model_id: Идентификатор модели (path parameter).

    Returns:
        dict: success, model_id, loaded (bool), cached (bool),
              status ('loaded'/'cached'/'not_downloaded').
    """
    loaded = await list_loaded_models()
    is_loaded = loaded.get("success") and any(m["id"] == model_id for m in loaded["models"])
    is_cached = is_foundry_model_cached(model_id)
    return {
        "success": True,
        "model_id": model_id,
        "loaded": is_loaded,
        "cached": is_cached,
        "status": "loaded" if is_loaded else ("cached" if is_cached else "not_downloaded"),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_foundry_ls(output: str) -> list:
    """! Парсинг вывода `foundry model ls`.

    Формат строки:
      Alias (optional)   Device   Task   File Size   License   Model ID

    Возвращает список {id, name, alias, device, task, size, license}.
    """
    models = []
    current_alias = ""

    for line in output.splitlines():
        # Разделительные строки (---) и заголовок — пропускаем
        stripped = line.strip()
        if not stripped or stripped.startswith("-") or stripped.startswith("Alias"):
            continue

        # Колонки разделены двумя и более пробелами.
        # Важно: когда Alias в CLI пустой, строка начинается с "GPU"/"CPU".
        parts = [p for p in re.split(r"\s{2,}", line.strip()) if p.strip()]
        if not parts:
            continue

        is_device_first = parts[0] in {"CPU", "GPU"}

        if is_device_first:
            # Формат: Device | Task | File Size | License | Model ID
            if len(parts) < 5:
                continue
            device = parts[0].strip()
            task = parts[1].strip()
            size = parts[2].strip()
            license_ = parts[3].strip()
            model_id = parts[4].strip()
            # Alias остаётся как был (current_alias).
        else:
            # Формат: Alias | Device | Task | File Size | License | Model ID
            if len(parts) < 6:
                continue
            current_alias = parts[0].strip()
            device = parts[1].strip()
            task = parts[2].strip()
            size = parts[3].strip()
            license_ = parts[4].strip()
            model_id = parts[5].strip()

        if not model_id:
            continue

        models.append({
            "id":          model_id,
            "name":        model_id,
            "alias":       current_alias,
            "device":      device,
            "type":        device.lower(),
            "task":        task,
            "size":        size,
            "license":     license_,
            "description": f"{current_alias} — {device}, {task}",
        })

    return models
