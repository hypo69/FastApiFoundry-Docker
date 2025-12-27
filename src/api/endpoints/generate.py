# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Generate Endpoint (Refactored)
# =============================================================================
# Описание:
#   Упрощенный endpoint для генерации текста через Foundry API
#
# File: generate.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from fastapi import APIRouter
from ...models.foundry_client import foundry_client

router = APIRouter()

@router.post("/generate")
async def generate_text(request: dict):
    """Генерация текста через Foundry API"""
    prompt = request.get("prompt", "")
    model = request.get("model")
    temperature = request.get("temperature", 0.7)
    max_tokens = request.get("max_tokens", 1000)
    
    if not prompt:
        return {
            "success": False,
            "error": "Prompt is required"
        }
    
    try:
        result = await foundry_client.generate_text(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if result["success"]:
            return {
                "success": True,
                "content": result["content"],
                "model": result["model"]
            }
        else:
            return {
                "success": False,
                "error": result["error"]
            }
                    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }