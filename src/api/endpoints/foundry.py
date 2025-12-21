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
        status = await foundry_client.get_service_status()
        return status
    except Exception as e:
        logger.error(f"Error getting Foundry status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/foundry/service/start")
async def start_foundry_service():
    """Запустить сервис Foundry"""
    try:
        result = await foundry_client.start_service()
        return result
    except Exception as e:
        logger.error(f"Error starting Foundry service: {e}")
        return {"success": False, "error": str(e)}

@router.post("/foundry/service/stop")
async def stop_foundry_service():
    """Остановить сервис Foundry"""
    try:
        result = await foundry_client.stop_service()
        return result
    except Exception as e:
        logger.error(f"Error stopping Foundry service: {e}")
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

@router.post("/foundry/models/run")
async def run_foundry_model(request: dict):
    """Запустить модель"""
    try:
        model_name = request.get("model_name")
        if not model_name:
            return {"success": False, "error": "model_name is required"}
        
        result = await foundry_client.run_model(model_name)
        return result
    except Exception as e:
        logger.error(f"Error running Foundry model: {e}")
        return {"success": False, "error": str(e)}