# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Generate Endpoint
# =============================================================================
# Description:
#   Text generation via Foundry, HuggingFace or llama.cpp.
#   Optionally translates request to English and response back to source lang.
#
# File: generate.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Changes in 0.6.0:
#   - Added auto-translation middleware (translate_enabled flag in config.json)
#   - source_lang request field; response translated back to user language
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

from fastapi import APIRouter
import aiohttp
from ...models.foundry_client import foundry_client
from ...models.hf_client import hf_client
from ...rag.rag_system import rag_system
from ...core.config import config as app_config
from ...utils.text_utils import count_tokens_approx
from ...utils.api_utils import api_response_handler
from ...utils.translator import translator
from .llama_cpp import llama_status

router = APIRouter()


async def _translate_in(prompt: str, source_lang: str) -> tuple[str, str]:
    """Translate prompt to English. Returns (translated_prompt, detected_source_lang)."""
    tr = await translator.translate_for_model(prompt, source_lang=source_lang)
    if tr["success"] and tr["was_translated"]:
        return tr["translated"], tr["source_lang"]
    return prompt, source_lang


async def _translate_out(content: str, target_lang: str) -> str:
    """Translate model response back to user language."""
    if not target_lang or target_lang == "en":
        return content
    tr = await translator.translate_response(content, target_lang)
    return tr["translated"] if tr["success"] else content


@router.post("/generate")
@api_response_handler
async def generate_text(request: dict) -> dict:
    """Generate text via Foundry, HuggingFace or llama.cpp.

    Args:
        request: JSON body with fields:
            prompt (str):        Input text (required).
            model (str):         Model ID. Prefix 'hf::' → HF, 'llama::' → llama.cpp,
                                 no prefix → Foundry.
            temperature (float): Generation temperature (default: 0.7).
            max_tokens (int):    Max tokens (default: 1000).
            use_rag (bool):      Inject RAG context (default: False).
            top_k (int):         RAG results count (default: from config).
            source_lang (str):   User language ISO 639-1 or 'auto' (default: 'auto').

    Returns:
        dict: success, content, model, usage, source_lang on success;
              success=False, error on failure.
    """
    prompt = request.get("prompt", "")
    model = request.get("model")
    temperature = request.get("temperature", 0.7)
    max_tokens = request.get("max_tokens", 1000)
    use_rag = bool(request.get("use_rag", False))
    top_k = request.get("top_k") or app_config.rag_top_k
    source_lang = request.get("source_lang", "auto")

    if not prompt:
        return {"success": False, "error": "Prompt is required"}

    # Translate prompt to English before sending to model
    translate_enabled = app_config.get_raw_config().get("translator", {}).get("enabled", False)
    if translate_enabled:
        prompt, source_lang = await _translate_in(prompt, source_lang)

    if use_rag:
        rag_results = await rag_system.search(prompt, top_k=top_k)
        if rag_results:
            context = rag_system.format_context(rag_results)
            prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

    # HuggingFace models
    if model and str(model).startswith("hf::"):
        try:
            hf_result = await hf_client.generate_text(
                prompt, model=str(model)[4:], temperature=temperature, max_new_tokens=max_tokens
            )
            if not hf_result.get("content"):
                return {"success": False, "error": hf_result.get("error") or "HF generation error"}
            content = hf_result["content"]
            if translate_enabled:
                content = await _translate_out(content, source_lang)
            return {
                "success": True, "content": content, "model": model, "source_lang": source_lang,
                "usage": {
                    "prompt_tokens": count_tokens_approx(prompt),
                    "completion_tokens": count_tokens_approx(content),
                    "total_tokens": count_tokens_approx(prompt) + count_tokens_approx(content),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # llama.cpp models
    if model and str(model).startswith("llama::"):
        try:
            st = await llama_status()
            openai_url = st.get("openai_url")
            if not openai_url:
                return {"success": False, "error": "llama.cpp is not running"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{openai_url.rstrip('/')}/chat/completions",
                    json={"model": "llama", "messages": [{"role": "user", "content": prompt}],
                          "temperature": temperature, "max_tokens": max_tokens, "stream": False},
                ) as resp:
                    if resp.status != 200:
                        return {"success": False, "error": f"llama.cpp HTTP {resp.status}: {await resp.text()}"}
                    data = await resp.json()
            choices = data.get("choices") or []
            if not choices:
                return {"success": False, "error": "llama.cpp returned no choices"}
            content = choices[0].get("message", {}).get("content", "")
            if translate_enabled:
                content = await _translate_out(content, source_lang)
            raw_usage = data.get("usage") or {}
            return {
                "success": True, "content": content, "model": model, "source_lang": source_lang,
                "usage": {
                    "prompt_tokens":     raw_usage.get("prompt_tokens")     or count_tokens_approx(prompt),
                    "completion_tokens": raw_usage.get("completion_tokens") or count_tokens_approx(content),
                    "total_tokens":      raw_usage.get("total_tokens")      or count_tokens_approx(prompt) + count_tokens_approx(content),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Default: Foundry API
    try:
        result = await foundry_client.generate_text(
            prompt, model=model, temperature=temperature, max_tokens=max_tokens
        )
        if "content" not in result:
            return {"success": False, "error": result.get("error", "Foundry error")}
        content = result["content"]
        if translate_enabled:
            content = await _translate_out(content, source_lang)
        raw_usage = result.get("usage") or {}
        return {
            "success": True, "content": content, "model": result["model"], "source_lang": source_lang,
            "usage": {
                "prompt_tokens":     raw_usage.get("prompt_tokens")     or count_tokens_approx(prompt),
                "completion_tokens": raw_usage.get("completion_tokens") or count_tokens_approx(content),
                "total_tokens":      raw_usage.get("total_tokens")      or count_tokens_approx(prompt) + count_tokens_approx(content),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
