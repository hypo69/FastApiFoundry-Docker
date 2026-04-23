# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: API Utilities
# =============================================================================
# Description:
#   Shared utilities for FastAPI endpoints, including standardized response
#   wrappers and error handling decorators.
#
# File: src/utils/api_utils.py
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Changes in 0.6.0:
#   - MIT License update
#   - Unified headers
# Author: hypo69
# Copyright: © 2026 hypo69
# License: MIT
# =============================================================================

import functools
import logging
from typing import Any, Callable
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def api_response_handler(func: Callable):
    """Decorator to unify API responses.
    
    - Adds 'success: true' to dictionary responses if missing.
    - Catches HTTPException and returns 'success: false' with the detail.
    - Catches generic Exception, logs it, and returns 'success: false' with error message.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any):
        try:
            result = await func(*args, **kwargs)
            
            # If the result is a dict, ensure it has a success flag
            if isinstance(result, dict):
                if "success" not in result:
                    return {"success": True, **result}
                return result
            
            # If result is None (e.g. background task started), return generic success
            if result is None:
                return {"success": True}
                
            return result
        except HTTPException as e:
            return {"success": False, "error": e.detail}
        except Exception as e:
            logger.exception(f"Unhandled API error in {func.__name__}: {e}")
            return {"success": False, "error": str(e)}
    return wrapper