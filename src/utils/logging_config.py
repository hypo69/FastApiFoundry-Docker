# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Logging Configuration for FastAPI Foundry
# =============================================================================
# Описание:
#   Настройка системы логирования с ротацией файлов и структурированными логами
#
# File: logging_config.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = "logs/fastapi-foundry.log"):
    """Настройка системы логирования"""
    
    # Создать директорию для логов
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    # Настройка форматирования
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Очистить существующие обработчики
    root_logger.handlers.clear()
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Файловый обработчик с ротацией
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Логгер для FastAPI
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    return root_logger