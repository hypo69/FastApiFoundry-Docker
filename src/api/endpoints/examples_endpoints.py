# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Examples API Endpoints
# =============================================================================
# Описание:
#   API endpoints для запуска примеров из веб-интерфейса
#
# File: examples_endpoints.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from ...utils.logging_system import get_logger

logger = get_logger("examples-api")
router = APIRouter(prefix="/api/v1/examples", tags=["Examples"])

class RunExampleRequest(BaseModel):
    example_type: str

@router.post("/run", response_model=Dict[str, Any])
async def run_example(request: RunExampleRequest):
    """
    Запустить пример скрипта
    
    Args:
        request: Тип примера для запуска
        
    Returns:
        Dict с результатом выполнения примера
    """
    example_type = request.example_type
    logger.info("Запуск примера через API", example_type=example_type)
    
    # Определение файла примера
    example_files = {
        "client": "examples/example_client.py",
        "rag": "examples/example_rag_client.py", 
        "mcp": "examples/example_mcp_client.py",
        "model": "examples/example_model_client.py"
    }
    
    if example_type not in example_files:
        logger.error("Неизвестный тип примера", example_type=example_type)
        raise HTTPException(status_code=400, detail=f"Unknown example type: {example_type}")
    
    example_file = example_files[example_type]
    example_path = Path(example_file)
    
    if not example_path.exists():
        logger.error("Файл примера не найден", file=str(example_path))
        raise HTTPException(status_code=404, detail=f"Example file not found: {example_file}")
    
    try:
        start_time = time.time()
        
        with logger.timer("example_execution", example_type=example_type, file=example_file):
            # Запуск примера как subprocess
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(example_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=Path.cwd()
            )
            
            # Ожидание завершения с таймаутом
            try:
                stdout, _ = await asyncio.wait_for(process.communicate(), timeout=60.0)
                output = stdout.decode('utf-8', errors='replace')
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.warning("Пример превысил таймаут", example_type=example_type)
                output = "⚠️ Example execution timed out (60s limit)"
        
        execution_time = time.time() - start_time
        
        if process.returncode == 0:
            logger.info("Пример выполнен успешно", 
                       example_type=example_type, 
                       execution_time=execution_time)
            return {
                "success": True,
                "example_type": example_type,
                "output": output,
                "execution_time": execution_time,
                "return_code": process.returncode
            }
        else:
            logger.warning("Пример завершился с ошибкой", 
                          example_type=example_type,
                          return_code=process.returncode)
            return {
                "success": False,
                "example_type": example_type,
                "output": output,
                "execution_time": execution_time,
                "return_code": process.returncode,
                "error": f"Process exited with code {process.returncode}"
            }
            
    except Exception as e:
        execution_time = time.time() - start_time
        logger.exception("Критическая ошибка выполнения примера", 
                        example_type=example_type, 
                        error=str(e))
        return {
            "success": False,
            "example_type": example_type,
            "error": f"Error running example: {str(e)}",
            "execution_time": execution_time
        }

@router.get("/list", response_model=Dict[str, Any])
async def list_examples():
    """
    Получить список доступных примеров
    
    Returns:
        Dict со списком примеров и их статусом
    """
    logger.info("Запрос списка примеров")
    
    examples = [
        {
            "type": "client",
            "name": "API Client Demo",
            "file": "examples/example_client.py",
            "description": "Демонстрация всех API endpoints",
            "icon": "bi-play-fill"
        },
        {
            "type": "rag", 
            "name": "RAG Search Demo",
            "file": "examples/example_rag_client.py",
            "description": "Поиск в документации",
            "icon": "bi-search"
        },
        {
            "type": "mcp",
            "name": "MCP Client Demo", 
            "file": "examples/example_mcp_client.py",
            "description": "Model Context Protocol",
            "icon": "bi-link-45deg"
        },
        {
            "type": "model",
            "name": "Model Client Demo",
            "file": "examples/example_model_client.py", 
            "description": "Работа с моделями",
            "icon": "bi-cpu"
        }
    ]
    
    # Проверка существования файлов
    for example in examples:
        example_path = Path(example["file"])
        example["available"] = example_path.exists()
        if example["available"]:
            stat = example_path.stat()
            example["size"] = stat.st_size
            example["modified"] = stat.st_mtime
    
    available_count = sum(1 for ex in examples if ex["available"])
    
    logger.info("Список примеров получен", 
               total=len(examples), 
               available=available_count)
    
    return {
        "success": True,
        "examples": examples,
        "total_count": len(examples),
        "available_count": available_count
    }