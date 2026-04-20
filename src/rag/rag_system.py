# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: RAG System for FastAPI Foundry
# =============================================================================
# Description:
#   Retrieval-Augmented Generation system using FAISS vector search
#   and sentence-transformers embeddings.
#
# File: rag_system.py
# Project: FastApiFoundry (Docker)
# Version: 0.5.5
# Changes in 0.5.5:
#   - Added granular try/except with logging in _load_index, search,
#     clear_index, get_all_chunks, reload_index
#   - Each except block explains why the error can occur
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from ..core.config import config

logger = logging.getLogger(__name__)

RAG_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    RAG_AVAILABLE = True
except ImportError:
    logger.warning('⚠️ RAG dependencies not installed. Run: pip install sentence-transformers faiss-cpu')


class RAGSystem:
    """Retrieval-Augmented Generation system."""

    def __init__(self) -> None:
        self.index_dir = Path(config.dir_rag)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f'RAG index directory: {self.index_dir}')
        self.model_name = config.rag_model
        self.index = None
        self.chunks: List[Dict[str, Any]] = []
        self.model = None
        self.loaded = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> bool:
        """Initialize the RAG system.

        Returns:
            bool: True if index loaded successfully, False if unavailable or disabled.
        """
        if not RAG_AVAILABLE:
            logger.warning('⚠️ RAG not available — missing dependencies')
            return False
        if not config.rag_enabled:
            logger.info('RAG disabled in configuration')
            return False
        async with self._lock:
            return await self._load_index()

    async def _load_index(self) -> bool:
        """Load FAISS index and chunk metadata from disk.

        Returns:
            bool: True if both faiss.index and chunks.json loaded successfully.
        """
        index_path = self.index_dir / 'faiss.index'
        meta_path  = self.index_dir / 'chunks.json'

        if not index_path.exists() or not meta_path.exists():
            logger.warning(f'⚠️ RAG index not found at {self.index_dir}')
            return False

        loop = asyncio.get_event_loop()

        try:
            logger.info(f'Loading embedding model: {self.model_name}')
            self.model = await loop.run_in_executor(None, SentenceTransformer, self.model_name)
        except Exception as e:
            # Model name wrong, no internet, or transformers version mismatch
            logger.error(f'❌ Failed to load embedding model "{self.model_name}": {e}')
            return False

        try:
            logger.info('Loading FAISS index…')
            self.index = await loop.run_in_executor(None, faiss.read_index, str(index_path))
        except Exception as e:
            # Index file corrupted or written by incompatible FAISS version
            logger.error(f'❌ Failed to read FAISS index from {index_path}: {e}')
            return False

        try:
            logger.info('Loading chunks metadata…')
            with open(meta_path, encoding='utf-8') as f:
                self.chunks = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            # chunks.json missing, empty, or malformed
            logger.error(f'❌ Failed to load chunks metadata from {meta_path}: {e}')
            return False

        self.loaded = True
        logger.info(f'✅ RAG loaded: {self.index.ntotal} vectors, {len(self.chunks)} chunks')
        return True

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find relevant chunks for a query.

        Args:
            query: Search query text.
            top_k: Number of results to return.

        Returns:
            List of matching chunks with score field added.
        """
        if not self.loaded:
            return []

        loop = asyncio.get_event_loop()

        try:
            query_vec = await loop.run_in_executor(None, self.model.encode, [query])
        except Exception as e:
            # Encoding can fail if model was unloaded or GPU OOM
            logger.error(f'❌ RAG encode failed for query={query!r}: {e}')
            return []

        try:
            query_vec = np.array(query_vec).astype('float32')
            faiss.normalize_L2(query_vec)
            scores, indices = await loop.run_in_executor(None, self.index.search, query_vec, top_k)
        except Exception as e:
            # FAISS search can fail if index is corrupted or dimension mismatch
            logger.error(f'❌ FAISS search failed: {e}')
            return []

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk['score'] = float(score)
                results.append(chunk)
        return results

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """Format search results as a context string for prompts.

        Args:
            results: List of chunk dicts returned by search().

        Returns:
            str: Formatted context block with source, section, relevance, and text.
        """
        if not results:
            return 'No relevant context found.'
        parts = ['=== PROJECT CONTEXT START ===\n']
        for i, r in enumerate(results, 1):
            # Use 'path' if available in metadata for better file identification
            source_id = r.get('path') or r.get('source', 'Unknown')
            parts.append(f"[{i}] Source: {source_id} | Section: {r['section']} | Relevance: {r['score']:.2f}")
            parts.append(r['text'])
            parts.append('')
        parts.append('=== PROJECT CONTEXT END ===')
        return '\n'.join(parts)

    async def get_status(self) -> Dict[str, Any]:
        """Return current RAG system status.

        Returns:
            dict: available, enabled, loaded, index_dir, model,
                  chunks_count, vectors_count.
        """
        return {
            'available':    RAG_AVAILABLE,
            'enabled':      config.rag_enabled,
            'loaded':       self.loaded,
            'index_dir':    str(self.index_dir),
            'model':        self.model_name,
            'chunks_count': len(self.chunks) if self.loaded else 0,
            'vectors_count': self.index.ntotal if self.loaded and self.index else 0,
        }

    async def reload_index(self, index_dir: Optional[str] = None) -> bool:
        """Reload RAG index, optionally from a new path.

        Args:
            index_dir: New index directory path. None = use config.dir_rag.

        Returns:
            bool: True if reload succeeded.
        """
        logger.info('Reloading RAG index…')
        self.loaded = False
        self.index  = None
        self.chunks = []
        self.model  = None

        if index_dir:
            self.index_dir = Path(index_dir)
            logger.info(f'Switching RAG index_dir to: {self.index_dir}')
        else:
            self.index_dir = Path(config.dir_rag)

        try:
            return await self.initialize()
        except Exception as e:
            # initialize() itself should not raise, but guard just in case
            logger.error(f'❌ Unexpected error during RAG reload: {e}')
            return False

    async def clear_index(self) -> bool:
        """Clear RAG index files and reset in-memory state.

        Returns:
            bool: True if all files removed successfully, False on OS error.
        """
        logger.info('Clearing RAG index…')
        self.loaded = False
        self.index  = None
        self.chunks = []
        self.model  = None

        removed = []
        for name in ('faiss.index', 'chunks.json', 'index_info.json'):
            p = self.index_dir / name
            try:
                if p.exists():
                    p.unlink()
                    removed.append(name)
                    logger.info(f'Removed: {p}')
            except OSError as e:
                # File locked by another process or permission denied
                logger.error(f'❌ Cannot remove {p}: {e}')
                return False

        logger.info(f'RAG index cleared. Removed: {removed or "nothing (already empty)"}')
        return True

    async def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Return all chunks with index metadata.

        Returns:
            List[Dict]: Each chunk dict extended with chunk_id and text_length.
                        Empty list if index not loaded.
        """
        if not self.loaded:
            return []
        try:
            return [
                {**chunk, 'chunk_id': i, 'text_length': len(chunk.get('text', ''))}
                for i, chunk in enumerate(self.chunks)
            ]
        except Exception as e:
            # Unexpected structure in chunks list
            logger.error(f'❌ Failed to build chunks list: {e}')
            return []


# Global singleton
rag_system = RAGSystem()
