# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Translation API Endpoints
# =============================================================================
# Description:
#   REST API for text translation via /api/v1/translation/*
#   Supports providers: llm, deepl, google, helsinki
#   Main scenario: translating incoming text to EN before sending to the model
#
# Examples:
#   POST /api/v1/translation/translate
#   POST /api/v1/translation/translate-for-model
#   POST /api/v1/translation/detect
#   POST /api/v1/translation/batch
#   GET  /api/v1/translation/providers
#
# File: translation.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import logging
from fastapi import APIRouter
from ...translator import translator

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/translation/translate")
async def translate(request: dict):
    """Translate text.

    Body: { text, provider?, source_lang?, target_lang?, api_key?, model? }
    """
    text = request.get("text", "").strip()
    if not text:
        return {"success": False, "error": "text is required"}

    return await translator.translate(
        text,
        provider=request.get("provider", "llm"),
        source_lang=request.get("source_lang", "auto"),
        target_lang=request.get("target_lang", "en"),
        api_key=request.get("api_key", ""),
        model=request.get("model"),
    )


@router.post("/translation/translate-for-model")
async def translate_for_model(request: dict):
    """Translate text to EN for sending to AI model.

    Body: { text, provider?, source_lang?, api_key?, model? }
    """
    text = request.get("text", "").strip()
    if not text:
        return {"success": False, "error": "text is required"}

    return await translator.translate_for_model(
        text,
        provider=request.get("provider", "llm"),
        source_lang=request.get("source_lang", "auto"),
        api_key=request.get("api_key", ""),
        model=request.get("model"),
    )


@router.post("/translation/detect")
async def detect_language(request: dict):
    """Detect text language.

    Body: { text, model? }
    """
    text = request.get("text", "").strip()
    if not text:
        return {"success": False, "error": "text is required"}

    return await translator.detect_language(text, model=request.get("model"))


@router.post("/translation/batch")
async def batch_translate(request: dict):
    """Translate a list of texts.

    Body: { texts: [...], provider?, source_lang?, target_lang?, api_key?, model? }
    """
    texts = request.get("texts", [])
    if not texts or not isinstance(texts, list):
        return {"success": False, "error": "texts must be a non-empty list"}
    if len(texts) > 100:
        return {"success": False, "error": "Maximum 100 texts per batch"}

    return await translator.batch_translate(
        texts,
        provider=request.get("provider", "llm"),
        source_lang=request.get("source_lang", "auto"),
        target_lang=request.get("target_lang", "en"),
        api_key=request.get("api_key", ""),
        model=request.get("model"),
    )


@router.get("/translation/providers")
async def get_providers():
    """List available providers and their status."""
    import os

    providers = [
        {
            "id": "llm",
            "name": "LLM (current model)",
            "description": "Uses the currently loaded AI model via Foundry",
            "requires_key": False,
            "available": True,
            "env_key": None,
        },
        {
            "id": "deepl",
            "name": "DeepL API",
            "description": "High-quality neural translation. Free tier: 500K chars/month",
            "requires_key": True,
            "available": bool(os.getenv("DEEPL_API_KEY")),
            "env_key": "DEEPL_API_KEY",
            "signup_url": "https://www.deepl.com/pro-api",
        },
        {
            "id": "google",
            "name": "Google Translate",
            "description": "Fast, supports 100+ languages. Requires Google Cloud project",
            "requires_key": True,
            "available": bool(os.getenv("GOOGLE_TRANSLATE_API_KEY")),
            "env_key": "GOOGLE_TRANSLATE_API_KEY",
            "signup_url": "https://cloud.google.com/translate",
        },
        {
            "id": "helsinki",
            "name": "Helsinki-NLP (local)",
            "description": "Open-source NMT models. Runs locally via HuggingFace transformers",
            "requires_key": False,
            "available": _check_hf_available(),
            "env_key": None,
        },
    ]
    return {"success": True, "providers": providers}


def _check_hf_available() -> bool:
    try:
        from ..models.hf_client import hf_client  # noqa
        return True
    except Exception:
        return False
