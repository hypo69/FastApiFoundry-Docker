# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker контейнер для FastAPI Foundry
# =============================================================================
# Описание:
#   Многоэтапная сборка Docker контейнера для FastAPI Foundry
#   Включает все зависимости, RAG систему и веб-интерфейс
#
# File: Dockerfile
# Project: FastAPI Foundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY static/ ./static/
COPY docs/ ./docs/
COPY mcp-servers/ ./mcp-servers/
COPY run.py .
COPY rag_indexer.py .
COPY .env.example .env

# Создание директорий для данных
RUN mkdir -p logs rag_index

# Создание пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Открытие порта
EXPOSE 8000

# Переменные окружения
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Команда запуска
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "8000"]