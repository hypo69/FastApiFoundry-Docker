#!/bin/bash
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker управление для FastAPI Foundry
# =============================================================================
# Описание:
#   Скрипт для сборки, запуска и управления Docker контейнером
#   Включает команды для экспорта/импорта образа
#
# File: docker-manager.sh
# Project: FastAPI Foundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

set -e

IMAGE_NAME="fastapi-foundry"
CONTAINER_NAME="fastapi-foundry"
VERSION="latest"

show_help() {
    echo "FastAPI Foundry Docker Manager"
    echo ""
    echo "Использование: $0 [КОМАНДА]"
    echo ""
    echo "Команды:"
    echo "  build     - Собрать Docker образ"
    echo "  run       - Запустить контейнер"
    echo "  stop      - Остановить контейнер"
    echo "  restart   - Перезапустить контейнер"
    echo "  logs      - Показать логи контейнера"
    echo "  shell     - Войти в контейнер"
    echo "  clean     - Удалить контейнер и образ"
    echo "  export    - Экспортировать образ в tar файл"
    echo "  import    - Импортировать образ из tar файла"
    echo "  status    - Показать статус контейнера"
    echo "  help      - Показать эту справку"
}

build_image() {
    echo "🔨 Сборка Docker образа..."
    docker build -t $IMAGE_NAME:$VERSION .
    echo "✅ Образ собран: $IMAGE_NAME:$VERSION"
}

run_container() {
    echo "🚀 Запуск контейнера..."
    docker-compose up -d
    echo "✅ Контейнер запущен"
    echo "🌐 Веб-интерфейс: http://localhost:8000"
    echo "📚 API документация: http://localhost:8000/docs"
}

stop_container() {
    echo "⏹️ Остановка контейнера..."
    docker-compose down
    echo "✅ Контейнер остановлен"
}

restart_container() {
    echo "🔄 Перезапуск контейнера..."
    docker-compose restart
    echo "✅ Контейнер перезапущен"
}

show_logs() {
    echo "📋 Логи контейнера:"
    docker-compose logs -f
}

enter_shell() {
    echo "🐚 Вход в контейнер..."
    docker exec -it $CONTAINER_NAME /bin/bash
}

clean_all() {
    echo "🧹 Очистка контейнера и образа..."
    docker-compose down
    docker rmi $IMAGE_NAME:$VERSION 2>/dev/null || true
    echo "✅ Очистка завершена"
}

export_image() {
    echo "📦 Экспорт образа в файл..."
    docker save -o fastapi-foundry-${VERSION}.tar $IMAGE_NAME:$VERSION
    echo "✅ Образ экспортирован: fastapi-foundry-${VERSION}.tar"
    echo "📊 Размер файла: $(du -h fastapi-foundry-${VERSION}.tar | cut -f1)"
}

import_image() {
    if [ ! -f "fastapi-foundry-${VERSION}.tar" ]; then
        echo "❌ Файл fastapi-foundry-${VERSION}.tar не найден"
        exit 1
    fi
    echo "📥 Импорт образа из файла..."
    docker load -i fastapi-foundry-${VERSION}.tar
    echo "✅ Образ импортирован"
}

show_status() {
    echo "📊 Статус контейнера:"
    docker-compose ps
    echo ""
    echo "🖼️ Docker образы:"
    docker images | grep $IMAGE_NAME || echo "Образ не найден"
}

case "$1" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    logs)
        show_logs
        ;;
    shell)
        enter_shell
        ;;
    clean)
        clean_all
        ;;
    export)
        export_image
        ;;
    import)
        import_image
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Неизвестная команда: $1"
        echo ""
        show_help
        exit 1
        ;;
esac