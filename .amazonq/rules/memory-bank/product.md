# FastAPI Foundry — Product Overview

## Purpose
FastAPI Foundry is a REST API server that bridges local AI models (via Microsoft Foundry Local CLI) with clients through a standardized HTTP interface. It enables developers and teams to run AI inference locally without cloud dependencies.

## Value Proposition
- Run AI models (DeepSeek, Qwen, Mistral, Llama) entirely on local hardware
- Unified REST API compatible with OpenAI-style clients
- Built-in RAG (Retrieval-Augmented Generation) for context-aware responses
- Web UI for model management, chat, and configuration — no CLI required
- MCP (Model Context Protocol) server for Claude Desktop integration

## Key Features

### AI & Models
- Text generation via Foundry Local CLI (ONNX/local models)
- Interactive chat with session/conversation support
- HuggingFace model support (local inference via `transformers`)
- llama.cpp integration for GGUF models
- Batch request processing
- Auto-load default model on startup

### RAG System
- FAISS vector index over project documentation
- `sentence-transformers` embeddings
- Web UI management (clear/rebuild index)
- Automatic indexing of project docs

### Infrastructure
- FastAPI + Uvicorn ASGI server (port 9696 default)
- Docker / docker-compose support
- Dynamic Foundry port discovery (auto-detects running Foundry process)
- API key + CORS security
- Structured JSON logging with per-component log files
- Health check endpoint (`/api/v1/health`)

### Web Interface
- `static/index.html` — main dashboard
- `static/chat.html` — chat UI
- `static/control.html` — Foundry service control
- `static/ai.html` — AI generation UI

### Browser Extension
- `extentions/browser-extention-summarizer/` — Chrome extension for page summarization
- Multi-provider support: Foundry, Gemini, OpenAI-compat, OpenRouter
- Multi-language prompts (en, ru, de, fr, es, ja, zh)

### MCP Servers
- `mcp-powershell-servers/` — PowerShell STDIO/HTTP MCP servers
- WordPress CLI MCP server
- HuggingFace MCP server
- Python client for MCP interaction

## Target Users
- Developers building AI-powered applications who want local inference
- Teams needing a self-hosted OpenAI-compatible API
- Claude Desktop users wanting local model integration via MCP
- Researchers experimenting with RAG pipelines on local docs

## Use Cases
1. Local AI chat assistant with web UI
2. RAG over internal documentation
3. Batch AI processing pipeline
4. Claude Desktop ↔ local model bridge via MCP
5. Browser-based page summarization with local or cloud AI
6. WordPress site management via AI + MCP

## Versioning
- Current version: **0.4.1** (app.py / API)
- Project: FastApiFoundry (Docker)
- License: CC BY-NC-SA 4.0
- Author: hypo69 / AiStros Team
