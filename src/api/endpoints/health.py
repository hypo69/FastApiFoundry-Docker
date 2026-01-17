# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Health Check Endpoint (Refactored)
# =============================================================================
# Описание:
#   Endpoint для проверки здоровья сервиса FastAPI Foundry
#   Проверяет статус API, Foundry сервера, RAG системы и количество моделей
#
# Примеры:
#   >>> import requests
#   >>> response = requests.get('http://localhost:9696/api/v1/health')
#   >>> print(response.json())
#   {'status': 'healthy', 'foundry_status': 'healthy', 'models_count': 3}
#
# File: health.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.3
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter
from ...models.foundry_client import foundry_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    try:
        foundry_health = await foundry_client.health_check()
        
        # API всегда здоров, если мы дошли до этой точки
        api_status = "healthy"
        foundry_status = foundry_health.get('status', 'disconnected')
        
        # Получаем список моделей только если Foundry доступен
        models_count = 0
        if foundry_status == 'healthy':
            try:
                models_result = await foundry_client.list_available_models()
                models_count = models_result.get('count', 0) if models_result.get('success') else 0
            except Exception:
                models_count = 0
        
        return {
            "status": api_status,
            "foundry_status": foundry_status,
            "foundry_details": {
                "port": foundry_health.get('port'),
                "url": foundry_health.get('url'),
                "error": foundry_health.get('error') if foundry_status != 'healthy' else None
            },
            "models_count": models_count,
            "timestamp": foundry_health.get('timestamp')
        }
    except Exception as e:
        # Даже если есть ошибка, API работает
        return {
            "status": "healthy",
            "foundry_status": "error",
            "foundry_details": {
                "port": None,
                "url": None,
                "error": str(e)
            },
            "models_count": 0,
            "timestamp": None
        }