# FastAPI Foundry — Project Structure

**Version:** 0.7.0
**Project:** AI Assistant (ai_assist)

---

## Root Directory Layout

```
FastApiFoundry-Docker/
├── src/                    # Core Python application
├── static/                 # Web UI (SPA)
├── docs/                   # MkDocs source (ru/ + en/)
├── site/                   # MkDocs built output
├── install/                # Guided installer (web UI + scripts)
├── scripts/                # Operational PowerShell scripts
├── check_engine/           # Diagnostic and smoke-test scripts
├── mcp-powershell-servers/ # MCP servers (PowerShell STDIO)
├── sdk/                    # Python SDKs (fastapi_foundry, microsoft_foundry)
├── extensions/             # Browser extensions
├── bin/                    # Native binaries (llama.cpp, Windows x64)
├── rag_index/              # FAISS index storage
├── logs/                   # Application logs
├── SANDBOX/                # Experimental SDK examples
├── utils/                  # Standalone utility scripts
├── examples/               # API usage examples
├── notebooks/              # Jupyter notebooks
├── archive/                # Rotated log archives
├── ~venv/                  # Python virtual environment
├── run.py                  # Python entry point
├── start.ps1               # Primary Windows launcher
├── install.ps1             # Dependency installer
├── config.json             # Public configuration
├── config_manager.py       # Config loader (singleton)
├── .env / .env.example     # Secrets and env vars
├── docker-compose.yml      # Docker deployment
├── Dockerfile
├── requirements.txt        # Core dependencies
├── requirements-rag.txt    # RAG-specific deps
├── requirements-extras.txt # Optional extras
└── mkdocs.yml              # Documentation config
```

---

## src/ — Application Source

```
src/
├── api/
│   ├── app.py              # FastAPI factory (create_app, lifespan)
│   ├── main.py             # Uvicorn entry point
│   ├── models.py           # Pydantic request/response models
│   └── endpoints/          # One file per feature area
│       ├── generate.py         # POST /api/v1/generate
│       ├── ai_endpoints.py     # POST /api/v1/ai/generate, /ai/chat, /ai/chat/stream
│       ├── chat_endpoints.py   # Chat session management
│       ├── health.py           # GET /api/v1/health
│       ├── models.py           # GET /api/v1/models
│       ├── foundry.py          # Foundry model operations
│       ├── foundry_management.py  # Start/stop/status Foundry service
│       ├── foundry_models.py   # List loaded Foundry models
│       ├── hf_models.py        # HuggingFace model management
│       ├── llama_cpp.py        # llama.cpp server management
│       ├── ollama.py           # Ollama integration
│       ├── rag.py              # RAG search + text extraction endpoints
│       ├── config.py           # Config read/write endpoint
│       ├── logs.py             # Log streaming endpoint
│       ├── agent.py            # AI agent execution
│       ├── translator.py       # Translation endpoint
│       ├── mcp_powershell.py   # MCP PowerShell bridge
│       ├── converter.py        # GGUF→ONNX converter endpoint
│       └── system_stats.py     # System resource stats
├── models/
│   ├── foundry_client.py       # Foundry Local HTTP client (singleton)
│   ├── enhanced_foundry_client.py
│   ├── hf_client.py            # HuggingFace Transformers client
│   ├── model_manager.py        # Unified model manager
│   └── ollama_client.py        # Ollama HTTP client
├── rag/
│   ├── rag_system.py           # RAGSystem: FAISS index, search, cache
│   ├── indexer.py              # Document indexing pipeline
│   └── text_extractor_4_rag/   # 40+ format text extraction module
├── core/
│   └── config.py               # Re-exports config_manager.config
├── agents/
│   ├── base.py                 # BaseAgent abstract class
│   └── powershell_agent.py     # PowerShell command agent
├── utils/
│   ├── command_agent.py        # Async CLI command runner with circuit breaker
│   ├── foundry_utils.py        # Foundry port discovery (parses `foundry service status`)
│   ├── foundry_finder.py       # Alternative Foundry discovery
│   ├── api_utils.py            # @api_response_handler decorator
│   ├── logging_config.py       # Logging setup
│   ├── logging_system.py       # Structured JSONL logging
│   ├── log_analyzer.py         # Log analysis utilities
│   ├── text_utils.py           # Token counting, text helpers
│   ├── translator.py           # Translation via MyMemory/LibreTranslate
│   ├── env_processor.py        # .env file processing
│   └── process_utils.py        # Process management helpers
└── converter/
    └── gguf_to_onnx.py         # GGUF to ONNX model conversion
```

---

## static/ — Web UI

```
static/
├── index.html              # Main SPA entry point
├── app.js                  # SPA bootstrap
├── css/main.css            # Global styles
├── js/
│   ├── ui.js               # Core UI: tab switching, modals, notifications
│   ├── chat.js             # Chat tab logic
│   ├── foundry.js          # Foundry tab: load/unload models, status polling
│   ├── models.js           # Models tab
│   ├── rag.js              # RAG tab: search, extract, index
│   ├── config.js           # Settings tab: load/save config
│   ├── hf.js               # HuggingFace tab
│   ├── llama.js            # llama.cpp tab
│   ├── ollama.js           # Ollama tab
│   ├── agent.js            # Agent tab
│   ├── mcp.js              # MCP tab
│   ├── i18n.js             # Internationalization (data-i18n attributes)
│   ├── model-badge.js      # Active model status badge
│   └── providers.js        # Provider registry UI
├── locales/
│   ├── en.json             # English strings
│   ├── ru.json             # Russian strings
│   └── he.json             # Hebrew strings
└── partials/               # HTML partials (one per tab/modal)
    ├── _tab_chat.html
    ├── _tab_foundry.html
    ├── _tab_rag.html
    ├── _tab_settings.html  # (+ sub-partials per settings section)
    └── ...
```

---

## Configuration System

- `config.json` — all public settings (server, AI backends, RAG, logging, security, i18n)
- `config_manager.py` — singleton `config` object; `src/core/config.py` re-exports it
- `.env` — secrets: `HF_TOKEN`, `FOUNDRY_BASE_URL`, `LLAMA_MODEL_PATH`, API keys
- `config.json` sections: `fastapi_server`, `foundry_ai`, `rag_system`, `security`, `logging`, `docs_server`, `llama_cpp`, `directories`, `huggingface`, `translator`, `text_extractor`

---

## Key Architectural Patterns

### Model Routing (generate.py)
Model selection by prefix in model ID string:
- `hf::model-name` → HuggingFace client
- `llama::path/to/model.gguf` → llama.cpp OpenAI-compatible API
- `ollama::model-name` → Ollama client
- no prefix → Foundry Local client

### Singleton Clients
`foundry_client`, `rag_system`, `hf_client` are module-level singletons imported across endpoints.

### API Response Decorator
`@api_response_handler` (from `src/utils/api_utils.py`) wraps endpoint functions for consistent error handling and response format.

### Lifespan Management
`app.py` uses FastAPI `@asynccontextmanager lifespan` for startup (RAG init, model auto-load) and shutdown (close aiohttp sessions).

### Logging
Dual output: standard Python `logging` + structured JSONL to `logs/fastapi-foundry-structured.jsonl`. Log rotation with archive management.
