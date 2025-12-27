# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Logging API Endpoints
# =============================================================================
# Описание:
#   Простые API endpoints для логирования
#   Минимальная функциональность без сложных зависимостей
#
# File: logging_endpoints.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/logs/recent")
async def get_recent_logs():
    """Получить последние записи логов"""
    try:
        return {
            "success": True,
            "data": {
                "logs": [],
                "total": 0,
                "message": "Logs endpoint working"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/logs/web")
async def log_web_message(request: dict):
    """Логирование сообщений с веб-интерфейса"""
    try:
        message = request.get('message', '')
        level = request.get('level', 'info')
        
        # Простое логирование
        if level == 'error':
            logger.error(f"Web UI: {message}")
        elif level == 'warning':
            logger.warning(f"Web UI: {message}")
        else:
            logger.info(f"Web UI: {message}")
        
        return {
            "success": True,
            "message": "Log message recorded"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }