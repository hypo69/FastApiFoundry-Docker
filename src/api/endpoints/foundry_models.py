# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Foundry Models Management API
# =============================================================================
# Описание:
#   API endpoints для управления моделями в Foundry
#   Использует правильные команды foundry model
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
    try:
        from pathlib import Path
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "list-models.ps1"
        
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path), '-Type', 'available'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Парсим вывод foundry model list
            models = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('Available') and not line.startswith('---') and not line.startswith('✅') and not line.startswith('Getting'):
                    models.append({
                        "id": line,
                        "name": line,
                        "status": "available",
                        "type": "unknown"
                    })
            
            return {
                "success": True,
                "models": models,
                "count": len(models)
            }
        else:
            return {
                "success": False,
                "models": [],
                "error": result.stderr or "Failed to list models"
            }
            
    except Exception as e:
        logger.error(f"Error listing available models: {e}")
        return {
            "success": False,
            "models": [],
            "error": str(e)
        }

@router.get("/loaded")
async def list_loaded_models():
    """Получить список загруженных моделей в Foundry"""
    try:
        from pathlib import Path
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "list-models.ps1"
        
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path), '-Type', 'loaded'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Парсим вывод foundry service list
            models = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line and not line.startswith('Service') and not line.startswith('---') and not line.startswith('✅') and not line.startswith('Getting'):
                    models.append({
                        "id": line,
                        "name": line,
                        "status": "loaded",
                        "type": "unknown"
                    })
            
            return {
                "success": True,
                "models": models,
                "count": len(models)
            }
        else:
            return {
                "success": False,
                "models": [],
                "error": result.stderr or "Failed to list loaded models"
            }
            
    except Exception as e:
        logger.error(f"Error listing loaded models: {e}")
        return {
            "success": False,
            "models": [],
            "error": str(e)
        }

@router.post("/download")
async def download_model(request: dict):
    """Скачать модель в кэш Foundry"""
    model_id = request.get("model_id")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")
    
    try:
        logger.info(f"Starting model download: {model_id}")
        
        from pathlib import Path
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "download-model.ps1"
        
        process = subprocess.Popen(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path), '-ModelId', model_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return {
            "success": True,
            "message": f"Начато скачивание модели {model_id}",
            "model_id": model_id,
            "status": "downloading",
            "pid": process.pid
        }
        
    except Exception as e:
        logger.error(f"Error downloading model {model_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/remove")
async def unload_model(request: dict):
    """Выгрузить модель из Foundry"""
    model_id = request.get("model_id")
    if not model_id:
        raise HTTPException(status_code=400, detail="model_id is required")
    
    try:
        # Используем PowerShell скрипт с абсолютным путем
        from pathlib import Path
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "unload-model.ps1"
        
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script_path), '-ModelId', model_id],
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
            ['powershell', '-Command', f'foundry model load {default_model}'],
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