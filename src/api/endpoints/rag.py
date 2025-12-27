# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: RAG Endpoints (Active)
# =============================================================================
# Описание:
#   Активные RAG endpoints для поиска и извлечения контекста
#   Интеграция с FAISS и sentence-transformers
#
# File: rag.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.3
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ...rag.rag_system import rag_system

router = APIRouter()

class RAGSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class RAGSearchResult(BaseModel):
    text: str
    source: str
    section: str
    score: float

class RAGSearchResponse(BaseModel):
    success: bool
    results: List[RAGSearchResult]
    context: str
    message: Optional[str] = None

@router.get("/rag/status")
async def rag_status():
    """Статус RAG системы"""
    try:
        status = await rag_system.get_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        return {
            "success": False,
            "status": {},
            "error": str(e)
        }

@router.post("/rag/search", response_model=RAGSearchResponse)
async def rag_search(request: RAGSearchRequest):
    """Поиск в RAG системе"""
    try:
        if not rag_system.loaded:
            raise HTTPException(status_code=503, detail="RAG система не загружена")
        
        # Выполнить поиск
        results = await rag_system.search(request.query, request.top_k)
        
        # Форматировать контекст
        context = rag_system.format_context(results)
        
        # Преобразовать результаты
        search_results = [
            RAGSearchResult(
                text=r['text'],
                source=r['source'],
                section=r['section'],
                score=r['score']
            )
            for r in results
        ]
        
        return RAGSearchResponse(
            success=True,
            results=search_results,
            context=context,
            message=f"Найдено {len(results)} релевантных результатов"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска RAG: {str(e)}")

@router.post("/rag/reload")
async def rag_reload():
    """Перезагрузить RAG индекс"""
    try:
        success = await rag_system.reload_index()
        return {
            "success": success,
            "message": "RAG индекс перезагружен" if success else "Ошибка перезагрузки RAG"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/rag/initialize")
async def rag_initialize():
    """Инициализировать RAG систему"""
    try:
        success = await rag_system.initialize()
        return {
            "success": success,
            "message": "RAG система инициализирована" if success else "Ошибка инициализации RAG"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/rag/clear")
async def rag_clear():
    """Очистить RAG индекс и все chunks"""
    try:
        success = await rag_system.clear_index()
        return {
            "success": success,
            "message": "RAG индекс и chunks успешно очищены" if success else "Ошибка очистки RAG"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }