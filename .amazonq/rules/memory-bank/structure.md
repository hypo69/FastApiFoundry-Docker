# FastAPI Foundry — Project Structure

## Root Directory Layout
```
FastApiFoundry-Docker/
├── src/                    # Core Python application source
├── static/                 # Web UI (SPA) — HTML, JS, CSS, partials
├── mcp-powershell-servers/ # MCP server implementations (PowerShell + Python)
├── scripts/                # PowerShell utility scripts
├── install/                # Installation scripts (Foundry, HuggingFace, models)
├── check_engine/           # Diagnostic and smoke-test scripts
├── examples/               # API usage examples
├── SANDBOX/sdk/            # Experimental SDK for the API
├── extentions/             # Browser extension (summarizer)
├── docs/                   # MkDocs source documentation (Russian)
├── site/                   # Built MkDocs static site
├── logs/                   # Runtime log files (structured + plain)
├── rag_index/              # FAISS vector index storage
├── bin/                    # llama.cpp binaries (Windows x64)
├── utils/                  # Standalone utility scripts
├── config.json             # Main application configuration
├── config_manager.py       # Singleton Config class (loads config.json)
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker deployment
├── Dockerfile              # Container image definition
├── launcher.ps1 / .exe     # Windows GUI launcher
├── install.ps1 / .exe      # One-click installer
└── .env / .env.example     # Environment variables
```

## src/ — Core Application
```
src/
├── api/
│   ├── app.py              # FastAPI application factory (create_app)
│   ├── main.py             # Uvicorn entry point
│   ├── models.py           # Pydantic request/response models
│   ├── endpoints/          # All API route handlers
│   │   ├── main.py         # Root routes (serves index.html)
│   │   ├── health.py       # GET /api/v1/health
│   │   ├── models.py       # Model listing endpoints
│   │   ├── generate.py     # Text generation endpoint
│   │   ├── chat_endpoints.py  # Chat with session history
│   │   ├── foundry.py      # Foundry status/control
│   │   ├── foundry_management.py  # Start/stop Foundry service
│   │   ├── foundry_models.py      # Foundry model management
│   │   ├── rag.py          # RAG search endpoints
│   │   ├── hf_models.py    # HuggingFace model endpoints
│   │   ├── llama_cpp.py    # llama.cpp endpoints
│   │   ├── mcp_powershell.py  # MCP PowerShell endpoints
│   │   ├── agent.py        # Agent endpoints
│   │   ├── ai_endpoints.py # Unified AI generation
│   │   ├── config.py       # Config read/write endpoints
│   │   ├── logs.py         # Log viewer endpoints
│   │   ├── converter.py    # GGUF→ONNX converter endpoints
│   │   └── translation.py  # Translation endpoints
│   └── middleware/         # Custom middleware
├── core/
│   └── config.py           # Re-exports config from config_manager.py
├── models/
│   ├── foundry_client.py   # Async Foundry API client (singleton)
│   ├── enhanced_foundry_client.py  # Extended Foundry client
│   ├── hf_client.py        # HuggingFace Transformers client
│   └── model_manager.py    # Unified model manager
├── rag/
│   ├── rag_system.py       # RAG orchestrator (FAISS + sentence-transformers)
│   └── indexer.py          # Document indexing logic
├── agents/
│   ├── base.py             # Base agent class
│   └── powershell_agent.py # PowerShell agent
├── translator/
│   └── translator.py       # Translation module
├── converter/
│   └── gguf_to_onnx.py     # GGUF to ONNX conversion
├── logger/
│   └── __init__.py         # Logger setup
└── utils/
    ├── logging_config.py   # Logging configuration
    ├── logging_system.py   # Structured logging system
    ├── log_analyzer.py     # Log analysis utilities
    ├── foundry_finder.py   # Auto-detect Foundry port
    └── env_processor.py    # .env variable processing
```

## static/ — Web Interface (SPA)
```
static/
├── index.html              # Main SPA shell
├── app.js                  # SPA bootstrap
├── js/
│   ├── ui.js               # UI state management
│   ├── models.js           # Model management UI
│   ├── chat.js             # Chat interface
│   ├── config.js           # Config editor UI
│   ├── foundry.js          # Foundry control UI
│   ├── rag.js              # RAG UI
│   ├── hf.js               # HuggingFace UI
│   ├── llama.js            # llama.cpp UI
│   ├── mcp.js              # MCP UI
│   ├── agent.js            # Agent UI
│   ├── editor.js           # Code/config editor
│   ├── i18n.js             # Internationalization
│   └── translation.js      # Translation UI
├── partials/               # HTML tab fragments (loaded dynamically)
│   ├── _tab_chat.html
│   ├── _tab_models.html
│   ├── _tab_foundry.html
│   ├── _tab_rag.html
│   ├── _tab_settings.html
│   └── ... (15 total tabs)
├── locales/                # i18n strings (en, ru, he)
└── css/main.css            # Global styles
```

## Configuration System
- `config.json` — primary config (sections: `fastapi_server`, `foundry_ai`, `rag_system`, `port_management`, `directories`)
- `config_manager.py` — singleton `Config` class, loaded once at startup
- `src/core/config.py` — re-exports `config` for backward compatibility
- `.env` — secrets: `API_KEY`, `SECRET_KEY`, `GITHUB_PAT`, `HF_TOKEN`, `FOUNDRY_DYNAMIC_PORT`

## Key Architectural Patterns
- **Singleton Config**: `Config.__new__` ensures one instance; `config = Config()` at module level
- **Singleton Clients**: `foundry_client = FoundryClient()` global instance in `foundry_client.py`
- **Async HTTP**: All Foundry API calls use `aiohttp.ClientSession` with lazy init
- **Lifespan Events**: RAG init and model auto-load happen in `@asynccontextmanager lifespan`
- **Router Prefix**: All API routes use `/api/v1` prefix; static files at `/static`
- **Model Prefixes**: `hf::model-name` for HuggingFace, `llama::model-name` for llama.cpp, bare name for Foundry
- **Port Discovery**: Foundry port auto-detected by scanning `[62171, 50477, 58130]`
