# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Endpoints (Refactored)
# =============================================================================
# Описание:
#   Упрощенные endpoints для работы с Foundry сервисом
#
# File: foundry.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from fastapi import APIRouter
from ...models.foundry_client import foundry_client

router = APIRouter()

@router.get("/foundry/status")
async def foundry_status():
    """Получить статус сервиса Foundry"""
    try:
        health = await foundry_client.health_check()
        return {
            "success": True,
            "status": health.get("status", "unknown"),
            "port": health.get("port", 50477),
            "url": health.get("url", "http://localhost:50477/v1")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/foundry/models/list")
async def list_foundry_models():
    """Получить список всех доступных моделей"""
    try:
        models = await foundry_client.list_available_models()
        return models
    except Exception as e:
        return {"success": False, "error": str(e), "models": []}