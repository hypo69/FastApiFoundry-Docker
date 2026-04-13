# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Models Management API
# =============================================================================
# Описание:
#   API endpoints для управления моделями Foundry:
#   список доступных, загруженных, загрузка, выгрузка, статус.
#
#   ПОЧЕМУ ПРЯМОЙ ВЫЗОВ foundry CLI, А НЕ ЧЕРЕЗ PowerShell-скрипты:
#     scripts/*.ps1 были тонкими обёртками над одной командой foundry.
#     Вызов через subprocess('powershell', '-File', script.ps1) добавлял
#     лишний процесс, зависимость от пути к файлу и усложнял отладку.
#     Python subprocess(['foundry', ...]) делает то же самое напрямую.
#
#   ПОЧЕМУ list_available_models ВОЗВРАЩАЕТ ХАРДКОД, А НЕ foundry model list:
#     foundry model list возвращает модели из каталога Foundry Hub —
#     их тысячи, вывод нестабильный и медленный. Хардкод содержит
#     проверенные модели совместимые с CPU, актуальные для проекта.
#
# Примеры:
#   GET  /api/v1/foundry/models/available
#   GET  /api/v1/foundry/models/loaded
#   POST /api/v1/foundry/models/download  {"model_id": "qwen2.5-0.5b-..."}
#   POST /api/v1/foundry/models/load      {"model_id": "qwen2.5-0.5b-..."}
#   POST /api/v1/foundry/models/unload    {"model_id": "qwen2.5-0.5b-..."}
#
# File: src/api/endpoints/foundry_models.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import subprocess
import logging
import os
import aiohttp
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/foundry/models", tags=["foundry-models"])

# Проверенные модели совместимые с CPU.
# ПОЧЕМУ СПИСОК ЗДЕСЬ, А НЕ В config.json:
#   Это каталог поддерживаемых моделей, а не пользовательская настройка.
#   config.json хранит выбор пользователя (default_model), а не весь каталог.
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


def _get_foundry_base_url() -> str:
    """! Получение base URL Foundry из переменной окружения.

    Returns:
        str: URL вида http://localhost:PORT/v1/
    """
    return os.getenv("FOUNDRY_BASE_URL", "http://localhost:50477/v1/")


def _run_foundry(args: list, timeout: int = 30) -> subprocess.CompletedProcess:
    """! Запуск команды foundry CLI через subprocess.

    Args:
        args (list): Аргументы команды, например ['model', 'load', 'qwen...'].
        timeout (int): Таймаут в секундах.

    Returns:
        subprocess.CompletedProcess: Результат выполнения.

    Raises:
        FileNotFoundError: Если foundry CLI не установлен.
        subprocess.TimeoutExpired: При превышении таймаута.
    """
    return subprocess.run(
        ["foundry"] + args,
        capture_output=True,
        text=True,
        timeout=timeout
    )


@router.get("/available")
async def list_available_models() -> dict:
    """! Список моделей доступных для загрузки."""
    return {
        "success": True,
        "models": AVAILABLE_MODELS,
        "count": len(AVAILABLE_MODELS),
    }


@router.get("/loaded")
async def list_loaded_models() -> dict:
    """! Список моделей загруженных в Foundry сервис.

    Обращается к Foundry API напрямую — актуальное состояние без CLI.
    """
    base_url: str = _get_foundry_base_url().rstrip("/")
    url: str = f"{base_url}/models"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if not response.status == 200:
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

    Запускает загрузку в фоне — возвращает PID процесса не дожидаясь завершения.
    ПОЧЕМУ НЕ ЖДЁМ ЗАВЕРШЕНИЯ:
      Загрузка модели может занять десятки минут.
      Синхронный вызов заблокирует весь API сервер.
    """
    model_id: str = request.get("model_id", "")

    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    try:
        # Запуск в фоне без ожидания завершения
        process = subprocess.Popen(
            ["foundry", "model", "download", model_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Загрузка модели {model_id} запущена (PID: {process.pid})")
        return {"success": True, "model_id": model_id, "status": "downloading", "pid": process.pid}

    except FileNotFoundError:
        return {"success": False, "error": "Foundry CLI не найден в PATH"}
    except Exception as e:
        logger.error(f"Ошибка запуска загрузки модели {model_id}: {e}")
        return {"success": False, "error": str(e)}


@router.post("/load")
async def load_model(request: dict) -> dict:
    """! Загрузка модели в Foundry сервис (foundry model load).

    Запускает в фоне — модель может загружаться несколько минут.
    """
    model_id: str = request.get("model_id", "")

    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    try:
        process = subprocess.Popen(
            ["foundry", "model", "load", model_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
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
    """! Выгрузка модели из Foundry сервиса (foundry model unload).

    Ждёт завершения — выгрузка быстрая (секунды).
    """
    model_id: str = request.get("model_id", "")

    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")

    try:
        result = _run_foundry(["model", "unload", model_id])

        if not result.returncode == 0:
            logger.error(f"Ошибка выгрузки модели {model_id}: {result.stderr}")
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


@router.get("/status/{model_id}")
async def get_model_status(model_id: str) -> dict:
    """! Статус конкретной модели — загружена или нет."""
    loaded: dict = await list_loaded_models()

    if not loaded["success"]:
        return {"success": False, "error": loaded.get("error")}

    is_loaded: bool = any(m["id"] == model_id for m in loaded["models"])
    return {
        "success": True,
        "model_id": model_id,
        "status": "loaded" if is_loaded else "not_loaded",
    }
