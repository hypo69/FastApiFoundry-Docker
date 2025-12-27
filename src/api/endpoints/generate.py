# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Простой Generate endpoint
# =============================================================================
# Описание:
#   Endpoint для генерации текста через Foundry API
#   Упрощенная версия без Pydantic
#
# File: generate.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import aiohttp
import asyncio
from fastapi import APIRouter
from ...models.foundry_client import foundry_client
# from ...rag.rag_system import rag_system

# Заглушка для RAG системы
class DummyRAGSystem:
    async def search(self, query, top_k=3):
        return []

rag_system = DummyRAGSystem()
from ..models import create_generate_response

router = APIRouter()

@router.post("/generate")
async def generate_text(request: dict):
    """Генерация текста через Foundry API"""
    prompt = request.get("prompt", "")
    model = request.get("model")
    temperature = request.get("temperature", 0.7)
    max_tokens = request.get("max_tokens", 1000)
    use_rag = request.get("use_rag", False)
    
    if not prompt:
        return create_generate_response(
            success=False,
            error="Prompt is required"
        )
    
    try:
        # RAG enhancement
        enhanced_prompt = prompt
        if use_rag:
            rag_results = await rag_system.search(prompt, top_k=3)
            if rag_results:
                context = "\n".join([r.get("text", "") for r in rag_results])
                enhanced_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
        
        # Генерация через Foundry клиент
        result = await foundry_client.generate_text(
            enhanced_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if result["success"]:
            return create_generate_response(
                success=True,
                content=result["content"],
                model=result["model"]
            )
        else:
            return create_generate_response(
                success=False,
                error=result["error"]
            )
                    
    except Exception as e:
        return create_generate_response(
            success=False,
            error=str(e)
        )