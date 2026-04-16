# FastAPI Foundry — Product Overview

## Purpose
FastAPI Foundry is a REST API server that bridges local AI models (via Microsoft Foundry Local CLI) with web clients, MCP integrations, and RAG-powered context retrieval. It is part of the AiStros ecosystem.

## Value Proposition
- Run local AI models (DeepSeek, Qwen, Mistral, Llama, Phi) without cloud dependency
- Unified REST API over multiple AI backends: Foundry, llama.cpp, HuggingFace
- Built-in RAG (Retrieval-Augmented Generation) for project documentation search
- MCP (Model Context Protocol) server for Claude Desktop and other MCP clients
- Web UI for model management, chat, and system monitoring

## Key Features
| Feature | Description |
|---|---|
| Text Generation | POST /api/v1/generate — single-shot generation |
| Chat | POST /api/v1/chat — session-aware conversation |
| RAG Search | FAISS-based vector search over indexed docs |
| Model Management | List, load, unload Foundry/llama.cpp/HF models |
| Foundry Control | Start/stop/monitor Microsoft Foundry Local service |
| Batch Processing | Multiple requests in one call |
| MCP Server | STDIO MCP server for Claude Desktop integration |
| PowerShell MCP | Proxy to PowerShell-based MCP servers |
| GGUF→ONNX Converter | Convert GGUF models to ONNX format |
| Browser Extension | Summarizer extension with multi-language prompts |
| Health Monitoring | /api/v1/health endpoint with model status |
| API Key Security | Optional API key + CORS protection |
| Docker Support | docker-compose.yml for containerized deployment |

## Target Users
- Developers building AI-powered applications on local hardware
- AiStros platform engineers integrating AI into WordPress/MCP workflows
- Users who want privacy-first AI without cloud API costs

## Use Cases
1. Local AI chat interface via web browser
2. RAG over project documentation for context-aware answers
3. Claude Desktop integration via MCP protocol
4. Batch AI processing pipelines
5. Model benchmarking and switching between backends
6. Browser-based page summarization (extension)

## Architecture Overview
```
Browser / MCP Client / CLI
        │
        ▼
FastAPI (Port 9696)
        │
   ┌────┴────────────────────┐
   │                         │
Foundry Local          llama.cpp / HF
(Port 50477)           (Port 9780)
   │
AI Models (ONNX/GGUF)
```

## Version
Current: **0.4.1** (app.py / config.py)  
Config version in VERSION.md: 0.2.1  
License: CC BY-NC-SA 4.0
