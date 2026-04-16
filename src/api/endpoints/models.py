# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Models Management Endpoints (Refactored)
# =============================================================================
# Description:
#   API endpoints for managing AI models
#   Getting the list of available and connected models via Foundry
#
# Examples:
#   >>> import requests
#   >>> response = requests.get('http://localhost:9696/api/v1/models')
#   >>> models = response.json()['models']
#   >>> print(f"Available models: {len(models)}")
#
# File: models.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.3
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: December 9, 2025
# =============================================================================

from fastapi import APIRouter
from ...models.foundry_client import foundry_client
from .llama_cpp import _get_server_url

router = APIRouter()


async def _get_llama_models() -> list:
    """Get models from a running llama.cpp server."""
    try:
        import aiohttp
        url = _get_server_url()
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{url}/v1/models", timeout=aiohttp.ClientTimeout(total=0.5)) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get("data", [])
    except Exception:
        pass
    return []


@router.get("/models")
async def get_models():
    """Get a list of all available models (Foundry + llama.cpp)"""
    try:
        models = []

        # Foundry models
        result = await foundry_client.list_available_models()
        if result["success"]:
            models.extend(result["models"])

        # llama.cpp models
        for m in await _get_llama_models():
            models.append({"id": m.get("id", "llama"), "object": "model", "provider": "llama.cpp"})

        return {"success": True, "models": models, "count": len(models)}
    except Exception as e:
        return {"success": False, "models": [], "error": str(e)}


@router.get("/models/connected")
async def get_connected_models():
    """Get a list of connected models (Foundry + llama.cpp)"""
    try:
        models = []

        # Foundry models
        result = await foundry_client.list_available_models()
        if result["success"]:
            for m in result["models"]:
                models.append({
                    "id": m["id"],
                    "name": m["id"],
                    "provider": "foundry",
                    "status": "connected",
                    "max_tokens": m.get("maxOutputTokens", 2048)
                })

        # llama.cpp models
        for m in await _get_llama_models():
            models.append({
                "id": m.get("id", "llama"),
                "name": m.get("id", "llama"),
                "provider": "llama.cpp",
                "status": "connected",
                "max_tokens": 4096
            })

        return {"success": True, "models": models, "count": len(models)}
    except Exception as e:
        return {"success": False, "models": [], "error": str(e)}
