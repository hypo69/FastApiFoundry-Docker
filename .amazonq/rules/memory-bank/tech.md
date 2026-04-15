# FastAPI Foundry — Technology Stack

## Languages & Runtimes
| Language | Version | Usage |
|----------|---------|-------|
| Python | 3.11+ | Core API server, RAG, clients |
| JavaScript | ES2020+ | Browser extension, web UI |
| PowerShell | 5.1+ | MCP servers, launcher scripts, utilities |
| HTML/CSS | — | Static web interface |

## Core Python Framework
| Package | Version | Role |
|---------|---------|------|
| `fastapi` | ≥0.104.0 | Web framework |
| `uvicorn[standard]` | ≥0.24.0 | ASGI server |
| `aiohttp` | ≥3.9.0 | Async HTTP client |
| `requests` | ≥2.31.0 | Sync HTTP client (Foundry discovery) |
| `python-dotenv` | ≥1.0.0 | `.env` loading |

## AI / ML
| Package | Version | Role |
|---------|---------|------|
| `sentence-transformers` | ≥2.2.0 | RAG embeddings |
| `faiss-cpu` | ≥1.7.0 | Vector similarity search |
| `numpy` | ≥1.24.0 | Numerical ops |
| `torch` | ≥2.0.0 | ML backend (RAG, HF) |
| `transformers` | ≥4.40.0 | HuggingFace model inference |
| `accelerate` | ≥0.30.0 | HF model acceleration |
| `huggingface_hub` | ≥0.23.0 | Model download/management |

## Utilities
| Package | Version | Role |
|---------|---------|------|
| `PyYAML` | ≥6.0 | Config parsing |
| `psutil` | ≥5.9.0 | Process/port management |
| `websockets` | ≥11.0.0 | WebSocket support |
| `watchfiles` | ≥0.20.0 | Hot reload (dev mode) |

## Testing
| Package | Version | Role |
|---------|---------|------|
| `pytest` | ≥7.4.0 | Test runner |
| `pytest-asyncio` | ≥0.21.0 | Async test support |

## External Services
| Service | Port | Protocol |
|---------|------|---------|
| Microsoft Foundry Local CLI | 50477 (dynamic) | HTTP REST (OpenAI-compat) |
| llama.cpp server | 8080 | HTTP REST |
| HuggingFace Hub | — | HTTPS |

## Configuration Files
| File | Purpose |
|------|---------|
| `config.json` | Runtime config: ports, modes, model defaults, RAG, Docker |
| `.env` | Secrets: `API_KEY`, `SECRET_KEY`, `GITHUB_PAT`, `FOUNDRY_BASE_URL` |
| `.env.example` | Template for `.env` |
| `config_manager.py` | Loads `config.json`, substitutes `${VAR}` from `.env` |

### Key config.json Sections
```json
{
  "fastapi_server": { "port": 9696, "host": "0.0.0.0", "mode": "dev", "reload": true },
  "foundry_ai":     { "base_url": "${FOUNDRY_BASE_URL}", "default_model": "...", "auto_load_default": false },
  "rag_system":     { "enabled": true, "model": "sentence-transformers/all-MiniLM-L6-v2", "top_k": 5 },
  "security":       { "api_key": "...", "secret_key": "${SECRET_KEY}" },
  "port_management":{ "auto_find_free_port": true, "port_range_start": 9696, "port_range_end": 9796 }
}
```

## Docker
- Base image: Python 3.11 (see `Dockerfile`)
- Compose: `docker-compose.yml`
- Exposed port: `${PORT:-8000}` → container 8000
- Volumes: `./logs`, `./rag_index`, `./.env`
- Health check: `curl http://localhost:9696/api/v1/health`

## Development Commands

### Start Server
```bash
# Direct (Foundry already running)
python run.py

# With virtual environment
venv\Scripts\python.exe run.py

# PowerShell launcher (interactive menu)
.\launcher.ps1

# Quick start
.\launcher.ps1 -Mode quick

# Docker
docker-compose up -d
```

### Install Dependencies
```bash
pip install -r requirements.txt

# RAG-specific
python install_rag_deps.py
```

### Environment Setup
```bash
cp .env.example .env
# Edit .env with your values
python check_env.py          # Validate config
.\launcher.ps1 -Mode setup   # Interactive setup
```

### Testing
```bash
pytest tests/ -v
pytest tests/test_api.py
python -m pytest tests/test_rag.py
```

### RAG Index
```bash
python create_rag_index.py
python rag_indexer.py
```

### Diagnostics
```bash
python diagnose.py
.\launcher.ps1 -Mode diag
```

### Syntax Check
```bash
python -m py_compile src/api/app.py
python -m flake8 src/ --max-line-length=120
```

## API Endpoints Summary
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/models` | List available models |
| POST | `/api/v1/generate` | Text generation |
| POST | `/api/v1/chat` | Chat with session |
| GET | `/api/v1/foundry/status` | Foundry service status |
| POST | `/api/v1/foundry/start` | Start Foundry |
| GET | `/api/v1/rag/search` | RAG search |
| GET/PUT | `/api/v1/config` | Read/write config |
| GET | `/api/v1/logs` | Log streaming |
| GET | `/docs` | Swagger UI |

## Browser Extension Tech
- Manifest V3 (Chrome)
- Service Worker (`background.js`)
- Multi-provider connectors (Foundry, Gemini, OpenAI-compat, OpenRouter)
- Localized prompts as ES modules (`prompts/*.js`)
- No build step — plain JS modules

## MCP Server Tech
- Protocol: MCP 2024-11-05
- Transport: STDIO (primary) and HTTPS
- PowerShell servers: `McpSTDIOServer.ps1`, `McpHttpsServer.ps1`
- Python client: `mcp-powershell-servers/src/clients/python_client.py`
- Config: `mcp-powershell-servers/src/config/*.json`
