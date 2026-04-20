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
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter
from ...models.foundry_client import foundry_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса.

    Returns:
        dict: status (always 'healthy'), foundry_status, foundry_details,
              models_count, timestamp.
    """
    try:
        foundry_health = await foundry_client.health_check()
        foundry_status = foundry_health.get('status', 'disconnected')
        
        return {
            "status": "healthy",
            "foundry_status": foundry_status,
            "foundry_details": {
                "port": foundry_health.get('port'),
                "url": foundry_health.get('url'),
                "error": foundry_health.get('error') if foundry_status != 'healthy' else None
            },
            "models_count": foundry_health.get('models_count', 0),
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