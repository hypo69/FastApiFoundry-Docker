# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: RAG Indexer for FastAPI Foundry
# =============================================================================
# Описание:
#   Создание FAISS индекса из документации проекта.
#   Поддерживает Markdown, HTML, TXT, RST файлы.
#
# Примеры:
#   >>> from src.rag.indexer import RAGIndexer
#   >>> indexer = RAGIndexer(); indexer.load_model()
#   >>> indexer.index_directory(Path("docs")); indexer.save_index(Path("rag_index"))
#
#   CLI:
#   python -m src.rag.indexer --docs-dir docs --output-dir rag_index
#
# File: indexer.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print("RAG dependencies not installed: pip install sentence-transformers faiss-cpu")
    raise

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'.md', '.txt', '.html', '.rst'}


class RAGIndexer:
    """Индексатор документов для RAG системы"""

    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        self.model_name = model_name
        self.model = None
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings = None

    def load_model(self) -> None:
        logger.info(f"Loading model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info("✅ Model loaded")

    def read_file(self, file_path: Path) -> str:
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"Cannot read {file_path}: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 50) -> List[str]:
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            if end < len(text):
                for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - overlap
        return chunks

    def process_markdown(self, content: str, source: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
        chunks = []
        current_section = "Introduction"
        current_text: List[str] = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                if current_text:
                    text = '\n'.join(current_text).strip()
                    if text:
                        for chunk in self.chunk_text(text, chunk_size, overlap):
                            chunks.append({'source': source, 'section': current_section, 'text': chunk})
                current_section = line.lstrip('#').strip()
                current_text = []
            elif line:
                current_text.append(line)

        if current_text:
            text = '\n'.join(current_text).strip()
            if text:
                for chunk in self.chunk_text(text, chunk_size, overlap):
                    chunks.append({'source': source, 'section': current_section, 'text': chunk})

        return chunks

    def process_file(self, file_path: Path, chunk_size: int = 1000, overlap: int = 50) -> List[Dict[str, Any]]:
        content = self.read_file(file_path)
        if not content:
            return []

        source = file_path.name
        if file_path.suffix.lower() == '.md':
            return self.process_markdown(content, source, chunk_size, overlap)

        return [
            {'source': source, 'section': 'Content', 'text': chunk}
            for chunk in self.chunk_text(content, chunk_size, overlap)
        ]

    def index_directory(self, docs_dir: Path, chunk_size: int = 1000, overlap: int = 50) -> None:
        logger.info(f"Indexing: {docs_dir}")
        files_processed = 0
        for file_path in docs_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                logger.info(f"Processing: {file_path}")
                self.chunks.extend(self.process_file(file_path, chunk_size, overlap))
                files_processed += 1
        logger.info(f"✅ Files: {files_processed}, chunks: {len(self.chunks)}")

    def create_embeddings(self) -> None:
        if not self.chunks:
            raise ValueError("No chunks to embed")

        logger.info("Creating embeddings...")
        texts = [c['text'] for c in self.chunks]
        batch_size = 32
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch_embeddings = self.model.encode(texts[i:i + batch_size], show_progress_bar=True)
            all_embeddings.extend(batch_embeddings)

        self.embeddings = np.array(all_embeddings).astype('float32')
        logger.info(f"✅ Embeddings shape: {self.embeddings.shape}")

    def save_index(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)

        faiss.normalize_L2(self.embeddings)
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(self.embeddings)
        logger.info(f"✅ FAISS index: {index.ntotal} vectors")

        faiss.write_index(index, str(output_dir / "faiss.index"))
        logger.info(f"✅ Saved: {output_dir / 'faiss.index'}")

        (output_dir / "chunks.json").write_text(
            json.dumps(self.chunks, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        logger.info(f"✅ Saved: {output_dir / 'chunks.json'}")

        (output_dir / "index_info.json").write_text(
            json.dumps({
                'model': self.model_name,
                'chunks_count': len(self.chunks),
                'dimension': dimension,
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0'
            }, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        logger.info(f"✅ Saved: {output_dir / 'index_info.json'}")


def main():
    parser = argparse.ArgumentParser(description="RAG Indexer for FastAPI Foundry")
    parser.add_argument('--docs-dir', type=str, required=True, help="Directory with documents")
    parser.add_argument('--output-dir', type=str, default='./rag_index', help="Output directory for index")
    parser.add_argument('--model', type=str, default='sentence-transformers/all-mpnet-base-v2')
    parser.add_argument('--chunk-size', type=int, default=1000)
    parser.add_argument('--overlap', type=int, default=50)
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        logger.error(f"Directory not found: {docs_dir}")
        return

    indexer = RAGIndexer(model_name=args.model)
    indexer.load_model()
    indexer.index_directory(docs_dir, chunk_size=args.chunk_size, overlap=args.overlap)

    if not indexer.chunks:
        logger.error("No documents found")
        return

    indexer.create_embeddings()
    indexer.save_index(Path(args.output_dir))
    logger.info(f"Done. Chunks: {len(indexer.chunks)}")


if __name__ == "__main__":
    main()
