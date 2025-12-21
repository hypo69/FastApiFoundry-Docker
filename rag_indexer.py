#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: RAG Indexer for FastAPI Foundry
# =============================================================================
# Описание:
#   Скрипт для создания FAISS индекса из документации
#   Поддерживает Markdown, HTML, TXT файлы
#
# File: rag_indexer.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import os
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

# Проверка зависимостей
try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print("❌ Требуются зависимости: pip install sentence-transformers faiss-cpu")
    exit(1)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGIndexer:
    """Индексатор документов для RAG системы"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.chunks = []
        self.embeddings = []
    
    def load_model(self):
        """Загрузить модель эмбеддингов"""
        logger.info(f"Загрузка модели: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info("✅ Модель загружена")
    
    def read_file(self, file_path: Path) -> str:
        """Прочитать содержимое файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Не удалось прочитать {file_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Разбить текст на чанки"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Найти ближайший разрыв предложения
            if end < len(text):
                # Ищем точку, восклицательный или вопросительный знак
                for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def process_markdown(self, content: str, source: str) -> List[Dict[str, Any]]:
        """Обработать Markdown файл"""
        chunks = []
        lines = content.split('\n')
        current_section = "Introduction"
        current_text = []
        
        for line in lines:
            line = line.strip()
            
            # Заголовки
            if line.startswith('#'):
                # Сохранить предыдущую секцию
                if current_text:
                    text = '\n'.join(current_text).strip()
                    if text:
                        for chunk in self.chunk_text(text):
                            chunks.append({
                                'source': source,
                                'section': current_section,
                                'text': chunk
                            })
                
                # Новая секция
                current_section = line.lstrip('#').strip()
                current_text = []
            else:
                if line:  # Пропускать пустые строки
                    current_text.append(line)
        
        # Последняя секция
        if current_text:
            text = '\n'.join(current_text).strip()
            if text:
                for chunk in self.chunk_text(text):
                    chunks.append({
                        'source': source,
                        'section': current_section,
                        'text': chunk
                    })
        
        return chunks
    
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Обработать один файл"""
        content = self.read_file(file_path)
        if not content:
            return []
        
        source = file_path.name
        
        if file_path.suffix.lower() == '.md':
            return self.process_markdown(content, source)
        else:
            # Для других файлов - простое разбиение на чанки
            chunks = []
            for chunk in self.chunk_text(content):
                chunks.append({
                    'source': source,
                    'section': 'Content',
                    'text': chunk
                })
            return chunks
    
    def index_directory(self, docs_dir: Path) -> None:
        """Индексировать директорию с документами"""
        logger.info(f"Индексация директории: {docs_dir}")
        
        # Поддерживаемые форматы
        supported_extensions = {'.md', '.txt', '.html', '.rst'}
        
        files_processed = 0
        for file_path in docs_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                logger.info(f"Обработка: {file_path}")
                chunks = self.process_file(file_path)
                self.chunks.extend(chunks)
                files_processed += 1
        
        logger.info(f"✅ Обработано файлов: {files_processed}")
        logger.info(f"✅ Создано чанков: {len(self.chunks)}")
    
    def create_embeddings(self) -> None:
        """Создать эмбеддинги для всех чанков"""
        if not self.chunks:
            logger.error("❌ Нет чанков для индексации")
            return
        
        logger.info("Создание эмбеддингов...")
        texts = [chunk['text'] for chunk in self.chunks]
        
        # Создать эмбеддинги батчами
        batch_size = 32
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch, show_progress_bar=True)
            embeddings.extend(batch_embeddings)
        
        self.embeddings = np.array(embeddings).astype('float32')
        logger.info(f"✅ Создано эмбеддингов: {self.embeddings.shape}")
    
    def build_faiss_index(self) -> faiss.Index:
        """Построить FAISS индекс"""
        logger.info("Построение FAISS индекса...")
        
        # Нормализовать эмбеддинги для косинусного сходства
        faiss.normalize_L2(self.embeddings)
        
        # Создать индекс
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner Product для нормализованных векторов = косинусное сходство
        
        # Добавить векторы
        index.add(self.embeddings)
        
        logger.info(f"✅ FAISS индекс создан: {index.ntotal} векторов")
        return index
    
    def save_index(self, output_dir: Path) -> None:
        """Сохранить индекс и метаданные"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Создать FAISS индекс
        index = self.build_faiss_index()
        
        # Сохранить FAISS индекс
        index_path = output_dir / "faiss.index"
        faiss.write_index(index, str(index_path))
        logger.info(f"✅ FAISS индекс сохранен: {index_path}")
        
        # Сохранить метаданные чанков
        chunks_path = output_dir / "chunks.json"
        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Метаданные сохранены: {chunks_path}")
        
        # Сохранить информацию об индексе
        info = {
            'model': self.model_name,
            'chunks_count': len(self.chunks),
            'dimension': self.embeddings.shape[1],
            'created_at': str(Path().cwd()),
            'version': '1.0.0'
        }
        
        info_path = output_dir / "index_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Информация об индексе: {info_path}")

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="RAG Indexer для FastAPI Foundry")
    
    parser.add_argument(
        '--docs-dir',
        type=str,
        required=True,
        help="Директория с документами для индексации"
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./rag_index',
        help="Директория для сохранения индекса (по умолчанию: ./rag_index)"
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='sentence-transformers/all-MiniLM-L6-v2',
        help="Модель для эмбеддингов"
    )
    
    args = parser.parse_args()
    
    # Проверить входную директорию
    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        logger.error(f"❌ Директория не найдена: {docs_dir}")
        return
    
    output_dir = Path(args.output_dir)
    
    # Создать индексатор
    indexer = RAGIndexer(model_name=args.model)
    
    try:
        # Загрузить модель
        indexer.load_model()
        
        # Индексировать документы
        indexer.index_directory(docs_dir)
        
        if not indexer.chunks:
            logger.error("❌ Не найдено документов для индексации")
            return
        
        # Создать эмбеддинги
        indexer.create_embeddings()
        
        # Сохранить индекс
        indexer.save_index(output_dir)
        
        logger.info("🎉 Индексация завершена успешно!")
        logger.info(f"📁 Индекс сохранен в: {output_dir}")
        logger.info(f"📊 Обработано чанков: {len(indexer.chunks)}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка индексации: {e}")
        raise

if __name__ == "__main__":
    main()