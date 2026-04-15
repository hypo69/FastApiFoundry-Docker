# FastAPI Foundry — Project Structure

## Root Layout
```
FastApiFoundry-Docker/
├── src/                    # Main application source code
├── static/                 # Web UI (HTML/JS)
├── docs/                   # Markdown documentation
├── examples/               # Client usage examples
├── mcp-servers/            # MCP server for Claude Desktop
├── SANDBOX/sdk/            # Experimental Python SDK
├── scripts/                # PowerShell management scripts
├── tests/                  # Test suite
├── utils/                  # Standalone utility scripts
├── logs/                   # Runtime log files
├── rag_index/              # FAISS index + chunk metadata
├── run.py                  # Main entry point
├── config_manager.py       # Unified config loader
├── config.json             # App configuration (GUI settings)
├── docker-compose.yml      # Docker deployment
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── launcher.ps1            # Interactive Windows launcher
└── start.ps1               # Quick start script
```

## src/ — Application Source
```
src/
├── api/
│   ├── app.py              # FastAPI application factory (create_app())
│   ├── main.py             # ASGI entry point (app instance)
│   ├── models.py           # Pydantic request/response models
│   └── endpoints/
│       ├── main.py         # Root routes (/, /static redirect)
│       ├── health.py       # GET /api/v1/health
│       ├── models.py       # GET/POST /api/v1/models
│       ├── generate.py     # POST /api/v1/generate
│       ├── chat_endpoints.py       # POST /api/v1/chat
│       ├── rag.py          # POST /api/v1/rag/search, DELETE /api/v1/rag/clear
│       ├── foundry.py      # Foundry status endpoints
│       ├── foundry_management.py   # Start/stop Foundry
│       ├── foundry_models.py       # Model load/unload
│       ├── config.py       # GET/POST /api/v1/config
│       ├── logs.py         # GET /api/v1/logs
│       └── logging_endpoints.py    # Structured logging API
├── core/
│   └── config.py           # Re-exports config from config_manager.py
├── models/
│   ├── foundry_client.py           # Primary Foundry HTTP client (aiohttp)
│   ├── enhanced_foundry_client.py  # Extended client with retry/fallback
│   └── model_manager.py            # Model lifecycle management
├── rag/
│   └── rag_system.py       # FAISS + sentence-transformers RAG engine
├── utils/
│   ├── logging_config.py   # Logging setup
│   ├── logging_system.py   # Structured logging (JSON + plain)
│   ├── log_analyzer.py     # Log parsing utilities
│   ├── env_processor.py    # .env loading and config processing
│   └── foundry_finder.py   # Auto-detect Foundry port via netstat/tasklist
└── logger/
    └── __init__.py         # Logger module init
```

## Key Architectural Patterns

### Application Factory
`src/api/app.py` exports `create_app()` which wires all routers, middleware, and lifespan. `src/api/main.py` calls it to produce the `app` instance used by uvicorn.

### Configuration Flow
```
.env → src/utils/env_processor.py → config_manager.py (ConfigManager) → src/core/config.py (re-export as `config` and `settings`)
```
`config.json` holds GUI/launcher settings; `.env` holds secrets and runtime overrides.

### Foundry Discovery
`run.py:resolve_foundry_base_url()` checks in order:
1. `FOUNDRY_BASE_URL` env var
2. `FOUNDRY_DYNAMIC_PORT` env var (legacy)
3. Auto-detect via `tasklist` + `netstat` (Windows)

### Router Registration (all under `/api/v1`)
health → models → foundry → foundry_management → foundry_models → generate → chat → rag → config → logs

### Static Web UI
Mounted at `/static` from `static/` directory. Key pages:
- `index.html` — main dashboard
- `chat.html` — chat interface
- `control.html` — Foundry control panel
- `ai.html` — AI generation UI

### MCP Server
`mcp-servers/aistros-foundry/server.py` — stdio MCP server exposing Foundry tools to Claude Desktop.

### SANDBOX/sdk/
Experimental Python SDK for the API. Contains `client.py`, `models.py`, `exceptions.py`, `cli.py`, `rag_basic.py`. Not part of the main app — for external consumers.

## Configuration Files
| File | Purpose |
|---|---|
| `config.json` | App settings: port, host, mode, foundry URL, RAG config |
| `.env` | Secrets: API_KEY, SECRET_KEY, GITHUB_PAT, FOUNDRY_BASE_URL |
| `.env.example` | Template for .env |
| `docker-compose.yml` | Docker service definition |
| `Dockerfile` | Container build |
