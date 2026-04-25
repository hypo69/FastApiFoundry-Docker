# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: AI Assistant — Application Factory
# =============================================================================
# Description:
#   Orchestrator for local AI models (Foundry, HuggingFace, llama.cpp, Ollama).
#   Creates and configures the FastAPI application instance.
#   Manages lifespan (RAG init, Foundry auto-load, session cleanup).
#   Registers all API routers under /api/v1 prefix.
#   Mounts static files and configures CORS + request-logging middleware.
#   Model routing by prefix: hf:: / llama:: / ollama:: / (none=Foundry).
#
# File: app.py
# Project: AI Assistant (ai_assist)
# Version: 0.7.0
# Changes in 0.7.0:
#   - Project renamed to AI Assistant (ai_assist)
#   - Updated title, description, version to 0.7.0
#   - Concept: orchestrator for multiple local AI backends
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import time
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from ..models.foundry_client import foundry_client
from ..rag.rag_system import rag_system

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle.

    Startup: initializes RAG system, auto-loads default Foundry model.
    Shutdown: closes aiohttp session of foundry_client.

    Args:
        app: FastAPI application instance.
    """
    logger.info("Starting FastAPI Foundry...")
    
    rag_initialized = await rag_system.initialize()
    if rag_initialized:
        logger.info("✅ RAG system initialized")
    else:
        logger.warning("⚠️ RAG system not initialized")

    # Auto-load default Foundry model on startup.
    # NOTE: Foundry does NOT auto-load models from .foundry/cache/models at service start.
    # Models are loaded on-demand (first inference request) or explicitly via `foundry model load`.
    # We trigger an explicit load here so the model is warm before the first request.
    from ..core.config import config as app_config
    if app_config.foundry_auto_load_default and app_config.foundry_default_model:
        import subprocess
        model_id = app_config.foundry_default_model
        # Skip non-Foundry models (hf::, llama::, ollama:: are handled by their own backends)
        if any(str(model_id).startswith(p) for p in ("hf::", "llama::", "ollama::")):
            logger.info(f"Skip auto-loading non-Foundry model: {model_id}")
        else:
            try:
                subprocess.Popen(
                    ["foundry", "model", "load", model_id],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                logger.info(f"✅ Triggered Foundry model load: {model_id} (async, may take 10-60s)")
            except FileNotFoundError:
                logger.warning("⚠️ foundry CLI not found — skipping auto-load")
            except Exception as e:
                logger.warning(f"⚠️ Could not auto-load model {model_id}: {e}")

    print("\n" + "═" * 60)
    print("  ✅  FastAPI Foundry — startup complete")
    print("  🌐  http://localhost:9696")
    print("═" * 60 + "\n")

    yield
    
    logger.info("Stopping FastAPI Foundry...")
    await foundry_client.close()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Mounts static files, adds CORS and request-logging middleware,
    registers global exception handler, and includes all API routers.

    Returns:
        FastAPI: Configured application instance ready for uvicorn.
    """
    
    app = FastAPI(
        title="AI Assistant",
        description="Local AI model orchestrator (Foundry, HuggingFace, llama.cpp, Ollama) with RAG",
        version="0.7.0",
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
        logger.error(f"Error: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc)
            }
        )
    
    # Connect all routers
    from .endpoints import main, models, health, generate, foundry, config, logs, rag
    from .endpoints.ai_endpoints import router as ai_router
    from .endpoints.chat_endpoints import router as chat_router
    from .endpoints.translator import router as translator_router
    from .endpoints.foundry_management import router as foundry_mgmt_router
    from .endpoints.foundry_models import router as foundry_models_router
    from .endpoints.hf_models import router as hf_router
    from .endpoints.llama_cpp import router as llama_router
    from .endpoints.ollama import router as ollama_router
    from .endpoints.mcp_powershell import router as mcp_ps_router
    from .endpoints.agent import router as agent_router
    from .endpoints.converter import router as converter_router
    from .endpoints.system_stats import router as system_stats_router
    from .endpoints.support import router as support_router
    from .endpoints.helpdesk import router as helpdesk_router
    from .endpoints.mcp_agent_endpoints import router as mcp_agent_router
    from .endpoints.training import router as training_router
    from .endpoints.recommender import router as recommender_router

    app.include_router(main.router)
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(models.router, prefix="/api/v1")
    app.include_router(foundry.router, prefix="/api/v1")
    app.include_router(foundry_mgmt_router, prefix="/api/v1")
    app.include_router(foundry_models_router, prefix="/api/v1")
    app.include_router(generate.router, prefix="/api/v1")
    app.include_router(ai_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(translator_router, prefix="/api/v1")
    app.include_router(rag.router, prefix="/api/v1")
    app.include_router(config.router, prefix="/api/v1")
    app.include_router(logs.router, prefix="/api/v1")
    app.include_router(hf_router, prefix="/api/v1")
    app.include_router(llama_router, prefix="/api/v1")
    app.include_router(ollama_router, prefix="/api/v1")
    app.include_router(mcp_ps_router, prefix="/api/v1")
    app.include_router(agent_router, prefix="/api/v1")
    app.include_router(converter_router, prefix="/api/v1")
    app.include_router(system_stats_router, prefix="/api/v1")
    app.include_router(support_router, prefix="/api/v1")
    app.include_router(helpdesk_router, prefix="/api/v1")
    app.include_router(mcp_agent_router, prefix="/api/v1")
    app.include_router(training_router, prefix="/api/v1")
    app.include_router(recommender_router, prefix="/api/v1")
    
    return app