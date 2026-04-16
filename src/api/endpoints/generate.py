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
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# =============================================================================

from fastapi import APIRouter
import aiohttp
from ...models.foundry_client import foundry_client
from ...models.hf_client import hf_client
from ...rag.rag_system import rag_system
from ...core.config import config as app_config

router = APIRouter()

@router.post("/generate")
async def generate_text(request: dict):
    """Генерация текста через Foundry API"""
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
            # Почему: форматирование контекста через `rag_system.format_context()` для сохранения структуры источников.
            context = rag_system.format_context(rag_results)
            prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

    # HF models are addressed as `hf::<model_id>` from UI.
    if model and str(model).startswith("hf::"):
        hf_model_id = str(model)[4:]
        try:
            hf_result = await hf_client.generate(
                prompt,
                hf_model_id,
                max_new_tokens=max_tokens,
                temperature=temperature,
            )
            if hf_result.get("success"):
                return {
                    "success": True,
                    "content": hf_result.get("content", ""),
                    "model": model,
                }
            return {
                "success": False,
                "error": hf_result.get("error") or hf_result.get("detail") or "HF generation failed",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # llama.cpp models are addressed as `llama::<gguf_path>` from UI.
    if model and str(model).startswith("llama::"):
        try:
            llama_model_path = str(model)[len("llama::"):]

            # Получаем текущий openai_url llama.cpp сервера из endpoint (/llama/status)
            from .llama_cpp import llama_status
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
            return {"success": True, "content": content, "model": model}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
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