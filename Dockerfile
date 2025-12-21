# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker контейнер для FastApiFoundry (Docker)
# =============================================================================
# Описание:
#   Docker контейнер с виртуальным окружением Python для FastApiFoundry
#   Использует venv для изоляции зависимостей и запускает run.py
#
# Примеры:
#   docker build -t fastapi-foundry:0.2.1 .
#   docker run -p 8000:8000 fastapi-foundry:0.2.1
#
# File: Dockerfile
# Project: FastApiFoundry (Docker)
# Version: 0.2.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Создание виртуального окружения (копирование существующего)
COPY venv/ ./venv/

# Обновление pip в существующем venv
RUN ./venv/Scripts/pip install --upgrade pip

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей в существующий venv
RUN ./venv/Scripts/pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/
COPY static/ ./static/
COPY docs/ ./docs/
COPY mcp-servers/ ./mcp-servers/
COPY run.py .
COPY rag_indexer.py .
COPY check_venv.py .
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
ENV PATH="/app/venv/Scripts:$PATH"
ENV HOST=0.0.0.0
ENV PORT=8000
ENV FASTAPI_FOUNDRY_MODE=production

# Проверка venv перед запуском
RUN ./venv/Scripts/python check_venv.py

# Команда запуска через venv
CMD ["./venv/Scripts/python", "run.py"]