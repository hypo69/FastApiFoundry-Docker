# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Health Check Endpoint (Refactored)
# =============================================================================
# Описание:
<<<<<<< HEAD
#   Упрощенный endpoint для проверки здоровья сервиса
=======
#   Endpoint для проверки здоровья сервиса FastAPI Foundry
#   Проверяет статус API, Foundry сервера, RAG системы и количество моделей
#
# Примеры:
#   >>> import requests
#   >>> response = requests.get('http://localhost:9696/api/v1/health')
#   >>> print(response.json())
#   {'status': 'healthy', 'foundry_status': 'healthy', 'models_count': 3}
>>>>>>> a76fcff509d3210e0d5dbe66516b2c1d02333d90
#
# File: health.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from fastapi import APIRouter
from ...models.foundry_client import foundry_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    foundry_health = await foundry_client.health_check()
    models_result = await foundry_client.list_available_models()
    models_count = models_result.get('count', 0) if models_result.get('success') else 0

    return {
        "status": "healthy" if foundry_health.get('status') == 'healthy' else "unhealthy",
        "foundry_status": foundry_health.get('status', 'unknown'),
        "foundry_details": {
            "port": foundry_health.get('port', 50477),
            "url": foundry_health.get('url', 'http://localhost:50477/v1')
        },
        "models_count": models_count,
        "timestamp": foundry_health.get('timestamp')
    }