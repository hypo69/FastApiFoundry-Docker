# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: RAG System for FastAPI Foundry
# =============================================================================
# Описание:
#   Система поиска и извлечения контекста (RAG) для FastAPI Foundry
#   Использует FAISS для векторного поиска и sentence-transformers для эмбеддингов
#
# File: rag_system.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import json
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from ..core.config import config

logger = logging.getLogger(__name__)

# Проверка доступности RAG зависимостей
RAG_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    RAG_AVAILABLE = True
except ImportError:
    logger.warning("RAG dependencies not installed. Install: pip install sentence-transformers faiss-cpu")

class RAGSystem:
    """Система поиска и извлечения контекста (RAG)"""
    
    def __init__(self):
        self.index_dir = Path(config.rag_index_dir)
        self.model_name = config.rag_model
        self.index = None
        self.chunks = []
        self.model = None
        self.loaded = False
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """Инициализировать RAG систему"""
        if not RAG_AVAILABLE:
            logger.warning("RAG not available - missing dependencies")
            return False
        
        if not config.rag_enabled:
            logger.info("RAG disabled in configuration")
            return False
        
        async with self._lock:
            return await self._load_index()
    
    async def _load_index(self) -> bool:
        """Загрузить FAISS индекс и метаданные"""
        index_path = self.index_dir / "faiss.index"
        meta_path = self.index_dir / "chunks.json"
        
        if not index_path.exists() or not meta_path.exists():
            logger.warning(f"RAG index not found at {self.index_dir}")
            return False
        
        try:
            # Загрузить модель эмбеддингов в отдельном потоке
            logger.info(f"Loading embedding model: {self.model_name}")
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                SentenceTransformer, 
                self.model_name
            )
            
            # Загрузить FAISS индекс
            logger.info("Loading FAISS index...")
            self.index = await loop.run_in_executor(
                None,
                faiss.read_index,
                str(index_path)
            )
            
            # Загрузить метаданные чанков
            logger.info("Loading chunks metadata...")
            with open(meta_path, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            
            self.loaded = True
            logger.info(f"RAG loaded: {self.index.ntotal} vectors from {len(self.chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load RAG index: {e}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Найти релевантные чанки для запроса
        
        Args:
            query: Поисковый запрос
            top_k: Количество результатов
            
        Returns:
            Список релевантных чанков с метаданными
        """
        if not self.loaded:
            return []
        
        try:
            # Кодировать запрос в отдельном потоке
            loop = asyncio.get_event_loop()
            query_vec = await loop.run_in_executor(
                None,
                self.model.encode,
                [query]
            )
            
            # Нормализовать вектор
            query_vec = np.array(query_vec).astype('float32')
            faiss.normalize_L2(query_vec)
            
            # Поиск в индексе
            scores, indices = await loop.run_in_executor(
                None,
                self.index.search,
                query_vec,
                top_k
            )
            
            # Собрать результаты
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx].copy()
                    chunk['score'] = float(score)
                    results.append(chunk)
            
            return results
            
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return []
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Форматировать результаты поиска как контекст
        
        Args:
            results: Результаты поиска RAG
            
        Returns:
            Отформатированный контекст для промпта
        """
        if not results:
            return "No relevant context found."
        
        context_parts = ["=== PROJECT CONTEXT START ===\n"]
        
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[{i}] Source: {r['source']} | Section: {r['section']} | Relevance: {r['score']:.2f}"
            )
            context_parts.append(r['text'])
            context_parts.append("")
        
        context_parts.append("=== PROJECT CONTEXT END ===")
        return "\n".join(context_parts)
    
    async def get_status(self) -> Dict[str, Any]:
        """Получить статус RAG системы"""
        return {
            'available': RAG_AVAILABLE,
            'enabled': config.rag_enabled,
            'loaded': self.loaded,
            'index_dir': str(self.index_dir),
            'model': self.model_name,
            'chunks_count': len(self.chunks) if self.loaded else 0,
            'vectors_count': self.index.ntotal if self.loaded and self.index else 0
        }
    
    async def reload_index(self) -> bool:
        """Перезагрузить RAG индекс"""
        logger.info("Reloading RAG index...")
        self.loaded = False
        self.index = None
        self.chunks = []
        self.model = None
        
        return await self.initialize()
    
    async def clear_index(self) -> bool:
        """Очистить RAG индекс и все chunks"""
        try:
            logger.info("Clearing RAG index...")
            
            # Сбросить состояние
            self.loaded = False
            self.index = None
            self.chunks = []
            self.model = None
            
            # Удалить файлы индекса
            index_path = self.index_dir / "faiss.index"
            chunks_path = self.index_dir / "chunks.json"
            info_path = self.index_dir / "index_info.json"
            
            files_removed = []
            for file_path in [index_path, chunks_path, info_path]:
                if file_path.exists():
                    file_path.unlink()
                    files_removed.append(file_path.name)
                    logger.info(f"Removed: {file_path}")
            
            if files_removed:
                logger.info(f"RAG index cleared. Removed files: {', '.join(files_removed)}")
            else:
                logger.info("RAG index was already empty")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear RAG index: {e}")
            return False

# Глобальный экземпляр RAG системы
rag_system = RAGSystem()