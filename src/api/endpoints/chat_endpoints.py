# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Chat Endpoints
# =============================================================================
# Description:
#   Session-based chat endpoints for interactive AI conversations.
#   POST /api/v1/chat/start          — create new session (UUID)
#   POST /api/v1/chat/message        — send message, get response
#   POST /api/v1/chat/stream         — streaming message (SSE)
#   GET  /api/v1/chat/history/{id}   — get session history
#   DELETE /api/v1/chat/session/{id} — delete session
#   POST /api/v1/chat/history/save   — persist history to disk
#   GET  /api/v1/chat/models         — list available Foundry models
#
#   Sessions are stored in-memory (chat_sessions dict).
#   Auto-translation: enabled via config translator.enabled.
#
# File: chat_endpoints.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
# Changes in 0.6.1:
#   - Updated version to match project
#   - Added source_lang translation support in /chat/message
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import json
import uuid
import time
import os
from typing import Dict, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path

from ...models.foundry_client import foundry_client
from ...utils.translator import translator
from ...core.config import config as app_config

router = APIRouter()


def _translate_enabled() -> bool:
    return app_config.get_raw_config().get("translator", {}).get("enabled", False)

# Хранение сессий чата в памяти
chat_sessions: Dict[str, List[Dict]] = {}

@router.post("/chat/start")
async def start_chat_session(request: dict):
    """Начать новую сессию чата.

    Args:
        request: JSON body с полями:
            model (str): ID модели (default: 'default').

    Returns:
        dict: success, session_id (UUID), model, message.
    """
    session_id = str(uuid.uuid4())
    model = request.get("model", "default")
    
    chat_sessions[session_id] = []
    
    return {
        "success": True,
        "session_id": session_id,
        "model": model,
        "message": "Сессия чата начата"
    }

@router.post("/chat/message")
async def send_chat_message(request: dict):
    """Отправить сообщение в чат.

    Args:
        request: JSON body с полями:
            session_id (str):    ID сессии (обязательно).
            message (str):       Текст сообщения (обязательно).
            model (str):         ID модели (optional).
            temperature (float): Температура (default: 0.7).
            max_tokens (int):    Максимум токенов (default: 2048).

    Returns:
        dict: success, response, session_id.

    Raises:
        HTTPException 400: Неверный session_id или пустое сообщение.
        HTTPException 500: Ошибка генерации.
    """
    session_id = request.get("session_id")
    message = request.get("message", "")
    source_lang = request.get("source_lang", "auto")

    if not session_id or session_id not in chat_sessions:
        raise HTTPException(status_code=400, detail="Неверный ID сессии")

    if not message:
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")

    # Translate user message to English before sending to model
    translate_on = _translate_enabled()
    model_message = message
    if translate_on:
        tr = await translator.translate_for_model(message, source_lang=source_lang)
        if tr["success"] and tr["was_translated"]:
            model_message = tr["translated"]
            source_lang = tr["source_lang"]

    chat_sessions[session_id].append({"role": "user", "content": model_message})
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_sessions[session_id]])

    try:
        response = await foundry_client.generate_text(
            prompt,
            model=request.get("model"),
            temperature=request.get("temperature", 0.7),
            max_tokens=request.get("max_tokens", 2048),
        )
        if not response["success"]:
            raise Exception(response.get("error", "Unknown error"))

        ai_response = response.get("content", "")
        chat_sessions[session_id].append({"role": "assistant", "content": ai_response})

        # Translate response back to user language
        if translate_on and source_lang and source_lang != "en":
            tr_back = await translator.translate_response(ai_response, source_lang)
            if tr_back["success"]:
                ai_response = tr_back["translated"]

        return {"success": True, "response": ai_response, "session_id": session_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")

@router.post("/chat/stream")
async def send_chat_message_stream(request: dict):
    """Отправить сообщение в чат с стримингом.

    Args:
        request: JSON body с полями:
            session_id (str):    ID сессии (обязательно).
            message (str):       Текст сообщения (обязательно).
            model (str):         ID модели (optional).
            temperature (float): Температура (default: 0.7).
            max_tokens (int):    Максимум токенов (default: 2048).

    Returns:
        StreamingResponse: SSE-поток с чанками {chunk} и финальным {done: True}.

    Raises:
        HTTPException 400: Неверный session_id или пустое сообщение.
    """
    session_id = request.get("session_id")
    message = request.get("message", "")
    
    if not session_id or session_id not in chat_sessions:
        raise HTTPException(status_code=400, detail="Неверный ID сессии")
    
    if not message:
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
    
    # Добавить сообщение пользователя
    chat_sessions[session_id].append({"role": "user", "content": message})
    
    # Подготовить промпт
    conversation_history = chat_sessions[session_id]
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    async def generate_stream():
        try:
            accumulated_response = ""
            async for chunk in foundry_client.generate_stream(
                prompt=prompt,
                model=request.get("model"),
                temperature=request.get("temperature", 0.7),
                max_tokens=request.get("max_tokens", 2048)
            ):
                if chunk["success"] and not chunk.get("finished", False):
                    content = chunk.get("content", "")
                    accumulated_response += content
                    yield f"data: {json.dumps({'chunk': content})}\n\n"
                elif chunk.get("finished", False):
                    break
            
            # Добавить полный ответ в историю
            chat_sessions[session_id].append({"role": "assistant", "content": accumulated_response})
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Получить историю разговора.

    Args:
        session_id: UUID сессии чата.

    Returns:
        dict: success, session_id, history (list of {role, content}).

    Raises:
        HTTPException 404: Сессия не найдена.
    """
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    return {
        "success": True,
        "session_id": session_id,
        "history": chat_sessions[session_id]
    }

@router.delete("/chat/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Удалить сессию чата.

    Args:
        session_id: UUID сессии чата.

    Returns:
        dict: success, message.

    Raises:
        HTTPException 404: Сессия не найдена.
    """
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"success": True, "message": "Сессия удалена"}
    else:
        raise HTTPException(status_code=404, detail="Сессия не найдена")


@router.post("/chat/history/save")
async def save_chat_history(request: dict) -> dict:
    """! Сохраняет историю чата на диск.

    Содержимое сохраняется в: ~/.ai-assistant-chat-history/

    Args:
        request: JSON body с полями:
            messages (list):    Список сообщений {role, content} (обязательно).
            session_id (str):   UUID сессии (optional, генерируется если пусто).
            model (str):        ID модели (optional).
            title (str):        Заголовок чата (optional).
            aborted (bool):     Был ли чат прерван (default: False).

    Returns:
        dict: success, file (path to saved JSON), session_id.

    Raises:
        HTTPException 400: messages отсутствуют или пусты.
    """
    messages: List[Dict] = request.get("messages") or []
    if not messages:
        raise HTTPException(status_code=400, detail="messages is required")

    session_id: str = request.get("session_id") or str(uuid.uuid4())
    model: str = request.get("model") or ""
    title: str = request.get("title") or ""
    aborted: bool = bool(request.get("aborted", False))

    history_dir = Path.home() / ".ai-assistant-chat-history"
    history_dir.mkdir(parents=True, exist_ok=True)

    ts = int(time.time())
    file_path = history_dir / f"{session_id}_{ts}.json"

    payload = {
        "session_id": session_id,
        "title": title,
        "model": model,
        "aborted": aborted,
        "created_at": ts,
        "messages": messages,
    }
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "success": True,
        "file": str(file_path),
        "session_id": session_id
    }

@router.get("/chat/models")
async def get_available_models():
    """Получить список доступных моделей.

    Returns:
        dict: success, models (list of {id, name, type, size}), count.
    """
    try:
        models_response = await foundry_client.list_available_models()
        
        if models_response.get("success", False):
            foundry_models = models_response.get("models", [])
            
            chat_models = []
            for model in foundry_models:
                model_id = model.get('id', '')
                if model_id:
                    chat_models.append({
                        'id': model_id,
                        'name': model_id,
                        'type': 'AI Model',
                        'size': 'Unknown'
                    })
            
            return {
                "success": True,
                "models": chat_models,
                "count": len(chat_models)
            }
        else:
            return {
                "success": False,
                "error": models_response.get("error", "Не удалось получить список моделей"),
                "models": []
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "models": []
        }