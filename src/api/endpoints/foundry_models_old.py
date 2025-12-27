# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Models Management API
# =============================================================================
# Описание:
#   API endpoints для управления моделями в Foundry
#   Загрузка, выгрузка и получение списка доступных моделей
#
# File: foundry_models.py
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

import subprocess
import asyncio
import aiohttp
import os
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/foundry/models", tags=["foundry-models"])

def get_foundry_url():
    """Получить URL Foundry из переменной окружения"""
    return os.getenv('FOUNDRY_BASE_URL', 'http://localhost:50477/v1/')

@router.get("/available")
async def list_available_models():
    """Получить список всех доступных моделей для загрузки"""
    # Популярные модели для загрузки
    available_models = [
        {
            "id": "qwen2.5-0.5b-instruct-generic-cpu:4",
            "name": "Qwen 2.5 0.5B (CPU)",
            "size": "0.8 GB",
            "type": "cpu",
            "description": "Самая легкая CPU модель"
        },
        {
            "id": "qwen2.5-1.5b-instruct-generic-cpu:4", 
            "name": "Qwen 2.5 1.5B (CPU)",
            "size": "1.78 GB",
            "type": "cpu",
            "description": "Средняя CPU модель"
        },
        {
            "id": "deepseek-r1-distill-qwen-7b-generic-cpu:3",
            "name": "DeepSeek R1 Distill 7B (CPU)",
            "size": "6.43 GB", 
            "type": "cpu",
            "description": "Продвинутая CPU модель"
        },
        {
            "id": "phi-3-mini-4k-instruct-openvino-gpu:1",
            "name": "Phi-3 Mini 4K (GPU)",
            "size": "2.4 GB",
            "type": "gpu", 
            "description": "GPU модель"
        }
    ]
    
    return {
        "success": True,
        "models": available_models,
        "count": len(available_models)
    }

@router.get("/loaded")
async def list_loaded_models():
    """Получить список загруженных моделей в Foundry"""
    try:
        foundry_url = get_foundry_url()
        base_url = foundry_url.rstrip('/v1/').rstrip('/')
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{base_url}/v1/models', timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('data', [])
                    
                    # Форматируем для фронтенда
                    formatted_models = []
                    for model in models:
                        formatted_models.append({
                            "id": model.get('id', 'unknown'),
                            "name": model.get('id', 'unknown'),
                            "status": "loaded",
                            "type": "unknown"
                        })
                    
                    return {
                        "success": True,
                        "models": formatted_models,
                        "count": len(formatted_models)
                    }
                else:
                    return {
                        "success": False,
                        "models": [],
                        "error": f"HTTP {response.status}"
                    }
    except Exception as e:
        logger.error(f"Error listing loaded models: {e}")
        return {
            "success": False,
            "models": [],
            "error": str(e)
        }

@router.post("/pull")
async def pull_model(request: dict):
    """Загрузить модель в Foundry"""
    model_id = request.get("model_id")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")
    
    try:
        logger.info(f"Starting model pull: {model_id}")
        
        # Запускаем foundry model pull в фоне
        process = subprocess.Popen(
            ['foundry', 'model', 'load', model_id],  # Правильная команда foundry model load
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Сохраняем PID процесса для отслеживания
        # В реальном приложении можно использовать Redis или базу данных
        
        return {
            "success": True,
            "message": f"Начата загрузка модели {model_id}",
            "model_id": model_id,
            "status": "downloading",
            "pid": process.pid
        }
        
    except FileNotFoundError:
        logger.error("Foundry command not found")
        return {
            "success": False,
            "error": "Foundry не установлен или не найден в PATH"
        }
    except Exception as e:
        logger.error(f"Error pulling model {model_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/remove")
async def remove_model(request: dict):
    """Удалить (выгрузить) модель из Foundry"""
    model_id = request.get("model_id")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")
    
    try:
        # Используем правильную команду foundry model unload
        result = subprocess.run(
            ['foundry', 'model', 'unload', model_id],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info(f"Model {model_id} unloaded successfully")
            return {
                "success": True,
                "message": f"Модель {model_id} выгружена",
                "model_id": model_id
            }
        else:
            logger.error(f"Failed to unload model {model_id}: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr or "Failed to unload model"
            }
            
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Foundry не установлен или не найден в PATH"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Операция выгрузки превысила время ожидания"
        }
    except Exception as e:
        logger.error(f"Error unloading model {model_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/auto-load-default")
async def auto_load_default_model():
    """Автоматически загрузить модель по умолчанию из config.json"""
    try:
        # Читаем config.json
        import json
        from pathlib import Path
        
        config_path = Path("config.json")
        if not config_path.exists():
            return {
                "success": False,
                "error": "Config file not found"
            }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        default_model = config.get('foundry_ai', {}).get('default_model')
        if not default_model:
            return {
                "success": False,
                "error": "No default model specified in config"
            }
        
        # Проверяем загружена ли модель
        loaded_result = await list_loaded_models()
        if loaded_result["success"]:
            for model in loaded_result["models"]:
                if model["id"] == default_model:
                    return {
                        "success": True,
                        "message": f"Default model {default_model} already loaded",
                        "model_id": default_model,
                        "status": "already_loaded"
                    }
        
        # Загружаем модель
        logger.info(f"Auto-loading default model: {default_model}")
        
        process = subprocess.Popen(
            ['foundry', 'model', 'load', default_model],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return {
            "success": True,
            "message": f"Started loading default model {default_model}",
            "model_id": default_model,
            "status": "loading"
        }
        
    except Exception as e:
        logger.error(f"Error auto-loading default model: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/status/{model_id}")
async def get_model_status(model_id: str):
    """Получить статус конкретной модели"""
    try:
        loaded_result = await list_loaded_models()
        if loaded_result["success"]:
            for model in loaded_result["models"]:
                if model["id"] == model_id:
                    return {
                        "success": True,
                        "model_id": model_id,
                        "status": "loaded"
                    }
        
        return {
            "success": True,
            "model_id": model_id,
            "status": "not_loaded"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }