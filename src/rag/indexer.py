# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: RAG Indexer for FastAPI Foundry
# =============================================================================
# Description:
#   Builds a FAISS index from project documentation.
#   Supports Markdown, HTML, TXT, RST files.
#
# Examples:
#   >>> from src.rag.indexer import RAGIndexer
#   >>> indexer = RAGIndexer(); indexer.load_model()
#   >>> indexer.index_directory(Path("docs")); indexer.save_index(Path("rag_index"))
#
#   CLI:
#   python -m src.rag.indexer --docs-dir docs --output-dir rag_index
#
# File: indexer.py
# Project: FastApiFoundry (Docker)
# Version: 0.5.5
# Changes in 0.5.5:
#   - Added try/except with logging in read_file, create_embeddings, save_index,
#     load_model, index_directory
#   - Each except block explains why the error can occur
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    print('RAG dependencies not installed: pip install sentence-transformers faiss-cpu')
    raise

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {'.md', '.txt', '.html', '.rst'}


class RAGIndexer:
    """Document indexer for the RAG system."""

    def __init__(self, model_name: str = 'sentence-transformers/all-mpnet-base-v2') -> None:
        self.model_name = model_name
        self.model = None
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings = None

    def load_model(self) -> None:
        """Load the sentence-transformer embedding model."""
        logger.info(f'Loading model: {self.model_name}')
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info('✅ Model loaded')
        except Exception as e:
            # Wrong model name, no internet, or incompatible transformers version
            logger.error(f'❌ Failed to load model "{self.model_name}": {e}')
            raise

    def read_file(self, file_path: Path) -> str:
        """Read a file and return its text content."""
        try:
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            # File is not UTF-8 encoded (binary or different encoding)
            logger.warning(f'⚠️ Encoding error reading {file_path}: {e}')
            return ''
        except OSError as e:
            # File locked, permission denied, or path disappeared during scan
            logger.warning(f'⚠️ Cannot read {file_path}: {e}')
            return ''

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]
        chunks, start = [], 0
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

    def process_markdown(self, content: str, source: str,
                         chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
        """Split Markdown content into section-aware chunks."""
        chunks: List[Dict[str, Any]] = []
        current_section = 'Introduction'
        current_lines: List[str] = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                if current_lines:
                    text = '\n'.join(current_lines).strip()
                    if text:
                        for c in self.chunk_text(text, chunk_size, overlap):
                            chunks.append({'source': source, 'section': current_section, 'text': c})
                current_section = line.lstrip('#').strip()
                current_lines = []
            elif line:
                current_lines.append(line)

        if current_lines:
            text = '\n'.join(current_lines).strip()
            if text:
                for c in self.chunk_text(text, chunk_size, overlap):
                    chunks.append({'source': source, 'section': current_section, 'text': c})
        return chunks

    def process_file(self, file_path: Path,
                     chunk_size: int = 1000, overlap: int = 50) -> List[Dict[str, Any]]:
        """Process a single file into chunks."""
        content = self.read_file(file_path)
        if not content:
            return []
        source = file_path.name
        if file_path.suffix.lower() == '.md':
            return self.process_markdown(content, source, chunk_size, overlap)
        return [
            {'source': source, 'section': 'Content', 'text': c}
            for c in self.chunk_text(content, chunk_size, overlap)
        ]

    def index_directory(self, docs_dir: Path,
                        chunk_size: int = 1000, overlap: int = 50) -> None:
        """Recursively index all supported files in a directory."""
        logger.info(f'Indexing: {docs_dir}')
        if not docs_dir.exists():
            logger.error(f'❌ Docs directory not found: {docs_dir}')
            return

        files_processed = 0
        try:
            for file_path in docs_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    logger.info(f'Processing: {file_path}')
                    self.chunks.extend(self.process_file(file_path, chunk_size, overlap))
                    files_processed += 1
        except Exception as e:
            # rglob can fail on permission-denied subdirectories
            logger.error(f'❌ Error scanning {docs_dir}: {e}')

        logger.info(f'✅ Files: {files_processed}, chunks: {len(self.chunks)}')

    def create_embeddings(self) -> None:
        """Encode all chunks into embedding vectors."""
        if not self.chunks:
            raise ValueError('No chunks to embed — run index_directory() first')

        logger.info('Creating embeddings…')
        texts = [c['text'] for c in self.chunks]
        batch_size = 32
        all_embeddings = []

        try:
            for i in range(0, len(texts), batch_size):
                batch = self.model.encode(texts[i:i + batch_size], show_progress_bar=True)
                all_embeddings.extend(batch)
        except Exception as e:
            # GPU OOM, model not loaded, or transformers internal error
            logger.error(f'❌ Embedding creation failed at batch starting at {i}: {e}')
            raise

        self.embeddings = np.array(all_embeddings).astype('float32')
        logger.info(f'✅ Embeddings shape: {self.embeddings.shape}')

    def save_index(self, output_dir: Path) -> None:
        """Build FAISS index and save all artifacts to output_dir."""
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            faiss.normalize_L2(self.embeddings)
            dimension = self.embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(self.embeddings)
            logger.info(f'✅ FAISS index: {index.ntotal} vectors')
        except Exception as e:
            # embeddings is None or wrong dtype
            logger.error(f'❌ Failed to build FAISS index: {e}')
            raise

        try:
            faiss.write_index(index, str(output_dir / 'faiss.index'))
            logger.info(f'✅ Saved: {output_dir / "faiss.index"}')
        except Exception as e:
            # Disk full or permission denied
            logger.error(f'❌ Failed to write faiss.index: {e}')
            raise

        try:
            (output_dir / 'chunks.json').write_text(
                json.dumps(self.chunks, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            (output_dir / 'index_info.json').write_text(
                json.dumps({
                    'model':        self.model_name,
                    'chunks_count': len(self.chunks),
                    'dimension':    dimension,
                    'created_at':   datetime.now().isoformat(),
                    'version':      '1.0.0',
                }, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            logger.info(f'✅ Saved metadata to {output_dir}')
        except OSError as e:
            # Disk full or permission denied when writing metadata
            logger.error(f'❌ Failed to write index metadata: {e}')
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description='RAG Indexer for FastAPI Foundry')
    parser.add_argument('--docs-dir',   required=True,  help='Directory with documents')
    parser.add_argument('--output-dir', default='./rag_index', help='Output directory')
    parser.add_argument('--model',      default='sentence-transformers/all-mpnet-base-v2')
    parser.add_argument('--chunk-size', type=int, default=1000)
    parser.add_argument('--overlap',    type=int, default=50)
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        logger.error(f'Directory not found: {docs_dir}')
        return

    indexer = RAGIndexer(model_name=args.model)
    indexer.load_model()
    indexer.index_directory(docs_dir, chunk_size=args.chunk_size, overlap=args.overlap)

    if not indexer.chunks:
        logger.error('No documents found — nothing to index')
        return

    indexer.create_embeddings()
    indexer.save_index(Path(args.output_dir))
    logger.info(f'Done. Chunks: {len(indexer.chunks)}')


if __name__ == '__main__':
    main()
