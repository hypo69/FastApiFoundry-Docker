# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Logging and Monitoring API Endpoints
# =============================================================================
# Описание:
#   API endpoints для мониторинга логов, метрик производительности и здоровья системы
#
# File: logging_endpoints.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime

from ...utils.log_analyzer import log_analyzer
from ...utils.logging_system import get_logger

logger = get_logger("logging-api")
router = APIRouter(prefix="/api/v1/logs", tags=["Logging & Monitoring"])

@router.get("/health", response_model=Dict[str, Any])
async def get_system_health():
    """
    Получить общее состояние системы на основе анализа логов
    
    Returns:
        Dict с информацией о состоянии системы, ошибках и метриках
    """
    logger.info("Запрос состояния системы через API")
    
    try:
        health_data = await log_analyzer.get_system_health()
        
        logger.info("Состояние системы получено", 
                   status=health_data.get("status"),
                   errors=health_data.get("metrics", {}).get("errors_count", 0))
        
        return {
            "success": True,
            "data": health_data,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.exception("Ошибка получения состояния системы", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting system health: {e}")

@router.get("/errors", response_model=Dict[str, Any])
async def get_error_summary(
    hours: int = Query(24, ge=1, le=168, description="Период анализа в часах (1-168)")
):
    """
    Получить сводку ошибок за указанный период
    
    Args:
        hours: Количество часов для анализа (по умолчанию 24)
        
    Returns:
        Dict с информацией об ошибках, их типах и временной динамике
    """
    logger.info("Запрос сводки ошибок", period_hours=hours)
    
    try:
        error_summary = await log_analyzer.get_error_summary(hours)
        
        logger.info("Сводка ошибок получена", 
                   total_errors=error_summary.get("total_errors", 0),
                   period_hours=hours)
        
        return {
            "success": True,
            "data": error_summary,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.exception("Ошибка получения сводки ошибок", 
                        period_hours=hours, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting error summary: {e}")

@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168, description="Период анализа в часах (1-168)")
):
    """
    Получить метрики производительности за указанный период
    
    Args:
        hours: Количество часов для анализа (по умолчанию 24)
        
    Returns:
        Dict с метриками API, моделей и системы
    """
    logger.info("Запрос метрик производительности", period_hours=hours)
    
    try:
        performance_metrics = await log_analyzer.get_performance_metrics(hours)
        
        api_metrics = performance_metrics.get("api_performance", {})
        logger.info("Метрики производительности получены",
                   period_hours=hours,
                   api_requests=api_metrics.get("total_requests", 0),
                   avg_response_time=api_metrics.get("avg_response_time", 0))
        
        return {
            "success": True,
            "data": performance_metrics,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.exception("Ошибка получения метрик производительности", 
                        period_hours=hours, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {e}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_logging_stats():
    """
    Получить общую статистику системы логирования
    
    Returns:
        Dict с информацией о файлах логов, их размерах и статистике
    """
    logger.info("Запрос статистики логирования")
    
    try:
        from pathlib import Path
        import os
        
        logs_dir = Path("logs")
        
        if not logs_dir.exists():
            return {
                "success": True,
                "data": {
                    "logs_directory_exists": False,
                    "message": "Logs directory not found"
                },
                "timestamp": datetime.now()
            }
        
        # Сбор информации о файлах логов
        log_files = []
        total_size = 0
        
        for log_file in logs_dir.glob("*.log"):
            try:
                stat = log_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                total_size += size_mb
                
                log_files.append({
                    "name": log_file.name,
                    "size_mb": round(size_mb, 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "type": "standard"
                })
            except Exception as e:
                logger.warning(f"Ошибка получения информации о файле {log_file}: {e}")
        
        # Структурированные логи
        for log_file in logs_dir.glob("*.jsonl"):
            try:
                stat = log_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                total_size += size_mb
                
                log_files.append({
                    "name": log_file.name,
                    "size_mb": round(size_mb, 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "type": "structured"
                })
            except Exception as e:
                logger.warning(f"Ошибка получения информации о файле {log_file}: {e}")
        
        stats = {
            "logs_directory_exists": True,
            "total_log_files": len(log_files),
            "total_size_mb": round(total_size, 2),
            "log_files": sorted(log_files, key=lambda x: x["modified"], reverse=True),
            "disk_usage": {
                "logs_directory": str(logs_dir.absolute()),
                "total_size_mb": round(total_size, 2)
            }
        }
        
        logger.info("Статистика логирования получена",
                   total_files=len(log_files),
                   total_size_mb=round(total_size, 2))
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.exception("Ошибка получения статистики логирования", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting logging stats: {e}")

@router.post("/test", response_model=Dict[str, Any])
async def test_logging_system():
    """
    Тестировать систему логирования (создать тестовые записи)
    
    Returns:
        Dict с результатами тестирования
    """
    logger.info("Запуск тестирования системы логирования")
    
    try:
        # Создание тестовых записей разных уровней
        test_logger = get_logger("logging-test")
        
        test_logger.debug("Тестовое debug сообщение", test_type="debug", test_id=1)
        test_logger.info("Тестовое info сообщение", test_type="info", test_id=2)
        test_logger.warning("Тестовое warning сообщение", test_type="warning", test_id=3)
        
        # Тест таймера
        with test_logger.timer("test_operation", test_id=4):
            import asyncio
            await asyncio.sleep(0.1)  # Имитация работы
        
        # Тест логирования API запроса
        test_logger.log_api_request(
            method="POST",
            path="/api/v1/logs/test",
            status_code=200,
            duration=0.05,
            test_id=5
        )
        
        # Тест логирования операции с моделью
        test_logger.log_model_operation(
            model_id="test-model",
            operation="test_generation",
            status="success",
            duration=0.2,
            test_id=6
        )
        
        logger.info("Тестирование системы логирования завершено успешно")
        
        return {
            "success": True,
            "data": {
                "message": "Logging system test completed successfully",
                "test_records_created": 6,
                "test_types": ["debug", "info", "warning", "timer", "api_request", "model_operation"]
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.exception("Ошибка тестирования системы логирования", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error testing logging system: {e}")

@router.get("/recent", response_model=Dict[str, Any])
async def get_recent_logs(
    level: Optional[str] = Query(None, description="Фильтр по уровню (debug, info, warning, error)"),
    limit: int = Query(50, ge=1, le=1000, description="Количество записей (1-1000)")
):
    """
    Получить последние записи из логов
    
    Args:
        level: Фильтр по уровню логирования
        limit: Максимальное количество записей
        
    Returns:
        Dict с последними записями логов
    """
    logger.info("Запрос последних записей логов", level=level, limit=limit)
    
    try:
        from pathlib import Path
        import json
        
        logs_dir = Path("logs")
        recent_logs = []
        
        # Чтение структурированных логов
        for log_file in logs_dir.glob("*-structured.jsonl"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    # Читаем последние записи
                    for line in lines[-limit*2:]:  # Берем больше для фильтрации
                        try:
                            entry = json.loads(line.strip())
                            
                            # Фильтр по уровню
                            if level and entry.get("level") != level:
                                continue
                            
                            recent_logs.append({
                                "timestamp": entry.get("timestamp"),
                                "level": entry.get("level"),
                                "logger": entry.get("logger"),
                                "message": entry.get("message"),
                                "file": log_file.name
                            })
                            
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                logger.warning(f"Ошибка чтения файла {log_file}: {e}")
        
        # Сортировка по времени и ограничение
        recent_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        recent_logs = recent_logs[:limit]
        
        logger.info("Последние записи логов получены",
                   total_records=len(recent_logs),
                   level_filter=level,
                   limit=limit)
        
        return {
            "success": True,
            "data": {
                "logs": recent_logs,
                "total_returned": len(recent_logs),
                "level_filter": level,
                "limit": limit
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.exception("Ошибка получения последних записей логов", 
                        level=level, limit=limit, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error getting recent logs: {e}")