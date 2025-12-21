# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Logger Module for FastAPI Foundry
# =============================================================================
# Описание:
#   Модуль логирования с поддержкой dev/prod режимов
#   Ведет файл логов и выводит сообщения в консоль
#
# File: __init__.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

class FastAPIFoundryLogger:
    """Логгер для FastAPI Foundry с поддержкой dev/prod режимов"""
    
    def __init__(self, name: str = "fastapi-foundry", mode: str = "dev"):
        self.name = name
        self.mode = mode.lower()
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Настройка логгера"""
        # Очистить существующие обработчики
        self.logger.handlers.clear()
        
        # Установить уровень логирования
        if self.mode == "prod":
            self.logger.setLevel(logging.INFO)
            console_level = logging.WARNING
            file_level = logging.INFO
        else:  # dev mode
            self.logger.setLevel(logging.DEBUG)
            console_level = logging.DEBUG
            file_level = logging.DEBUG
        
        # Создать директорию для логов
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Форматтеры
        if self.mode == "prod":
            # Продакшн: компактный формат
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-7s | %(message)s',
                datefmt='%H:%M:%S'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-15s | %(funcName)-15s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # Разработка: подробный формат
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-7s | %(name)-12s | %(funcName)-12s | %(message)s',
                datefmt='%H:%M:%S'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(lineno)-4d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Консольный обработчик
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Файловый обработчик с ротацией
        log_file = log_dir / f"{self.name}.log"
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(file_level)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
        
        # Обработчик ошибок (отдельный файл)
        error_file = log_dir / f"{self.name}-errors.log"
        try:
            error_handler = logging.handlers.RotatingFileHandler(
                error_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            self.logger.addHandler(error_handler)
        except Exception as e:
            print(f"Warning: Could not setup error logging: {e}")
    
    def debug(self, message: str, *args, **kwargs):
        """Отладочное сообщение"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Информационное сообщение"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Предупреждение"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, exc_info=None, **kwargs):
        """Ошибка"""
        self.logger.error(message, *args, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Критическая ошибка"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Ошибка с трассировкой стека"""
        self.logger.exception(message, *args, **kwargs)

# Определить режим из переменной окружения
MODE = os.getenv("FASTAPI_FOUNDRY_MODE", "dev").lower()

# Создать глобальный логгер
logger = FastAPIFoundryLogger("fastapi-foundry", MODE)

# Экспортировать методы для удобства
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
exception = logger.exception

def get_logger(name: str, mode: Optional[str] = None) -> FastAPIFoundryLogger:
    """Получить именованный логгер"""
    return FastAPIFoundryLogger(name, mode or MODE)

def set_mode(mode: str):
    """Изменить режим логирования"""
    global logger, MODE
    MODE = mode.lower()
    logger = FastAPIFoundryLogger("fastapi-foundry", MODE)