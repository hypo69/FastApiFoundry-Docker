# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Enhanced AI Endpoints
# =============================================================================
# Description:
#   Extended AI endpoints for AI Assistant orchestrator.
#   All generation routes use router.route_generate() — no direct backend calls.
#   POST /api/v1/ai/generate        — text generation with optional RAG context
#   POST /api/v1/ai/generate/stream — streaming text generation (SSE, Foundry only)
#   POST /api/v1/ai/chat            — stateful chat (messages array, RAG, system_prompt)
#   POST /api/v1/ai/chat/stream     — streaming chat with session history persistence
#   GET  /api/v1/ai/models          — list Foundry models
#   GET  /api/v1/ai/models/recommended — categorized model recommendations
#   POST /api/v1/ai/models/{id}/load   — load model into Foundry
#   POST /api/v1/ai/models/{id}/unload — unload model from Foundry
#   GET  /api/v1/ai/health          — Foundry health check
#   POST /api/v1/ai/optimize        — suggest optimal model for task type
#
# File: ai_endpoints.py
# Project: AI Assistant (ai_assist)
# Version: 0.7.0
# Changes in 0.7.0:
#   - /ai/generate and /ai/chat now use router.route_generate() instead of
#     calling foundry_client directly — all backends supported uniformly
#   - /ai/generate/stream and /ai/chat/stream remain Foundry-only (streaming
#     not yet implemented for hf/llama/ollama backends)
#   - Updated header and project name
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import json
import asyncio
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.logger import logger
from ...models.foundry_client import foundry_client
from ...models.router import route_generate
from ...utils.text_utils import count_tokens_approx
try:
    from ...rag.rag_system import rag_system
except Exception:
    # ПОЧЕМУ DummyRAGSystem:
    #   RAG-зависимости (faiss, torch) могут отсутствовать либо падать при импорте на части окружений.
    # Fallback гарантирует работоспособность AI endpoints без контекста.
    class DummyRAGSystem:
        """! Заглушка для системы RAG при отсутствии зависимостей."""
        
        async def search(self, query, top_k=3):
            """! Поиск (заглушка)."""
            return []
            
        async def reload_index(self, index_dir: str) -> bool:
            """! Перезагрузка индекса (заглушка)."""
            return False
            
        def _profile_index_dir(self, name: str):
            """! Определение пути профиля (заглушка)."""
            from pathlib import Path
            return Path.home() / ".rag" / name
            
        def format_context(self, results: list) -> str:
            """! Форматирование контекста (заглушка)."""
            # Возврат пустой строки для предотвращения ошибок склейки
            # Return of an empty string to prevent joining errors
            return ""

        def filter_by_score(self, results: list, min_score: float) -> list:
            """! Фильтрация по порогу схожести (заглушка)."""
            # Возврат оригинального списка без изменений
            # Return of the original list without changes
            return results

    rag_system = DummyRAGSystem()

router = APIRouter()


def _save_session_history(history: list, session_id: str = "default", chat_type: str = "fastapi") -> None:
    """! Автоматическое сохранение истории чата в локальный файл.

    Обоснование:
      - Унифицированное хранение истории для разных источников (FastAPI, Telegram).
      - Использование `session_id` для разделения диалогов.
      - Сохранение контекста между перезапусками.

    Args:
        history (list): Список сообщений для сохранения.
        session_id (str): Идентификатор сессии. По умолчанию 'default'.
        chat_type (str): Тип источника чата. По умолчанию 'fastapi'.
    """
    history_file: Path = Path("session_history.json")
    
    try:
        # Добавление метаданных к истории
        # Adding metadata to the history
        full_history = {
            "session_id": session_id,
            "chat_type": chat_type,
            "timestamp": asyncio.get_event_loop().time(),
            "messages": history
        }
        # Запись всей истории в формате JSON
        # Writing of the full history in JSON format
        history_file.write_text(json.dumps(full_history, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logger.error(f"Ошибка при автоматическом сохранении истории: {e}")


@router.post("/ai/generate")
async def generate_text(request: dict):
    """Generate text via AI Assistant orchestrator (all backends).

    Model prefix determines backend:
    foundry:: / hf:: / llama:: / ollama::
    """
    prompt = request.get("prompt", "")
    min_score = float(request.get("min_score", 0.0))

    if not prompt:
        return {"success": False, "error": "Prompt is required"}

    params = {
        "model":       request.get("model"),
        "temperature": request.get("temperature", 0.7),
        "max_tokens":  request.get("max_tokens", 2048),
    }

    # RAG enhancement
    if request.get("use_rag", False):
        try:
            rag_results = await rag_system.search(prompt, top_k=3)
            if rag_results and min_score > 0 and hasattr(rag_system, "filter_by_score"):
                rag_results = rag_system.filter_by_score(rag_results, min_score)
            if rag_results:
                context = rag_system.format_context(rag_results) if hasattr(rag_system, "format_context") else ""
                if context:
                    prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
        except Exception:
            pass

    return await route_generate(prompt=prompt, **params)

@router.post("/ai/generate/stream")
async def generate_text_stream(request: dict):
    """Стриминговая генерация текста"""
    prompt = request.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    params = {
        "model": request.get("model"),
        "temperature": request.get("temperature", 0.7),
        "max_tokens": request.get("max_tokens", 2048)
    }
    
    async def generate():
        async for chunk in foundry_client.generate_stream(prompt, **params):
            yield f"data: {json.dumps(chunk)}\\n\\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/ai/models")
async def list_models():
    """Получить список доступных моделей с детальной информацией"""
    await foundry_client._update_base_url()
    result = await foundry_client.list_models()
    return result

@router.get("/ai/models/recommended")
async def get_recommended_models():
    """Получить рекомендуемые модели для разных задач"""
    await foundry_client._update_base_url()
    models_result = await foundry_client.list_models()
    
    if not models_result["success"]:
        return models_result
    
    models = models_result["models"]
    recommendations = {
        "reasoning": [],
        "coding": [],
        "general": [],
        "fast": [],
        "quality": []
    }
    
    for model in models:
        model_type = model.get("type", "general")
        size = model.get("size", "unknown")
        
        # Категоризация по типу
        if model_type in recommendations:
            recommendations[model_type].append(model)
        
        # Быстрые модели (меньшего размера)
        if size in ["7B", "14B"]:
            recommendations["fast"].append(model)
        
        # Качественные модели (большего размера)
        if size in ["32B", "70B"] or "deepseek" in model["id"].lower():
            recommendations["quality"].append(model)
    
    return {
        "success": True,
        "recommendations": recommendations,
        "total_models": len(models)
    }

@router.post("/ai/models/{model_id}/load")
async def load_model(model_id: str):
    """Загрузить модель в память"""
    # Принудительно обновляем URL перед запросом
    await foundry_client._update_base_url()
    result = await foundry_client.load_model(model_id)
    return result

@router.post("/ai/models/{model_id}/unload")
async def unload_model(model_id: str):
    """Выгрузить модель из памяти"""
    await foundry_client._update_base_url()
    result = await foundry_client.unload_model(model_id)
    return result

@router.get("/ai/health")
async def health_check():
    """Проверка здоровья AI сервиса"""
    await foundry_client._update_base_url()
    result = await foundry_client.health_check()
    return result

@router.post("/ai/chat")
async def chat_completion(request: dict):
    """Chat with message history via AI Assistant orchestrator (all backends)."""
    messages = request.get("messages", [])
    use_rag = request.get("use_rag", False)
    system_prompt = request.get("system_prompt")
    min_score = float(request.get("min_score", 0.0))

    if not messages:
        return {"success": False, "error": "Messages are required"}

    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
        elif role == "system":
            prompt_parts.append(f"System: {content}")

    if use_rag:
        last_user_content = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
        if last_user_content:
            try:
                rag_results = await rag_system.search(last_user_content, top_k=3)
                if rag_results and min_score > 0 and hasattr(rag_system, "filter_by_score"):
                    rag_results = rag_system.filter_by_score(rag_results, min_score)
                if rag_results:
                    context = rag_system.format_context(rag_results) if hasattr(rag_system, "format_context") else ""
                    if context:
                        prompt_parts.insert(0, f"Context:\n{context}")
            except Exception:
                pass

    if system_prompt:
        prompt_parts.insert(0, f"System: {system_prompt}")

    prompt = "\n".join(prompt_parts)

    result = await route_generate(
        prompt=prompt,
        model=request.get("model"),
        temperature=request.get("temperature", 0.7),
        max_tokens=request.get("max_tokens", 2048),
    )

    if result.get("success"):
        messages.append({"role": "assistant", "content": result["content"]})
        _save_session_history(messages)
        return {
            "id": f"chatcmpl-{int(asyncio.get_event_loop().time())}",
            "object": "chat.completion",
            "model": result["model"],
            "choices": [{"index": 0, "message": {"role": "assistant", "content": result["content"]}, "finish_reason": "stop"}],
            "usage": result.get("usage", {}),
        }
    return result


@router.post("/ai/chat/stream")
async def chat_completion_stream(request: dict):
    """! Стриминговый чат с автоматическим сохранением истории после завершения."""
    # Получение или генерация ID сессии для отслеживания в логах
    # Retrieval or generation of session ID for log tracking
    session_id: str = request.get("session_id") or str(uuid.uuid4())
    
    messages: list = request.get("messages", [])
    use_rag: bool = request.get("use_rag", False)
    system_prompt: str = request.get("system_prompt", "")
    min_score: float = float(request.get("min_score", 0.0))
    prompt_parts: list = []
    params: dict = {}

    if not messages:
        raise HTTPException(status_code=400, detail="Messages are required")

    logger.info(f"Запуск стриминга чата. Session ID: {session_id}")

    # Преобразование истории в единый промпт
    # Conversion of history to a single prompt string
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
        elif role == "system":
            prompt_parts.append(f"System: {content}")

    # Интеграция RAG
    if use_rag:
        last_user_content = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
        if last_user_content:
            try:
                rag_results = await rag_system.search(last_user_content, top_k=3)
                if rag_results and min_score > 0 and hasattr(rag_system, "filter_by_score"):
                    rag_results = rag_system.filter_by_score(rag_results, min_score)
                if rag_results:
                    context = rag_system.format_context(rag_results) if hasattr(rag_system, "format_context") else ""
                    if context:
                        prompt_parts.insert(0, f"Context:\n{context}")
            except Exception:
                pass

    if system_prompt:
        prompt_parts.insert(0, f"System: {system_prompt}")

    prompt = "\n".join(prompt_parts)
    
    params = {
        "model": request.get("model"),
        "temperature": request.get("temperature", 0.7),
        "max_tokens": request.get("max_tokens", 2048)
    }

    async def event_generator():
        accumulated_text: str = ""
        
        await foundry_client._update_base_url()
        async for chunk in foundry_client.generate_stream(prompt, **params):
            # Сборка полного текста ответа для истории
            # Accumulation of the full response text for history
            if isinstance(chunk, dict) and chunk.get("success"):
                content = chunk.get("content", "")
                accumulated_text += content
            
            yield f"data: {json.dumps(chunk)}\n\n"
        
        # Сохранение истории после успешного завершения потока
        # History persistence after successful stream completion
        if accumulated_text:
            messages.append({
                "role": "assistant",
                "content": accumulated_text
            })
            _save_session_history(messages)
            # Отправка технического чанка о завершении сохранения
            yield f"data: {json.dumps({'status': 'history_saved'})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={"X-Session-Id": session_id}
    )


@router.post("/ai/optimize")
async def optimize_generation(request: dict):
    """Оптимизация параметров генерации для конкретной задачи"""
    task_type = request.get("task_type", "general")  # general, coding, reasoning, creative
    model_preference = request.get("model_preference", "balanced")  # fast, balanced, quality
    
    # Получаем список моделей
    await foundry_client._update_base_url()
    models_result = await foundry_client.list_models()
    if not models_result["success"]:
        return models_result
    
    models = models_result["models"]
    
    # Выбираем оптимальную модель
    optimal_model = None
    for model in models:
        if task_type in model.get("capabilities", []):
            if model_preference == "fast" and model.get("size") in ["7B", "14B"]:
                optimal_model = model
                break
            elif model_preference == "quality" and "deepseek" in model["id"].lower():
                optimal_model = model
                break
            elif model_preference == "balanced":
                optimal_model = model
                break
    
    if not optimal_model:
        optimal_model = models[0] if models else None
    
    if not optimal_model:
        return {"success": False, "error": "No suitable model found"}
    
    # Получаем рекомендуемые настройки
    recommended_settings = optimal_model.get("recommended_settings", {})
    
    return {
        "success": True,
        "optimal_model": optimal_model["id"],
        "recommended_settings": recommended_settings,
        "task_type": task_type,
        "model_preference": model_preference,
        "explanation": f"Selected {optimal_model['id']} for {task_type} tasks with {model_preference} preference"
    }