# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Main Endpoints (Refactored)
# =============================================================================
# Description:
#   Main endpoints for root routes
#
# File: main.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/")
async def root():
    """FastAPI Foundry Control Panel"""
    return FileResponse('static/index.html')

@router.get("/api")
async def api_info():
    """API Information"""
    return {
        "service": "FastAPI Foundry",
        "version": "0.4.1",
        "description": "REST API for local AI models",
        "endpoints": {
            "generate": "/api/v1/generate",
            "models": "/api/v1/models",
            "health": "/api/v1/health",
            "chat": "/api/v1/chat"
        },
        "docs": "/docs",
        "web_interface": "/",
        "timestamp": datetime.now().isoformat()
    }
