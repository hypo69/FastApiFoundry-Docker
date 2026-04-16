# FastAPI Foundry — Product Overview

## Purpose
FastAPI Foundry is a REST API server that bridges local AI models (via Microsoft Foundry Local CLI) with a rich web interface and developer API. It enables running AI inference locally without cloud dependencies, with integrated RAG (Retrieval-Augmented Generation) for context-aware responses.

## Value Proposition
- Run AI models (DeepSeek, Qwen, Mistral, Llama) entirely on local hardware
- Single unified API for multiple AI backends: Foundry, HuggingFace, llama.cpp
- Built-in RAG system for project documentation search
- Web UI for model management, chat, and configuration — no CLI required
- MCP (Model Context Protocol) server for Claude Desktop integration

## Key Features
- **Text Generation** — `/api/v1/generate` endpoint for prompt-based generation
- **Interactive Chat** — session-aware chat with conversation history
- **RAG System** — FAISS-based vector search over indexed project docs
- **Multi-backend Models** — Foundry, HuggingFace (`hf::` prefix), llama.cpp (`llama::` prefix)
- **Batch Processing** — multiple requests in a single API call
- **API Key Security** — key-based auth + CORS protection
- **Health Monitoring** — `/api/v1/health` and model status endpoints
- **Docker Support** — containerized deployment via `docker-compose.yml`
- **Web Interface** — tabbed SPA at `http://localhost:9696` (chat, models, RAG, logs, settings, etc.)
- **MCP Server** — PowerShell-based MCP servers for Claude Desktop / MCP clients
- **Foundry Management** — start/stop/monitor Foundry service via web UI
- **GGUF → ONNX Converter** — convert GGUF models to ONNX format
- **Translation** — built-in translation module
- **Agent System** — PowerShell agent integration

## Target Users
- Developers building AI-powered applications who want local inference
- Teams needing a self-hosted AI API compatible with OpenAI-style endpoints
- Users integrating AI into Claude Desktop via MCP
- Researchers experimenting with local LLMs (DeepSeek, Qwen, Mistral, Gemma, Llama)

## Use Cases
1. Local AI chat assistant with web UI
2. RAG-powered documentation Q&A
3. AI API backend for internal tools
4. Model evaluation and comparison
5. Claude Desktop extension via MCP protocol
6. Automated text generation pipelines

## Architecture Overview
```
Client (Browser / API) → FastAPI (port 9696)
                              ↓
              ┌───────────────┼───────────────┐
         Foundry CLI     HuggingFace      llama.cpp
         (port 50477)    Transformers     (local bin)
              ↓
         AI Models (ONNX/GGUF)
```

## Version
Current: **0.4.1** (FastApiFoundry Docker)  
License: CC BY-NC-SA 4.0  
Author: hypo69 / AiStros Team  
