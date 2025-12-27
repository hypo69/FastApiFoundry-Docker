# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Chat Endpoints (Refactored)
# =============================================================================
# Описание:
#   Упрощенные endpoints для интерактивного чата с AI моделями
#
# File: chat_endpoints.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import json
import uuid
from typing import Dict, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ...models.foundry_client import foundry_client

router = APIRouter()

# Хранение сессий чата в памяти
chat_sessions: Dict[str, List[Dict]] = {}

@router.post("/chat/start")
async def start_chat_session(request: dict):
    """Начать новую сессию чата"""
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
    """Отправить сообщение в чат"""
    session_id = request.get("session_id")
    message = request.get("message", "")
    
    if not session_id or session_id not in chat_sessions:
        raise HTTPException(status_code=400, detail="Неверный ID сессии")
    
    if not message:
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
    
    # Добавить сообщение пользователя
    chat_sessions[session_id].append({"role": "user", "content": message})
    
    # Подготовить промпт из истории
    conversation_history = chat_sessions[session_id]
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    try:
        response = await foundry_client.generate_text(
            prompt,
            model=request.get("model"),
            temperature=request.get("temperature", 0.7),
            max_tokens=request.get("max_tokens", 2048)
        )
        
        if response["success"]:
            ai_response = response.get("content", "")
            chat_sessions[session_id].append({"role": "assistant", "content": ai_response})
            
            return {
                "success": True,
                "response": ai_response,
                "session_id": session_id
            }
        else:
            raise Exception(response.get("error", "Unknown error"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")

@router.post("/chat/stream")
async def send_chat_message_stream(request: dict):
    """Отправить сообщение в чат с стримингом"""
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
    """Получить историю разговора"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    return {
        "success": True,
        "session_id": session_id,
        "history": chat_sessions[session_id]
    }

@router.delete("/chat/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Удалить сессию чата"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"success": True, "message": "Сессия удалена"}
    else:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

@router.get("/chat/models")
async def get_available_models():
    """Получить список доступных моделей"""
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