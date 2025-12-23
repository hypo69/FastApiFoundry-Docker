#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Docker управление для FastAPI Foundry
# =============================================================================
# Описание:
#   Скрипт для сборки, запуска и управления Docker контейнером
#   Использует docker-compose как основной backend
#   Поддерживает экспорт и импорт Docker образов
#
# File: docker-manager.sh
# Project: FastAPI Foundry
# Author: hypo69
# License: CC BY-NC-SA 4.0
# Copyright: © 2025 AiStros
# =============================================================================

set -euo pipefail

IMAGE_NAME='fastapi-foundry'
VERSION='latest'
COMPOSE_FILE='docker-compose.yml'
SERVICE_NAME='fastapi-foundry'

# -----------------------------------------------------------------------------
# Проверки окружения
# -----------------------------------------------------------------------------
check_requirements() {
    command -v docker >/dev/null 2>&1 || {
        echo 'Docker не установлен'
        exit 1
    }

    command -v docker-compose >/dev/null 2>&1 || {
        echo 'docker-compose не установлен'
        exit 1
    }
}

# -----------------------------------------------------------------------------
# Справка
# -----------------------------------------------------------------------------
show_help() {
    cat <<EOF
FastAPI Foundry Docker Manager

Использование:
  $0 <команда>

Команды:
  build     Собрать Docker образ
  run       Запустить контейнер
  stop      Остановить контейнер
  restart   Перезапустить контейнер
  logs      Показать логи
  shell     Войти в контейнер
  clean     Удалить контейнер и образ
  export    Экспортировать Docker образ
  import    Импортировать Docker образ
  status    Показать статус
  help      Показать справку
EOF
}

# -----------------------------------------------------------------------------
# Docker operations
# -----------------------------------------------------------------------------
build_image() {
    check_requirements
    docker-compose build
}

run_container() {
    check_requirements
    docker-compose up -d
}

stop_container() {
    check_requirements
    docker-compose down
}

restart_container() {
    check_requirements
    docker-compose restart
}

show_logs() {
    check_requirements
    docker-compose logs -f
}

enter_shell() {
    check_requirements
    docker-compose exec ${SERVICE_NAME} /bin/bash
}

clean_all() {
    check_requirements
    docker-compose down --remove-orphans
    docker rmi "${IMAGE_NAME}:${VERSION}" 2>/dev/null || true
}

export_image() {
    check_requirements
    docker save -o "${IMAGE_NAME}-${VERSION}.tar" "${IMAGE_NAME}:${VERSION}"
}

import_image() {
    check_requirements
    local tar_file="${IMAGE_NAME}-${VERSION}.tar"

    if [ ! -f "${tar_file}" ]; then
        echo "Файл ${tar_file} не найден"
        exit 1
    fi

    docker load -i "${tar_file}"
}

show_status() {
    check_requirements
    docker-compose ps
    docker images | grep "${IMAGE_NAME}" || true
}

# -----------------------------------------------------------------------------
# Router
# -----------------------------------------------------------------------------
case "${1:-}" in
    build)    build_image ;;
    run)      run_container ;;
    stop)     stop_container ;;
    restart)  restart_container ;;
    logs)     show_logs ;;
    shell)    enter_shell ;;
    clean)    clean_all ;;
    export)   export_image ;;
    import)   import_image ;;
    status)   show_status ;;
    help|-h|--help) show_help ;;
    *)
        echo "Неизвестная команда: ${1:-}"
        echo
        show_help
        exit 1
        ;;
esac
