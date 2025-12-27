# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Config Endpoints (Refactored)
# =============================================================================
# Описание:
#   Endpoint для получения конфигурации в веб-интерфейсе
#
# File: config.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from fastapi import APIRouter
from ...core.config import config

router = APIRouter()

@router.get("/config")
async def get_config():
    """Получить конфигурацию для веб-интерфейса"""
    return {
        "success": True,
        "foundry_ai": {
            "base_url": config.foundry_base_url,
            "default_model": config.foundry_default_model,
            "auto_load_default": config.foundry_auto_load_default
        },
        "api": {
            "host": config.api_host,
            "port": config.api_port
        }
    }

@router.post("/config/update")
async def update_config(request: dict):
    """Обновить конфигурацию"""
    try:
        # Обновляем только разрешенные поля
        if "foundry_ai" in request:
            foundry_config = request["foundry_ai"]
            if "default_model" in foundry_config:
                # Обновляем в config.json
                raw_config = config.get_raw_config()
                if "foundry_ai" not in raw_config:
                    raw_config["foundry_ai"] = {}
                raw_config["foundry_ai"]["default_model"] = foundry_config["default_model"]
                config.update_config(raw_config)
        
        return {"success": True, "message": "Конфигурация обновлена"}
    except Exception as e:
        return {"success": False, "error": str(e)}