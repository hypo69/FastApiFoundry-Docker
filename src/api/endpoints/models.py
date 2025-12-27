# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Models Management Endpoints (Refactored)
# =============================================================================
# Описание:
<<<<<<< HEAD
#   Упрощенные API endpoints для управления моделями AI
=======
#   API endpoints для управления моделями AI
#   Получение списка доступных и подключенных моделей через Foundry
#
# Примеры:
#   >>> import requests
#   >>> response = requests.get('http://localhost:9696/api/v1/models')
#   >>> models = response.json()['models']
#   >>> print(f"Available models: {len(models)}")
>>>>>>> a76fcff509d3210e0d5dbe66516b2c1d02333d90
#
# File: models.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from fastapi import APIRouter
from ...models.foundry_client import foundry_client

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
        return {
            "success": False,
            "models": [],
            "error": str(e)
        }