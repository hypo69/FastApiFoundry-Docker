# -*- coding: utf-8 -*-
# =============================================================================
# Название процесса: Agents Package
# =============================================================================
# File: src/agents/__init__.py
# Project: FastApiFoundry (Docker)
# Version: 0.4.1
# Author: hypo69
# License: CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
# Copyright: © 2025 AiStros
# =============================================================================

from .base import BaseAgent, ToolDefinition, ToolCallResult
from .powershell_agent import PowerShellAgent

__all__ = ["BaseAgent", "ToolDefinition", "ToolCallResult", "PowerShellAgent"]
