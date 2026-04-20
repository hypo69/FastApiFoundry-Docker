# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Unified Configuration Class (Refactored)
# =============================================================================
# Description:
#   Simplified Config class for the entire FastApiFoundry project.
#   Loads settings from config.json and provides a unified interface.
#
# File: config_manager.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Changes in 0.6.0:
#   - MIT License update
#   - Unified headers and return type hints
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Config:
    """Unified configuration class for the entire project."""

    _instance = None
    _config_data: Dict[str, Any] = {}
    _foundry_base_url = None  # Dynamically set in run.py

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from config.json.

        Raises:
            FileNotFoundError: If config.json does not exist.
            json.JSONDecodeError: If config.json contains invalid JSON.
            OSError: If config.json cannot be read (permissions, lock).
        """
        config_path = Path('config.json')

        if not config_path.is_file():
            # Config file missing — cannot start; re-raise so caller sees it
            raise FileNotFoundError(f'config.json not found at {config_path.absolute()}')

        _quiet = os.getenv('_UVICORN_CHILD') == '1'
        if not _quiet:
            print(f'Loading config from: {config_path.absolute()}')

        try:
            with open(config_path, encoding='utf-8') as f:
                self._config_data = json.load(f)
            if not _quiet:
                print(f'Config loaded with sections: {list(self._config_data.keys())}')
        except json.JSONDecodeError as e:
            # Malformed JSON — log and re-raise; server cannot start with broken config
            logger.error(f'❌ config.json contains invalid JSON: {e}')
            raise
        except OSError as e:
            logger.error(f'❌ Cannot read config.json: {e}')
            raise

    def reload_config(self) -> None:
        """Reload configuration from disk.

        Raises:
            Same as _load_config().
        """
        self._load_config()

    # ── FastAPI Server ────────────────────────────────────────────────────

    @property
    def api_host(self) -> str:
        return self._config_data.get('fastapi_server', {}).get('host') or '0.0.0.0'

    @property
    def api_port(self) -> int:
        return self._config_data.get('fastapi_server', {}).get('port') or 9696

    @property
    def api_workers(self) -> int:
        return self._config_data.get('fastapi_server', {}).get('workers') or 1

    @property
    def api_reload(self) -> bool:
        return self._config_data.get('fastapi_server', {}).get('reload', True)

    @property
    def api_log_level(self) -> str:
        return self._config_data.get('fastapi_server', {}).get('log_level', 'INFO')

    # ── Foundry AI ────────────────────────────────────────────────────────

    @property
    def foundry_base_url(self) -> str:
        return self._foundry_base_url

    @foundry_base_url.setter
    def foundry_base_url(self, value: str) -> None:
        self._foundry_base_url = value

    @property
    def foundry_default_model(self) -> str:
        return self._config_data.get('foundry_ai', {}).get('default_model', '')

    @property
    def foundry_auto_load_default(self) -> bool:
        return self._config_data.get('foundry_ai', {}).get('auto_load_default', False)

    @property
    def foundry_temperature(self) -> float:
        return self._config_data.get('foundry_ai', {}).get('temperature', 0.7)

    @property
    def foundry_max_tokens(self) -> int:
        return self._config_data.get('foundry_ai', {}).get('max_tokens', 2048)

    @property
    def foundry_top_p(self) -> float:
        return self._config_data.get('foundry_ai', {}).get('top_p', 0.9)

    @property
    def foundry_top_k(self) -> int:
        return self._config_data.get('foundry_ai', {}).get('top_k', 50)

    # ── Port Management ───────────────────────────────────────────────────

    @property
    def port_auto_find_free(self) -> bool:
        return self._config_data.get('port_management', {}).get('auto_find_free_port', False)

    @property
    def port_range_start(self) -> int:
        return self._config_data.get('port_management', {}).get('port_range_start', 8000)

    @property
    def port_range_end(self) -> int:
        return self._config_data.get('port_management', {}).get('port_range_end', 8100)

    # ── RAG System ────────────────────────────────────────────────────────

    @property
    def rag_enabled(self) -> bool:
        return self._config_data.get('rag_system', {}).get('enabled', False)

    @property
    def rag_index_dir(self) -> str:
        raw = self._config_data.get('rag_system', {}).get('index_dir') or '~/.rag'
        return str(Path(raw).expanduser())

    @property
    def rag_model(self) -> str:
        return self._config_data.get('rag_system', {}).get('model', 'sentence-transformers/all-MiniLM-L6-v2')

    @property
    def rag_chunk_size(self) -> int:
        return self._config_data.get('rag_system', {}).get('chunk_size', 1000)

    @property
    def rag_top_k(self) -> int:
        return self._config_data.get('rag_system', {}).get('top_k', 5)

    # ── Directories ───────────────────────────────────────────────────────

    @property
    def dir_models(self) -> str:
        raw = self._config_data.get('directories', {}).get('models') or '~/.models'
        return str(Path(raw).expanduser())

    @property
    def dir_rag(self) -> str:
        raw = self._config_data.get('directories', {}).get('rag') or '~/.rag'
        return str(Path(raw).expanduser())

    @property
    def dir_hf_models(self) -> str:
        raw = self._config_data.get('directories', {}).get('hf_models') or '~/.hf_models'
        return str(Path(raw).expanduser())

    # ── Helpers ───────────────────────────────────────────────────────────

    def get_section(self, section: str) -> Dict[str, Any]:
        """Return an entire configuration section.

        Args:
            section: Section name, e.g. 'fastapi_server', 'foundry_ai'.

        Returns:
            dict: Section content, or empty dict if section does not exist.
        """
        return self._config_data.get(section, {})

    def get_raw_config(self) -> Dict[str, Any]:
        """Return a copy of the entire configuration.

        Returns:
            dict: Full config.json content as a dict.
        """
        return self._config_data.copy()

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration in memory and persist to config.json.

        Args:
            new_config: New configuration dict to replace current config.

        Raises:
            OSError: If config.json cannot be written (disk full, permissions).
        """
        self._config_data = new_config
        config_path = Path('config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
        except OSError as e:
            # Disk write failed — config updated in memory but not persisted
            logger.error(f'❌ Failed to write config.json: {e}')
            raise


# Global configuration instance
config = Config()
