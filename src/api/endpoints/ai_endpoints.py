# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Enhanced AI Endpoints
# =============================================================================
# Описание:
#   Расширенные endpoints для работы с AI моделями
#   Поддержка стриминга, управления моделями, оптимизации
#
# File: ai_endpoints.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ...models.enhanced_foundry_client import enhanced_foundry_client
# from ...rag.rag_system import rag_system

# Заглушка для RAG системы
class DummyRAGSystem:
    async def search(self, query, top_k=3):
        return []

rag_system = DummyRAGSystem()
import json
import asyncio

router = APIRouter()

@router.post("/ai/generate")
async def generate_text(request: dict):
    """Генерация текста с расширенными параметрами"""
    prompt = request.get("prompt", "")
    if not prompt:
        return {"success": False, "error": "Prompt is required"}
    
    # Параметры генерации
    params = {
        "model": request.get("model"),
        "temperature": request.get("temperature", 0.7),
        "max_tokens": request.get("max_tokens", 2048),
        "top_p": request.get("top_p", 0.9),
        "top_k": request.get("top_k", 40),
        "presence_penalty": request.get("presence_penalty", 0.0),
        "frequency_penalty": request.get("frequency_penalty", 0.0),
        "stop": request.get("stop", [])
    }
    
    # RAG enhancement
    if request.get("use_rag", False):
        try:
            rag_results = await rag_system.search(prompt, top_k=3)
            if rag_results:
                context = "\\n".join([r.get("text", "") for r in rag_results])
                prompt = f"Context:\\n{context}\\n\\nQuestion: {prompt}"
        except Exception as e:
            # Продолжаем без RAG если ошибка
            pass
    
    result = await enhanced_foundry_client.generate_text(prompt, **params)
    return result

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
        async for chunk in enhanced_foundry_client.generate_stream(prompt, **params):
            yield f"data: {json.dumps(chunk)}\\n\\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

@router.get("/ai/models")
async def list_models():
    """Получить список доступных моделей с детальной информацией"""
    result = await enhanced_foundry_client.list_models()
    return result

@router.get("/ai/models/recommended")
async def get_recommended_models():
    """Получить рекомендуемые модели для разных задач"""
    models_result = await enhanced_foundry_client.list_models()
    
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
    result = await enhanced_foundry_client.load_model(model_id)
    return result

@router.post("/ai/models/{model_id}/unload")
async def unload_model(model_id: str):
    """Выгрузить модель из памяти"""
    result = await enhanced_foundry_client.unload_model(model_id)
    return result

@router.get("/ai/health")
async def health_check():
    """Проверка здоровья AI сервиса"""
    result = await enhanced_foundry_client.health_check()
    return result

@router.post("/ai/chat")
async def chat_completion(request: dict):
    """Чат с поддержкой истории сообщений"""
    messages = request.get("messages", [])
    if not messages:
        return {"success": False, "error": "Messages are required"}
    
    # Преобразуем историю в один промпт
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
    
    prompt = "\\n".join(prompt_parts)
    
    params = {
        "model": request.get("model"),
        "temperature": request.get("temperature", 0.7),
        "max_tokens": request.get("max_tokens", 2048)
    }
    
    result = await enhanced_foundry_client.generate_text(prompt, **params)
    
    if result["success"]:
        # Форматируем ответ в стиле OpenAI
        return {
            "id": f"chatcmpl-{int(asyncio.get_event_loop().time())}",
            "object": "chat.completion",
            "model": result["model"],
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["content"]
                },
                "finish_reason": "stop"
            }],
            "usage": result.get("usage", {}),
            "performance": result.get("performance", {})
        }
    else:
        return result

@router.post("/ai/optimize")
async def optimize_generation(request: dict):
    """Оптимизация параметров генерации для конкретной задачи"""
    task_type = request.get("task_type", "general")  # general, coding, reasoning, creative
    model_preference = request.get("model_preference", "balanced")  # fast, balanced, quality
    
    # Получаем список моделей
    models_result = await enhanced_foundry_client.list_models()
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