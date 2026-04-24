# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Health Check Endpoint
# =============================================================================
# Description:
#   Health check and service restart endpoints for FastAPI Foundry.
#   GET /api/v1/health — returns status of Foundry, llama.cpp, MkDocs, RAG.
#   POST /api/v1/restart/{service} — restarts foundry|llama|docs|rag.
#
# Examples:
#   >>> import requests
#   >>> r = requests.get('http://localhost:9696/api/v1/health')
#   >>> r.json()['status']
#   'healthy'
#
# File: health.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.1
# Changes in 0.6.1:
#   - Updated version to match project
#   - restart/rag now uses config.get_section() correctly
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import asyncio
import subprocess
import sys
import aiohttp
from pathlib import Path
from fastapi import APIRouter
from ...models.foundry_client import foundry_client
from config_manager import config

router = APIRouter()


def _check_rag_status() -> str:
    """Check RAG index availability."""
    if not config.rag_enabled:
        return 'disabled'
    index_dir = Path(config.rag_index_dir)
    return 'enabled' if (index_dir / 'faiss.index').exists() else 'no index'


async def _check_llama_status() -> str:
    """Check llama.cpp server availability."""
    port = config.get_section('llama_cpp').get('port', 9780)
    url = f'http://127.0.0.1:{port}/health'
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
            async with session.get(url) as resp:
                return 'running' if resp.status == 200 else 'stopped'
    except Exception:
        return 'stopped'


async def _check_docs_status() -> str:
    """Check MkDocs documentation server availability."""
    port = config.get_section('docs_server').get('port', 9697)
    url = f'http://127.0.0.1:{port}/'
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
            async with session.get(url) as resp:
                return 'running' if resp.status == 200 else 'stopped'
    except Exception:
        return 'stopped'


@router.post("/restart/{service}")
async def restart_service(service: str) -> dict:
    """Restart a background service.

    Args:
        service: One of 'foundry', 'llama', 'docs', 'rag'.

    Returns:
        dict: success, message.
    """
    try:
        if service == 'foundry':
            subprocess.Popen(['foundry', 'service', 'start'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return {'success': True, 'message': 'Foundry start command sent'}

        elif service == 'llama':
            llama_cfg = config.get_section('llama_cpp')
            model_path = llama_cfg.get('model_path', '')
            if not model_path or not Path(model_path).exists():
                return {'success': False, 'error': 'No model_path set in config.json → llama_cpp.model_path'}
            from .llama_cpp import llama_start
            result = await llama_start({'model_path': model_path,
                                        'port': llama_cfg.get('port', 9780)})
            return result

        elif service == 'docs':
            docs_cfg = config.get_section('docs_server')
            port = docs_cfg.get('port', 9697)
            root = Path(__file__).parents[4]
            python = sys.executable
            subprocess.Popen(
                [python, '-m', 'mkdocs', 'serve', '-a', f'0.0.0.0:{port}'],
                cwd=str(root),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return {'success': True, 'message': f'MkDocs started on port {port}'}

        elif service == 'rag':
            rag_cfg = config.get_section('rag_system')
            if not rag_cfg.get('enabled', False):
                return {'success': False, 'error': 'RAG is disabled in config.json → rag_system.enabled'}
            index_dir = Path(rag_cfg.get('index_dir', '~/.rag')).expanduser()
            if not (index_dir / 'faiss.index').exists():
                return {'success': False, 'error': f'No FAISS index found in {index_dir}. Build index first in the RAG tab.'}
            from ...rag.rag_system import rag_system
            await rag_system.reload_index(index_dir=str(index_dir))
            return {'success': True, 'message': 'RAG index reloaded'}

        else:
            return {'success': False, 'error': f'Unknown service: {service}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса.

    Returns:
        dict: status, foundry_status, foundry_details, llama_status,
              docs_status, models_count, timestamp.
    """
    try:
        foundry_health, llama_status, docs_status = await asyncio.gather(
            foundry_client.health_check(),
            _check_llama_status(),
            _check_docs_status(),
        )
        foundry_status = foundry_health.get('status', 'disconnected')
        rag_status = _check_rag_status()

        return {
            "status": "healthy",
            "foundry_status": foundry_status,
            "foundry_details": {
                "port": foundry_health.get('port'),
                "url": foundry_health.get('url'),
                "error": foundry_health.get('error') if foundry_status != 'healthy' else None
            },
            "llama_status": llama_status,
            "docs_status": docs_status,
            "rag_status": rag_status,
            "models_count": foundry_health.get('models_count', 0),
            "timestamp": foundry_health.get('timestamp')
        }
    except Exception as e:
        return {
            "status": "healthy",
            "foundry_status": "error",
            "foundry_details": {"port": None, "url": None, "error": str(e)},
            "llama_status": "stopped",
            "docs_status": "stopped",
            "rag_status": "disabled",
            "models_count": 0,
            "timestamp": None
        }