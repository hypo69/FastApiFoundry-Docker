# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Foundry Management API
# =============================================================================
# Description:
#   API endpoints for controlling the Foundry service lifecycle.
#
# File: src/api/endpoints/foundry_management.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Changes in 0.6.0:
#   - MIT License update
#   - Unified headers and return type hints
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================

import subprocess
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...utils.foundry_utils import find_foundry_port
from ...utils.process_utils import run_command, DEFAULT_SUBPROCESS_KWARGS
from ...utils.api_utils import api_response_handler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/foundry", tags=["foundry"])

class FoundryStatus(BaseModel):
    running: bool
    success: bool = True
    port: Optional[int] = None
    url: Optional[str] = None

@router.get("/status", response_model=FoundryStatus)
@api_response_handler
async def get_foundry_status() -> FoundryStatus:
    """Get Foundry service status.

    Returns:
        FoundryStatus: running (bool), port (int|None), url (str|None).
    """
    port = find_foundry_port()
    if port:
        return FoundryStatus(
            running=True,
            port=port,
            url=f"http://localhost:{port}/v1/"
        )
    return FoundryStatus(running=False, success=False)

@router.post("/start")
@api_response_handler
async def start_foundry() -> dict:
    """Start the Foundry service via CLI (non-blocking).

    Returns:
        dict: success, message, pid on success; success=False, error on failure.
    """
    try:
        process = subprocess.Popen(
            ["foundry", "service", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **DEFAULT_SUBPROCESS_KWARGS,
        )
        logger.info(f"Foundry service start launched (PID: {process.pid})")
        return {"success": True, "message": "Foundry start command executed", "pid": process.pid}
    except FileNotFoundError:
        return {"success": False, "error": "foundry CLI not found — is Foundry Local installed?"}
    except Exception as e:
        logger.error(f"❌ Failed to start Foundry: {e}")
        return {"success": False, "error": str(e)}

@router.post("/stop")
@api_response_handler
async def stop_foundry() -> dict:
    """Stop the Foundry service via CLI.

    Returns:
        dict: message on success.

    Raises:
        HTTPException 500: If foundry CLI returns non-zero exit code.
        HTTPException 404: If foundry CLI is not installed.
    """
    run_command(["foundry", "service", "stop"])
    return {"message": "Foundry stop command executed"}