# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Foundry Finder Utility
# =============================================================================
# Description:
#   Utility for locating a running Foundry service.
#   Checks known ports and environment variables.
#
# File: foundry_finder.py
# Project: FastApiFoundry (Docker)
# Version: 0.5.5
# Changes in 0.5.5:
#   - Added try/except with logging in find_foundry_port and _test_foundry_port
#   - ValueError on bad FOUNDRY_DYNAMIC_PORT now logged instead of silently skipped
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import logging
import os

import requests

logger = logging.getLogger(__name__)

_KNOWN_PORTS = [62171, 50477, 58130]


def find_foundry_port() -> int | None:
    """Locate the port of a running Foundry service.

    Returns:
        int | None: Port number if found, None otherwise.
    """
    # Check environment variable first
    raw_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
    if raw_port:
        try:
            port = int(raw_port)
            if _test_foundry_port(port):
                logger.info(f'✅ Foundry found via env variable: {port}')
                return port
        except ValueError:
            # FOUNDRY_DYNAMIC_PORT is set but not a valid integer
            logger.warning(f'⚠️ FOUNDRY_DYNAMIC_PORT is not a valid integer: {raw_port!r}')

    logger.info(f'🔍 Scanning known ports: {_KNOWN_PORTS}')
    for port in _KNOWN_PORTS:
        if _test_foundry_port(port):
            logger.info(f'✅ Foundry found on port: {port}')
            return port

    logger.warning('❌ Foundry not found on any known port')
    return None


def _test_foundry_port(port: int) -> bool:
    """Check whether Foundry is responding on the given port.

    Args:
        port: TCP port to probe.

    Returns:
        bool: True if Foundry API responds with HTTP 200.
    """
    try:
        logger.debug(f'Probing port {port}…')
        resp = requests.get(f'http://127.0.0.1:{port}/v1/models', timeout=2)
        if resp.status_code == 200:
            return True
        logger.debug(f'Port {port}: HTTP {resp.status_code}')
        return False
    except requests.exceptions.ConnectionError:
        # Port is closed or service not running — expected during scan
        logger.debug(f'Port {port}: connection refused')
        return False
    except requests.exceptions.Timeout:
        # Service exists but too slow — treat as unavailable
        logger.debug(f'Port {port}: timeout')
        return False
    except Exception as e:
        # Unexpected error (e.g. SSL, socket error) — log and skip
        logger.warning(f'⚠️ Unexpected error probing port {port}: {e}')
        return False


def find_foundry_url() -> str | None:
    """Return the base URL of a running Foundry service.

    Returns:
        str | None: URL like 'http://localhost:50477/v1/' or None.
    """
    port = find_foundry_port()
    if port:
        return f'http://localhost:{port}/v1/'
    return None
