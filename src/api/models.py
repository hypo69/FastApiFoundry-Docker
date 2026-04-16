#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Simple Data Models for FastAPI Foundry
# =============================================================================
# Description:
#   Simple functions for creating standard API responses
#   No Pydantic - only dictionaries
#
# File: models.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: December 9, 2025
# =============================================================================

from datetime import datetime

def create_generate_response(success: bool, content: str = None, model: str = None, error: str = None) -> dict:
    """Create a text generation response"""
    return {
        "success": success,
        "content": content,
        "model": model,
        "error": error
    }

def create_health_response(status: str, foundry_status: str, rag_available: bool) -> dict:
    """Create a health check response"""
    return {
        "status": status,
        "foundry_status": foundry_status,
        "rag_available": rag_available,
        "timestamp": datetime.now().isoformat()
    }

def create_error_response(error: str, detail: str = None) -> dict:
    """Create an error response"""
    return {
        "error": error,
        "detail": detail
    }

def create_models_response(success: bool, models: list = None, error: str = None) -> dict:
    """Create a models list response"""
    return {
        "success": success,
        "models": models or [],
        "error": error
    }