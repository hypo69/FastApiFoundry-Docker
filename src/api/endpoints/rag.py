# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: RAG System API Endpoints
# =============================================================================
# Описание:
#   REST API endpoints для управления RAG системой
#   Включает конфигурацию, статус, поиск и управление индексом
#
# Примеры:
#   GET /api/v1/rag/status - получить статус RAG
#   PUT /api/v1/rag/config - обновить конфигурацию
#   POST /api/v1/rag/search - поиск в RAG
#
# File: src/api/endpoints/rag.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
from pathlib import Path

router = APIRouter(prefix="/rag", tags=["RAG"])

class RAGConfig(BaseModel):
    enabled: bool = False
    index_dir: str = "./rag_index"
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    top_k: int = 5

class RAGSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class RAGSearchResult(BaseModel):
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

@router.get("/status")
async def get_rag_status():
    """Получить статус RAG системы"""
    try:
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            rag_config = config.get("rag_system", {})
        else:
            rag_config = {}
        
        # Подсчет chunks
        index_dir = Path(rag_config.get("index_dir", "./rag_index"))
        total_chunks = 0
        if index_dir.exists():
            chunk_files = list(index_dir.glob("*.json"))
            total_chunks = len(chunk_files)
        
        return {
            "success": True,
            "enabled": rag_config.get("enabled", False),
            "index_dir": str(index_dir),
            "model": rag_config.get("model", "sentence-transformers/all-MiniLM-L6-v2"),
            "chunk_size": rag_config.get("chunk_size", 1000),
            "top_k": rag_config.get("top_k", 5),
            "total_chunks": total_chunks
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.put("/config")
async def update_rag_config(config: RAGConfig):
    """Обновить конфигурацию RAG системы"""
    try:
        config_path = Path("config.json")
        
        # Загружаем существующую конфигурацию
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
        else:
            full_config = {}
        
        # Обновляем RAG секцию
        full_config["rag_system"] = {
            "enabled": config.enabled,
            "index_dir": config.index_dir,
            "model": config.model,
            "chunk_size": config.chunk_size,
            "top_k": config.top_k
        }
        
        # Сохраняем конфигурацию
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2, ensure_ascii=False)
        
        return {"success": True, "message": "RAG configuration updated"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/search")
async def search_rag(request: RAGSearchRequest):
    """Поиск в RAG системе"""
    try:
        # Простая заглушка для поиска
        results = [
            {
                "content": f"Mock result for query: {request.query}",
                "score": 0.95,
                "metadata": {"source": "mock"}
            },
            {
                "content": f"Another result for: {request.query}",
                "score": 0.87,
                "metadata": {"source": "mock"}
            }
        ]
        
        return {
            "success": True,
            "results": results[:request.top_k],
            "total": len(results)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/rebuild")
async def rebuild_rag_index():
    """Перестроить RAG индекс"""
    try:
        # Заглушка для перестройки индекса
        return {
            "success": True,
            "message": "RAG index rebuild started (mock)",
            "chunks_processed": 42
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/clear")
async def clear_rag_chunks():
    """Очистить все RAG chunks"""
    try:
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            index_dir = Path(config.get("rag_system", {}).get("index_dir", "./rag_index"))
        else:
            index_dir = Path("./rag_index")
        
        # Удаляем файлы индекса
        deleted_count = 0
        if index_dir.exists():
            for file in index_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    deleted_count += 1
        
        return {
            "success": True,
            "message": f"Cleared {deleted_count} RAG chunks",
            "deleted_count": deleted_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}