# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Application Factory
# =============================================================================
# Описание:
#   Фабрика для создания FastAPI приложения с настройками и middleware
#
# File: app.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import logging
import json
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ..models.foundry_client import foundry_client
# from ..rag.rag_system import rag_system

# Заглушка для RAG системы
class DummyRAGSystem:
    async def initialize(self):
        pass
    async def search(self, query, top_k=3):
        return []

rag_system = DummyRAGSystem()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запуск
    logger.info("Запуск FastAPI Foundry...")
    
    # Инициализация RAG системы (отключена)
    # await rag_system.initialize()
    
    # Проверка Foundry сервера (отключена)
    # health = await foundry_client.health_check()
    # logger.info(f"Foundry health: {health}")
    
    yield
    
    # Остановка
    logger.info("Остановка FastAPI Foundry...")
    # await foundry_client.close()

def create_app() -> FastAPI:
    """Создание и настройка FastAPI приложения"""
    
    app = FastAPI(
        title="FastAPI Foundry",
        description="REST API для локальных AI моделей через Foundry с поддержкой RAG",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Подключение статических файлов
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Обработчики исключений
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Глобальный обработчик исключений"""
        logger.error(f"Необработанное исключение: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Внутренняя ошибка сервера",
                "detail": str(exc)
            }
        )
    
    # Подключение роутеров
    from .endpoints import main, models, rag, foundry, health, generate, config
    from .endpoints.ai_endpoints import router as ai_router
    from .endpoints.logging_endpoints import router as logging_router
    from .endpoints.examples_endpoints import router as examples_router
    from .endpoints.foundry_management import router as foundry_management_router
    from .endpoints.foundry_models import router as foundry_models_router
    from .endpoints.chat_endpoints import router as chat_router
    
    app.include_router(main.router)
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(models.router, prefix="/api/v1")
    app.include_router(rag.router, prefix="/api/v1")
    app.include_router(foundry.router, prefix="/api/v1")
    app.include_router(foundry_management_router, prefix="/api/v1")
    app.include_router(foundry_models_router, prefix="/api/v1")  # Новые Foundry models endpoints
    app.include_router(ai_router, prefix="/api/v1")  # Новые AI endpoints
    app.include_router(logging_router)
    app.include_router(examples_router)
    app.include_router(generate.router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")  # Chat endpoints
    app.include_router(config.router, prefix="/api/v1")  # Config endpoint
    
    return app