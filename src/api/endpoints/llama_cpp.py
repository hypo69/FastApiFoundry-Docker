# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: llama.cpp Server Management API
# =============================================================================
# Описание:
#   Endpoints для запуска/остановки llama.cpp сервера с GGUF моделями.
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
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import subprocess
import logging
import os
import aiohttp
from pathlib import Path
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llama", tags=["llama-cpp"])

# Текущий процесс llama.cpp сервера.
# Хранится на уровне модуля — один сервер на весь процесс FastAPI.
_server_process: subprocess.Popen | None = None

# Настройки по умолчанию — переопределяются через .env или тело запроса
DEFAULT_HOST    = "127.0.0.1"
DEFAULT_PORT    = 8080
DEFAULT_CTX     = 4096
DEFAULT_THREADS = os.cpu_count() or 4


def _get_server_url() -> str:
    """! Собрать URL llama.cpp сервера из переменных окружения.

    Returns:
        str: URL вида http://host:port
    """
    port = os.getenv("LLAMA_PORT", str(DEFAULT_PORT))
    host = os.getenv("LLAMA_HOST", DEFAULT_HOST)
    return f"http://{host}:{port}"


@router.get("/status")
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

    return {
        "success": True,
        "running": reachable,
        "pid": running_pid,
        "url": url,
        "openai_url": f"{url}/v1",
    }


@router.post("/models/copy")
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

    dest_dir = Path.home() / ".models"
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
async def llama_start(request: dict) -> dict:
    """! Запустить llama.cpp сервер с указанной GGUF моделью.

    Body:
        model_path:  Путь к .gguf файлу (обязательно)
        port:        Порт (default: 8080)
        ctx_size:    Размер контекста (default: 4096)
        threads:     Количество потоков CPU (default: auto)
        n_gpu_layers: Слоёв на GPU, 0 = только CPU (default: 0)
        host:        Хост (default: 127.0.0.1)
    """
    global _server_process

    model_path = request.get("model_path", "")
    if not model_path:
        raise HTTPException(status_code=400, detail="model_path is required")

    src = Path(model_path)
    if not src.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {model_path}")

    # Копировать в ~/.models если модель не там и запрошено copy_to_models
    copy_to_models = request.get("copy_to_models", True)
    models_home = Path.home() / ".models"
    dest = models_home / src.name

    if copy_to_models and not dest.exists():
        import shutil
        models_home.mkdir(parents=True, exist_ok=True)
        logger.info(f"Копирование {src.name} → {dest}")
        shutil.copy2(str(src), str(dest))

    # Используем путь в ~/.models если файл там есть
    model_path = str(dest) if dest.exists() else model_path

    # Остановить предыдущий если запущен
    if _server_process and _server_process.poll() is None:
        _server_process.terminate()
        _server_process.wait(timeout=5)
        logger.info("Предыдущий llama.cpp сервер остановлен")

    port        = int(request.get("port", os.getenv("LLAMA_PORT", DEFAULT_PORT)))
    host        = request.get("host", os.getenv("LLAMA_HOST", DEFAULT_HOST))
    ctx_size    = int(request.get("ctx_size", DEFAULT_CTX))
    threads     = int(request.get("threads", DEFAULT_THREADS))
    n_gpu_layers = int(request.get("n_gpu_layers", 0))

    # Ищем llama-server в PATH и стандартных местах
    server_bin = _find_llama_server()
    if not server_bin:
        return {
            "success": False,
            "error": "llama-server не найден. Установите llama.cpp: https://github.com/ggerganov/llama.cpp/releases"
        }

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
        _server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
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
        logger.error(f"Ошибка запуска llama.cpp: {e}")
        return {"success": False, "error": str(e)}


@router.post("/stop")
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
async def llama_scan_models(extra_dir: str = "") -> dict:
    """! Сканировать .gguf файлы в ~/.models и опциональном extra_dir.

    Основная директория: ~/.models
    Дополнительная: extra_dir из query-параметра (например D:\ если модель ещё не скопирована)
    """
    models_home = Path.home() / ".models"
    search_dirs = [models_home]

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
        "success":    True,
        "models":     found,
        "count":      len(found),
        "search_dir": str(models_home)
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _find_llama_server() -> str | None:
    """! Найти исполняемый файл llama-server в PATH и стандартных местах.

    Порядок поиска:
        1. LLAMA_SERVER_PATH из .env (явный путь к бинарнику)
        2. PATH (shutil.which)
        3. Директория рядом с LLAMA_MODEL_PATH из .env
        4. Директории из GGUF_SEARCH_DIRS из .env
        5. Стандартные места установки на Windows

    Returns:
        str | None: Полный путь к бинарнику или None если не найден.
    """
    import shutil

    # 1. Явный путь из .env
    explicit = os.getenv("LLAMA_SERVER_PATH", "")
    if explicit and Path(explicit).exists():
        return explicit

    # 2. PATH
    for name in ("llama-server", "llama-server.exe", "server", "server.exe"):
        found = shutil.which(name)
        if found:
            return found

    # 3. Директория рядом с моделью из LLAMA_MODEL_PATH
    model_path = os.getenv("LLAMA_MODEL_PATH", "")
    if model_path:
        model_dir = Path(model_path).parent
        for name in ("llama-server.exe", "server.exe", "llama-server", "server"):
            candidate = model_dir / name
            if candidate.exists():
                return str(candidate)

    # 4. Директории из GGUF_SEARCH_DIRS
    search_dirs = os.getenv("GGUF_SEARCH_DIRS", "")
    for d in search_dirs.split(","):
        d = d.strip()
        if not d:
            continue
        for name in ("llama-server.exe", "server.exe", "llama-server", "server"):
            candidate = Path(d) / name
            if candidate.exists():
                return str(candidate)

    # 5. Стандартные места установки на Windows
    candidates = [
        Path("C:/llama.cpp/llama-server.exe"),
        Path("C:/llama.cpp/server.exe"),
        Path("C:/Program Files/llama.cpp/llama-server.exe"),
        Path(os.getenv("LOCALAPPDATA", "")) / "llama.cpp" / "llama-server.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)

    return None
