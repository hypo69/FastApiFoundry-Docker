# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
import logging
from ...models.foundry_client import foundry_client

logger = logging.getLogger(__name__)
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
        logger.error(f"Error getting Foundry status: {e}")
        return {"success": False, "error": str(e)}

@router.get("/foundry/models/list")
async def list_foundry_models():
    """Получить список всех доступных моделей"""
    try:
        models = await foundry_client.list_available_models()
        return models
    except Exception as e:
        logger.error(f"Error listing Foundry models: {e}")
        return {"success": False, "error": str(e), "models": []}