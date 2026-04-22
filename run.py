#!/usr/bin/env python311
# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Запуск сервера FastApiFoundry
# =============================================================================
# Описание:
#   Упрощенный запуск сервера FastAPI.
#   Если Foundry уже запущен, функции ИИ будут доступны автоматически.
#   Для полного запуска со всеми зависимостями используйте start.ps1.
#
# File: run.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.5
# Изменения в 0.6.5:
#   - Полная русификация документации и комментариев
#   - MIT Лицензия (автор: hypo69)
#   - Добавлены строгие аннотации типов возвращаемых значений
#   - Комментарии к проверкам `if` в стиле "Проверка ..."
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================

# FORCED UTF-8 ENCODING SETUP
import os
import sys
import locale
from typing import Optional

# Принудительная настройка кодировки UTF-8 для всего процесса Python
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32': # Проверка платформы Windows
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    except:
        pass  # Проверка: если кодировка уже установлена
    # Попытка установить UTF-8 локаль
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass  # Проверка: использование системной локали по умолчанию

import json
import socket
import logging
from pathlib import Path

# Добавление текущей директории в sys.path для импорта модулей
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path: # Проверка наличия пути в sys.path
    sys.path.insert(0, str(current_dir))

# Добавление site-packages для python311
# Проверка: добавлять только если путь существует и это Windows
if sys.platform == 'win32' and Path('C:/python311/Lib/site-packages').exists(): 
    sys.path.append('C:/python311/Lib/site-packages')

# Загрузка переменных окружения перед импортом конфигурации
# Проверка: защита от двойного выполнения в режиме перезагрузки uvicorn
_in_reloader_child = os.getenv('_UVICORN_CHILD') == '1'
if not _in_reloader_child:
    os.environ['_UVICORN_CHILD'] = '1'

try:
    from src.utils.env_processor import load_env_variables, process_config
    load_env_variables()
    if not _in_reloader_child: # Проверка: вывод только для основного процесса
        print("Переменные окружения загружены")
except ImportError:
    if not _in_reloader_child: # Проверка отсутствия процессора окружения
        print("Процессор окружения недоступен, используется конфигурация по умолчанию")

from src.core.config import config

# Импорт requests только если библиотека доступна
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("Предупреждение: библиотека requests недоступна, некоторые функции отключены")
    REQUESTS_AVAILABLE = False

try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    print("Ошибка: библиотека uvicorn недоступна, запуск сервера невозможен")
    UVICORN_AVAILABLE = False
    sys.exit(1)

# Инициализация подсистемы логирования
from src.logger import logger as _root_logger  # noqa: E402 — must follow sys.path setup
from src.utils.logging_config import setup_logging
setup_logging(os.getenv('LOG_LEVEL', 'INFO'))

logger = logging.getLogger(__name__)


# =============================================================================
# Утилиты
# =============================================================================
def find_free_port(start_port: int = 9696, end_port: int = 9796) -> Optional[int]:
    """Поиск свободного порта в заданном диапазоне.

    Args:
        start_port (int): Начальный порт диапазона. По умолчанию 9696.
        end_port (int): Конечный порт диапазона. По умолчанию 9796.

    Returns:
        Optional[int]: Номер свободного порта или None, если порты заняты.

    Raises:
        OSError: При системных ошибках работы с сокетами.
    """
    logger.debug(f"Поиск свободного порта в диапазоне {start_port}-{end_port}")
    
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
                logger.info(f"Найден свободный порт: {port}")
                return port
            except OSError:
                logger.debug(f"Порт {port} занят")
                continue
    
    logger.warning(f"Не удалось найти свободный порт в диапазоне {start_port}-{end_port}")
    return None


# =============================================================================
# Управление портами
# =============================================================================
def get_server_port() -> int:
    """Определение порта для запуска сервера FastAPI.

    Returns:
        int: Номер порта для сервера.
    """
    default_port = config.api_port
    auto_find = config.port_auto_find_free
    
    logger.info(f"Определение порта сервера FastAPI...")
    logger.debug(f"Порт по умолчанию: {default_port}")
    logger.debug(f"Автоматический поиск порта: {auto_find}")

    if not auto_find: # Проверка: если автопоиск отключен, используем фиксированный порт
        logger.info(f'Использование фиксированного порта: {default_port}')
        return default_port

    start_port = config.port_range_start
    end_port = config.port_range_end

    free_port = find_free_port(start_port, end_port)
    if free_port: # Проверка: если свободный порт найден
        logger.info(f'Найден свободный порт: {free_port}')
        return free_port

    logger.warning(f'Свободный порт не найден, используется порт по умолчанию {default_port}')
    return default_port


# =============================================================================
# Foundry
# =============================================================================
def find_foundry_port() -> Optional[int]:
    """Поиск порта работающего сервиса Foundry.

    Returns:
        Optional[int]: Номер порта Foundry или None, если сервис не найден.
    """
    from src.utils.foundry_utils import find_foundry_port as _find_port
    return _find_port()


def resolve_foundry_base_url() -> Optional[str]:
    """Динамическое определение базового URL для Foundry.

    Returns:
        Optional[str]: Полный URL сервиса Foundry или None.
    """
    # Проверка переменной окружения FOUNDRY_BASE_URL
    foundry_url = os.getenv('FOUNDRY_BASE_URL')
    if foundry_url: # Проверка: если URL задан явно
        logger.info(f'Foundry найден через переменную окружения: {foundry_url}')
        return foundry_url
    
    # Проверка устаревшей переменной FOUNDRY_DYNAMIC_PORT
    foundry_port = os.getenv('FOUNDRY_DYNAMIC_PORT')
    if foundry_port: # Проверка наличия порта в окружении
        try:
            port = int(foundry_port)
            foundry_url = f'http://localhost:{port}/v1/'
            logger.info(f'Foundry найден через системную переменную порта: {foundry_url}')
            return foundry_url
        except ValueError:
            pass
    
    # Автоматическое определение порта
    foundry_port = find_foundry_port()
    if foundry_port: # Проверка: если порт успешно обнаружен
        foundry_url = f'http://localhost:{foundry_port}/v1/'
        logger.info(f'Foundry автоматически обнаружен на порту: {foundry_url}')
        return foundry_url

    logger.warning('Foundry не обнаружен')
    return None


def check_foundry(foundry_base_url: Optional[str]) -> bool:
    """Проверка доступности Foundry API по HTTP.

    Args:
        foundry_base_url (Optional[str]): Базовый URL для проверки.

    Returns:
        bool: True, если API ответило кодом 200.
    """
    if not foundry_base_url or not REQUESTS_AVAILABLE: # Проверка входных данных и зависимостей
        return False

    try:
        response = requests.get(
            f'{foundry_base_url}models',
            timeout=3,
        )
        return response.status_code == 200 # Проверка успешности HTTP запроса
    except Exception:
        return False


# =============================================================================
# Основная функция
# =============================================================================
def main() -> bool:
    """Главная функция запуска сервера.

    Returns:
        bool: True при успешном запуске и работе сервера.
    """
    try:
        logger.info('FastAPI Foundry')
        logger.info('=' * 50)

        # -------------------------------------------------------------------------
        # Поиск и инициализация Foundry
        # -------------------------------------------------------------------------
        logger.info("Поиск Foundry...")
        foundry_base_url = resolve_foundry_base_url()

        if foundry_base_url and check_foundry(foundry_base_url): # Проверка работоспособности Foundry
            # Обновление настроек найденным URL
            config.foundry_base_url = foundry_base_url
            logger.info(f'Foundry доступен: {foundry_base_url}')
        else:
            logger.warning('Foundry недоступен - функции ИИ будут отключены')

        # -------------------------------------------------------------------------
        # Параметры и запуск FastAPI
        # -------------------------------------------------------------------------
        host = config.api_host
        reload_enabled = config.api_reload
        log_level = config.api_log_level.lower()
        workers = config.api_workers

        if reload_enabled: # Проверка режима перезагрузки: в нем может быть только 1 воркер
            workers = 1

        port = get_server_port()

        logger.info('\nЗапуск сервера FastAPI')
        logger.info(f'   Хост: {host}')
        logger.info(f'   Порт: {port}')
        logger.info(f'   Перезагрузка: {reload_enabled}')
        logger.info(f'   Процессы (Workers): {workers}')
        logger.info('-' * 50)
        logger.info(f'Интерфейс: http://localhost:{port}')
        logger.info(f'Документация: http://localhost:{port}/docs')
        logger.info(f'Проверка: http://localhost:{port}/api/v1/health')
        logger.info('-' * 50)

        # Запуск uvicorn с полным контролем ошибок
        try:
            uvicorn.run(
                'src.api.main:app',
                host=host,
                port=port,
                reload=reload_enabled,
                workers=workers,
                log_level=log_level,
                timeout_keep_alive=300,
                timeout_graceful_shutdown=10,
            )
            return True
        except KeyboardInterrupt:
            logger.info('\nСервер остановлен пользователем')
            return True
        except ImportError as e:
            logger.error(f'Ошибка импорта - отсутствуют зависимости: {e}')
            logger.error('Попробуйте: venv\\Scripts\\python.exe -m pip install -r requirements.txt')
            return False
        except Exception as exc:
            logger.error(f'Ошибка запуска сервера: {exc}')
            logger.error('Проверьте, не занят ли порт и установлены ли все зависимости')
            return False
            
    except Exception as e:
        logger.error(f'Критическая ошибка в функции main: {e}')
        return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
