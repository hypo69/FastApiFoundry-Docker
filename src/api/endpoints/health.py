# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Простой Health endpoint
# =============================================================================
# Описание:
#   Endpoint для проверки здоровья сервиса
#   Упрощенная версия без Pydantic
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
from ...rag.rag_system import rag_system
from ..models import create_health_response

router = APIRouter()

@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    foundry_health = await foundry_client.health_check()
    rag_status = await rag_system.get_status()
    
    return create_health_response(
        status="healthy" if foundry_health.get('status') == 'healthy' else "unhealthy",
        foundry_status=foundry_health.get('status', 'unknown'),
        rag_available=rag_status['available']
    )