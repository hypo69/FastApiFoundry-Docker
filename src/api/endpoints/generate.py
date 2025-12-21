# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Generate endpoint with detailed logging
# =============================================================================
# Описание:
#   Endpoint для генерации текста через Foundry API
#   Включает детальное логирование для отладки
#
# File: generate.py
# Project: FastAPI Foundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import logging
import aiohttp
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...core.config import settings
from ...rag.rag_system import rag_system

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    use_rag: Optional[bool] = False

class GenerateResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = None

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Генерация текста через Foundry API"""
    logger.info(f"Generate request: model={request.model}, prompt_len={len(request.prompt)}, use_rag={request.use_rag}")
    
    try:
        # RAG enhancement
        enhanced_prompt = request.prompt
        if request.use_rag:
            logger.info("Enhancing prompt with RAG")
            rag_results = await rag_system.search(request.prompt, top_k=3)
            if rag_results:
                context = "\n".join([r.get("text", "") for r in rag_results])
                enhanced_prompt = f"Context:\n{context}\n\nQuestion: {request.prompt}"
                logger.info(f"RAG context added: {len(context)} chars")
            else:
                logger.warning("RAG search returned no results")
        
        # Foundry API call
        foundry_url = f"{settings.foundry_base_url.rstrip('/')}/chat/completions"
        logger.info(f"Calling Foundry API: {foundry_url}")
        
        payload = {
            "model": request.model or "deepseek-r1-distill-qwen-7b-generic-cpu:3",
            "messages": [{"role": "user", "content": enhanced_prompt}],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        logger.info(f"Foundry payload: {payload}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(foundry_url, json=payload, timeout=60) as response:
                logger.info(f"Foundry response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Foundry response data keys: {list(data.keys())}")
                    
                    # Extract content from OpenAI-compatible response
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        tokens_used = data.get("usage", {}).get("total_tokens", 0)
                        
                        logger.info(f"Generated content: {len(content)} chars, {tokens_used} tokens")
                        
                        return GenerateResponse(
                            success=True,
                            content=content,
                            model=payload["model"],
                            tokens_used=tokens_used
                        )
                    else:
                        logger.error(f"Unexpected Foundry response format: {data}")
                        return GenerateResponse(
                            success=False,
                            error=f"Unexpected response format: {data}"
                        )
                else:
                    error_text = await response.text()
                    logger.error(f"Foundry API error {response.status}: {error_text}")
                    return GenerateResponse(
                        success=False,
                        error=f"Foundry API error {response.status}: {error_text}"
                    )
                    
    except asyncio.TimeoutError:
        logger.error("Foundry API timeout")
        return GenerateResponse(
            success=False,
            error="Foundry API timeout - model may be loading or busy"
        )
    except Exception as e:
        logger.error(f"Generate error: {e}", exc_info=True)
        return GenerateResponse(
            success=False,
            error=str(e)
        )