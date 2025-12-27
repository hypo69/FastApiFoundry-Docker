# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Chat Endpoints
# =============================================================================
# Описание:
#   Endpoints для интерактивного чата с AI моделями
#   Поддержка сессий разговора и стриминга ответов
#
# File: chat_endpoints.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 26 декабря 2025
# =============================================================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ...models.foundry_client import foundry_client
# from ...rag.rag_system import rag_system

# Заглушка для RAG системы
class DummyRAGSystem:
    async def search(self, query, top_k=3):
        return []

rag_system = DummyRAGSystem()
import json
import uuid
import asyncio
from typing import List, Dict, Optional

router = APIRouter()

# Хранение сессий чата (в памяти, для простоты)
chat_sessions: Dict[str, List[Dict]] = {}

@router.post("/chat/start")
async def start_chat_session(request: dict):
    """Начать новую сессию чата"""
    session_id = str(uuid.uuid4())
    model = request.get("model", "default")
    use_rag = request.get("use_rag", False)
    
    chat_sessions[session_id] = []
    
    return {
        "success": True,
        "session_id": session_id,
        "model": model,
        "use_rag": use_rag,
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
    
    # Добавить сообщение пользователя в историю
    chat_sessions[session_id].append({"role": "user", "content": message})
    
    # Получить настройки сессии (предполагаем, что они хранятся где-то, или передать в запросе)
    model = request.get("model")
    use_rag = request.get("use_rag", False)
    temperature = request.get("temperature", 0.7)
    max_tokens = request.get("max_tokens", 2048)
    
    # Подготовить промпт из истории разговора
    conversation_history = chat_sessions[session_id]
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    # RAG enhancement
    if use_rag:
        try:
            rag_results = await rag_system.search(message, top_k=3)
            if rag_results:
                context = "\n".join([r.get("text", "") for r in rag_results])
                prompt = f"Context:\n{context}\n\n{prompt}"
        except Exception as e:
            print(f"RAG error: {e}")
    
    # Генерация ответа
    try:
        response = await foundry_client.generate_text(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if response["success"]:
            ai_response = response.get("content", "")
        else:
            raise Exception(response.get("error", "Unknown error"))
        
        # Добавить ответ AI в историю
        chat_sessions[session_id].append({"role": "assistant", "content": ai_response})
        
        return {
            "success": True,
            "response": ai_response,
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")

@router.post("/chat/stream")
async def send_chat_message_stream(request: dict):
    """Отправить сообщение в чат с стримингом ответа"""
    session_id = request.get("session_id")
    message = request.get("message", "")
    
    if not session_id or session_id not in chat_sessions:
        raise HTTPException(status_code=400, detail="Неверный ID сессии")
    
    if not message:
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")
    
    # Добавить сообщение пользователя в историю
    chat_sessions[session_id].append({"role": "user", "content": message})
    
    model = request.get("model")
    use_rag = request.get("use_rag", False)
    temperature = request.get("temperature", 0.7)
    max_tokens = request.get("max_tokens", 2048)
    
    # Подготовить промпт
    conversation_history = chat_sessions[session_id]
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    if use_rag:
        try:
            rag_results = await rag_system.search(message, top_k=3)
            if rag_results:
                context = "\n".join([r.get("text", "") for r in rag_results])
                prompt = f"Context:\n{context}\n\n{prompt}"
        except Exception as e:
            print(f"RAG error: {e}")
    
    async def generate_stream():
        try:
            accumulated_response = ""
            async for chunk in foundry_client.generate_stream(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                if chunk["success"] and not chunk.get("finished", False):
                    content = chunk.get("content", "")
                    accumulated_response += content
                    yield f"data: {json.dumps({'chunk': content})}\n\n"
                elif chunk.get("finished", False):
                    break
            
            # После завершения стриминга добавить полный ответ в историю
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
        models_info = await foundry_client.list_available_models()
        if models_info.get("success", False):
            return {
                "success": True,
                "models": models_info.get("models", []),
                "count": models_info.get("count", 0)
            }
        else:
            return {
                "success": False,
                "error": models_info.get("error", "Не удалось получить список моделей"),
                "models": []
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "models": []
        }