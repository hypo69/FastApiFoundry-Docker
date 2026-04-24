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
# Copyright: © 2026 hypo69
# Copyright: © 2026 hypo69
# Date: 9 декабря 2025
# =============================================================================

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
import uuid
import time # Добавлено для работы с метками времени
import logging # Добавлено для логирования
from src.core.config import config # Добавлено для доступа к настройкам конфигурации

router = APIRouter()

# Простое хранилище сессий в памяти
chat_sessions = {}

# Добавлено для периодической очистки старых сессий
_last_cleanup_time = 0
_cleanup_interval_seconds = 60 * 5 # Интервал очистки: каждые 5 минут

logger = logging.getLogger(__name__) # Инициализация логгера для модуля

def _perform_session_cleanup():
    """
    Очищает старые сессии из памяти на основе времени последней активности.
    Сессии, которые не использовались дольше `session_retention_minutes`, удаляются.
    """
    global _last_cleanup_time
    current_time = time.time()

    # Проверка, чтобы не выполнять очистку слишком часто
    if (current_time - _last_cleanup_time) < _cleanup_interval_seconds:
        return

    _last_cleanup_time = current_time
    
    # Получение срока хранения из конфигурации, по умолчанию 60 минут
    retention_minutes = config.get_section("chat_settings").get("session_retention_minutes", 60)
    retention_seconds = retention_minutes * 60
    
    sessions_to_delete = []
    # Итерация по копии словаря, чтобы избежать RuntimeError при изменении размера во время итерации
    for session_id, messages in list(chat_sessions.items()):
        # Если сессия пуста или последнее сообщение слишком старое, пометить для удаления
        if not messages or (current_time - messages[-1]["timestamp"]) > retention_seconds:
            sessions_to_delete.append(session_id)
    
    for session_id in sessions_to_delete:
        del chat_sessions[session_id]
        logger.debug(f"Очищена старая сессия чата: {session_id}")
    
    if sessions_to_delete:
        logger.info(f"Очищено {len(sessions_to_delete)} старых сессий чата.")


@router.post("/chat/message")
async def send_chat_message(request: Dict[str, Any]):
    """Отправить сообщение в чат"""
    _perform_session_cleanup() # Выполнить очистку перед обработкой запроса

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
    _perform_session_cleanup() # Выполнить очистку перед обработкой запроса
    """Получить историю чата"""
    if not session_id or session_id not in chat_sessions:
        return {
            "success": True,
            "session_id": session_id,
            "messages": [],
            "message_count": 0
        }
    
    # Обновляем timestamp последнего сообщения в сессии, чтобы пометить её как активную
    # Это предотвращает удаление активно используемых сессий
    if chat_sessions[session_id]:
        chat_sessions[session_id][-1]["timestamp"] = time.time()

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
        logger.debug(f"Сессия чата {session_id} удалена вручную.")
    
    return {
        "success": True,
        "message": f"Session {session_id} cleared"
    }