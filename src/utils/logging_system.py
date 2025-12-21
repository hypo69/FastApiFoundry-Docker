# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Enhanced Logging System for FastAPI Foundry
# =============================================================================
# Описание:
#   Централизованная система логирования с поддержкой структурированных логов,
#   метрик производительности и автоматической ротации файлов
#
# File: logging_system.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import logging
import logging.handlers
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager

class StructuredLogger:
    """Структурированный логгер с поддержкой JSON и метрик"""
    
    def __init__(self, name: str, mode: str = "dev"):
        self.name = name
        self.mode = mode.lower()
        self.logger = logging.getLogger(name)
        self.metrics = {}
        self._setup_logger()
    
    def _setup_logger(self):
        """Настройка логгера"""
        self.logger.handlers.clear()
        
        # Уровни логирования
        if self.mode == "prod":
            self.logger.setLevel(logging.INFO)
            console_level = logging.WARNING
            file_level = logging.INFO
        else:
            self.logger.setLevel(logging.DEBUG)
            console_level = logging.DEBUG
            file_level = logging.DEBUG
        
        # Создать директории
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Форматтеры
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(name)-12s | %(message)s',
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
        
        # Основной файл логов
        main_log = log_dir / f"{self.name}.log"
        main_handler = logging.handlers.RotatingFileHandler(
            main_log, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        main_handler.setLevel(file_level)
        main_handler.setFormatter(file_formatter)
        self.logger.addHandler(main_handler)
        
        # Файл ошибок
        error_log = log_dir / f"{self.name}-errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # JSON лог для структурированных данных
        json_log = log_dir / f"{self.name}-structured.jsonl"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log, maxBytes=20*1024*1024, backupCount=3, encoding='utf-8'
        )
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(logging.Formatter('%(message)s'))
        self.json_handler = json_handler
        self.logger.addHandler(json_handler)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Структурированное логирование в JSON"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
            **kwargs
        }
        
        # Логировать в JSON файл
        json_record = logging.LogRecord(
            name=self.name,
            level=getattr(logging, level.upper()),
            pathname="",
            lineno=0,
            msg=json.dumps(log_entry, ensure_ascii=False),
            args=(),
            exc_info=None
        )
        self.json_handler.emit(json_record)
    
    def debug(self, message: str, **kwargs):
        """Отладочное сообщение"""
        self.logger.debug(message)
        if kwargs:
            self._log_structured("debug", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Информационное сообщение"""
        self.logger.info(message)
        if kwargs:
            self._log_structured("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Предупреждение"""
        self.logger.warning(message)
        self._log_structured("warning", message, **kwargs)
    
    def error(self, message: str, exc_info=None, **kwargs):
        """Ошибка"""
        self.logger.error(message, exc_info=exc_info)
        if exc_info:
            kwargs["exception"] = str(exc_info) if exc_info != True else "Exception occurred"
        self._log_structured("error", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Критическая ошибка"""
        self.logger.critical(message)
        self._log_structured("critical", message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Ошибка с трассировкой"""
        self.logger.exception(message)
        self._log_structured("error", message, exception_trace=True, **kwargs)
    
    @contextmanager
    def timer(self, operation: str, **kwargs):
        """Контекстный менеджер для измерения времени выполнения"""
        start_time = time.time()
        self.debug(f"Начало операции: {operation}", operation=operation, **kwargs)
        
        try:
            yield
            duration = time.time() - start_time
            self.info(f"Операция завершена: {operation} ({duration:.3f}s)", 
                     operation=operation, duration=duration, status="success", **kwargs)
        except Exception as e:
            duration = time.time() - start_time
            self.error(f"Ошибка операции: {operation} ({duration:.3f}s): {e}", 
                      operation=operation, duration=duration, status="error", 
                      error=str(e), **kwargs)
            raise
    
    def log_api_request(self, method: str, path: str, status_code: int, 
                       duration: float, **kwargs):
        """Логирование API запросов"""
        self.info(f"API {method} {path} -> {status_code} ({duration:.3f}s)",
                 api_method=method, api_path=path, status_code=status_code,
                 duration=duration, **kwargs)
    
    def log_model_operation(self, model_id: str, operation: str, 
                           status: str, duration: Optional[float] = None, **kwargs):
        """Логирование операций с моделями"""
        message = f"Model {operation}: {model_id} -> {status}"
        if duration:
            message += f" ({duration:.3f}s)"
        
        level = "info" if status == "success" else "error"
        getattr(self, level)(message, model_id=model_id, operation=operation,
                           status=status, duration=duration, **kwargs)

# Глобальные логгеры
_loggers: Dict[str, StructuredLogger] = {}
_mode = os.getenv("FASTAPI_FOUNDRY_MODE", "dev").lower()

def get_logger(name: str, mode: Optional[str] = None) -> StructuredLogger:
    """Получить именованный логгер"""
    effective_mode = mode or _mode
    logger_key = f"{name}:{effective_mode}"
    
    if logger_key not in _loggers:
        _loggers[logger_key] = StructuredLogger(name, effective_mode)
    
    return _loggers[logger_key]

def set_global_mode(mode: str):
    """Установить глобальный режим логирования"""
    global _mode
    _mode = mode.lower()
    _loggers.clear()  # Пересоздать логгеры с новым режимом

# Основной логгер приложения
logger = get_logger("fastapi-foundry")

# Экспорт методов для обратной совместимости
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
exception = logger.exception