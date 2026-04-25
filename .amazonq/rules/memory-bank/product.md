# FastAPI Foundry — Product Overview

**Version:** 0.7.0 | **Internal name:** ai_assist | **Platform:** Windows | **Language:** Python 3.11+

---

## Purpose

AI Assistant (`ai_assist`) is a local AI model **orchestrator** that provides a unified REST API for running and interacting with multiple AI backends. It routes requests to Microsoft Foundry Local, HuggingFace Transformers, llama.cpp, or Ollama based on a model prefix convention, with an integrated web UI, RAG system, and MCP server support.

---

## Key Features

### AI Model Backends
- **Microsoft Foundry Local** — ONNX-based inference via CLI (`foundry` command), auto-discovery of port, auto-load on startup
- **HuggingFace Transformers** — download and run models from Hub (PyTorch-based)
- **llama.cpp** — GGUF model inference on CPU/GPU via bundled Windows x64 binaries (`bin/`)
- **Ollama** — integration with locally running Ollama service

### API Capabilities
- `POST /api/v1/generate` — single text generation
- `POST /api/v1/ai/generate` — AI generation with optional RAG context
- `POST /api/v1/ai/chat` — stateful chat with session history
- `GET /api/v1/ai/chat/stream` — streaming chat via SSE
- `GET /api/v1/models` — list available models across all backends
- `GET /api/v1/health` — service health check
- Full Foundry management: start/stop/status/load/unload model
- RAG: index documents, search, extract text from 40+ file formats
- Batch processing, translation, agent execution

### RAG System
- FAISS vector index with SentenceTransformers embeddings
- Text extraction from PDF, DOCX, XLSX, PPTX, images (OCR), HTML, archives, source code
- Configurable chunk size, min_score filtering, result caching
- Deduplication of chunks on load

### Web Interface (SPA)
- Single-page app at `http://localhost:9696`
- Tabs: Chat, Models, Foundry, HuggingFace, llama.cpp, Ollama, RAG, Agent, MCP, Logs, Settings, Editor, Docs
- i18n support: English, Russian, Hebrew (`static/locales/`)
- Real-time model status badge, WebSocket notifications

### MCP Server
- PowerShell-based MCP servers in `mcp-powershell-servers/`
- Integration with Claude Desktop
- STDIO protocol

### Additional Tools
- Browser extensions: summarizer, locator-editor
- SDK: `fastapi_foundry_sdk`, `microsoft_foundry_sdk`
- Installer web UI (`install/server.py`) with guided setup
- Diagnostic scripts (`check_engine/`, `diagnose.py`, `check_env.py`)
- GGUF→ONNX converter (`src/converter/`)
- Translation utility (`src/utils/translator.py`) via MyMemory/LibreTranslate

---

## Target Users

- Developers building AI-powered applications who want a local, privacy-preserving inference server
- Researchers experimenting with multiple LLM backends without cloud dependency
- Teams needing a self-hosted RAG pipeline over internal documents
- Windows users wanting a GUI-managed local AI stack

---

## Entry Points

| Entry Point | Purpose |
|---|---|
| `start.ps1` | Primary launcher (installs deps, starts Foundry, runs server) |
| `run.py` | Direct Python entry point (assumes Foundry already running) |
| `install.ps1` | Dependency installer |
| `docker-compose.yml` | Docker deployment |
| `http://localhost:9696` | Web UI after startup |
| `http://localhost:9696/docs` | Swagger UI |
| `http://localhost:9697` | MkDocs documentation server |
