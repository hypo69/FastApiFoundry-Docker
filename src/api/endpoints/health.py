# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Health Check Endpoint
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
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter
from ...models.foundry_client import foundry_client

# Заглушка для RAG системы
class DummyRAGSystem:
    async def get_status(self):
        return {"status": "disabled", "message": "RAG system is disabled"}

rag_system = DummyRAGSystem()

router = APIRouter()

@router.get("/health")
async def health_check():
    """! Проверка здоровья сервиса

    Returns:
        dict: Статус API, Foundry, RAG системы и количество моделей

    Example:
        >>> health = await health_check()
        >>> print(health['status'])
        'healthy'
    """
    foundry_health = await foundry_client.health_check()
    rag_status = await rag_system.get_status()

    # Определяем доступность RAG
    rag_available = rag_status.get('available', False)
    if isinstance(rag_available, str):
        rag_available = rag_available.lower() in ('true', 'enabled', 'available')

    # Получаем список моделей для подсчета
    models_result = await foundry_client.list_available_models()
    models_count = models_result.get('count', 0) if models_result.get('success') else 0

    return {
        "status": "healthy" if foundry_health.get('status') == 'healthy' else "unhealthy",
        "foundry_status": foundry_health.get('status', 'unknown'),
        "foundry_details": {
            "port": foundry_health.get('port', 50477),
            "url": foundry_health.get('url', 'http://localhost:50477/v1')
        },
        "rag_loaded": rag_available,
        "rag_chunks": 0,
        "models_count": models_count,
        "timestamp": foundry_health.get('timestamp')
    }