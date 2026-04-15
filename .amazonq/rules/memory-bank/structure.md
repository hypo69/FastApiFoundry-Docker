# FastAPI Foundry — Project Structure

## Root Layout
```
FastApiFoundry-Docker/
├── src/                        # Core application source
├── static/                     # Web UI (HTML/JS/CSS)
├── extentions/                 # Browser extension
├── mcp-powershell-servers/     # MCP server implementations
├── SANDBOX/sdk/                # Experimental SDK
├── scripts/                    # PowerShell utility scripts
├── utils/                      # Python utility scripts
├── tests/                      # Test suite
├── docs/                       # Documentation (Markdown)
├── examples/                   # API usage examples
├── logs/                       # Runtime log files
├── rag_index/                  # FAISS vector index storage
├── models/hf/                  # Local HuggingFace model cache
├── run.py                      # Main entry point
├── config.json                 # App configuration (GUI/runtime)
├── config_manager.py           # Unified config loader
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker setup
├── Dockerfile                  # Container definition
├── launcher.ps1                # Interactive PowerShell launcher
└── start.ps1                   # Quick start script
```

## Source Code (`src/`)
```
src/
├── api/
│   ├── app.py                  # FastAPI application factory (create_app())
│   ├── main.py                 # ASGI entry point (app instance)
│   ├── models.py               # Pydantic request/response models
│   └── endpoints/
│       ├── main.py             # Root routes (/, /static)
│       ├── health.py           # GET /api/v1/health
│       ├── models.py           # GET /api/v1/models
│       ├── generate.py         # POST /api/v1/generate
│       ├── chat_endpoints.py   # POST /api/v1/chat
│       ├── foundry.py          # Foundry status endpoints
│       ├── foundry_management.py  # Start/stop Foundry service
│       ├── foundry_models.py   # Foundry model list/load
│       ├── rag.py              # RAG search endpoints
│       ├── config.py           # Config read/write endpoints
│       ├── logs.py             # Log streaming endpoints
│       ├── hf_models.py        # HuggingFace model endpoints
│       ├── llama_cpp.py        # llama.cpp endpoints
│       └── mcp_powershell.py   # MCP PowerShell bridge
├── core/
│   └── config.py               # Re-exports config from config_manager
├── models/
│   ├── foundry_client.py       # Foundry HTTP client (singleton)
│   ├── enhanced_foundry_client.py  # Extended Foundry client
│   ├── hf_client.py            # HuggingFace inference client
│   └── model_manager.py        # Multi-backend model manager
├── rag/
│   └── rag_system.py           # FAISS RAG pipeline
├── logger/
│   └── __init__.py             # Logger setup
└── utils/
    ├── logging_config.py       # Logging configuration
    ├── logging_system.py       # Structured logging system
    ├── log_analyzer.py         # Log analysis utilities
    ├── env_processor.py        # .env loading + config substitution
    └── foundry_finder.py       # Foundry process/port discovery
```

## Configuration System
- `config.json` — primary runtime config (ports, modes, RAG settings, Foundry URL)
- `.env` — secrets (API keys, tokens, GitHub PAT)
- `config_manager.py` — loads both, substitutes `${VAR}` references from `.env` into `config.json`
- `src/core/config.py` — thin re-export: `from config_manager import config; settings = config`

## Web Interface (`static/`)
| File | Purpose |
|------|---------|
| `index.html` | Main dashboard |
| `chat.html` | Chat UI with session support |
| `control.html` | Foundry service start/stop/status |
| `ai.html` | Direct AI generation UI |
| `app.js` | Shared frontend logic |

## Browser Extension (`extentions/browser-extention-summarizer/`)
```
├── manifest.json               # Chrome extension manifest
├── popup.html / popup.js       # Extension popup
├── chat.html / chat.js         # In-extension chat
├── providers.html / providers.js  # Provider configuration UI
├── connectors/                 # AI provider connectors
│   ├── foundry.js              # Local Foundry connector
│   ├── gemini.js               # Google Gemini connector
│   ├── openai-compat.js        # OpenAI-compatible connector
│   └── openrouter.js           # OpenRouter connector
├── prompts/                    # Localized system prompts
│   └── {en,ru,de,fr,es,ja,zh,factcheck}.js
├── summarizer.js               # Core summarization logic
├── background.js               # Service worker
└── logger.js                   # Extension logging
```

## MCP Servers (`mcp-powershell-servers/`)
```
src/
├── servers/
│   ├── McpSTDIOServer.ps1      # STDIO MCP server (main)
│   ├── McpHttpsServer.ps1      # HTTPS MCP server
│   ├── McpWPCLIServer.ps1      # WordPress CLI MCP server
│   ├── McpHuggingFaceServer.ps1
│   ├── huggingface_mcp.py      # Python HuggingFace MCP
│   ├── aistros-foundry/        # Foundry MCP server
│   └── wordpress-cli/          # WP-CLI MCP server
└── clients/
    ├── python_client.py        # Python MCP client
    ├── nodejs.js               # Node.js MCP client
    └── powershell.ps1          # PowerShell MCP client
```

## Architectural Patterns

### Request Flow
```
Client → FastAPI (port 9696)
           ↓
    Endpoint Router
           ↓
    foundry_client (HTTP) → Foundry Local (port 50477)
                                    ↓
                              AI Model (ONNX)
```

### Singleton Clients
- `foundry_client` — module-level singleton in `src/models/foundry_client.py`
- Shared across all endpoint handlers via import

### Lifespan Management
- `app.py` uses `@asynccontextmanager` lifespan for startup/shutdown
- Foundry client closed on shutdown via `await foundry_client.close()`

### Logging Architecture
- Per-component log files in `logs/` (e.g., `foundry-client.log`, `fastapi-app.log`)
- Structured JSONL sidecars (`*-structured.jsonl`)
- Error-only files (`*-errors.log`)
- Configured via `src/utils/logging_config.py`

### Port Management
- Default API port: 9696
- Auto-find free port in range 9696–9796 (configurable)
- Foundry port: auto-discovered via `tasklist` + `netstat` or `FOUNDRY_BASE_URL` env var
