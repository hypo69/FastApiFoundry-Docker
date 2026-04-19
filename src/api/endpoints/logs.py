# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Logs API Endpoints
# =============================================================================
# Description:
#   REST endpoints for the log viewer tab.
#   Supports file selection, level filtering, text search, pagination.
#
# File: logs.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter()
logger = logging.getLogger(__name__)

_LOG_DIR = Path('logs')

# Files exposed to the viewer, in display order
_LOG_FILES = [
    'fastapi-foundry.log',
    'fastapi-foundry-errors.log',
    'fastapi-foundry-structured.jsonl',
    'app.log',
]


def _resolve_file(filename: str) -> Path:
    """Return validated path inside logs/ or raise 404."""
    path = (_LOG_DIR / Path(filename).name).resolve()
    if not str(path).startswith(str(_LOG_DIR.resolve())):
        raise HTTPException(status_code=400, detail='Invalid file path')
    if not path.exists():
        raise HTTPException(status_code=404, detail=f'File not found: {filename}')
    return path


@router.get('/logs/files')
async def list_log_files() -> dict[str, Any]:
    """Return available log files with size info."""
    files = []
    for name in _LOG_FILES:
        p = _LOG_DIR / name
        if p.exists():
            files.append({
                'name': name,
                'size': p.stat().st_size,
                'size_kb': round(p.stat().st_size / 1024, 1),
            })
    return {'success': True, 'files': files}


@router.get('/logs')
async def get_logs(
    file: str = Query(default='fastapi-foundry.log', description='Log file name'),
    lines: int = Query(default=200, ge=1, le=5000, description='Max lines to return'),
    level: str = Query(default='', description='Filter by level: DEBUG|INFO|WARNING|ERROR'),
    search: str = Query(default='', description='Text search (case-insensitive)'),
    offset: int = Query(default=0, ge=0, description='Skip last N lines (pagination)'),
) -> dict[str, Any]:
    """Return filtered log lines from the requested file."""
    path = _resolve_file(file)

    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            all_lines = [l.rstrip('\r\n') for l in f if l.strip()]
    except Exception as e:
        logger.error(f'Error reading {path}: {e}')
        raise HTTPException(status_code=500, detail=str(e))

    total = len(all_lines)

    # Apply filters
    filtered = all_lines
    if level:
        filtered = [l for l in filtered if f'| {level.upper()}' in l or f' {level.upper()} ' in l]
    if search:
        needle = search.lower()
        filtered = [l for l in filtered if needle in l.lower()]

    # Newest-first pagination: take from the tail
    filtered_total = len(filtered)
    start = max(0, filtered_total - lines - offset)
    end   = max(0, filtered_total - offset)
    page  = filtered[start:end]

    return {
        'success': True,
        'file': file,
        'lines': page,
        'returned': len(page),
        'filtered_total': filtered_total,
        'total_lines': total,
        'has_more': start > 0,
    }


@router.post('/logs/clear')
async def clear_log(
    file: str = Query(default='fastapi-foundry.log'),
) -> dict[str, Any]:
    """Truncate a log file."""
    path = _resolve_file(file)
    try:
        path.write_text('', encoding='utf-8')
        logger.info(f'Log file cleared: {file}')
        return {'success': True, 'message': f'{file} cleared'}
    except Exception as e:
        logger.error(f'Error clearing {file}: {e}')
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/logs/download')
async def download_log(
    file: str = Query(default='fastapi-foundry.log'),
) -> FileResponse:
    """Download a log file."""
    path = _resolve_file(file)
    return FileResponse(path=str(path), filename=file, media_type='text/plain')
