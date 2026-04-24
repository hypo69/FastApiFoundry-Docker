# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Foundry Utilities
# =============================================================================
# Description:
#   Shared utility functions for Foundry service interaction.
#
# File: src/utils/foundry_utils.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Changes in 0.6.0:
#   - MIT License update
#   - Unified headers and return type hints
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================

import os
import re
from pathlib import Path
import subprocess
from .process_utils import run_command
import logging
from typing import Optional

# Import requests only if available to avoid crashing during early startup checks
try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)

# Known ports often used by Foundry or local LLM proxies
_KNOWN_PORTS = [52632, 62171, 50477, 58130]

# Default cache location — reads from config.json (foundry_ai.models_dir) with env override
def _get_foundry_cache_dir() -> Path:
    env_override = os.getenv("FOUNDRY_CACHE_DIR", "")
    if env_override:
        return Path(env_override)
    try:
        from config_manager import config as _cfg
        return Path(_cfg.foundry_models_dir)
    except Exception:
        return Path(os.path.expanduser(r"~\.foundry\cache\models"))

FOUNDRY_CACHE_DIR = _get_foundry_cache_dir()

def test_foundry_port(port: int) -> bool:
    """Check whether Foundry is responding on the given port.

    Args:
        port: TCP port to probe.

    Returns:
        bool: True if Foundry API responds with HTTP 200.
    """
    if requests is None:
        return False
    try:
        logger.debug(f'Probing port {port}...')
        resp = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=2)
        if resp.status_code == 200:
            return True
        logger.debug(f'Port {port}: HTTP {resp.status_code}')
        return False
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False
    except Exception as e:
        logger.warning(f'⚠️ Unexpected error probing port {port}: {e}')
        return False

def find_foundry_port() -> Optional[int]:
    """Locate the port of a running Foundry service.
    Order: 1. FOUNDRY_DYNAMIC_PORT env, 2. foundry service status output, 3. known ports.

    Returns:
        int | None: Port number if found, None otherwise.
    """
    # 1. Check environment variable override
    raw_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
    if raw_port and raw_port.isdigit() and test_foundry_port(int(raw_port)):
        return int(raw_port)

    # 2. Parse port from `foundry service status` output
    # Output contains: "running on http://127.0.0.1:PORT/..."
    try:
        result = run_command(['foundry', 'service', 'status'], timeout=10)
        output = (result.stdout or '') + (result.stderr or '')
        match = re.search(r'http://127\.0\.0\.1:(\d+)', output)
        if match:
            port = int(match.group(1))
            if test_foundry_port(port):
                logger.info(f'✅ Foundry found via status command on port {port}')
                return port
    except Exception as e:
        logger.debug(f'foundry service status failed: {e}')

    # 3. Last resort: scan known default ports
    for p in _KNOWN_PORTS:
        if test_foundry_port(p):
            return p

    return None

def find_foundry_url() -> Optional[str]:
    """Return the base URL of a running Foundry service."""
    port = find_foundry_port()
    return f'http://localhost:{port}/v1/' if port else None

def model_id_to_cache_dir(model_id: str) -> str:
    """Convert a Foundry model ID to its filesystem directory name.
    
    Example: qwen2.5-0.5b-instruct-generic-cpu:4 -> qwen2.5-0.5b-instruct-generic-cpu-4
    """
    if ":" in model_id:
        name, version = model_id.rsplit(":", 1)
        return f"{name}-{version}"
    return model_id

def is_foundry_model_cached(model_id: str) -> bool:
    """Check whether a model exists in the local Foundry cache directory."""
    if not FOUNDRY_CACHE_DIR.exists():
        return False
    
    dir_name = model_id_to_cache_dir(model_id)
    model_dir = FOUNDRY_CACHE_DIR / dir_name
    
    if not model_dir.exists():
        return False
        
    # Check for version subfolder (vX)
    if ":" in model_id:
        version = model_id.rsplit(":", 1)[1]
        return (model_dir / f"v{version}").exists()
    
    return True