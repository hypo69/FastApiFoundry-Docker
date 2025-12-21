# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry Data Models
# =============================================================================
# Описание:
#   Pydantic модели для запросов и ответов FastAPI Foundry
#   Валидация данных и автоматическая документация API
#
# File: models.py
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class GenerateRequest(BaseModel):
    """Запрос на генерацию текста"""
    
    prompt: str = Field(
        ...,
        description="Промпт для генерации",
        min_length=1,
        max_length=10000
    )
    
    model: Optional[str] = Field(
        None,
        description="Модель для использования (по умолчанию из конфига)"
    )
    
    temperature: Optional[float] = Field(
        None,
        description="Температура генерации (0.0-2.0)",
        ge=0.0,
        le=2.0
    )
    
    max_tokens: Optional[int] = Field(
        None,
        description="Максимум токенов для генерации",
        ge=1,
        le=8192
    )
    
    top_p: Optional[float] = Field(
        None,
        description="Top-p sampling (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    
    system_prompt: Optional[str] = Field(
        None,
        description="Системный промпт",
        max_length=5000
    )
    
    use_rag: bool = Field(
        True,
        description="Использовать RAG контекст"
    )
    
    rag_query: Optional[str] = Field(
        None,
        description="Кастомный запрос для RAG (по умолчанию используется prompt)"
    )

class GenerateResponse(BaseModel):
    """Ответ на генерацию текста"""
    
    success: bool = Field(..., description="Успешность операции")
    content: Optional[str] = Field(None, description="Сгенерированный текст")
    model: Optional[str] = Field(None, description="Использованная модель")
    tokens_used: Optional[int] = Field(None, description="Использовано токенов")
    finish_reason: Optional[str] = Field(None, description="Причина завершения")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время генерации")
    error: Optional[str] = Field(None, description="Ошибка (если есть)")
    rag_context: Optional[bool] = Field(None, description="Был ли использован RAG контекст")

class RAGSearchRequest(BaseModel):
    """Запрос поиска в RAG"""
    
    query: str = Field(
        ...,
        description="Поисковый запрос",
        min_length=1,
        max_length=1000
    )
    
    top_k: int = Field(
        5,
        description="Количество результатов",
        ge=1,
        le=20
    )

class RAGResult(BaseModel):
    """Результат поиска RAG"""
    
    source: str = Field(..., description="Источник документа")
    section: str = Field(..., description="Раздел документа")
    text: str = Field(..., description="Текст фрагмента")
    score: float = Field(..., description="Релевантность (0.0-1.0)")

class RAGSearchResponse(BaseModel):
    """Ответ поиска RAG"""
    
    success: bool = Field(..., description="Успешность поиска")
    results: List[RAGResult] = Field(default_factory=list, description="Результаты поиска")
    query: str = Field(..., description="Исходный запрос")
    total_found: int = Field(..., description="Всего найдено результатов")
    error: Optional[str] = Field(None, description="Ошибка (если есть)")

class ModelInfo(BaseModel):
    """Информация о модели"""
    
    id: str = Field(..., description="ID модели")
    name: Optional[str] = Field(None, description="Название модели")
    description: Optional[str] = Field(None, description="Описание")
    parameters: Optional[str] = Field(None, description="Количество параметров")
    type: Optional[str] = Field(None, description="Тип модели")
    provider: Optional[str] = Field(None, description="Провайдер модели")
    status: Optional[str] = Field(None, description="Статус модели")
    connected: Optional[bool] = Field(None, description="Подключена ли модель")

class ModelsResponse(BaseModel):
    """Ответ со списком моделей"""
    
    success: bool = Field(..., description="Успешность операции")
    models: List[ModelInfo] = Field(default_factory=list, description="Список моделей")
    count: int = Field(..., description="Количество моделей")
    error: Optional[str] = Field(None, description="Ошибка (если есть)")

class HealthResponse(BaseModel):
    """Ответ проверки здоровья"""
    
    status: str = Field(..., description="Статус сервера")
    foundry_url: str = Field(..., description="URL Foundry сервера")
    foundry_status: str = Field(..., description="Статус Foundry")
    rag_available: bool = Field(..., description="Доступность RAG")
    rag_loaded: bool = Field(..., description="Загружен ли RAG индекс")
    rag_chunks: int = Field(..., description="Количество RAG чанков")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время проверки")
    error: Optional[str] = Field(None, description="Ошибка (если есть)")

class ConfigResponse(BaseModel):
    """Ответ с конфигурацией"""
    
    foundry: Dict[str, Any] = Field(..., description="Конфигурация Foundry")
    api: Dict[str, Any] = Field(..., description="Конфигурация API")
    rag: Dict[str, Any] = Field(..., description="Конфигурация RAG")
    available_models: List[str] = Field(default_factory=list, description="Доступные модели")

class ErrorResponse(BaseModel):
    """Стандартный ответ с ошибкой"""
    
    error: str = Field(..., description="Описание ошибки")
    detail: Optional[str] = Field(None, description="Детали ошибки")
    timestamp: datetime = Field(default_factory=datetime.now, description="Время ошибки")
    request_id: Optional[str] = Field(None, description="ID запроса")

class BatchGenerateRequest(BaseModel):
    """Запрос на пакетную генерацию"""
    
    prompts: List[str] = Field(
        ...,
        description="Список промптов",
        min_items=1,
        max_items=10
    )
    
    model: Optional[str] = Field(None, description="Модель для всех промптов")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)
    use_rag: bool = Field(True, description="Использовать RAG для всех промптов")

class BatchGenerateResponse(BaseModel):
    """Ответ на пакетную генерацию"""
    
    success: bool = Field(..., description="Общий успех операции")
    results: List[GenerateResponse] = Field(..., description="Результаты для каждого промпта")
    total_prompts: int = Field(..., description="Всего промптов")
    successful: int = Field(..., description="Успешных генераций")
    failed: int = Field(..., description="Неудачных генераций")
    total_tokens: int = Field(..., description="Всего использовано токенов")
    timestamp: datetime = Field(default_factory=datetime.now)

class TunnelStartRequest(BaseModel):
    """Запрос на запуск туннеля"""
    
    tunnel_type: str = Field(
        ...,
        description="Тип туннеля",
        pattern="^(ngrok|cloudflared|localtunnel)$"
    )
    
    port: int = Field(
        8000,
        description="Порт для туннеля",
        ge=1,
        le=65535
    )
    
    subdomain: Optional[str] = Field(
        None,
        description="Кастомный поддомен (ngrok/localtunnel)",
        max_length=50
    )

class TunnelResponse(BaseModel):
    """Ответ операций с туннелем"""
    
    success: bool = Field(..., description="Успешность операции")
    url: Optional[str] = Field(None, description="URL туннеля")
    type: Optional[str] = Field(None, description="Тип туннеля")
    port: Optional[int] = Field(None, description="Порт")
    message: Optional[str] = Field(None, description="Сообщение")
    error: Optional[str] = Field(None, description="Ошибка")
    timestamp: datetime = Field(default_factory=datetime.now)

class TunnelStatusResponse(BaseModel):
    """Статус туннеля"""
    
    active: bool = Field(..., description="Активен ли туннель")
    type: Optional[str] = Field(None, description="Тип туннеля")
    url: Optional[str] = Field(None, description="URL туннеля")
    port: Optional[int] = Field(None, description="Порт")
    pid: Optional[int] = Field(None, description="Process ID")

# ============================================================================
# Модели для управления подключением моделей
# ============================================================================

class ModelConnectionRequest(BaseModel):
    """Запрос на подключение модели"""
    
    model_id: str = Field(
        ...,
        description="ID модели для подключения",
        min_length=1,
        max_length=200
    )
    
    model_name: Optional[str] = Field(
        None,
        description="Человекочитаемое название модели",
        max_length=100
    )
    
    provider: str = Field(
        "foundry",
        description="Провайдер модели (foundry, ollama, openai, anthropic)",
        pattern="^(foundry|ollama|openai|anthropic|custom)$"
    )
    
    endpoint_url: Optional[str] = Field(
        None,
        description="URL эндпоинта для кастомных провайдеров"
    )
    
    api_key: Optional[str] = Field(
        None,
        description="API ключ для провайдера (если требуется)"
    )
    
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Дополнительные параметры модели"
    )
    
    default_temperature: Optional[float] = Field(
        0.7,
        description="Температура по умолчанию",
        ge=0.0,
        le=2.0
    )
    
    default_max_tokens: Optional[int] = Field(
        2048,
        description="Максимум токенов по умолчанию",
        ge=1,
        le=32768
    )
    
    enabled: bool = Field(
        True,
        description="Включена ли модель"
    )

class ModelConnectionResponse(BaseModel):
    """Ответ на подключение модели"""
    
    success: bool = Field(..., description="Успешность операции")
    model_id: str = Field(..., description="ID подключенной модели")
    message: str = Field(..., description="Сообщение о результате")
    error: Optional[str] = Field(None, description="Ошибка (если есть)")
    timestamp: datetime = Field(default_factory=datetime.now)

class ConnectedModel(BaseModel):
    """Информация о подключенной модели"""
    
    model_id: str = Field(..., description="ID модели")
    model_name: Optional[str] = Field(None, description="Название модели")
    provider: str = Field(..., description="Провайдер")
    endpoint_url: Optional[str] = Field(None, description="URL эндпоинта")
    enabled: bool = Field(..., description="Включена ли модель")
    status: str = Field(..., description="Статус подключения (online, offline, error)")
    last_check: datetime = Field(..., description="Время последней проверки")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Параметры модели")
    usage_count: int = Field(0, description="Количество использований")
    avg_response_time: Optional[float] = Field(None, description="Среднее время ответа (сек)")

class ConnectedModelsResponse(BaseModel):
    """Ответ со списком подключенных моделей"""
    
    success: bool = Field(..., description="Успешность операции")
    models: List[ConnectedModel] = Field(..., description="Список подключенных моделей")
    total_count: int = Field(..., description="Общее количество моделей")
    online_count: int = Field(..., description="Количество онлайн моделей")
    default_model: Optional[str] = Field(None, description="Модель по умолчанию")
    timestamp: datetime = Field(default_factory=datetime.now)

class ModelUpdateRequest(BaseModel):
    """Запрос на обновление настроек модели"""
    
    model_name: Optional[str] = Field(None, description="Новое название")
    enabled: Optional[bool] = Field(None, description="Включить/выключить модель")
    default_temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    default_max_tokens: Optional[int] = Field(None, ge=1, le=32768)
    parameters: Optional[Dict[str, Any]] = Field(None, description="Обновить параметры")
    api_key: Optional[str] = Field(None, description="Обновить API ключ")

class ModelTestRequest(BaseModel):
    """Запрос на тестирование модели"""
    
    test_prompt: str = Field(
        "Hello, how are you?",
        description="Тестовый промпт",
        max_length=500
    )
    
    timeout: int = Field(
        30,
        description="Таймаут теста в секундах",
        ge=5,
        le=300
    )

class ModelTestResponse(BaseModel):
    """Ответ тестирования модели"""
    
    success: bool = Field(..., description="Успешность теста")
    model_id: str = Field(..., description="ID тестируемой модели")
    response_text: Optional[str] = Field(None, description="Ответ модели")
    response_time: Optional[float] = Field(None, description="Время ответа (сек)")
    tokens_used: Optional[int] = Field(None, description="Использовано токенов")
    error: Optional[str] = Field(None, description="Ошибка теста")
    timestamp: datetime = Field(default_factory=datetime.now)

class ModelProviderInfo(BaseModel):
    """Информация о провайдере моделей"""
    
    provider_id: str = Field(..., description="ID провайдера")
    name: str = Field(..., description="Название провайдера")
    description: str = Field(..., description="Описание")
    supported_features: List[str] = Field(..., description="Поддерживаемые функции")
    requires_api_key: bool = Field(..., description="Требует ли API ключ")
    default_endpoint: Optional[str] = Field(None, description="Эндпоинт по умолчанию")
    documentation_url: Optional[str] = Field(None, description="Ссылка на документацию")

class ProvidersResponse(BaseModel):
    """Ответ со списком провайдеров"""
    
    success: bool = Field(..., description="Успешность операции")
    providers: List[ModelProviderInfo] = Field(..., description="Список провайдеров")
    timestamp: datetime = Field(default_factory=datetime.now)

