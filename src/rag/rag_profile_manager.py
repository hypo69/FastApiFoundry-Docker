# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: RAG Profile Manager
# =============================================================================
# Description:
#   Manages multiple named RAG indexes stored under ~/.rag/<profile>/
#   Each profile has its own FAISS index and metadata.
#
# File: src/rag/rag_profile_manager.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import logging
from pathlib import Path
from typing import Dict, List, Optional

from ..core.config import config

logger = logging.getLogger(__name__)


class RAGProfileManager:
    """Manages named RAG index profiles under the base rag directory."""

    def __init__(self) -> None:
        self._base: Path = Path(config.dir_rag)

    def list_profiles(self) -> List[Dict]:
        """Return all available RAG profiles with metadata.

        Returns:
            List[Dict]: Each item has keys: name, path, has_index, description.
        """
        profiles: List[Dict] = []
        if not self._base.exists():
            return profiles

        for d in sorted(self._base.iterdir()):
            if not d.is_dir():
                continue
            has_index = (d / "index.faiss").exists() or (d / "faiss.index").exists()
            desc_file = d / "description.txt"
            description = desc_file.read_text(encoding="utf-8").strip() if desc_file.exists() else ""
            profiles.append({
                "name": d.name,
                "path": str(d),
                "has_index": has_index,
                "description": description,
            })
        return profiles

    def get_profile_path(self, name: str) -> Optional[Path]:
        """Return path for a named profile, or None if it doesn't exist.

        Args:
            name (str): Profile name (directory name under ~/.rag/).

        Returns:
            Optional[Path]: Path to profile directory or None.
        """
        path = self._base / name
        return path if path.is_dir() else None

    def create_profile(self, name: str, description: str = "") -> Path:
        """Create a new profile directory.

        Args:
            name (str): Profile name.
            description (str): Optional description saved to description.txt.

        Returns:
            Path: Created profile directory.
        """
        path = self._base / name
        path.mkdir(parents=True, exist_ok=True)
        if description:
            (path / "description.txt").write_text(description, encoding="utf-8")
        logger.info(f"✅ RAG profile created: {path}")
        return path

    def delete_profile(self, name: str) -> bool:
        """Rename profile directory with ~ suffix (soft delete).

        Args:
            name (str): Profile name to delete.

        Returns:
            bool: True if renamed, False if not found.
        """
        path = self._base / name
        if not path.is_dir():
            return False
        target = self._base / f"{name}~"
        path.rename(target)
        logger.info(f"✅ RAG profile disabled: {target}")
        return True


rag_profile_manager = RAGProfileManager()
