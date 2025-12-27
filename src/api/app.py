# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Application Factory (Refactored)
# =============================================================================
# Описание:
#   Упрощенная фабрика для создания FastAPI приложения
#
# File: app.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ..models.foundry_client import foundry_client
# from ..rag.rag_system import rag_system

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("Zapusk FastAPI Foundry...")
    
    # RAG система временно отключена из-за проблем с torch DLL
    print("RAG system disabled (torch DLL issue)")
    # rag_initialized = await rag_system.initialize()
    # if rag_initialized:
    #     print("✅ RAG система инициализирована")
    # else:
    #     print("⚠️ RAG система не инициализирована")
    
    yield
    
    print("Ostanovka FastAPI Foundry...")
    await foundry_client.close()

def create_app() -> FastAPI:
    """Создание и настройка FastAPI приложения"""
    
    app = FastAPI(
        title="FastAPI Foundry",
        description="REST API для локальных AI моделей через Foundry",
        version="0.4.1",
        lifespan=lifespan
    )
    
    # Статические файлы
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware для логирования запросов
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import logging
        logger = logging.getLogger(__name__)
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        log_message = f"{request.method} {request.url.path} -> {response.status_code} ({process_time:.3f}s)"
        logger.info(log_message)
        print(log_message)
        
        return response
    
    # Глобальный обработчик исключений
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        print(f"Error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Внутренняя ошибка сервера",
                "detail": str(exc)
            }
        )
    
    # Подключение основных роутеров
    from .endpoints import main, models, health, generate, foundry, config, logs
    from .endpoints.chat_endpoints import router as chat_router
    
    app.include_router(main.router)
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(models.router, prefix="/api/v1")
    app.include_router(foundry.router, prefix="/api/v1")
    app.include_router(generate.router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    # app.include_router(rag.router, prefix="/api/v1")
    app.include_router(config.router, prefix="/api/v1")
    app.include_router(logs.router, prefix="/api/v1")
    
    return app