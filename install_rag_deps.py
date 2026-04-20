# -*- coding: utf-8 -*-
# =============================================================================
# Process name: RAG Dependency Installation
# =============================================================================
# Description:
#   Installing heavy RAG dependencies: torch, sentence-transformers, faiss-cpu.
#
#   WHY SEPARATE FROM requirements.txt:
#     torch (~2 GB) and sentence-transformers pull in a large dependency
#     graph. Including them in requirements.txt makes the base installation
#     of the project unjustifiably long for users who do not need RAG.
#     Separation allows installing only core dependencies via install.ps1,
#     and RAG separately as desired.
#
#   WHY NOT pip install -r rag_requirements.txt:
#     A separate requirements file creates version confusion during updates.
#     It's easier to keep the list of three packages directly in the script.
#
# Examples:
#   >>> python install_rag_deps.py
#
# File: install_rag_deps.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Mapping pip name → import name.
# WHY A DICTIONARY, NOT A LIST:
#   pip names and import names often don't match (faiss-cpu → faiss,
#   sentence-transformers → sentence_transformers). A dictionary makes the
#   installation check explicit without fragile hyphen-to-underscore replacements.
RAG_PACKAGES: dict = {
    "torch": "torch",
    "sentence-transformers": "sentence_transformers",
    "faiss-cpu": "faiss",
}


def is_installed(import_name: str) -> bool:
    """! Checking for a package in the current environment via import.

    WHY VIA IMPORT, NOT pip show:
      pip show is a separate subprocess with stdout parsing.
      __import__ is faster and more accurate: it checks the exact environment
      in which the application will run.

    Args:
        import_name (str): Module name for import.

    Returns:
        bool: True if the package is available.

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
    """! Installing a single package via pip.

    Args:
        package (str): Name of the package to install.

    Returns:
        bool: True if installation is successful.

    Example:
        >>> install_package("faiss-cpu")
        True
    """
    # Calling via sys.executable guarantees installation in the current venv
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        capture_output=True, text=True
    )

    if not result.returncode == 0:
        logger.error(f"Error installing {package}: {result.stderr.strip()}")
        return False

    return True


def main() -> None:
    """! Entry point: checking and installing RAG dependencies."""
    already: list = []
    to_install: list = []

    # Separating into already installed and requiring installation
    for pkg, imp in RAG_PACKAGES.items():
        if is_installed(imp):
            already.append(pkg)
        else:
            to_install.append(pkg)

    if already:
        logger.info(f"Already installed: {', '.join(already)}")

    if not to_install:
        logger.info("All RAG dependencies are already installed")
        logger.info("Next step: python create_rag_index.py")
        return

    logger.info(f"Installing ({len(to_install)} packages, ~2 GB): {', '.join(to_install)}")

    failed: list = []
    for pkg in to_install:
        logger.info(f"  Installing {pkg}...")
        if install_package(pkg):
            logger.info(f"  OK: {pkg}")
        else:
            failed.append(pkg)

    if failed:
        logger.error(f"Failed to install: {', '.join(failed)}")
        for pkg in failed:
            logger.error(f"  pip install {pkg}")
        sys.exit(1)

    logger.info("RAG dependencies installed")
    logger.info("Next step: python create_rag_index.py")


if __name__ == "__main__":
    main()
