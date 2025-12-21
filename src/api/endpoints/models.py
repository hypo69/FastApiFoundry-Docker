# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
import logging
from ...models.foundry_client import foundry_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/models")
async def get_models():
    """Получить список всех доступных моделей"""
    try:
        result = await foundry_client.list_available_models()
        if result["success"]:
            return {
                "success": True,
                "models": result["models"],
                "count": result["count"]
            }
        else:
            return {
                "success": False,
                "models": [],
                "error": result.get("error", "Failed to load models")
            }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return {
            "success": False,
            "models": [],
            "error": str(e)
        }

@router.get("/models/connected")
async def get_connected_models():
    """Получить список подключенных моделей"""
    try:
        result = await foundry_client.list_available_models()
        if result["success"]:
            # Форматируем модели для совместимости с фронтендом
            models = []
            for model in result["models"]:
                models.append({
                    "id": model["id"],
                    "name": model["id"],
                    "provider": "foundry",
                    "status": "connected",
                    "max_tokens": model.get("maxOutputTokens", 2048)
                })
            
            return {
                "success": True,
                "models": models,
                "count": len(models)
            }
        else:
            return {
                "success": False,
                "models": [],
                "error": result.get("error", "Failed to load models")
            }
    except Exception as e:
        logger.error(f"Error getting connected models: {e}")
        return {
            "success": False,
            "models": [],
            "error": str(e)
        }