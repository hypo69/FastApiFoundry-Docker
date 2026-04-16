# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Translation Module — перевод текста перед отправкой в модель
# =============================================================================
# Описание:
#   Модуль перевода текста с поддержкой нескольких провайдеров:
#   - llm: перевод через текущую AI модель (Foundry)
#   - deepl: DeepL API (требует ключ)
#   - google: Google Translate API (требует ключ)
#   - helsinki: Helsinki-NLP локальные модели через HuggingFace
#
#   Основной сценарий: автоматический перевод входящего текста на английский
#   перед отправкой в AI модель для улучшения качества ответа.
#
# Примеры:
#   >>> from src.translator import translator
#   >>> result = await translator.translate("Привет мир", target_lang="en")
#   >>> result["translated"]  # "Hello world"
#
# File: translator.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import logging
import os
import time
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

# Человекочитаемые названия языков для промптов
LANG_NAMES: dict[str, str] = {
    "en": "English", "ru": "Russian", "de": "German", "fr": "French",
    "es": "Spanish", "zh": "Chinese", "ja": "Japanese", "ar": "Arabic",
    "uk": "Ukrainian", "pl": "Polish", "it": "Italian", "pt": "Portuguese",
    "nl": "Dutch", "ko": "Korean", "tr": "Turkish",
}

# DeepL target lang codes
DEEPL_LANG_MAP: dict[str, str] = {
    "en": "EN-US", "ru": "RU", "de": "DE", "fr": "FR", "es": "ES",
    "zh": "ZH", "ja": "JA", "uk": "UK", "pl": "PL", "it": "IT",
    "pt": "PT-PT", "nl": "NL", "ko": "KO", "tr": "TR",
}


class Translator:
    """Переводчик текста с поддержкой нескольких провайдеров."""

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # ── Public API ────────────────────────────────────────────────────────

    async def translate(
        self,
        text: str,
        *,
        provider: str = "llm",
        source_lang: str = "auto",
        target_lang: str = "en",
        api_key: str = "",
        model: Optional[str] = None,
    ) -> dict:
        """Перевести текст.

        Args:
            text: Исходный текст.
            provider: Провайдер — "llm" | "deepl" | "google" | "helsinki".
            source_lang: Исходный язык (ISO 639-1) или "auto".
            target_lang: Целевой язык (ISO 639-1).
            api_key: API ключ для DeepL / Google.
            model: Модель для LLM провайдера (опционально).

        Returns:
            dict с ключами: success, translated, provider, source_lang,
                            target_lang, elapsed_ms, error.
        """
        if not text or not text.strip():
            return self._err("Empty text")

        t0 = time.monotonic()

        try:
            if provider == "llm":
                translated = await self._via_llm(text, source_lang, target_lang, model)
            elif provider == "deepl":
                translated = await self._via_deepl(text, target_lang, api_key)
            elif provider == "google":
                translated = await self._via_google(text, source_lang, target_lang, api_key)
            elif provider == "helsinki":
                translated = await self._via_helsinki(text, source_lang, target_lang)
            else:
                return self._err(f"Unknown provider: {provider}")

            elapsed = int((time.monotonic() - t0) * 1000)
            logger.info(f"✅ Translated via {provider} in {elapsed}ms")
            return {
                "success": True,
                "translated": translated,
                "provider": provider,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "elapsed_ms": elapsed,
                "error": None,
            }

        except Exception as e:
            logger.error(f"❌ Translation error ({provider}): {e}")
            return self._err(str(e), provider=provider)

    async def detect_language(self, text: str, model: Optional[str] = None) -> dict:
        """Определить язык текста через LLM.

        Returns:
            dict с ключами: success, language, language_name, error.
        """
        if not text or not text.strip():
            return {"success": False, "language": None, "language_name": None, "error": "Empty text"}

        try:
            from ..models.foundry_client import foundry_client
            prompt = (
                f"Detect the language of the following text. "
                f"Reply with ONLY the ISO 639-1 language code (e.g. 'en', 'ru', 'de'). "
                f"Text: \"{text[:300]}\""
            )
            result = await foundry_client.generate_text(
                prompt, model=model, temperature=0, max_tokens=5
            )
            if not result["success"]:
                return {"success": False, "language": None, "language_name": None, "error": result["error"]}

            code = result["content"].strip().lower().split()[0].strip("'\".,")[:5]
            name = LANG_NAMES.get(code, code.upper())
            return {"success": True, "language": code, "language_name": name, "error": None}

        except Exception as e:
            logger.error(f"❌ Language detection error: {e}")
            return {"success": False, "language": None, "language_name": None, "error": str(e)}

    async def translate_for_model(
        self,
        text: str,
        *,
        provider: str = "llm",
        source_lang: str = "auto",
        api_key: str = "",
        model: Optional[str] = None,
    ) -> dict:
        """Перевести текст на английский для отправки в AI модель.

        Удобный метод — всегда переводит в EN.
        Возвращает оригинал если текст уже на английском.
        """
        # Быстрая проверка: если уже английский — не переводим
        if source_lang == "en":
            return {
                "success": True,
                "translated": text,
                "original": text,
                "was_translated": False,
                "provider": provider,
                "source_lang": "en",
                "target_lang": "en",
                "elapsed_ms": 0,
                "error": None,
            }

        result = await self.translate(
            text,
            provider=provider,
            source_lang=source_lang,
            target_lang="en",
            api_key=api_key,
            model=model,
        )
        result["original"] = text
        result["was_translated"] = result["success"]
        return result

    async def batch_translate(
        self,
        texts: list[str],
        *,
        provider: str = "llm",
        source_lang: str = "auto",
        target_lang: str = "en",
        api_key: str = "",
        model: Optional[str] = None,
    ) -> dict:
        """Перевести список текстов.

        Returns:
            dict с ключами: success, results (list), total, failed, elapsed_ms.
        """
        if not texts:
            return {"success": False, "results": [], "total": 0, "failed": 0, "error": "Empty list"}

        t0 = time.monotonic()
        results = []
        failed = 0

        for text in texts:
            r = await self.translate(
                text,
                provider=provider,
                source_lang=source_lang,
                target_lang=target_lang,
                api_key=api_key,
                model=model,
            )
            results.append(r)
            if not r["success"]:
                failed += 1

        elapsed = int((time.monotonic() - t0) * 1000)
        return {
            "success": True,
            "results": results,
            "total": len(texts),
            "failed": failed,
            "elapsed_ms": elapsed,
        }

    # ── Providers ─────────────────────────────────────────────────────────

    async def _via_llm(
        self, text: str, source_lang: str, target_lang: str, model: Optional[str]
    ) -> str:
        from ..models.foundry_client import foundry_client

        to_name = LANG_NAMES.get(target_lang, target_lang)
        if source_lang == "auto":
            prompt = (
                f"Translate the following text to {to_name}. "
                f"Output ONLY the translation, no explanations:\n\n{text}"
            )
        else:
            from_name = LANG_NAMES.get(source_lang, source_lang)
            prompt = (
                f"Translate the following text from {from_name} to {to_name}. "
                f"Output ONLY the translation, no explanations:\n\n{text}"
            )

        result = await foundry_client.generate_text(
            prompt,
            model=model,
            temperature=0.1,
            max_tokens=max(512, len(text) * 3),
        )
        if not result["success"]:
            raise RuntimeError(result["error"])
        return result["content"].strip()

    async def _via_deepl(self, text: str, target_lang: str, api_key: str) -> str:
        key = api_key or os.getenv("DEEPL_API_KEY", "")
        if not key:
            raise ValueError("DeepL API key not set. Add DEEPL_API_KEY to .env or pass api_key.")

        tgt = DEEPL_LANG_MAP.get(target_lang, target_lang.upper())
        session = await self._get_session()

        async with session.post(
            "https://api-free.deepl.com/v2/translate",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"auth_key": key, "text": text, "target_lang": tgt},
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"DeepL HTTP {resp.status}: {body[:200]}")
            data = await resp.json()
            return data["translations"][0]["text"]

    async def _via_google(
        self, text: str, source_lang: str, target_lang: str, api_key: str
    ) -> str:
        key = api_key or os.getenv("GOOGLE_TRANSLATE_API_KEY", "")
        if not key:
            raise ValueError("Google API key not set. Add GOOGLE_TRANSLATE_API_KEY to .env or pass api_key.")

        session = await self._get_session()
        payload: dict = {"q": text, "target": target_lang, "format": "text"}
        if source_lang != "auto":
            payload["source"] = source_lang

        async with session.post(
            f"https://translation.googleapis.com/language/translate/v2?key={key}",
            json=payload,
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"Google Translate HTTP {resp.status}: {body[:200]}")
            data = await resp.json()
            return data["data"]["translations"][0]["translatedText"]

    async def _via_helsinki(
        self, text: str, source_lang: str, target_lang: str
    ) -> str:
        from ..models.foundry_client import foundry_client  # noqa — used for HF endpoint

        src = "ru" if source_lang == "auto" else source_lang
        model_id = f"Helsinki-NLP/opus-mt-{src}-{target_lang}"

        # Вызываем через HF endpoint если он доступен
        try:
            from ..models.hf_client import hf_client
            result = await hf_client.generate(
                model_id=model_id,
                prompt=text,
                max_new_tokens=max(256, len(text) * 2),
                temperature=0.1,
            )
            if result["success"]:
                return result["content"].strip()
            raise RuntimeError(result["error"])
        except ImportError:
            raise RuntimeError(
                f"Helsinki-NLP requires HuggingFace client. "
                f"Load model '{model_id}' in the HuggingFace tab first."
            )

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _err(msg: str, provider: str = "") -> dict:
        return {
            "success": False,
            "translated": None,
            "provider": provider,
            "source_lang": None,
            "target_lang": None,
            "elapsed_ms": 0,
            "error": msg,
        }


# Глобальный синглтон
translator = Translator()
