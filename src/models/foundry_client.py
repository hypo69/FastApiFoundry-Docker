# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Foundry Client
# =============================================================================
# Description:
#   Thin async adapter for Microsoft Foundry Local.
#
#   Keep this deliberately small:
#   - discover a live Foundry OpenAI-compatible URL
#   - list models via GET /models
#   - generate via POST /chat/completions
#   - "load" means warm up with a tiny chat request
#   - "unload" is best-effort via foundry-local-sdk, with CLI fallback
#
# File: foundry_client.py
# Project: AI Assistant (ai_assist)
# =============================================================================

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import AsyncIterator
from urllib.parse import urlparse

import aiohttp

from ..utils.foundry_utils import find_foundry_url

logger = logging.getLogger(__name__)


class FoundryClient:
    """Small OpenAI-compatible client for Foundry Local."""

    def __init__(self, base_url: str | None = None) -> None:
        env_port = os.getenv("FOUNDRY_DYNAMIC_PORT")
        self.base_url: str | None = base_url or (
            f"http://127.0.0.1:{env_port}/v1/" if env_port else None
        )
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session: aiohttp.ClientSession | None = None
        logger.info("Foundry client: %s", self.base_url or "waiting for URL...")

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def _url_ok(self, base_url: str | None) -> bool:
        if not base_url:
            return False
        try:
            timeout = aiohttp.ClientTimeout(total=2)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{base_url.rstrip('/')}/models") as response:
                    return response.status == 200
        except Exception:
            return False

    async def _update_base_url(self) -> None:
        """Find the live Foundry OpenAI-compatible URL.

        Config is only a hint. The source of truth is the URL that actually
        answers GET /models.
        """
        from ..core.config import config

        candidates = [
            self.base_url,
            os.getenv("FOUNDRY_BASE_URL"),
            config.foundry_base_url,
            find_foundry_url(),
        ]

        seen: set[str] = set()
        for candidate in candidates:
            if not candidate:
                continue
            url = candidate.rstrip("/") + "/"
            if url in seen:
                continue
            seen.add(url)
            if await self._url_ok(url):
                self.base_url = url
                return

        self.base_url = None

    async def _request_json(self, method: str, path: str, **kwargs: object) -> tuple[int, object]:
        await self._update_base_url()
        if not self.base_url:
            return 0, {"error": "Foundry недоступен"}

        session = await self._get_session()
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        async with session.request(method, url, **kwargs) as response:
            text = await response.text()
            if not text:
                return response.status, {}
            try:
                return response.status, json.loads(text)
            except json.JSONDecodeError:
                return response.status, {"error": text}

    def _port(self) -> int | None:
        try:
            return urlparse(self.base_url or "").port
        except ValueError:
            return None

    async def health_check(self) -> dict:
        await self._update_base_url()
        if not self.base_url:
            return {
                "status": "disconnected",
                "error": "Foundry не найден",
                "url": None,
                "port": None,
                "timestamp": datetime.now().isoformat(),
            }

        status, data = await self._request_json("GET", "/models")
        if status == 200 and isinstance(data, dict):
            return {
                "status": "healthy",
                "models_count": len(data.get("data", [])),
                "url": self.base_url,
                "port": self._port(),
                "timestamp": datetime.now().isoformat(),
            }

        error = data.get("error") if isinstance(data, dict) else str(data)
        return {
            "status": "unhealthy",
            "error": f"HTTP {status}: {error}",
            "url": self.base_url,
            "port": self._port(),
            "timestamp": datetime.now().isoformat(),
        }

    async def list_available_models(self) -> dict:
        """Return models reported by Foundry GET /models.

        Foundry Local does not expose a reliable separate "loaded models" list
        here, so callers should treat this as available/registered models.
        """
        status, data = await self._request_json("GET", "/models")
        if status != 200 or not isinstance(data, dict):
            error = data.get("error") if isinstance(data, dict) else str(data)
            return {"success": False, "error": f"HTTP {status}: {error}", "models": []}

        models = data.get("data", [])
        return {"success": True, "models": models, "count": len(models)}

    async def list_models(self) -> dict:
        return await self.list_available_models()

    async def _chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> tuple[int, object]:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        return await self._request_json("POST", "/chat/completions", json=payload)

    async def _default_model(self) -> str | None:
        models_resp = await self.list_available_models()
        models = models_resp.get("models", [])
        if not models:
            return None
        return models[0].get("id")

    async def load_model(self, model_id: str) -> dict:
        """Warm up a model with a tiny inference request."""
        logger.info("📥 Warm-up Foundry model: %s", model_id)
        status, data = await self._chat_completion(
            [{"role": "user", "content": "ping"}],
            model=model_id,
            temperature=0,
            max_tokens=1,
        )
        if status == 200:
            return {"success": True, "message": f"Модель {model_id} готова"}

        error = data.get("error") if isinstance(data, dict) else str(data)
        return {"success": False, "error": f"HTTP {status}: {error}"}

    def _sdk_unload(self, model_id: str) -> dict:
        try:
            from foundry_local_sdk import Configuration, FoundryLocalManager

            if getattr(FoundryLocalManager, "instance", None) is None:
                FoundryLocalManager.initialize(Configuration(app_name="fastapi_foundry"))

            selected = None
            for model in FoundryLocalManager.instance.catalog.list_models():
                for candidate in [model, *getattr(model, "variants", [])]:
                    if model_id in (getattr(candidate, "id", None), getattr(candidate, "alias", None)):
                        selected = candidate
                        break
                if selected:
                    break

            if not selected:
                return {"success": False, "error": f"Model not found in Foundry catalog: {model_id}"}

            selected.unload()
            return {"success": True}
        except Exception as exc:
            return {"success": False, "error": f"{type(exc).__name__}: {exc}"}

    async def unload_model(self, model_id: str) -> dict:
        """Best-effort unload.

        Foundry's OpenAI HTTP API does not provide a reliable unload endpoint.
        SDK is the primary path; CLI is a fallback for environments where SDK
        cannot initialize.
        """
        logger.info("📤 Unload Foundry model: %s", model_id)

        sdk_result = await asyncio.get_running_loop().run_in_executor(None, self._sdk_unload, model_id)
        if sdk_result.get("success"):
            return {"success": True, "message": f"Модель {model_id} выгружена"}

        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                "foundry",
                "model",
                "unload",
                model_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
            output = (stdout or b"").decode("utf-8", errors="replace").strip()
            error = (stderr or b"").decode("utf-8", errors="replace").strip()
            if proc.returncode == 0:
                return {"success": True, "message": f"Модель {model_id} выгружена"}
            return {"success": False, "error": error or output or "foundry model unload failed"}
        except asyncio.TimeoutError:
            if proc:
                proc.kill()
                await proc.communicate()
            return {"success": False, "error": "foundry model unload timed out after 30 seconds"}
        except Exception as exc:
            return {
                "success": False,
                "error": sdk_result.get("error") or f"{type(exc).__name__}: {exc}",
            }

    async def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> dict:
        model = model or await self._default_model()
        if not model:
            return {"success": False, "error": "Нет доступных моделей Foundry"}

        status, data = await self._chat_completion(
            [{"role": "user", "content": prompt}],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if status == 200 and isinstance(data, dict):
            choices = data.get("choices") or []
            if choices:
                return {
                    "success": True,
                    "content": choices[0].get("message", {}).get("content", ""),
                    "model": model,
                    "usage": data.get("usage") or {},
                }
            return {"success": False, "error": "Некорректный ответ от Foundry"}

        error = data.get("error") if isinstance(data, dict) else str(data)
        result = {"success": False, "error": f"HTTP {status}: {error}"}
        if status == 400:
            result.update({"error_code": "model_not_loaded", "model_id": model})
        return result

    async def generate_stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: object,
    ) -> AsyncIterator[dict]:
        model = model or await self._default_model()
        if not model:
            yield {"success": False, "error": "Нет доступных моделей Foundry"}
            return

        await self._update_base_url()
        if not self.base_url:
            yield {"success": False, "error": "Foundry недоступен"}
            return

        session = await self._get_session()
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    yield {"success": False, "error": f"HTTP {response.status}: {await response.text()}"}
                    return

                async for line in response.content:
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str.startswith("data: "):
                        continue
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        yield {"success": True, "finished": True}
                        return
                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue
                    choices = chunk.get("choices") or []
                    content = choices[0].get("delta", {}).get("content", "") if choices else ""
                    if content:
                        yield {"success": True, "content": content, "finished": False}
        except Exception as exc:
            yield {"success": False, "error": f"{type(exc).__name__}: {exc}"}

    async def completions(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: object,
    ) -> dict:
        model = model or await self._default_model()
        if not model:
            return {"success": False, "error": "Нет доступных моделей Foundry"}

        payload = {"model": model, "prompt": prompt, "temperature": temperature, "max_tokens": max_tokens, **kwargs}
        status, data = await self._request_json("POST", "/completions", json=payload)
        if status == 200 and isinstance(data, dict):
            return {"success": True, **data}
        error = data.get("error") if isinstance(data, dict) else str(data)
        return {"success": False, "error": f"HTTP {status}: {error}"}

    async def embeddings(self, input: str | list, model: str | None = None) -> dict:
        model = model or await self._default_model()
        if not model:
            return {"success": False, "error": "Нет доступных моделей Foundry"}

        status, data = await self._request_json("POST", "/embeddings", json={"input": input, "model": model})
        if status == 200 and isinstance(data, dict):
            return {"success": True, **data}
        error = data.get("error") if isinstance(data, dict) else str(data)
        return {"success": False, "error": f"HTTP {status}: {error}"}


foundry_client = FoundryClient()
