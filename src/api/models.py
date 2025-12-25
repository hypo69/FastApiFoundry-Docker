#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Модели данных FastAPI Foundry
# =============================================================================
# Описание:
#   Упрощенные Pydantic модели для API
#
# File: models.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class GenerateRequest(BaseModel):
    """Запрос на генерацию текста"""
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    use_rag: bool = True

class GenerateResponse(BaseModel):
    """Ответ на генерацию текста"""
    success: bool
    content: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Ответ проверки здоровья"""
    status: str
    foundry_status: str
    rag_available: bool
    timestamp: datetime = datetime.now()

class ErrorResponse(BaseModel):
    """Стандартный ответ с ошибкой"""
    error: str
    detail: Optional[str] = None

class ModelInfo(BaseModel):
    """Информация о модели"""
    id: str
    name: Optional[str] = None
    status: Optional[str] = None

class ModelsResponse(BaseModel):
    """Ответ со списком моделей"""
    success: bool
    models: List[ModelInfo] = []
    error: Optional[str] = None