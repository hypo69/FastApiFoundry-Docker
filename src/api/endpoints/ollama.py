# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Ollama Provider API Endpoints
# =============================================================================
# Description:
#   REST endpoints for managing Ollama local model server.
#   Ollama exposes an OpenAI-compatible API at /v1, so it can be used
#   as a drop-in provider alongside Foundry, HuggingFace, and llama.cpp.
#
# Examples:
#   GET  /api/v1/ollama/status
#   GET  /api/v1/ollama/models
#   POST /api/v1/ollama/models/pull    {"model": "qwen2.5:0.5b"}
#   POST /api/v1/ollama/models/delete  {"model": "qwen2.5:0.5b"}
#   POST /api/v1/ollama/generate       {"prompt": "Hello", "model": "qwen2.5:0.5b"}
#
# File: src/api/endpoints/ollama.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import logging
from fastapi import APIRouter, HTTPException

from ...models.ollama_client import ollama_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ollama", tags=["ollama"])


@router.get("/status")
async def ollama_status() -> dict:
    """! Ollama server status — running, version, URL."""
    return await ollama_client.get_status()


@router.get("/models")
async def ollama_list_models() -> dict:
    """! List locally available Ollama models."""
    return await ollama_client.list_models()


@router.post("/models/pull")
async def ollama_pull_model(request: dict) -> dict:
    """! Pull (download) a model from Ollama Hub.

    Body: {"model": "qwen2.5:0.5b"}

    Popular models: qwen2.5:0.5b, qwen2.5:1.5b, llama3.2:1b,
                    llama3.2:3b, mistral:7b, deepseek-r1:1.5b
    """
    model: str = request.get("model", "")
    if not model:
        raise HTTPException(status_code=400, detail="model is required")
    logger.info(f"📥 Ollama pull requested: {model}")
    return await ollama_client.pull_model(model)


@router.post("/models/delete")
async def ollama_delete_model(request: dict) -> dict:
    """! Delete a local Ollama model to free disk space.

    Body: {"model": "qwen2.5:0.5b"}
    """
    model: str = request.get("model", "")
    if not model:
        raise HTTPException(status_code=400, detail="model is required")
    return await ollama_client.delete_model(model)


@router.post("/generate")
async def ollama_generate(request: dict) -> dict:
    """! Generate text via Ollama.

    Body:
        model:       Model name (required)
        prompt:      Input text (required)
        max_tokens:  Max tokens to generate (default: 512)
        temperature: Sampling temperature (default: 0.7)
    """
    model: str = request.get("model", "")
    prompt: str = request.get("prompt", "")
    max_tokens: int = request.get("max_tokens", 512)
    temperature: float = request.get("temperature", 0.7)

    if not model:
        raise HTTPException(status_code=400, detail="model is required")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    return await ollama_client.generate(prompt, model, max_tokens, temperature)
