# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: AI Model Router — Orchestrator Core
# =============================================================================
# Description:
#   Central routing logic for AI Assistant orchestrator.
#   Dispatches generate requests to the correct backend by model prefix.
#
#   Workflow:
#     request.model  →  detect_backend()  →  backend + clean_model_id
#                                         ↓
#                          ┌──────────────┼──────────────┬──────────────┐
#                          ▼              ▼              ▼              ▼
#                       Foundry      HuggingFace     llama.cpp      Ollama
#                    (ONNX/local)   (PyTorch/Hub)  (GGUF/CPU)   (local HTTP)
#                          └──────────────┴──────────────┴──────────────┘
#                                         ↓
#                          {"success": bool, "content": str,
#                           "model": str, "usage": {...}}
#
#   Model prefix routing:
#     foundry::model-id   → Microsoft Foundry Local (ONNX)
#     hf::model-id        → HuggingFace Transformers (PyTorch)
#     llama::path.gguf    → llama.cpp (GGUF / CPU)
#     ollama::model-name  → Ollama (local HTTP)
#
#   No prefix → legacy bare ID forwarded to Foundry with deprecation warning.
#
# File: src/models/router.py
# Project: AI Assistant (ai_assist)
# Version: 0.7.1
# Changes in 0.7.1:
#   - Added workflow diagram to header
#   - Enriched docstrings with examples
#   - Added type annotations to private backend functions
# Changes in 0.7.0:
#   - Created: extracted routing from generate.py / ai_endpoints.py
#   - Added foundry:: prefix support
#   - Unified response shape across all backends
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import logging
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)

# ── Prefix constants — single source of truth ────────────────────────────────
PREFIX_FOUNDRY = "foundry::"
PREFIX_HF      = "hf::"
PREFIX_LLAMA   = "llama::"
PREFIX_OLLAMA  = "ollama::"

_KNOWN_PREFIXES = (PREFIX_FOUNDRY, PREFIX_HF, PREFIX_LLAMA, PREFIX_OLLAMA)


def detect_backend(model: Optional[str]) -> tuple[str, str]:
    """Detect backend and strip prefix from model ID.

    Workflow:
        model string → prefix check → (backend_name, clean_id)

    Args:
        model: Raw model string from request. Supported formats:
            - ``'foundry::qwen3-0.6b-generic-cpu:4'``
            - ``'hf::Qwen/Qwen2.5-0.5B-Instruct'``
            - ``'llama::D:/models/gemma-2b-q4.gguf'``
            - ``'ollama::qwen2.5:0.5b'``
            - ``None`` or ``''`` → defaults to Foundry with empty model ID

    Returns:
        tuple[str, str]: ``(backend, clean_model_id)``

            - ``backend``: one of ``'foundry'``, ``'hf'``, ``'llama'``, ``'ollama'``
            - ``clean_model_id``: model ID with prefix stripped

    Example:
        >>> detect_backend("foundry::qwen3-0.6b")
        ('foundry', 'qwen3-0.6b')

        >>> detect_backend("hf::Qwen/Qwen2.5-0.5B")
        ('hf', 'Qwen/Qwen2.5-0.5B')

        >>> detect_backend("llama::D:/models/q4.gguf")
        ('llama', 'D:/models/q4.gguf')

        >>> detect_backend("ollama::mistral")
        ('ollama', 'mistral')

        >>> detect_backend(None)
        ('foundry', '')

        >>> detect_backend("bare-model-id")  # legacy, warns
        ('foundry', 'bare-model-id')
    """
    if not model:
        return "foundry", ""

    m = str(model)

    if m.startswith(PREFIX_FOUNDRY):
        return "foundry", m[len(PREFIX_FOUNDRY):]
    if m.startswith(PREFIX_HF):
        return "hf", m[len(PREFIX_HF):]
    if m.startswith(PREFIX_LLAMA):
        return "llama", m[len(PREFIX_LLAMA):]
    if m.startswith(PREFIX_OLLAMA):
        return "ollama", m[len(PREFIX_OLLAMA):]

    # Legacy: bare model ID — forward to Foundry with deprecation warning.
    # Kept for backward compatibility with old integrations.
    logger.warning(
        f"⚠️ Bare model ID '{m}' has no backend prefix. "
        f"Use 'foundry::{m}' explicitly. Forwarding to Foundry (legacy)."
    )
    return "foundry", m


async def route_generate(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> dict:
    """Route a generation request to the correct backend.

    Workflow:
        prompt + model → detect_backend() → backend call → unified response

    Args:
        prompt:      Input text (required, non-empty).
        model:       Model ID with prefix, e.g. ``'foundry::qwen3-0.6b'``.
                     If ``None``, routes to Foundry and uses its first loaded model.
        temperature: Sampling temperature (0.0–2.0, default 0.7).
        max_tokens:  Maximum tokens to generate (default 1000).

    Returns:
        dict: On success::

            {"success": True, "content": "...", "model": "foundry::...", "usage": {...}}

        On failure::

            {"success": False, "error": "description"}

        Special error on Foundry model not loaded::

            {"success": False, "error": "...", "error_code": "model_not_loaded", "model_id": "..."}

    Example:
        >>> result = await route_generate("Hello", model="foundry::qwen3-0.6b")
        >>> result["success"]
        True

        >>> result = await route_generate("Summarize", model="hf::Qwen/Qwen2.5-0.5B")

        >>> result = await route_generate("Code review", model="ollama::codellama")

        >>> result = await route_generate("Translate", model="llama::D:/models/q4.gguf")
    """
    if not prompt:
        return {"success": False, "error": "Prompt is required"}

    backend, clean_model = detect_backend(model)

    if backend == "hf":
        return await _generate_hf(prompt, clean_model, temperature, max_tokens)
    if backend == "llama":
        return await _generate_llama(prompt, clean_model, temperature, max_tokens)
    if backend == "ollama":
        return await _generate_ollama(prompt, clean_model, temperature, max_tokens)
    # Default: Foundry
    return await _generate_foundry(prompt, clean_model or None, temperature, max_tokens)


# ── Backend implementations ───────────────────────────────────────────────────

async def _generate_foundry(
    prompt: str,
    model: Optional[str],
    temperature: float,
    max_tokens: int,
) -> dict:
    """Call Foundry Local backend.

    Args:
        prompt: Input text.
        model: Foundry model ID (without prefix), or None to use first loaded.
        temperature: Sampling temperature.
        max_tokens: Max tokens to generate.

    Returns:
        dict: Unified response with ``model`` prefixed as ``foundry::<id>``.
    """
    from .foundry_client import foundry_client

    result = await foundry_client.generate_text(
        prompt, model=model, temperature=temperature, max_tokens=max_tokens
    )

    # Propagate model_not_loaded error to caller
    if result.get("error_code") == "model_not_loaded":
        return {
            "success": False,
            "error": result["error"],
            "error_code": "model_not_loaded",
            "model_id": result.get("model_id"),
        }

    if "content" not in result:
        return {"success": False, "error": result.get("error", "Foundry error")}

    return {
        "success": True,
        "content": result["content"],
        "model": f"{PREFIX_FOUNDRY}{result['model']}",
        "usage": result.get("usage") or {},
    }


async def _generate_hf(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    """Call HuggingFace Transformers backend.

    Args:
        prompt: Input text.
        model: HuggingFace model ID (without prefix), e.g. ``'Qwen/Qwen2.5-0.5B'``.
        temperature: Sampling temperature.
        max_tokens: Max new tokens to generate.

    Returns:
        dict: Unified response with ``model`` prefixed as ``hf::<id>``.
    """
    from .hf_client import hf_client

    result = await hf_client.generate(
        prompt, model_id=model, temperature=temperature, max_new_tokens=max_tokens
    )

    if not result.get("content"):
        return {"success": False, "error": result.get("error") or "HF generation error"}

    return {
        "success": True,
        "content": result["content"],
        "model": f"{PREFIX_HF}{model}",
        "usage": {},
    }


async def _generate_llama(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    """Call llama.cpp backend via its OpenAI-compatible HTTP API.

    Requires llama.cpp server to be running (started via ``/api/v1/llama/start``).

    Args:
        prompt: Input text.
        model: Path to GGUF file (without prefix), used only for response labeling.
        temperature: Sampling temperature.
        max_tokens: Max tokens to generate.

    Returns:
        dict: Unified response with ``model`` prefixed as ``llama::<path>``.
    """
    from ..api.endpoints.llama_cpp import llama_status

    # Check llama.cpp server is running and get its OpenAI-compatible URL
    st = await llama_status()
    openai_url = st.get("openai_url")
    if not openai_url:
        return {"success": False, "error": "llama.cpp is not running. Start it via /api/v1/llama/start"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{openai_url.rstrip('/')}/chat/completions",
                json={
                    "model": "llama",  # llama.cpp ignores model name, uses loaded model
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
            ) as resp:
                if resp.status != 200:
                    return {"success": False, "error": f"llama.cpp HTTP {resp.status}: {await resp.text()}"}
                data = await resp.json()

        choices = data.get("choices") or []
        if not choices:
            return {"success": False, "error": "llama.cpp returned no choices"}

        content = choices[0].get("message", {}).get("content", "")
        return {
            "success": True,
            "content": content,
            "model": f"{PREFIX_LLAMA}{model}",
            "usage": data.get("usage") or {},
        }
    except Exception as e:
        logger.error(f"❌ llama.cpp request failed: {e}")
        return {"success": False, "error": str(e)}


async def _generate_ollama(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    """Call Ollama backend.

    Requires Ollama service running locally (default port 11434).

    Args:
        prompt: Input text.
        model: Ollama model name (without prefix), e.g. ``'qwen2.5:0.5b'``.
        temperature: Sampling temperature.
        max_tokens: Max tokens to generate.

    Returns:
        dict: Unified response with ``model`` prefixed as ``ollama::<name>``.
    """
    from .ollama_client import ollama_client

    result = await ollama_client.generate(
        prompt, model=model, temperature=temperature, max_tokens=max_tokens
    )

    if not result.get("content"):
        return {"success": False, "error": result.get("error") or "Ollama generation error"}

    return {
        "success": True,
        "content": result["content"],
        "model": f"{PREFIX_OLLAMA}{model}",
        "usage": {},
    }
