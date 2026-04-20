# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Generate Endpoint
# =============================================================================
# Description:
#   API endpoint for text generation via Foundry, HuggingFace, or llama.cpp.
#
# File: generate.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Changes in 0.6.0:
#   - MIT License update
#   - Unified headers and return type hints
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================

from fastapi import APIRouter
import aiohttp
from ...models.foundry_client import foundry_client
from ...models.hf_client import hf_client
from ...rag.rag_system import rag_system
from ...core.config import config as app_config
from ...utils.text_utils import count_tokens_approx
from ...utils.api_utils import api_response_handler
from .llama_cpp import llama_status

router = APIRouter()

@router.post("/generate")
@api_response_handler
async def generate_text(request: dict) -> dict:
    """Генерация текста через Foundry, HuggingFace или llama.cpp.

    Args:
        request: JSON body с полями:
            prompt (str):       Входной текст (обязательно).
            model (str):        ID модели. Префикс 'hf::' → HF, 'llama::' → llama.cpp,
                                без префикса → Foundry.
            temperature (float): Температура генерации (default: 0.7).
            max_tokens (int):   Максимум токенов (default: 1000).
            use_rag (bool):     Добавить RAG-контекст к промпту (default: False).
            top_k (int):        Количество RAG-результатов (default: из config).

    Returns:
        dict: success, content, model, usage (prompt_tokens, completion_tokens,
              total_tokens) on success; success=False, error on failure.
    """
    prompt = request.get("prompt", "")
    model = request.get("model")
    temperature = request.get("temperature", 0.7)
    max_tokens = request.get("max_tokens", 1000)
    use_rag = bool(request.get("use_rag", False))
    top_k = request.get("top_k") or app_config.rag_top_k

    # Почему: согласование UI-флага `use_rag` с endpoint `/api/v1/generate`.
    # Контекст добавляется только при наличии загруженного FAISS индекса и включенном `rag_enabled`.
    if not prompt:
        return {
            "success": False,
            "error": "Prompt is required"
        }
    
    if use_rag:
        rag_results = await rag_system.search(prompt, top_k=top_k)
        if rag_results:
            context = rag_system.format_context(rag_results)
            prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

    # HuggingFace models
    if model and str(model).startswith("hf::"):
        try:
            hf_model_id = str(model)[4:]
            hf_result = await hf_client.generate_text(
                prompt, 
                model=hf_model_id, 
                temperature=temperature, 
                max_new_tokens=max_tokens
            )
            if hf_result.get("content"):
                content = hf_result.get("content", "")
                return {
                    "success": True,
                    "content": content,
                    "model": model,
                    "usage": {
                        "prompt_tokens": count_tokens_approx(prompt),
                        "completion_tokens": count_tokens_approx(content),
                        "total_tokens": count_tokens_approx(prompt) + count_tokens_approx(content),
                    },
                }
            return {"success": False, "error": hf_result.get("error") or hf_result.get("detail") or "HF generation failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # llama.cpp models
    if model and str(model).startswith("llama::"):
        try:
            st = await llama_status()
            openai_url = st.get("openai_url")
            if not openai_url:
                return {"success": False, "error": "llama.cpp is not running (no openai_url)"}

            url = f"{openai_url.rstrip('/')}/chat/completions"
            payload = {
                "model": "llama",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        err_text = await resp.text()
                        return {"success": False, "error": f"llama.cpp HTTP {resp.status}: {err_text}"}
                    data = await resp.json()

            choices = data.get("choices") or []
            if not choices:
                return {"success": False, "error": "llama.cpp returned no choices"}

            content = choices[0].get("message", {}).get("content", "")
            # Use real usage from llama.cpp if available, else estimate
            raw_usage = data.get("usage") or {}
            usage = {
                "prompt_tokens":     raw_usage.get("prompt_tokens")     or count_tokens_approx(prompt),
                "completion_tokens": raw_usage.get("completion_tokens") or count_tokens_approx(content),
                "total_tokens":      raw_usage.get("total_tokens")      or count_tokens_approx(prompt) + count_tokens_approx(content),
            }
            return {"success": True, "content": content, "model": model, "usage": usage}
        except Exception as e:
            return {"success": False, "error": str(e)}

    try:
        result = await foundry_client.generate_text(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        if "content" in result:
            content = result["content"]
            raw_usage = result.get("usage") or {}
            usage = {
                "prompt_tokens":     raw_usage.get("prompt_tokens")     or count_tokens_approx(prompt),
                "completion_tokens": raw_usage.get("completion_tokens") or count_tokens_approx(content),
                "total_tokens":      raw_usage.get("total_tokens")      or count_tokens_approx(prompt) + count_tokens_approx(content),
            }
            return {
                "success": True,
                "content": content,
                "model": result["model"],
                "usage": usage,
            }
        return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}