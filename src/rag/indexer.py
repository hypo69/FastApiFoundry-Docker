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
# Version: 0.6.4
# Changes in 0.6.4:
#   - MIT License update
#   - Unified headers and versioning to 0.6.4
#   - Explicit return type hints for all methods
#   - Added checksum, relative path, and mtime to chunk metadata
#   - Added incremental indexing support via checksum comparison
#   - Enhanced create_embeddings to reuse vectors from existing FAISS index
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================
import faiss
import argparse
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        self.docs_root: Optional[Path] = None
        self.has_changes: bool = False

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

    def _read_file(self, file_path: Path) -> str:
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

    def _calculate_checksum(self, content: str) -> str:
        """Calculate MD5 checksum of string content.

        Returns:
            str: Hex digest of the MD5 hash.
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()

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

    def process_markdown(self, content: str, metadata: Dict[str, Any], chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
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
                            chunks.append({**metadata, 'section': current_section, 'text': c, 'char_count': len(c)})
                current_section = line.lstrip('#').strip()
                current_lines = []
            elif line:
                current_lines.append(line)

        if current_lines:
            text = '\n'.join(current_lines).strip()
            if text:
                for c in self.chunk_text(text, chunk_size, overlap):
                    chunks.append({**metadata, 'section': current_section, 'text': c, 'char_count': len(c)})
        return chunks

    def process_file(self, file_path: Path, # type: ignore
                     chunk_size: int = 1000, overlap: int = 50,
                     content: Optional[str] = None) -> List[Dict[str, Any]]:
        """Process a single file into chunks."""
        if content is None:
            content = self._read_file(file_path)
            
        if not content:
            return []

        # Relative path is better for citations than just filename
        rel_path = str(file_path.relative_to(self.docs_root)) if self.docs_root else file_path.name

        metadata = {
            'source': file_path.name,
            'path': rel_path,
            'checksum': self._calculate_checksum(content),
            'mtime': file_path.stat().st_mtime if file_path.exists() else 0
        }

        if file_path.suffix.lower() == '.md':
            return self.process_markdown(content, metadata, chunk_size, overlap)

        return [
            {**metadata, 'section': 'Content', 'text': c, 'char_count': len(c)}
            for c in self.chunk_text(content, chunk_size, overlap)
        ]

    def index_directory(self, docs_dir: Path,
                        chunk_size: int = 1000, overlap: int = 50,
                        existing_chunks: Optional[List[Dict[str, Any]]] = None) -> None:
        """Recursively index all supported files in a directory."""
        logger.info(f'Indexing: {docs_dir}')
        if not docs_dir.exists():
            logger.error(f'❌ Docs directory not found: {docs_dir}')
            return

        self.docs_root = docs_dir
        self.has_changes = False
        
        # Group existing chunks by path for quick comparison
        existing_map: Dict[str, List[Dict[str, Any]]] = {}
        if existing_chunks:
            for i, c in enumerate(existing_chunks):
                path = c.get('path')
                if path:
                    chunk_with_idx = c.copy()
                    chunk_with_idx['_old_idx'] = i
                    existing_map.setdefault(path, []).append(chunk_with_idx)

        files_processed = 0
        found_paths = set()

        try:
            for file_path in docs_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    rel_path = str(file_path.relative_to(self.docs_root))
                    found_paths.add(rel_path)
                    
                    content = self._read_file(file_path)
                    if not content:
                        continue
                        
                    checksum = self._calculate_checksum(content)
                    
                    # Check if file changed
                    if rel_path in existing_map and existing_map[rel_path][0].get('checksum') == checksum:
                        self.chunks.extend(existing_map[rel_path])
                    else:
                        logger.info(f'Processing: {file_path}')
                        self.chunks.extend(self.process_file(file_path, chunk_size, overlap, content=content))
                        self.has_changes = True
                        files_processed += 1
        except Exception as e:
            logger.error(f'❌ Error scanning {docs_dir}: {e}')

        # Check for deleted files
        if existing_map and not self.has_changes:
            if any(p not in found_paths for p in existing_map):
                self.has_changes = True

        logger.info(f'✅ Files: {files_processed}, chunks: {len(self.chunks)}')

    def create_embeddings(self, existing_index: Optional[Any] = None) -> None:
        """Encode all chunks into embedding vectors, reusing existing ones if possible.

        Args:
            existing_index: Optional FAISS index to reconstruct vectors from for unchanged chunks.
        """
        if not self.chunks:
            raise ValueError('No chunks to embed — run index_directory() first')

        logger.info('Creating embeddings…')

        dimension = self.model.get_sentence_embedding_dimension()
        final_embeddings = np.zeros((len(self.chunks), dimension), dtype='float32')

        to_encode_indices = []
        to_encode_texts = []
        reused_count = 0

        for i, chunk in enumerate(self.chunks):
            old_idx = chunk.get('_old_idx')
            reused = False

            if existing_index is not None and old_idx is not None and old_idx < existing_index.ntotal:
                if existing_index.d == dimension:
                    try:
                        final_embeddings[i] = existing_index.reconstruct(old_idx)
                        reused_count += 1
                        reused = True
                    except Exception:
                        pass  # Fallback to encoding

            if not reused:
                to_encode_indices.append(i)
                to_encode_texts.append(chunk['text'])

        if to_encode_texts:
            logger.info(f"Encoding {len(to_encode_texts)} new/changed chunks...")
            batch_size = 32
            try:
                for start_idx in range(0, len(to_encode_texts), batch_size):
                    end_idx = start_idx + batch_size
                    batch_texts = to_encode_texts[start_idx:end_idx]
                    batch_embeddings = self.model.encode(batch_texts, show_progress_bar=True)

                    for j, emb in enumerate(batch_embeddings):
                        final_embeddings[to_encode_indices[start_idx + j]] = emb
            except Exception as e:
                logger.error(f'❌ Embedding creation failed: {e}')
                raise

        # Cleanup temporary metadata to avoid saving it to chunks.json
        for chunk in self.chunks:
            chunk.pop('_old_idx', None)

        self.embeddings = final_embeddings
        logger.info(f'✅ Embeddings shape: {self.embeddings.shape} (Reused: {reused_count})')

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


def main() -> None: # type: ignore
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
