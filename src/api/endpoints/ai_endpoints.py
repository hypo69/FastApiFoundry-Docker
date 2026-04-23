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
# Version: 0.6.1
# Author: hypo69
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: 9 декабря 2025
# =============================================================================

import json
import asyncio
import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.logger import logger
from ...models.foundry_client import foundry_client
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
      - Добавление метаданных для удобства анализа.

    Args:
        history (list): Список сообщений для сохранения.
      - Сохранение контекста между перезапусками.
      - Упрощение отладки промптов.

    Args:
        history (list): Список сообщений для сохранения.
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
    """Генерация текста с расширенными параметрами"""
    prompt = request.get("prompt", "")

    # Получение порога схожести для RAG (по умолчанию 0.0)
    # Retrieval of the similarity threshold for RAG (default 0.0)
    min_score = float(request.get("min_score", 0.0))

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

            # Фильтрация результатов по порогу схожести
            # Filtration of results by the similarity threshold
            if rag_results and min_score > 0 and hasattr(rag_system, "filter_by_score"):
                # ПОЧЕМУ ВЫБРАН ЭТОТ МЕТОД:
                #   Использование централизованной логики фильтрации из ядра RAGSystem 
                #   гарантирует одинаковое поведение API и внутренних модулей генерации.
                rag_results = rag_system.filter_by_score(rag_results, min_score)

            if rag_results:
                # Почему: единый формат контекста через `format_context()` при наличии, иначе простой join.
                if hasattr(rag_system, "format_context"):
                    context = rag_system.format_context(rag_results)
                else:
                    context = "\\n".join([r.get("text", "") for r in rag_results])
                prompt = f"Context:\\n{context}\\n\\nQuestion: {prompt}"
        except Exception as e:
            # Продолжаем без RAG если ошибка
            pass
    
    result = await foundry_client.generate_text(prompt, **params)
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
    """Чат с поддержкой истории сообщений"""
    messages = request.get("messages", [])

    # Получение параметров RAG и системных инструкций
    use_rag = request.get("use_rag", False)
    system_prompt = request.get("system_prompt")
    min_score = float(request.get("min_score", 0.0))

    if not messages:
        return {"success": False, "error": "Messages are required"}
    
    # Преобразование истории в единый промпт
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
    
    # Интеграция RAG в контекст чата
    if use_rag:
        # Определение запроса: использование последнего сообщения пользователя
        # Search query definition: using the last user message
        last_user_content = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
        if last_user_content:
            try:
                # Поиск релевантных данных в векторной базе
                rag_results = await rag_system.search(last_user_content, top_k=3)

                # Фильтрация результатов по порогу схожести
                if rag_results and min_score > 0 and hasattr(rag_system, "filter_by_score"):
                    # ПОЧЕМУ ВЫБРАН ЭТОТ МЕТОД:
                    #   Гарантия консистентности логики отбора контекста во всей системе.
                    rag_results = rag_system.filter_by_score(rag_results, min_score)

                if rag_results:
                    # Форматирование найденных фрагментов и вставка в начало промпта
                    context = rag_system.format_context(rag_results) if hasattr(rag_system, "format_context") else ""
                    if context:
                        prompt_parts.insert(0, f"Context:\\n{context}")
            except Exception:
                # Игнорирование ошибок RAG для сохранения работоспособности базового чата
                pass

    # Вставка явной системной инструкции в начало контекста
    if system_prompt:
        # Обоснование: системный промпт из параметров запроса должен иметь 
        # приоритет над историей и контекстом RAG для управления поведением модели.
        # System prompt from request params takes precedence for behavior control.
        prompt_parts.insert(0, f"System: {system_prompt}")

    prompt = "\\n".join(prompt_parts)
    
    params = {
        "model": request.get("model"),
        "temperature": request.get("temperature", 0.7),
        "max_tokens": request.get("max_tokens", 2048)
    }
    
    await foundry_client._update_base_url()
    result = await foundry_client.generate_text(prompt, **params)
    
    if result["success"]:
        # Синхронизация истории: добавление ответа модели
        # History synchronization: addition of the model response
        messages.append({
            "role": "assistant",
            "content": result["content"]
        })

        # Автоматическое сохранение при каждом успешном ответе
        # Automatic saving on every successful response
        _save_session_history(messages)

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