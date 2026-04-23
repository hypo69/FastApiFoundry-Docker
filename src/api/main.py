# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: FastAPI Foundry Main Entry Point
# =============================================================================
# Description:
#   Entry point for the FastAPI Foundry application
#
# File: main.py
# Project: AiStros
# Version: 0.6.1
# Module: FastApiFoundry
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

from fastapi import WebSocket, WebSocketDisconnect
from .app import create_app
from .endpoints import router as rag_router
from .docs_generator import export_to_markdown
from .websocket_manager import manager
from src.logger import logger
import os

# Application creation
app = create_app()

# Подключение роутера для RAG операций
# Inclusion of the router for RAG operations
app.include_router(rag_router)

# Запуск генерации документации при обновлении роутеров
# Initiation of documentation generation on router updates
if os.getenv("ENVIRONMENT") == "dev" or True:
    try:
        logger.info("Генерация актуальной API документации...")
        export_to_markdown(app)
    except Exception as e:
        logger.error(f"Сбой при генерации документации: {e}")

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    """! Эндпоинт для WebSocket соединений с распределением по комнатам.

    Args:
        websocket (WebSocket): Объект веб-сокета.
        room (str): Название комнаты для подписки (foundry, rag, system).
    """
    await manager.connect(websocket, room)
    try:
        while True:
            # Ожидание входящих данных для поддержания активности соединения
            # Waiting for incoming data to keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
    except Exception as e:
        logger.error(f"WebSocket error in room '{room}': {e}")
        manager.disconnect(websocket, room)

if __name__ == "__main__":
    import uvicorn
    from ..core.config import settings
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=settings.api_workers,
        log_level=settings.log_level.lower()
    )