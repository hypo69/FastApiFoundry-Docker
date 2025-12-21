#!/bin/bash
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: FastAPI Foundry Linux Installation Script
# =============================================================================
# Описание:
#   Автоматический установщик FastAPI Foundry для Linux/macOS
#   Создает виртуальное окружение, устанавливает зависимости
#
# File: install.sh
# Project: AiStros
# Module: FastApiFoundry
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

set -e  # Выход при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функции логирования
log_info() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
}

log_highlight() {
    echo -e "${PURPLE}[$(date +'%H:%M:%S')] $1${NC}"
}

# Заголовок
show_header() {
    clear
    echo -e "${PURPLE}"
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║         FastAPI Foundry - Installation Wizard (Linux/macOS)           ║"
    echo "║                                                                        ║"
    echo "║  REST API для локальных AI моделей через Foundry с RAG поддержкой   ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Проверка Python
check_python() {
    log_info "🐍 Проверка Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        log_success "Python найден: $PYTHON_VERSION"
        PYTHON_CMD="python3"
        return 0
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
            log_success "Python найден: $PYTHON_VERSION"
            PYTHON_CMD="python"
            return 0
        else
            log_error "Найден Python 2, требуется Python 3.8+"
            return 1
        fi
    else
        log_error "Python не найден!"
        echo ""
        log_info "Установите Python 3.8+ для вашей системы:"
        log_info "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
        log_info "  CentOS/RHEL:   sudo yum install python3 python3-pip"
        log_info "  macOS:         brew install python3"
        echo ""
        return 1
    fi
}

# Проверка Git
check_git() {
    log_info "💻 Проверка Git..."
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version 2>&1)
        log_success "Git уже установлен: $GIT_VERSION"
        return 0
    else
        log_warning "Git не установлен"
        echo ""
        log_info "Git нужен для клонирования репозиториев"
        echo ""
        
        read -p "Установить Git? (y/n): " install_git
        if [[ $install_git == "y" || $install_git == "Y" ]]; then
            log_info "Установка Git..."
            
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                if command -v apt &> /dev/null; then
                    sudo apt update && sudo apt install -y git
                elif command -v yum &> /dev/null; then
                    sudo yum install -y git
                elif command -v dnf &> /dev/null; then
                    sudo dnf install -y git
                else
                    log_error "Неизвестный пакетный менеджер. Установите Git вручную"
                    return 1
                fi
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                if command -v brew &> /dev/null; then
                    brew install git
                else
                    log_error "Homebrew не найден. Установите Git вручную"
                    return 1
                fi
            fi
            
            if command -v git &> /dev/null; then
                log_success "Git установлен успешно"
                return 0
            else
                log_error "Ошибка установки Git"
                return 1
            fi
        fi
        return 0
    fi
}

# Проверка Docker
check_docker() {
    log_info "🐳 Проверка Docker..."
    
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version 2>&1)
        log_success "Docker уже установлен: $DOCKER_VERSION"
        return 0
    else
        log_warning "Docker не установлен"
        echo ""
        log_info "Docker нужен для контейнеризации (опционально)"
        echo ""
        
        read -p "Установить Docker? (y/n): " install_docker
        if [[ $install_docker == "y" || $install_docker == "Y" ]]; then
            log_info "Установка Docker..."
            
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                if command -v apt &> /dev/null; then
                    # Ubuntu/Debian
                    sudo apt update
                    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
                    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                    sudo apt update
                    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                    sudo usermod -aG docker $USER
                    log_success "Docker установлен. Перелогиньтесь для применения прав"
                elif command -v yum &> /dev/null; then
                    # CentOS/RHEL
                    sudo yum install -y yum-utils
                    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                    sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                    sudo systemctl start docker
                    sudo systemctl enable docker
                    sudo usermod -aG docker $USER
                    log_success "Docker установлен. Перелогиньтесь для применения прав"
                else
                    log_error "Неизвестный пакетный менеджер. Установите Docker вручную"
                    log_info "https://docs.docker.com/engine/install/"
                    return 1
                fi
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                log_info "Откройте https://www.docker.com/products/docker-desktop/"
                log_info "и скачайте Docker Desktop для macOS"
                if command -v open &> /dev/null; then
                    open "https://www.docker.com/products/docker-desktop/" &> /dev/null &
                fi
                return 1
            fi
            
            return 0
        fi
        return 0
    fi
}

# Создание виртуального окружения
create_venv() {
    log_info ""
    log_info "🐍 Создание виртуального окружения..."
    
    if [ -d "venv" ]; then
        log_success "venv уже существует"
        return 0
    fi
    
    log_info "Создание venv..."
    if $PYTHON_CMD -m venv venv; then
        log_success "venv создана успешно"
        return 0
    else
        log_error "Ошибка при создании venv"
        return 1
    fi
}

# Установка зависимостей
install_dependencies() {
    log_info ""
    log_info "📦 Установка зависимостей в venv..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt не найден!"
        return 1
    fi
    
    log_info "Активация venv..."
    source venv/bin/activate
    
    log_info "Это может занять несколько минут..."
    
    log_info "Обновление pip..."
    if python -m pip install --upgrade pip > /dev/null 2>&1; then
        log_success "pip обновлен"
    fi
    
    log_info "Установка пакетов из requirements.txt..."
    if python -m pip install -r requirements.txt > /dev/null 2>&1; then
        log_success "Зависимости установлены в venv"
        return 0
    else
        log_error "Ошибка при установке зависимостей"
        return 1
    fi
}

# Проверка Foundry
check_foundry() {
    log_info ""
    log_info "🔧 Проверка Foundry CLI..."
    
    if command -v foundry &> /dev/null; then
        FOUNDRY_VERSION=$(foundry --version 2>&1)
        log_success "Foundry уже установлена: $FOUNDRY_VERSION"
        return 0
    else
        log_warning "Foundry не установлена (опционально)"
        echo ""
        log_info "Foundry требуется для работы с локальными AI моделями"
        log_info "Скачать можно с: https://github.com/foundryai/foundry"
        echo ""
        
        read -p "Установить Foundry? (y/n): " install_foundry
        if [[ $install_foundry == "y" || $install_foundry == "Y" ]]; then
            log_info "Перейдите на https://github.com/foundryai/foundry"
            log_info "и скачайте последнюю версию для вашей системы"
            if command -v xdg-open &> /dev/null; then
                xdg-open "https://github.com/foundryai/foundry/releases" &> /dev/null &
            elif command -v open &> /dev/null; then
                open "https://github.com/foundryai/foundry/releases" &> /dev/null &
            fi
            return 1
        fi
        return 0
    fi
}

# Настройка окружения
setup_environment() {
    log_info ""
    log_info "⚙️  Настройка окружения..."
    
    # Проверить .env
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_info "Создание .env из шаблона..."
            cp ".env.example" ".env"
            log_success ".env создан"
        else
            log_warning ".env.example не найден"
        fi
    else
        log_success ".env уже существует"
    fi
    
    # Создать директории
    for dir in "logs" "rag_index" "static"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_success "Создана директория: $dir"
        fi
    done
}

# Тестирование установки
test_installation() {
    log_info ""
    log_info "🧪 Тестирование установки в venv..."
    
    source venv/bin/activate
    
    passed=0
    failed=0
    
    # Test Python
    if python --version &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        log_success "Python: $PYTHON_VERSION"
        ((passed++))
    else
        log_error "Python: не найден в venv"
        ((failed++))
    fi
    
    # Test FastAPI
    if python -c "import fastapi; print(fastapi.__version__)" &> /dev/null; then
        FASTAPI_VERSION=$(python -c "import fastapi; print(fastapi.__version__)" 2>&1)
        log_success "FastAPI: версия $FASTAPI_VERSION"
        ((passed++))
    else
        log_error "FastAPI: не установлен"
        ((failed++))
    fi
    
    # Test uvicorn
    if python -c "import uvicorn; print(uvicorn.__version__)" &> /dev/null; then
        UVICORN_VERSION=$(python -c "import uvicorn; print(uvicorn.__version__)" 2>&1)
        log_success "Uvicorn: версия $UVICORN_VERSION"
        ((passed++))
    else
        log_error "Uvicorn: не установлен"
        ((failed++))
    fi
    
    echo ""
    if [ $failed -eq 0 ]; then
        log_success "Все тесты пройдены!"
        return 0
    else
        log_error "$failed тестов не пройдено"
        return 1
    fi
}

# Показать следующие шаги
show_next_steps() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ✅ УСТАНОВКА ЗАВЕРШЕНА!                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log_highlight "🎉 Следующие шаги:"
    echo ""
    log_info "1. Запустить на порту по умолчанию (8000):"
    log_info "   python run.py"
    echo ""
    log_info "2. Запустить с проверкой занятости порта (если порт занят - подключиться к существующему):"
    log_info "   python run.py --fixed-port 8000"
    echo ""
    log_info "3. Запустить с автопоиском свободного порта:"
    log_info "   python run.py --auto-port"
    echo ""
    log_info "4. Запустить с MCP консолью и браузером:"
    log_info "   python run.py --mcp --browser"
    echo ""
    log_info "5. Production режим:"
    log_info "   python run.py --prod"
    echo ""
    log_info "6. Справка:"
    log_info "   python run.py --help"
    echo ""
    log_info "📚 Документация:"
    log_info "   - README.md - основная информация"
    log_info "   - docs/ - полная документация"
    echo ""
    log_info "🌐 После запуска:"
    log_info "   - Веб-интерфейс: http://localhost:8000"
    log_info "   - API документация: http://localhost:8000/docs"
    log_info "   - Health Check: http://localhost:8000/api/v1/health"
    echo ""
    log_info "💡 Порт можно изменить через --port или --fixed-port"
}

# Основная функция
main() {
    show_header
    log_highlight "Начало установки FastAPI Foundry..."
    echo ""
    
    # Проверка Python
    if ! check_python; then
        exit 1
    fi
    
    # Проверка Git
    if ! check_git; then
        log_warning "Git не установлен, но продолжаем..."
    fi
    
    # Проверка Docker
    if ! check_docker; then
        log_warning "Docker не установлен, но продолжаем..."
    fi
    
    # Создание виртуального окружения
    if ! create_venv; then
        exit 1
    fi
    
    # Установка зависимостей
    if ! install_dependencies; then
        log_warning "Попытка переустановки с параметром --upgrade"
        source venv/bin/activate
        python -m pip install --upgrade -r requirements.txt
    fi
    
    # Проверка Foundry
    check_foundry
    
    # Настройка окружения
    setup_environment
    
    # Тестирование установки
    if ! test_installation; then
        echo ""
        log_error "Некоторые компоненты не прошли проверку"
        log_warning "Пожалуйста, проверьте установку вручную"
    fi
    
    # Показать завершение
    show_next_steps
    
    echo ""
    log_info "Нажмите Enter для выхода..."
    read
}

# Запуск
main "$@"