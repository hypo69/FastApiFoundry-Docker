# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: llama.cpp Server Management API
# =============================================================================
# Description:
#   Endpoints for launching and stopping llama.cpp server with GGUF models.
#   llama.cpp поднимает OpenAI-совместимый API (/v1/chat/completions),
#   поэтому FastAPI Foundry подключается к нему как к обычному провайдеру.
#
# Примеры:
#   GET  /api/v1/llama/status
#   POST /api/v1/llama/start   {"model_path": "D:/models/gemma-2-2b-it-Q6_K.gguf"}
#   POST /api/v1/llama/stop
#   GET  /api/v1/llama/models  — сканирует диск на .gguf файлы
#
# File: src/api/endpoints/llama_cpp.py
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
import aiohttp
from pathlib import Path
from fastapi import APIRouter, HTTPException
from ...utils.process_utils import DEFAULT_SUBPROCESS_KWARGS
from ...utils.api_utils import api_response_handler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llama", tags=["llama-cpp"])

# Текущий процесс llama.cpp сервера.
# Хранится на уровне модуля — один сервер на весь процесс FastAPI.
_server_process: subprocess.Popen | None = None
_last_error: str | None = None  # Last start/stop error, shown in /status

# Настройки по умолчанию — переопределяются через .env или тело запроса
DEFAULT_HOST    = "127.0.0.1"
DEFAULT_PORT    = 9780
DEFAULT_CTX     = 4096
DEFAULT_THREADS = os.cpu_count() or 4


def _get_server_url() -> str:
    """! Собрать URL llama.cpp сервера из config.json.

    Returns:
        str: URL вида http://host:port
    """
    try:
        from ...core.config import config
        port = config.get_section("llama_cpp").get("port", DEFAULT_PORT)
        host = config.get_section("llama_cpp").get("host", DEFAULT_HOST)
    except Exception:
        port = DEFAULT_PORT
        host = DEFAULT_HOST
    return f"http://{host}:{port}"


@router.get("/status")
@api_response_handler
async def llama_status() -> dict:
    """! Статус llama.cpp сервера."""
    global _server_process
    running_pid = None

    # Проверяем наш процесс
    if _server_process and _server_process.poll() is None:
        running_pid = _server_process.pid

    # Проверяем HTTP доступность
    url = _get_server_url()
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=3)) as r:
                reachable = r.status == 200
    except Exception:
        reachable = False

    # Capture stderr from a crashed process
    process_error: str | None = None
    if _server_process and _server_process.poll() is not None:
        try:
            stderr_out = _server_process.stderr.read() if _server_process.stderr else ""
            if stderr_out:
                process_error = stderr_out.strip()[-500:]  # last 500 chars
        except Exception:
            pass

    return {
        "success": True,
        "running": reachable,
        "pid": running_pid,
        "url": url,
        "openai_url": f"{url}/v1",
        "last_error": process_error or _last_error,
    }


@router.post("/models/copy")
@api_response_handler
async def llama_copy_model(request: dict) -> dict:
    """! Скопировать .gguf модель в ~/.models.

    Если модель уже там есть — пропускает копирование.

    Body: {"model_path": "D:/gemma-2-2b-it-Q6_K.gguf"}
    """
    import shutil
    import asyncio

    src = Path(request.get("model_path", ""))
    if not src.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {src}")

    from ...core.config import config as _cfg
    dest_dir = Path(_cfg.llama_models_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name

    if dest.exists():
        return {"success": True, "path": str(dest), "status": "already_exists"}

    size_gb = round(src.stat().st_size / 1024**3, 2)
    logger.info(f"Копирование {src.name} ({size_gb} GB) → {dest}")

    def _copy():
        shutil.copy2(str(src), str(dest))
        return str(dest)

    try:
        result_path = await asyncio.get_event_loop().run_in_executor(None, _copy)
        logger.info(f"✅ Скопировано: {result_path}")
        return {"success": True, "path": result_path, "status": "copied", "size_gb": size_gb}
    except Exception as e:
        logger.error(f"Ошибка копирования: {e}")
        return {"success": False, "error": str(e)}


@router.post("/start")
@api_response_handler
async def llama_start(request: dict) -> dict:
    """! Запустить llama.cpp сервер с указанной GGUF моделью.

    Body:
        model_path:   Путь к .gguf файлу или директории с моделями.
                      Если не указан — берётся из config.json (llama_cpp.model_path → directories.models).
                      Если указана директория — берётся первый .gguf файл в ней.
        port:         Порт (default: 9780)
        ctx_size:     Размер контекста (default: 4096)
        threads:      Количество потоков CPU (default: auto)
        n_gpu_layers: Слоёв на GPU, 0 = только CPU (default: 0)
        host:         Хост (default: 127.0.0.1)
    """
    global _server_process, _last_error

    from ...core.config import config as _config

    # Resolve model_path: request body → config.llama_model_path
    model_path = request.get("model_path", "").strip() or _config.llama_model_path

    src = Path(model_path)

    # If a directory is given — pick the first .gguf inside it
    if src.is_dir():
        gguf_files = sorted(src.glob("*.gguf"))
        if not gguf_files:
            raise HTTPException(status_code=404, detail=f"No .gguf files found in: {src}")
        src = gguf_files[0]
        logger.info(f"📂 Директория моделей: выбран {src.name}")

    if not src.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {src}")

    # Copy to models dir if not already there
    copy_to_models = request.get("copy_to_models", True)
    models_home = Path(_config.llama_models_dir)
    dest = models_home / src.name

    if copy_to_models and not dest.exists():
        import shutil
        models_home.mkdir(parents=True, exist_ok=True)
        logger.info(f"Копирование {src.name} → {dest}")
        shutil.copy2(str(src), str(dest))

    model_path = str(dest) if dest.exists() else str(src)

    # Остановить предыдущий если запущен
    if _server_process and _server_process.poll() is None:
        _server_process.terminate()
        _server_process.wait(timeout=5)
        logger.info("Предыдущий llama.cpp сервер остановлен")

    _llama_cfg = _config.get_section("llama_cpp")

    port         = int(request.get("port") or _llama_cfg.get("port", DEFAULT_PORT))
    host         = request.get("host") or _llama_cfg.get("host", DEFAULT_HOST)
    ctx_size     = int(request.get("ctx_size") or DEFAULT_CTX)
    threads      = int(request.get("threads") or DEFAULT_THREADS)
    n_gpu_layers = int(request.get("n_gpu_layers") or 0)

    # Ищем llama-server в PATH и стандартных местах
    server_bin = _find_llama_server()
    if not server_bin:
        _last_error = "llama-server binary not found. Install llama.cpp: https://github.com/ggerganov/llama.cpp/releases"
        return {"success": False, "error": _last_error}

    cmd = [
        server_bin,
        "--model",       model_path,
        "--host",        host,
        "--port",        str(port),
        "--ctx-size",    str(ctx_size),
        "--threads",     str(threads),
        "--n-gpu-layers", str(n_gpu_layers),
        "--log-disable",
    ]

    try:
        _last_error = None
        _server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **DEFAULT_SUBPROCESS_KWARGS
        )
        logger.info(f"llama.cpp запущен: {Path(model_path).name} (PID: {_server_process.pid})")
        return {
            "success": True,
            "pid": _server_process.pid,
            "model": Path(model_path).name,
            "url": f"http://{host}:{port}",
            "openai_url": f"http://{host}:{port}/v1",
            "status": "starting"
        }
    except Exception as e:
        _last_error = str(e)
        logger.error(f"Ошибка запуска llama.cpp: {e}")
        return {"success": False, "error": _last_error}


@router.post("/stop")
@api_response_handler
async def llama_stop() -> dict:
    """! Остановить llama.cpp сервер."""
    global _server_process
    if not _server_process or _server_process.poll() is not None:
        return {"success": True, "message": "Сервер не запущен"}
    try:
        _server_process.terminate()
        _server_process.wait(timeout=10)
        logger.info("llama.cpp сервер остановлен")
        return {"success": True, "message": "Сервер остановлен"}
    except Exception as e:
        _server_process.kill()
        return {"success": True, "message": f"Сервер принудительно остановлен: {e}"}


@router.get("/models")
@api_response_handler
async def llama_scan_models(extra_dir: str = "") -> dict:
    """! Сканировать .gguf файлы в ~/.models, ~/.lmstudio/models и опциональном extra_dir.

    Основные директории: ~/.models, ~/.lmstudio/models
    Дополнительная: extra_dir из query-параметра (например D:\ если модель ещё не скопирована)
    """
    from ...core.config import config as _cfg
    models_home = Path(_cfg.llama_models_dir)
    lmstudio_dir = Path.home() / ".lmstudio" / "models"
    search_dirs = [models_home, lmstudio_dir]

    if extra_dir:
        search_dirs.insert(0, Path(extra_dir))

    found = []
    seen = set()  # избежать дубликатов
    for d in search_dirs:
        if not d.exists():
            continue
        try:
            for gguf in d.rglob("*.gguf"):
                if str(gguf) in seen:
                    continue
                seen.add(str(gguf))
                found.append({
                    "name":    gguf.name,
                    "path":    str(gguf),
                    "size_gb": round(gguf.stat().st_size / 1024**3, 2),
                    "dir":     str(gguf.parent),
                })
        except PermissionError:
            continue

    found.sort(key=lambda x: x["name"])
    return {
        "success":     True,
        "models":      found,
        "count":       len(found),
        "search_dirs": [str(d) for d in search_dirs if d.exists()],
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _find_llama_server() -> str | None:
    """! Find llama-server executable.

    Search order:
        1. LLAMA_SERVER_PATH env var (explicit path)
        2. PATH (shutil.which)
        3. bin/<bin_version>/ from config.json
        4. Any subdirectory of bin/ (fallback scan)
        5. Standard Windows install locations

    Returns:
        str | None: Full path to binary or None.
    """
    import shutil

    # 1. Explicit path from .env
    explicit = os.getenv("LLAMA_SERVER_PATH", "")
    if explicit and Path(explicit).exists():
        return explicit

    # 2. PATH
    for name in ("llama-server", "llama-server.exe"):
        found = shutil.which(name)
        if found:
            return found

    # 3. bin/<bin_version>/ from config.json (primary — version-aware)
    bin_dir = Path(__file__).parents[3] / "bin"
    try:
        from ...core.config import config as _cfg
        bin_version = _cfg.get_section("llama_cpp").get("bin_version", "")
        if bin_version:
            versioned_dir = bin_dir / bin_version
            for name in ("llama-server.exe", "llama-server"):
                candidate = versioned_dir / name
                if candidate.exists():
                    logger.info(f"✅ llama-server found via config bin_version: {candidate}")
                    return str(candidate)
    except Exception:
        pass

    # 4. Fallback: scan all subdirs of bin/
    if bin_dir.exists():
        for d in sorted(bin_dir.iterdir(), reverse=True):  # newest first by name
            if not d.is_dir():
                continue
            for name in ("llama-server.exe", "llama-server"):
                candidate = d / name
                if candidate.exists():
                    logger.info(f"✅ llama-server found via bin/ scan: {candidate}")
                    return str(candidate)

    # 5. Standard Windows locations
    for c in [
        Path("C:/llama.cpp/llama-server.exe"),
        Path("C:/Program Files/llama.cpp/llama-server.exe"),
        Path(os.getenv("LOCALAPPDATA", "")) / "llama.cpp" / "llama-server.exe",
    ]:
        if c.exists():
            return str(c)

    return None
