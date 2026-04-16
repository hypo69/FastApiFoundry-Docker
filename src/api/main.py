# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: FastAPI Foundry Main Entry Point
# =============================================================================
# Description:
#   Entry point for the FastAPI Foundry application
#
# File: main.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from .app import create_app

# Application creation
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