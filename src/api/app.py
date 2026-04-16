# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: FastAPI Application Factory (Refactored)
# =============================================================================
# Description:
#   Simplified factory for creating the FastAPI application
#
# File: app.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ..models.foundry_client import foundry_client
from ..rag.rag_system import rag_system

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    print("Starting FastAPI Foundry...")
    
    rag_initialized = await rag_system.initialize()
    if rag_initialized:
        print("✅ RAG system initialized")
    else:
        print("⚠️ RAG system not initialized")

    # Автозагрузка модели по умолчанию
    from ..core.config import config as app_config
    if app_config.foundry_auto_load_default and app_config.foundry_default_model:
        import asyncio, subprocess
        model_id = app_config.foundry_default_model
        try:
            subprocess.Popen(
                ["foundry", "model", "load", model_id],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            print(f"✅ Auto-loading default model: {model_id}")
        except Exception as e:
            print(f"⚠️ Could not auto-load model {model_id}: {e}")
    
    yield
    
    print("Stopping FastAPI Foundry...")
    await foundry_client.close()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="FastAPI Foundry",
        description="REST API for local AI models via Foundry",
        version="0.4.1",
        lifespan=lifespan
    )
    
    # Static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware for request logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import asyncio
        import logging
        logger = logging.getLogger(__name__)

        start_time = time.time()
        try:
            response = await call_next(request)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(f"Middleware error: {exc}")
            raise
        process_time = time.time() - start_time
        log_message = f"{request.method} {request.url.path} -> {response.status_code} ({process_time:.3f}s)"
        logger.info(log_message)
        return response
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        print(f"Error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc)
            }
        )
    
    # Connect main routers
    from .endpoints import main, models, health, generate, foundry, config, logs, rag
    from .endpoints.chat_endpoints import router as chat_router
    from .endpoints.foundry_management import router as foundry_mgmt_router
    from .endpoints.foundry_models import router as foundry_models_router
    from .endpoints.hf_models import router as hf_router
    from .endpoints.llama_cpp import router as llama_router
    from .endpoints.mcp_powershell import router as mcp_ps_router
    from .endpoints.agent import router as agent_router
    from .endpoints.converter import router as converter_router
    from .endpoints.translation import router as translation_router

    app.include_router(main.router)
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(models.router, prefix="/api/v1")
    app.include_router(foundry.router, prefix="/api/v1")
    app.include_router(foundry_mgmt_router, prefix="/api/v1")
    app.include_router(foundry_models_router, prefix="/api/v1")
    app.include_router(generate.router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(rag.router, prefix="/api/v1")
    app.include_router(config.router, prefix="/api/v1")
    app.include_router(logs.router, prefix="/api/v1")
    app.include_router(hf_router, prefix="/api/v1")
    app.include_router(llama_router, prefix="/api/v1")
    app.include_router(mcp_ps_router, prefix="/api/v1")
    app.include_router(agent_router, prefix="/api/v1")
    app.include_router(converter_router, prefix="/api/v1")
    app.include_router(translation_router, prefix="/api/v1")
    
    return app