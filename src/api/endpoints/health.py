# -*- coding: utf-8 -*-
import logging
from fastapi import APIRouter
from ..models import HealthResponse
from ...core.config import settings
from ...models.foundry_client import foundry_client
from ...rag.rag_system import rag_system

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка здоровья сервиса"""
    logger.info("Health check requested")
    
    foundry_health = await foundry_client.health_check()
    logger.info(f"Foundry health result: {foundry_health}")
    
    rag_status = await rag_system.get_status()
    logger.info(f"RAG status: {rag_status}")
    
    response = HealthResponse(
        status="healthy" if foundry_health.get('status') == 'healthy' else "unhealthy",
        foundry_url=settings.foundry_base_url,
        foundry_status=foundry_health.get('status', 'unknown'),
        rag_available=rag_status['available'],
        rag_loaded=rag_status['loaded'],
        rag_chunks=rag_status['chunks_count']
    )
    
    logger.info(f"Health response: {response.dict()}")
    return response