# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: RAG Index Creator
# =============================================================================
# Описание:
#   Создание FAISS индекса для RAG системы из документации проекта
#   Сканирует .md файлы и создает векторные эмбеддинги
#
# File: create_rag_index.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.3
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

# Проверка зависимостей
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    RAG_AVAILABLE = True
except ImportError:
    print("❌ RAG dependencies not installed!")
    print("Install: pip install sentence-transformers faiss-cpu")
    exit(1)

from config_manager import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGIndexCreator:
    """Создатель RAG индекса"""
    
    def __init__(self):
        self.model_name = config.rag_model
        self.chunk_size = config.rag_chunk_size
        self.index_dir = Path(config.rag_index_dir)
        self.model = None
        
    def load_model(self):
        """Загрузить модель эмбеддингов"""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
    def scan_documents(self) -> List[Dict[str, Any]]:
        """Сканировать документы проекта"""
        chunks = []
        
        # Сканируем документацию
        docs_dir = Path("docs")
        if docs_dir.exists():
            for md_file in docs_dir.rglob("*.md"):
                chunks.extend(self._process_file(md_file, "docs"))
        
        # Сканируем README файлы
        for readme in Path(".").glob("README*.md"):
            chunks.extend(self._process_file(readme, "root"))
            
        # Сканируем другие важные .md файлы
        for md_file in Path(".").glob("*.md"):
            if md_file.name not in ["README.md"]:
                chunks.extend(self._process_file(md_file, "root"))
        
        logger.info(f"Found {len(chunks)} text chunks")
        return chunks
    
    def _process_file(self, file_path: Path, source_type: str) -> List[Dict[str, Any]]:
        """Обработать один файл"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Разбить на чанки
            text_chunks = self._split_text(content)
            
            for i, chunk in enumerate(text_chunks):
                if len(chunk.strip()) > 50:  # Игнорируем слишком короткие чанки
                    chunks.append({
                        'text': chunk.strip(),
                        'source': str(file_path),
                        'source_type': source_type,
                        'section': f"chunk_{i}",
                        'file_name': file_path.name
                    })
                    
        except Exception as e:
            logger.warning(f"Error processing {file_path}: {e}")
            
        return chunks
    
    def _split_text(self, text: str) -> List[str]:
        """Разбить текст на чанки"""
        # Простое разбиение по параграфам и размеру
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def create_index(self, chunks: List[Dict[str, Any]]):
        """Создать FAISS индекс"""
        logger.info("Creating embeddings...")
        
        # Извлечь тексты
        texts = [chunk['text'] for chunk in chunks]
        
        # Создать эмбеддинги
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        
        # Нормализовать для косинусного сходства
        faiss.normalize_L2(embeddings)
        
        # Создать FAISS индекс
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner Product для нормализованных векторов
        index.add(embeddings)
        
        logger.info(f"Created FAISS index with {index.ntotal} vectors, dimension {dimension}")
        
        # Сохранить индекс и метаданные
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        index_path = self.index_dir / "faiss.index"
        meta_path = self.index_dir / "chunks.json"
        
        faiss.write_index(index, str(index_path))
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved index to {index_path}")
        logger.info(f"Saved metadata to {meta_path}")
        
        return index, chunks

def main():
    """Главная функция"""
    print("🚀 Creating RAG Index for FastAPI Foundry")
    print("=" * 50)
    
    creator = RAGIndexCreator()
    
    # Загрузить модель
    creator.load_model()
    
    # Сканировать документы
    chunks = creator.scan_documents()
    
    if not chunks:
        print("❌ No documents found to index!")
        return
    
    # Создать индекс
    index, chunks = creator.create_index(chunks)
    
    print(f"✅ RAG Index created successfully!")
    print(f"   📁 Index directory: {creator.index_dir}")
    print(f"   📊 Total chunks: {len(chunks)}")
    print(f"   🔍 Vector dimension: {index.d}")
    print(f"   📈 Total vectors: {index.ntotal}")
    
    # Тестовый поиск
    print("\n🧪 Testing search...")
    test_query = "FastAPI configuration"
    query_vec = creator.model.encode([test_query])
    query_vec = np.array(query_vec).astype('float32')
    faiss.normalize_L2(query_vec)
    
    scores, indices = index.search(query_vec, 3)
    
    print(f"Query: '{test_query}'")
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(chunks):
            chunk = chunks[idx]
            print(f"  📄 {chunk['file_name']} (score: {score:.3f})")
            print(f"     {chunk['text'][:100]}...")

if __name__ == "__main__":
    main()