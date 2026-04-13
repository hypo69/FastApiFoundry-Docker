# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Установка RAG зависимостей
# =============================================================================
# Описание:
#   Установка тяжёлых RAG зависимостей: torch, sentence-transformers, faiss-cpu.
#
#   ПОЧЕМУ ОТДЕЛЬНО ОТ requirements.txt:
#     torch (~2 GB) и sentence-transformers тянут за собой большой граф
#     зависимостей. Включение их в requirements.txt делает базовую установку
#     проекта неоправданно долгой для пользователей, которым RAG не нужен.
#     Разделение позволяет установить только core-зависимости через install.ps1,
#     а RAG — отдельно по желанию.
#
#   ПОЧЕМУ НЕ pip install -r rag_requirements.txt:
#     Отдельный файл требований создаёт путаницу с версиями при обновлении.
#     Список из трёх пакетов проще держать прямо в скрипте.
#
# Примеры:
#   >>> python install_rag_deps.py
#
# File: install_rag_deps.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Соответствие pip-имени → import-имени.
# ПОЧЕМУ СЛОВАРЬ, А НЕ СПИСОК:
#   pip-имя и import-имя часто не совпадают (faiss-cpu → faiss,
#   sentence-transformers → sentence_transformers). Словарь делает
#   проверку установки явной без хрупких замен дефисов на подчёркивания.
RAG_PACKAGES: dict = {
    "torch": "torch",
    "sentence-transformers": "sentence_transformers",
    "faiss-cpu": "faiss",
}


def is_installed(import_name: str) -> bool:
    """! Проверка наличия пакета в текущем окружении через импорт.

    ПОЧЕМУ ЧЕРЕЗ ИМПОРТ, А НЕ pip show:
      pip show — отдельный subprocess с парсингом stdout.
      __import__ быстрее и точнее: проверяет именно то окружение,
      в котором будет работать приложение.

    Args:
        import_name (str): Имя модуля для импорта.

    Returns:
        bool: True если пакет доступен.

    Example:
        >>> is_installed("torch")
        False
    """
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_package(package: str) -> bool:
    """! Установка одного пакета через pip.

    Args:
        package (str): Имя пакета для установки.

    Returns:
        bool: True при успешной установке.

    Example:
        >>> install_package("faiss-cpu")
        True
    """
    # Вызов через sys.executable — гарантия установки в текущий venv
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        capture_output=True, text=True
    )

    if not result.returncode == 0:
        logger.error(f"Ошибка установки {package}: {result.stderr.strip()}")
        return False

    return True


def main() -> None:
    """! Точка входа: проверка и установка RAG зависимостей."""
    already: list = []
    to_install: list = []

    # Разделение на уже установленные и требующие установки
    for pkg, imp in RAG_PACKAGES.items():
        if is_installed(imp):
            already.append(pkg)
        else:
            to_install.append(pkg)

    if already:
        logger.info(f"Уже установлено: {', '.join(already)}")

    if not to_install:
        logger.info("Все RAG зависимости уже установлены")
        logger.info("Следующий шаг: python create_rag_index.py")
        return

    logger.info(f"Установка ({len(to_install)} пакетов, ~2 GB): {', '.join(to_install)}")

    failed: list = []
    for pkg in to_install:
        logger.info(f"  Установка {pkg}...")
        if install_package(pkg):
            logger.info(f"  OK: {pkg}")
        else:
            failed.append(pkg)

    if failed:
        logger.error(f"Не удалось установить: {', '.join(failed)}")
        for pkg in failed:
            logger.error(f"  pip install {pkg}")
        sys.exit(1)

    logger.info("RAG зависимости установлены")
    logger.info("Следующий шаг: python create_rag_index.py")


if __name__ == "__main__":
    main()
