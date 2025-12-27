# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Chat Endpoints
# =============================================================================
# Описание:
#   Endpoints для чат функциональности
#
# File: chat_endpoints.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
import uuid
import time

router = APIRouter()

# Простое хранилище сессий в памяти
chat_sessions = {}

@router.post("/chat/message")
async def send_chat_message(request: Dict[str, Any]):
    """Отправить сообщение в чат"""
    message = request.get("message", "")
    session_id = request.get("session_id", "")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Создаем сессию если не существует
    if not session_id or len(session_id) < 5:
        session_id = str(uuid.uuid4())
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    # Добавляем сообщение пользователя
    user_message = {
        "role": "user",
        "content": message,
        "timestamp": time.time()
    }
    chat_sessions[session_id].append(user_message)
    
    # Генерируем ответ (заглушка)
    bot_response = {
        "role": "assistant", 
        "content": f"Mock response to: {message}",
        "timestamp": time.time()
    }
    chat_sessions[session_id].append(bot_response)
    
    return {
        "success": True,
        "session_id": session_id,
        "response": bot_response["content"],
        "message_count": len(chat_sessions[session_id])
    }

@router.get("/chat/history")
async def get_chat_history(session_id: str = Query(..., description="Chat session ID")):
    """Получить историю чата"""
    if not session_id or session_id not in chat_sessions:
        return {
            "success": True,
            "session_id": session_id,
            "messages": [],
            "message_count": 0
        }
    
    return {
        "success": True,
        "session_id": session_id,
        "messages": chat_sessions[session_id],
        "message_count": len(chat_sessions[session_id])
    }

@router.delete("/chat/session/{session_id}")
async def clear_chat_session(session_id: str):
    """Очистить сессию чата"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return {
        "success": True,
        "message": f"Session {session_id} cleared"
    }