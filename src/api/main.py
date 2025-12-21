# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry Main Entry Point
# =============================================================================
# Описание:
#   Точка входа для FastAPI Foundry приложения
#
# File: main.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from .app import create_app

# Создание приложения
app = create_app()

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