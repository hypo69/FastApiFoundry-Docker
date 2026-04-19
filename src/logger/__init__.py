# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Logging Subsystem for FastAPI Foundry
# =============================================================================
# Description:
#   Cross-platform logging with rotating file handlers and structured JSONL.
#   Console + plain rotating log + errors-only log + structured JSONL.
#
# Examples:
#   >>> from src.logger import logger
#   >>> logger.info("✅ Server started")
#   >>> logger.error("❌ Connection failed", exc_info=True)
#
# File: __init__.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import logging
import logging.handlers
import sys
from pathlib import Path


def _build_logger(name: str = 'fastapi-foundry') -> logging.Logger:
    """Build and configure the application logger.

    Args:
        name (str): Root logger name.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log = logging.getLogger(name)
    if log.handlers:
        return log

    log.setLevel(logging.DEBUG)
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    fmt_console = logging.Formatter(
        '%(asctime)s | %(levelname)-7s | %(name)-15s | %(message)s',
        datefmt='%H:%M:%S',
    )
    fmt_file = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(lineno)-4d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt_console)
    log.addHandler(ch)

    # Rotating plain-text file — all levels
    fh = logging.handlers.RotatingFileHandler(
        log_dir / f'{name}.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt_file)
    log.addHandler(fh)

    # Errors-only file
    eh = logging.handlers.RotatingFileHandler(
        log_dir / f'{name}-errors.log',
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8',
    )
    eh.setLevel(logging.ERROR)
    eh.setFormatter(fmt_file)
    log.addHandler(eh)

    # Structured JSONL — for log viewer and analysis
    jh = logging.handlers.RotatingFileHandler(
        log_dir / f'{name}-structured.jsonl',
        maxBytes=20 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8',
    )
    jh.setLevel(logging.INFO)
    jh.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(jh)

    return log


logger: logging.Logger = _build_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a child logger sharing the root handler chain.

    Args:
        name (str): Logger name (typically module __name__).

    Returns:
        logging.Logger: Configured logger instance.

    Example:
        >>> log = get_logger(__name__)
        >>> log.info("Module ready")
    """
    return logging.getLogger(name)
