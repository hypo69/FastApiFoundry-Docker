# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request
import logging
from ...logger import get_logger

logger = get_logger("web-logs")
router = APIRouter()

@router.post("/logs/web")
async def receive_web_logs(request: Request):
    """Получение логов от веб-интерфейса"""
    try:
        log_data = await request.json()
        level = log_data.get("level", "INFO").upper()
        message = log_data.get("message", "")
        data = log_data.get("data")
        
        # Логирование в зависимости от уровня
        if level == "ERROR":
            logger.error(f"WEB-UI: {message}")
        elif level == "WARNING":
            logger.warning(f"WEB-UI: {message}")
        elif level == "DEBUG":
            logger.debug(f"WEB-UI: {message}")
        else:
            logger.info(f"WEB-UI: {message}")
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to process web log: {e}")
        return {"success": False, "error": str(e)}