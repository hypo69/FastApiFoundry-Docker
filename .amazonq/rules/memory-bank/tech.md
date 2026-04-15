# FastAPI Foundry — Technology Stack

## Language & Runtime
- Python 3.11+ (entry point shebang: `python311`)
- Windows primary platform (PowerShell launchers, tasklist/netstat for Foundry discovery)
- Linux/Docker secondary (Dockerfile, docker-compose)

## Core Framework
| Package | Version | Role |
|---|---|---|
| fastapi | >=0.104.0 | Web framework, routing, OpenAPI docs |
| uvicorn[standard] | >=0.24.0 | ASGI server |
| aiohttp | >=3.9.0 | Async HTTP client for Foundry API |
| requests | >=2.31.0 | Sync HTTP (Foundry health checks in run.py) |
| python-dotenv | >=1.0.0 | .env loading |

## RAG System
| Package | Version | Role |
|---|---|---|
| sentence-transformers | >=2.2.0 | Text embeddings (default: all-MiniLM-L6-v2) |
| faiss-cpu | >=1.7.0 | Vector similarity search |
| numpy | >=1.24.0 | Array operations |
| torch | >=2.0.0 | Backend for sentence-transformers |

## Utilities
| Package | Version | Role |
|---|---|---|
| PyYAML | >=6.0 | YAML config parsing |
| psutil | >=5.9.0 | Process/system monitoring |
| websockets | >=11.0.0 | WebSocket support |
| watchfiles | >=0.20.0 | Hot reload (dev mode) |

## Testing
| Package | Version | Role |
|---|---|---|
| pytest | >=7.4.0 | Test runner |
| pytest-asyncio | >=0.21.0 | Async test support |

## External Service Dependency
- **Microsoft Foundry Local CLI** — must be running separately on port 50477 (auto-detected)
- Exposes OpenAI-compatible `/v1/` API

## Configuration System
- `config.json` — primary config file (loaded by `Config` singleton in `config_manager.py`)
- `.env` — secrets and runtime overrides (loaded via `src/utils/env_processor.py`)
- `src/core/config.py` — thin re-export: `from config_manager import config; settings = config`
- `Config` is a singleton (`__new__` pattern), properties map to `config.json` sections

### config.json Sections
```json
{
  "fastapi_server": { "host", "port", "workers", "reload", "log_level" },
  "foundry_ai": { "base_url", "default_model", "auto_load_default", "temperature", "max_tokens" },
  "port_management": { "auto_find_free_port", "port_range_start", "port_range_end" },
  "rag_system": { "enabled", "index_dir", "model", "chunk_size", "top_k" }
}
```

## Docker
- `Dockerfile` — builds image `fastapi-foundry:0.2.1`
- `docker-compose.yml` — single service, port `${PORT:-8000}:8000`
- Volumes: `./logs`, `./rag_index`, `./.env` (read-only)
- Healthcheck: `curl http://localhost:9696/api/v1/health`

## Development Commands

### Start server (manual)
```bash
python run.py
# or with venv
venv\Scripts\python.exe run.py
```

### Start with launcher (Windows)
```powershell
.\launcher.ps1              # Interactive menu
.\launcher.ps1 -Mode quick  # Auto-install + Foundry + FastAPI
.\launcher.ps1 -Mode diag   # Diagnostics
.\launcher.ps1 -Mode setup  # Configure .env
```

### Docker
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Tests
```bash
python -m pytest tests/ -v
python -m pytest tests/test_api.py
```

### Config validation
```bash
python check_env.py
python diagnose.py
```

### Syntax check (pre-commit)
```bash
python -m py_compile src/**/*.py
python -m flake8 src/ --max-line-length=120
```

## API Endpoints Summary
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/health | Service health |
| GET | /api/v1/models | List available models |
| POST | /api/v1/generate | Text generation |
| POST | /api/v1/chat | Chat completion |
| POST | /api/v1/rag/search | RAG context search |
| DELETE | /api/v1/rag/clear | Clear RAG index |
| GET/POST | /api/v1/config | Read/write config.json |
| GET | /api/v1/logs | Log retrieval |
| GET | /docs | Swagger UI |

## Default Ports
| Service | Port |
|---|---|
| FastAPI | 9696 (config.json default) |
| Foundry Local | 50477 (auto-detected) |
| Docker mapped | 8000 (docker-compose) |

## Logging
- Runtime logs in `logs/` directory
- Per-component log files: `fastapi-app.log`, `foundry-client.log`, `models-api.log`, etc.
- Structured JSON logs: `*-structured.jsonl`
- Error logs: `*-errors.log`
- Configured via `src/utils/logging_config.py` and `src/utils/logging_system.py`
