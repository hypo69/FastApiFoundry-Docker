# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: System Stats Endpoint
# =============================================================================
# Description:
#   Returns RAM and CPU usage for the active model banner in the web UI.
#   Uses psutil if available; returns nulls otherwise.
#
# File: src/api/endpoints/system_stats.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/system", tags=["system"])

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False
    logger.warning("⚠️ psutil not installed — /system/stats will return nulls")


@router.get("/stats")
async def system_stats() -> dict:
    """RAM and CPU usage for the active model banner."""
    if not _PSUTIL:
        return {"success": True, "ram_used_mb": None, "ram_total_mb": None, "cpu_pct": None}

    mem = psutil.virtual_memory()
    return {
        "success":      True,
        "ram_used_mb":  round(mem.used  / 1024 / 1024, 1),
        "ram_total_mb": round(mem.total / 1024 / 1024, 1),
        "cpu_pct":      psutil.cpu_percent(interval=0.2),
    }
