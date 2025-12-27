# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Health Check Endpoint (Refactored)
# =============================================================================
# Описание:
#   Упрощенный endpoint для проверки здоровья сервиса
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