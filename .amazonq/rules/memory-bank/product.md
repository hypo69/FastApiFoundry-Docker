# FastAPI Foundry — Product Overview

## Purpose
FastAPI Foundry is a REST API server that bridges local AI models (via Microsoft Foundry Local CLI) with web clients, providing text generation, interactive chat, and RAG (Retrieval-Augmented Generation) capabilities. It is part of the AiStros ecosystem.

## Value Proposition
- Run AI models locally (no cloud dependency) via Foundry Local CLI
- Unified REST API over local ONNX/quantized models (DeepSeek, Qwen, Mistral, Llama)
- Integrated RAG system for context-aware responses using project documentation
- Web UI + MCP server for Claude Desktop integration
- Docker-ready for easy deployment

## Architecture
```
FastAPI (Port 9696) → Foundry Local CLI (Port 50477) → AI Models (ONNX/Local)
```

## Key Features
| Feature | Description |
|---|---|
| Text Generation | POST /api/v1/generate — single prompt completion |
| Chat | POST /api/v1/chat — multi-turn conversation with session support |
| RAG Search | FAISS vector index over project docs, sentence-transformers embeddings |
| Model Management | List, load, unload models via API and web UI |
| Foundry Management | Start/stop/monitor Foundry service via web UI |
| Batch Processing | Multiple requests in one call |
| Health Monitoring | GET /api/v1/health — service and model status |
| MCP Server | stdio MCP server for Claude Desktop integration |
| Web Interface | Static HTML/JS UI at /static |
| Security | API key auth, CORS protection |

## Target Users
- Developers building AI-powered applications who want local inference
- Teams needing a self-hosted AI API compatible with OpenAI-style endpoints
- Claude Desktop users wanting local model integration via MCP
- AiStros platform developers

## Use Cases
1. Local AI chat interface without cloud costs
2. RAG over internal documentation
3. Batch text generation pipelines
4. MCP tool server for Claude Desktop
5. Docker-based AI microservice

## Current Version
- App version: 0.4.1 (src/api/app.py)
- Project version: 0.3.4 (README)
- License: CC BY-NC-SA 4.0
- Author: hypo69 / AiStros Team (https://aistros.com)
