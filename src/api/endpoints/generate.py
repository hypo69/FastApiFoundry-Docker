# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Generate Endpoint
# =============================================================================
# Description:
#   Text generation via Foundry, HuggingFace or llama.cpp.
#   Per-request translation: user prompt → English → model → user language.
#   Fields: translate_model_dialog (bool, default true), user_language (str|null).
#   When user_language is null, language is auto-detected from the prompt.
#
# File: generate.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
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


async def _resolve_user_lang(prompt: str, user_language: str | None) -> str:
    """Return user language code. Auto-detects from prompt when user_language is None.

    Args:
        prompt: User input text used for detection.
        user_language: Explicit ISO 639-1 code or None for auto-detect.

    Returns:
        str: ISO 639-1 language code, e.g. 'ru', 'en', 'he'.
    """
    if user_language:
        return user_language.lower().strip()
    det = await translator.detect_language(prompt)
    return det.get("language") or "en"


async def _translate_in(prompt: str, user_lang: str) -> str:
    """Translate prompt to English. Returns original if already English."""
    if user_lang == "en":
        return prompt
    tr = await translator.translate_for_model(prompt, source_lang=user_lang)
    return tr["translated"] if tr["success"] and tr["was_translated"] else prompt


async def _translate_out(content: str, user_lang: str) -> str:
    """Translate model response back to user language."""
    if not user_lang or user_lang == "en":
        return content
    tr = await translator.translate_response(content, user_lang)
    return tr["translated"] if tr["success"] else content


def _should_translate(request: dict) -> bool:
    """Determine whether translation is active for this request.

    Per-request field translate_model_dialog takes priority over global config.
    Default: True (translate when translator provider is configured).
    """
    per_request = request.get("translate_model_dialog")
    if per_request is not None:
        return bool(per_request)
    # Fall back to global config flag
    return app_config.get_raw_config().get("translator", {}).get("enabled", False)


@router.post("/generate")
@api_response_handler
async def generate_text(request: dict) -> dict:
    """Generate text via Foundry, HuggingFace or llama.cpp.

    Args:
        request: JSON body with fields:
            prompt (str):                 Input text (required).
            model (str):                  Model ID. Prefix 'hf::' → HF, 'llama::' → llama.cpp,
                                          no prefix → Foundry.
            temperature (float):          Generation temperature (default: 0.7).
            max_tokens (int):             Max tokens (default: 1000).
            use_rag (bool):               Inject RAG context (default: False).
            top_k (int):                  RAG results count (default: from config).
            translate_model_dialog (bool): Translate prompt→EN and response→user lang.
                                          Default: True. Pass false to disable.
            user_language (str|null):     User language ISO 639-1 (e.g. 'ru', 'he').
                                          null = auto-detect from prompt text.

    Returns:
        dict: success, content, model, usage, user_language, translated (bool)
              on success; success=False, error on failure.
    """
    prompt: str = request.get("prompt", "")
    model = request.get("model")
    temperature: float = request.get("temperature", 0.7)
    max_tokens: int = request.get("max_tokens", 1000)
    use_rag: bool = bool(request.get("use_rag", False))
    top_k: int = request.get("top_k") or app_config.rag_top_k
    user_language: str | None = request.get("user_language") or None

    if not prompt:
        return {"success": False, "error": "Prompt is required"}

    do_translate: bool = _should_translate(request)
    translated: bool = False

    if do_translate:
        user_lang = await _resolve_user_lang(prompt, user_language)
        prompt_for_model = await _translate_in(prompt, user_lang)
        translated = prompt_for_model != prompt
    else:
        user_lang = user_language or "en"
        prompt_for_model = prompt

    if use_rag:
        rag_results = await rag_system.search(prompt_for_model, top_k=top_k)
        if rag_results:
            context = rag_system.format_context(rag_results)
            prompt_for_model = f"Context:\n{context}\n\nQuestion: {prompt_for_model}"

    async def _post_process(content: str) -> str:
        if do_translate:
            return await _translate_out(content, user_lang)
        return content

    def _usage(p: str, c: str, raw: dict) -> dict:
        return {
            "prompt_tokens":     raw.get("prompt_tokens")     or count_tokens_approx(p),
            "completion_tokens": raw.get("completion_tokens") or count_tokens_approx(c),
            "total_tokens":      raw.get("total_tokens")      or count_tokens_approx(p) + count_tokens_approx(c),
        }

    # HuggingFace
    if model and str(model).startswith("hf::"):
        try:
            hf_result = await hf_client.generate_text(
                prompt_for_model, model=str(model)[4:],
                temperature=temperature, max_new_tokens=max_tokens
            )
            if not hf_result.get("content"):
                return {"success": False, "error": hf_result.get("error") or "HF generation error"}
            content = await _post_process(hf_result["content"])
            return {
                "success": True, "content": content, "model": model,
                "user_language": user_lang, "translated": translated,
                "usage": _usage(prompt_for_model, content, {}),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # llama.cpp
    if model and str(model).startswith("llama::"):
        try:
            st = await llama_status()
            openai_url = st.get("openai_url")
            if not openai_url:
                return {"success": False, "error": "llama.cpp is not running"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{openai_url.rstrip('/')}/chat/completions",
                    json={"model": "llama",
                          "messages": [{"role": "user", "content": prompt_for_model}],
                          "temperature": temperature, "max_tokens": max_tokens, "stream": False},
                ) as resp:
                    if resp.status != 200:
                        return {"success": False, "error": f"llama.cpp HTTP {resp.status}: {await resp.text()}"}
                    data = await resp.json()
            choices = data.get("choices") or []
            if not choices:
                return {"success": False, "error": "llama.cpp returned no choices"}
            content = await _post_process(choices[0].get("message", {}).get("content", ""))
            return {
                "success": True, "content": content, "model": model,
                "user_language": user_lang, "translated": translated,
                "usage": _usage(prompt_for_model, content, data.get("usage") or {}),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Foundry
    try:
        result = await foundry_client.generate_text(
            prompt_for_model, model=model, temperature=temperature, max_tokens=max_tokens
        )
        if result.get("error_code") == "model_not_loaded":
            return {
                "success": False, "error": result["error"],
                "error_code": "model_not_loaded", "model_id": result.get("model_id"),
            }
        if "content" not in result:
            return {"success": False, "error": result.get("error", "Foundry error")}
        content = await _post_process(result["content"])
        return {
            "success": True, "content": content, "model": result["model"],
            "user_language": user_lang, "translated": translated,
            "usage": _usage(prompt_for_model, content, result.get("usage") or {}),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
