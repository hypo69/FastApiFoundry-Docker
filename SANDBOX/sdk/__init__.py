# -*- coding: utf-8 -*-
# =============================================================================
# FastAPI Foundry SDK
# =============================================================================
# Описание:
#   Python SDK для работы с FastAPI Foundry API
#
# File: __init__.py
# Project: FastApiFoundry (Docker)
# Version: 0.3.4
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# Date: 9 декабря 2025
# =============================================================================

from .client import FoundryClient
from .models import GenerationRequest, GenerationResponse, ModelInfo, HealthStatus
from .exceptions import FoundryError, FoundryConnectionError, FoundryAPIError

__version__ = "0.2.1"
__all__ = [
    "FoundryClient",
    "GenerationRequest", 
    "GenerationResponse",
    "ModelInfo",
    "HealthStatus",
    "FoundryError",
    "FoundryConnectionError", 
    "FoundryAPIError"
]