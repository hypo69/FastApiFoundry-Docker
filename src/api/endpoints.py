# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: API Endpoints (RAG)
# =============================================================================
# Описание:
#   Эндпоинты для управления векторным индексом RAG.
#   Позволяет запускать индексацию директорий через HTTP POST запросы.
#
# File: src/api/endpoints.py
# Project: FastApiFoundry
# Package: src.api
# Module: endpoints
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.rag.rag_system import rag_system
from src.logger import logger

# Инициализация роутера для RAG операций
# Initialization of the router for RAG operations
router = APIRouter(prefix="/v1/rag", tags=["RAG"])

class IndexRequest(BaseModel):
    """Схема запроса на индексацию."""
    source_dirs: Optional[List[str]] = None

@router.post("/index")
async def index_rag(request: IndexRequest):
    """! Запуск процесса индексации указанных или настроенных директорий.
    
    ОБОСНОВАНИЕ:
      - Обеспечение актуальности базы знаний через API.
      - Использование TextExtractor для автоматического извлечения текста.
    """
    try:
        logger.info(f"RAG API: Запуск индексации для: {request.source_dirs or 'директории из конфига'}")
        
        # Выполнение индексации через ядро системы
        # Execution of indexing via the system core
        success = await rag_system.index_directories(source_dirs=request.source_dirs)
        
        if not success:
            raise HTTPException(status_code=400, detail="Ошибка выполнения индексации.")
            
        return {"status": "success", "message": "Индексация успешно завершена."}
    except Exception as e:
        logger.error(f"RAG API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))