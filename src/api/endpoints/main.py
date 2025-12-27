# -*- coding: utf-8 -*-
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
        "version": "1.0.0",
        "description": "REST API для локальных AI моделей",
        "endpoints": {
            "generate": "/api/v1/generate",
            "batch_generate": "/api/v1/batch-generate",
            "models": "/api/v1/models",
            "health": "/api/v1/health",
            "rag_search": "/api/v1/rag/search",
            "config": "/api/v1/config"
        },
        "docs": "/docs",
        "web_interface": "/",
        "timestamp": datetime.now().isoformat()
    }