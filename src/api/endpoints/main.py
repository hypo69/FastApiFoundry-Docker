# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Main Endpoints (Refactored)
# =============================================================================
# Описание:
#   Основные endpoints для корневых маршрутов
#
# File: main.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/")
async def root():
    """Панель управления FastAPI Foundry"""
    return FileResponse('static/index.html')

@router.get("/api")
async def api_info():
    """Информация об API"""
    return {
        "service": "FastAPI Foundry",
        "version": "0.4.1",
        "description": "REST API для локальных AI моделей",
        "endpoints": {
            "generate": "/api/v1/generate",
            "models": "/api/v1/models",
            "health": "/api/v1/health",
            "chat": "/api/v1/chat"
        },
        "docs": "/docs",
        "web_interface": "/",
        "timestamp": datetime.now().isoformat()
    }