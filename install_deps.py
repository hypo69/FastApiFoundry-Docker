# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Установка Python зависимостей из requirements.txt
# =============================================================================
# Описание:
#   Запуск pip install -r requirements.txt с проверкой результата.
#
#   ПОЧЕМУ ОТДЕЛЬНЫЙ СКРИПТ, А НЕ ПРОСТО pip install:
#     Используется когда pip недоступен напрямую из текущего окружения —
#     например, при запуске через install-gui.ps1, который вызывает python.exe
#     из venv и не знает путь к pip. Скрипт использует sys.executable,
#     что гарантирует вызов pip из того же окружения что и сам скрипт.
#
# Примеры:
#   >>> python install_deps.py
#
# File: install_deps.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def install_requirements(req_file: Path) -> bool:
    """! Установка зависимостей из requirements.txt через pip.

    Args:
        req_file (Path): Путь к файлу requirements.txt.

    Returns:
        bool: True при успешной установке.

    Example:
        >>> install_requirements(Path("requirements.txt"))
        True
    """
    # Проверка существования файла перед вызовом pip
    if not req_file.exists():
        logger.error(f"Файл не найден: {req_file}")
        return False

    # Вызов pip через sys.executable — гарантия использования pip из текущего venv,
    # а не системного pip, который может указывать на другое окружение
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
        text=True
    )

    if not result.returncode == 0:
        logger.error("Ошибка установки зависимостей")
        return False

    return True


def check_imports() -> dict:
    """! Проверка ключевых импортов после установки.

    ПОЧЕМУ ТОЛЬКО ТРИ ПАКЕТА:
      fastapi, uvicorn, aiohttp — минимальный набор для запуска сервера.
      Остальные пакеты (requests, pydantic и т.д.) являются транзитивными
      зависимостями и установятся автоматически вместе с ними.

    Returns:
        dict: Словарь {package: bool} — результат проверки каждого пакета.

    Example:
        >>> results = check_imports()
        >>> print(results)
        {'fastapi': True, 'uvicorn': True, 'aiohttp': True}
    """
    # Минимальный набор для проверки работоспособности сервера
    packages: dict = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "aiohttp": "aiohttp",
    }
    results: dict = {}

    for name, imp in packages.items():
        try:
            __import__(imp)
            results[name] = True
        except ImportError:
            results[name] = False

    return results


def main() -> None:
    """! Точка входа: установка зависимостей и проверка результата."""
    req_file: Path = Path(__file__).parent / "requirements.txt"

    logger.info("Установка зависимостей из requirements.txt...")

    if not install_requirements(req_file):
        logger.error("Попробуйте вручную: pip install -r requirements.txt")
        sys.exit(1)

    logger.info("Проверка ключевых пакетов...")
    results: dict = check_imports()

    for pkg, ok in results.items():
        if ok:
            logger.info(f"  OK: {pkg}")
        else:
            logger.error(f"  FAIL: {pkg}")

    if not all(results.values()):
        logger.error("Некоторые пакеты не установлены")
        sys.exit(1)

    logger.info("Зависимости установлены успешно")


if __name__ == "__main__":
    main()
