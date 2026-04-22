# -*- coding: utf-8 -*-
# =============================================================================
# Process Name: Microsoft Foundry Local SDK — Full Reference
# =============================================================================
# Description:
#   Complete description of Microsoft Foundry Local SDK capabilities:
#   model lifecycle management, chat interface, agent creation,
#   MCP server integration, streaming, and Azure migration path.
#
# File: README.md
# Project: FastApiFoundry (Docker)
# Version: 0.6.0
# Author: hypo69
# Copyright: © 2026 hypo69
# =============================================================================

# Microsoft Foundry Local SDK

## Install

```bash
pip install foundry-local-sdk
pip install agent-framework --pre   # for agents + MCP
```

## Core Concepts

| Concept | Description |
|---|---|
| `FoundryLocalManager` | Singleton — manages Foundry Local process lifecycle |
| `Configuration` | App-level config (name, model cache dir) |
| `model.load()` | Loads model into memory, starts local endpoint |
| `model.get_chat_client()` | Returns OpenAI-compatible client |
| `ChatAgent` | Microsoft Agent Framework — orchestrates tools + MCP |
| `StdioClientTransport` | Connects to local MCP server via stdin/stdout |

## Capabilities

### 1. Model Lifecycle
- Initialize Foundry Local manager
- List available models from catalog
- Download models from catalog
- Load / unload models
- Get model status

### 2. Chat Interface
- OpenAI-compatible chat client
- Streaming responses
- System prompts
- Temperature / max_tokens control
- Multi-turn conversation history

### 3. Agent Framework
- `ChatAgent` with tool use
- Automatic tool selection from user input
- Streaming agent responses
- Thread-based conversation state

### 4. MCP Integration
- Connect local MCP servers via `StdioClientTransport`
- Connect remote MCP servers via `SseClientTransport`
- Register MCP tools in agent
- Agent auto-calls MCP tools when needed

### 5. Azure Migration
- Same `ChatAgent` API works with Azure AI Foundry
- Swap `FoundryLocalManager` → `AzureAIClient`
- Local MCP servers need tunnel (ngrok) or remote deployment
