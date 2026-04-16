# FastAPI Foundry — Project Structure

## Root Layout
```
FastApiFoundry-Docker/
├── src/                    # Core Python application
├── static/                 # Web UI (HTML/JS)
├── mcp-powershell-servers/ # PowerShell MCP server suite
├── extentions/             # Browser extension (summarizer)
├── SANDBOX/sdk/            # Experimental SDK / client library
├── examples/               # Usage examples (Python clients)
├── tests/                  # pytest test suite
├── scripts/                # PowerShell utility scripts
├── utils/                  # Standalone Python utilities
├── docs/                   # Full documentation (Markdown)
├── logs/                   # Runtime log files
├── rag_index/              # FAISS index + metadata (runtime)
├── bin/                    # llama.cpp binaries (Windows x64)
├── config.json             # Main application configuration
├── config_manager.py       # Unified config loader (JSON + .env)
├── run.py                  # Entry point — starts uvicorn
├── launcher.ps1            # Interactive PowerShell launcher
├── docker-compose.yml      # Docker deployment
└── requirements.txt        # Python dependencies
```

## src/ — Application Source
```
src/
├── api/
│   ├── app.py              # FastAPI factory (create_app)
│   ├── main.py             # Uvicorn entry
│   ├── models.py           # Shared Pydantic request/response models
│   └── endpoints/          # One file per feature area
│       ├── health.py       # GET /api/v1/health
│       ├── generate.py     # POST /api/v1/generate
│       ├── chat_endpoints.py  # POST /api/v1/chat
│       ├── models.py       # GET/POST /api/v1/models
│       ├── foundry.py      # Foundry status/control
│       ├── foundry_management.py  # Start/stop Foundry service
│       ├── foundry_models.py      # Foundry model list/load
│       ├── rag.py          # RAG search + index management
│       ├── config.py       # Runtime config read/write
│       ├── logs.py         # Log streaming
│       ├── hf_models.py    # HuggingFace model endpoints
│       ├── llama_cpp.py    # llama.cpp server endpoints
│       ├── mcp_powershell.py  # PowerShell MCP proxy
│       ├── agent.py        # Agent endpoints
│       └── converter.py    # GGUF→ONNX converter endpoint
├── core/
│   └── config.py           # Re-exports config_manager.config as `settings`
├── models/
│   ├── foundry_client.py   # Async HTTP client for Foundry Local API
│   ├── enhanced_foundry_client.py  # Extended client with retry/fallback
│   ├── hf_client.py        # HuggingFace transformers client
│   └── model_manager.py    # Unified model switching logic
├── rag/
│   └── rag_system.py       # FAISS + sentence-transformers RAG
├── agents/
│   ├── base.py             # Abstract agent base class
│   └── powershell_agent.py # PowerShell execution agent
├── converter/
│   └── gguf_to_onnx.py     # GGUF→ONNX conversion logic
├── logger/
│   └── __init__.py         # Logger factory
└── utils/
    ├── logging_config.py   # Logging setup (file + console)
    ├── logging_system.py   # Structured JSON logging
    ├── log_analyzer.py     # Log parsing utilities
    ├── env_processor.py    # .env variable substitution in config
    └── foundry_finder.py   # Auto-detect Foundry installation path
```

## mcp-powershell-servers/
```
mcp-powershell-servers/
├── src/
│   ├── servers/            # PowerShell MCP server scripts
│   │   ├── McpSTDIOServer.ps1      # STDIO MCP server
│   │   ├── McpHttpsServer.ps1      # HTTPS MCP server
│   │   ├── McpWPCLIServer.ps1      # WordPress CLI MCP server
│   │   └── huggingface_mcp.py      # HuggingFace MCP (Python)
│   ├── clients/
│   │   ├── python_client.py        # Python MCP client
│   │   ├── nodejs.js               # Node.js MCP client
│   │   └── powershell.ps1          # PowerShell MCP client
│   └── config/                     # Server configuration JSONs
└── Start-MCPServers.ps1            # Launcher for all MCP servers
```

## extentions/browser-extention-summarizer/
```
browser-extention-summarizer/
├── connectors/             # AI provider connectors
│   ├── foundry.js          # Foundry Local connector
│   ├── gemini.js           # Google Gemini connector
│   ├── openai-compat.js    # OpenAI-compatible connector
│   └── openrouter.js       # OpenRouter connector
├── prompts/                # Localized system prompts
│   ├── en.js, ru.js, de.js, fr.js, es.js, ja.js, zh.js
│   └── factcheck.js        # Fact-checking prompt
├── popup.html/js           # Extension popup UI
├── chat.html/js            # Chat interface
├── providers.html/js       # Provider configuration UI
├── summarizer.js           # Core summarization logic
├── background.js           # Service worker
└── manifest.json           # Chrome extension manifest
```

## Configuration Files
| File | Purpose |
|---|---|
| `config.json` | Main config: server, foundry, RAG, llama.cpp, security, docker |
| `.env` | Secrets: API keys, tokens, URLs (substituted into config.json via `${VAR}`) |
| `.env.example` | Template for .env |
| `config_manager.py` | Loads config.json, resolves `${VAR}` and `${VAR:default}` from .env |

## Key Architectural Patterns
- **Factory pattern**: `create_app()` in `src/api/app.py` builds the FastAPI instance
- **Singleton clients**: `foundry_client` is a module-level singleton
- **Router-per-feature**: each endpoint file registers its own `APIRouter`
- **Config via JSON+env**: `config.json` holds structure, `.env` holds secrets
- **Lifespan context manager**: startup/shutdown hooks via `@asynccontextmanager`
- **Multi-backend**: same API surface over Foundry, llama.cpp, or HuggingFace
