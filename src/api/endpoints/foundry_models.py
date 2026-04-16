# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Models Management API
# =============================================================================
# Описание:
#   API endpoints для управления моделями Foundry:
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
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import subprocess
import logging
import os
import re
import aiohttp
from pathlib import Path
from fastapi import APIRouter, HTTPException

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

# Директория кэша Foundry.
# Переопределяется через FOUNDRY_CACHE_DIR в .env.
# Структура: ~\.foundry\cache\models\Microsoft\<model-dir>\v<version>
FOUNDRY_CACHE_DIR = Path(os.getenv(
    "FOUNDRY_CACHE_DIR",
    os.path.expanduser(r"~\.foundry\cache\models\Microsoft")
))

# Активные фоновые процессы скачивания: {pid: {"model_id": str, "process": Popen}}
_download_processes: dict = {}


SUBPROCESS_TEXT_KWARGS = {
    "text": True,
    "encoding": "utf-8",
    "errors": "replace",
}


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
    return subprocess.run(
        ["foundry"] + args,
        capture_output=True,
        **SUBPROCESS_TEXT_KWARGS,
        timeout=timeout
    )


@router.post("/auto-load-default")
async def auto_load_default_model() -> dict:
    """! Загрузить модель по умолчанию из config.json (foundry_ai.default_model)."""
    import os
    from ...core.config import config as app_config

    model_id: str = app_config.foundry_default_model
    if not model_id:
        return {"success": False, "message": "default_model not set in config"}

    if not app_config.foundry_auto_load_default:
        return {"success": False, "message": "auto_load_default is disabled in config"}

    try:
        process = subprocess.Popen(
            ["foundry", "model", "load", model_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **SUBPROCESS_TEXT_KWARGS,
        )
        logger.info(f"Загрузка модели по умолчанию {model_id} (PID: {process.pid})")
        return {"success": True, "model_id": model_id, "message": f"Загрузка {model_id} запущена", "pid": process.pid}
    except FileNotFoundError:
        return {"success": False, "error": "Foundry CLI не найден"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("")
@router.get("/")
async def list_models_root() -> dict:
    """! Алиас для /available — список моделей из каталога Foundry."""
    return await list_available_models()


@router.get("/available")
async def list_available_models() -> dict:
    """! Список моделей из каталога Foundry (foundry model ls).

    Если CLI недоступен — возвращает хардкод из AVAILABLE_MODELS.
    """
    try:
        result = _run_foundry(["model", "ls"], timeout=15)
        if result.returncode == 0 and result.stdout.strip():
            models = _parse_foundry_ls(result.stdout)
            if models:
                return {"success": True, "models": [
                    {**m, "cached": _is_model_cached(m["id"])} for m in models
                ], "count": len(models), "source": "foundry-cli"}
    except Exception as e:
        logger.warning(f"foundry model ls недоступен: {e}")

    # Fallback на хардкод
    models = [{**m, "cached": _is_model_cached(m["id"])} for m in AVAILABLE_MODELS]
    return {"success": True, "models": models, "count": len(models), "source": "hardcoded"}


@router.get("/cached")
async def list_cached_models() -> dict:
    """! Список моделей скачанных в кэш Foundry на диске.

    Возвращает model_id моделей, которые присутствуют в локальном кэше Foundry.
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
    cached_models = [m for m in all_models if _is_model_cached(m["id"])]

    logger.info(f"Найдено {len(cached_models)} моделей в кэше: {FOUNDRY_CACHE_DIR}")
    return {
        "success": True,
        "models": [m["id"] for m in cached_models],
        "items": cached_models,
        "count": len(cached_models),
        "cache_dir": str(FOUNDRY_CACHE_DIR)
    }


@router.get("/loaded")
async def list_loaded_models() -> dict:
    """! Список моделей загруженных в Foundry сервис."""
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
        logger.error(f"Ошибка получения загруженных моделей: {e}")
        return {"success": False, "models": [], "error": str(e)}


@router.post("/download")
async def download_model(request: dict) -> dict:
    """! Скачивание модели в кэш Foundry (foundry model download).

    Запускает загрузку в фоне — возвращает PID не дожидаясь завершения.
    """
    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    # Проверить — уже скачана?
    if _is_model_cached(model_id):
        return {"success": True, "model_id": model_id, "status": "already_cached"}

    try:
        process = subprocess.Popen(
            ["foundry", "model", "download", model_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **SUBPROCESS_TEXT_KWARGS,
        )
        _download_processes[process.pid] = {"model_id": model_id, "process": process}
        logger.info(f"Скачивание модели {model_id} запущено (PID: {process.pid})")
        return {"success": True, "model_id": model_id, "status": "downloading", "pid": process.pid}
    except FileNotFoundError:
        return {"success": False, "error": "Foundry CLI не найден в PATH"}
    except Exception as e:
        logger.error(f"Ошибка запуска скачивания {model_id}: {e}")
        return {"success": False, "error": str(e)}


@router.get("/download/status/{pid}")
async def get_download_status(pid: int) -> dict:
    """! Статус процесса скачивания по PID."""
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

    cached = _is_model_cached(model_id)
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
async def load_model(request: dict) -> dict:
    """! Загрузка модели в Foundry сервис (foundry model load)."""
    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    try:
        process = subprocess.Popen(
            ["foundry", "model", "load", model_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **SUBPROCESS_TEXT_KWARGS,
        )
        logger.info(f"Загрузка модели {model_id} в сервис запущена (PID: {process.pid})")
        return {"success": True, "model_id": model_id, "status": "loading", "pid": process.pid}
    except FileNotFoundError:
        return {"success": False, "error": "Foundry CLI не найден в PATH"}
    except Exception as e:
        logger.error(f"Ошибка загрузки модели {model_id}: {e}")
        return {"success": False, "error": str(e)}


@router.post("/unload")
async def unload_model(request: dict) -> dict:
    """! Выгрузка модели из Foundry сервиса (foundry model unload)."""
    model_id: str = request.get("model_id", "")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    try:
        result = _run_foundry(["model", "unload", model_id])
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip() or "Ошибка выгрузки"}
        logger.info(f"Модель {model_id} выгружена")
        return {"success": True, "model_id": model_id, "message": f"Модель {model_id} выгружена"}
    except FileNotFoundError:
        return {"success": False, "error": "Foundry CLI не найден в PATH"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Таймаут операции выгрузки"}
    except Exception as e:
        logger.error(f"Ошибка выгрузки модели {model_id}: {e}")
        return {"success": False, "error": str(e)}


@router.get("/status/{model_id:path}")
async def get_model_status(model_id: str) -> dict:
    """! Статус модели: загружена в сервис и/или скачана в кэш."""
    loaded = await list_loaded_models()
    is_loaded = loaded.get("success") and any(m["id"] == model_id for m in loaded["models"])
    is_cached = _is_model_cached(model_id)
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


def _model_id_to_dir(model_id: str) -> str:
    """! Преобразовать model_id в имя директории кэша.

    Foundry сохраняет модели как: <name>-<version>/v<version>
    Пример: qwen2.5-0.5b-instruct-generic-cpu:4 → qwen2.5-0.5b-instruct-generic-cpu-4

    Args:
        model_id: Идентификатор модели в формате 'name:version'.

    Returns:
        str: Имя директории в кэше.
    """
    if ":" in model_id:
        name, version = model_id.rsplit(":", 1)
        return f"{name}-{version}"
    return model_id


def _is_model_cached(model_id: str) -> bool:
    """Проверить наличие модели в кэше — директория существует и содержит v<version>."""
    if not FOUNDRY_CACHE_DIR.exists():
        return False
    dir_name = _model_id_to_dir(model_id)
    model_dir = FOUNDRY_CACHE_DIR / dir_name
    if not model_dir.exists():
        return False
    # Проверяем наличие подпапки v<version>
    if ":" in model_id:
        version = model_id.rsplit(":", 1)[1]
        return (model_dir / f"v{version}").exists()
    return True
