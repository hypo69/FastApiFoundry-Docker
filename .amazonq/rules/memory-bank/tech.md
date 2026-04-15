# FastAPI Foundry — Technology Stack

## Languages & Runtimes
| Language | Version | Usage |
|---|---|---|
| Python | 3.11+ | Core application, MCP servers, utilities |
| JavaScript | ES2020+ | Browser extension, web UI |
| PowerShell | 5.1+ | MCP servers, launcher scripts, Windows automation |
| HTML/CSS | — | Static web interface |

## Core Python Framework
| Package | Version | Role |
|---|---|---|
| fastapi | >=0.104.0 | Web framework |
| uvicorn[standard] | >=0.24.0 | ASGI server |
| aiohttp | >=3.9.0 | Async HTTP client (Foundry API calls) |
| requests | >=2.31.0 | Sync HTTP client (startup checks) |
| python-dotenv | >=1.0.0 | .env loading |

## AI / ML Dependencies
| Package | Version | Role |
|---|---|---|
| sentence-transformers | >=2.2.0 | RAG embeddings |
| faiss-cpu | >=1.7.0 | Vector similarity search |
| torch | >=2.0.0 | Required by sentence-transformers |
| numpy | >=1.24.0 | Numerical operations |
| transformers | >=4.40.0 | HuggingFace model inference |
| accelerate | >=0.30.0 | HF model acceleration |
| huggingface_hub | >=0.23.0 | HF model download |
| optimum[onnxruntime] | >=1.16.0 | GGUF→ONNX conversion |
| onnxruntime | >=1.17.0 | ONNX model inference |

## Utilities
| Package | Version | Role |
|---|---|---|
| PyYAML | >=6.0 | YAML config parsing |
| psutil | >=5.9.0 | Process/port management |
| websockets | >=11.0.0 | WebSocket support |
| watchfiles | >=0.20.0 | Hot reload (dev mode) |

## Testing
| Package | Version | Role |
|---|---|---|
| pytest | >=7.4.0 | Test runner |
| pytest-asyncio | >=0.21.0 | Async test support |

## External Services / Binaries
| Component | Port | Notes |
|---|---|---|
| Microsoft Foundry Local | 50477 (dynamic) | AI model inference backend |
| llama.cpp server | 9780 | Alternative GGUF inference |
| FastAPI app | 9696 (default) | Main API, auto-finds free port |
| llama.cpp binaries | — | Bundled in `bin/llama-b8802-bin-win-cpu-x64/` |

## Configuration System
- `config.json` — structured JSON config with `${VAR}` and `${VAR:default}` substitution
- `.env` — secrets and environment-specific overrides
- `config_manager.py` — singleton `Config` class, loads `config.json`, exposes typed properties
- `src/core/config.py` — re-exports `config` as `settings` for backward compatibility
- `src/utils/env_processor.py` — resolves `${VAR}` placeholders at startup

## Development Commands

### Start server (Foundry already running)
```bash
python run.py
# or with venv
venv\Scripts\python.exe run.py
```

### Interactive launcher (recommended)
```powershell
.\launcher.ps1           # interactive menu
.\launcher.ps1 -Mode quick   # auto-install + Foundry + FastAPI
.\launcher.ps1 -Mode diag    # diagnostics
.\launcher.ps1 -Mode setup   # configure .env
```

### Docker
```bash
docker-compose up --build
```

### Run tests
```bash
python -m pytest tests/ -v
python -m pytest tests/test_api.py -v
```

### Syntax check
```bash
python -m py_compile src/api/app.py
python -m flake8 src/ --max-line-length=120
```

### Check environment
```bash
python check_env.py
```

### Create RAG index
```bash
python create_rag_index.py
python rag_indexer.py
```

### Health check
```bash
curl http://localhost:9696/api/v1/health
curl http://localhost:9696/docs
```

## Key API Endpoints
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/health | Service health + model status |
| GET | /api/v1/models | List available models |
| POST | /api/v1/generate | Single text generation |
| POST | /api/v1/chat | Chat with session history |
| GET | /api/v1/foundry/status | Foundry service status |
| POST | /api/v1/foundry/start | Start Foundry service |
| POST | /api/v1/foundry/stop | Stop Foundry service |
| GET | /api/v1/foundry/models | List Foundry models |
| POST | /api/v1/rag/search | RAG context search |
| DELETE | /api/v1/rag/index | Clear RAG index |
| GET | /api/v1/config | Read config.json |
| PUT | /api/v1/config | Update config.json |
| GET | /api/v1/logs | Stream log files |
| GET | /docs | Swagger UI |

## Docker Configuration
- Image: `fastapi-foundry:0.2.1`
- Container: `fastapi-foundry-docker`
- Volumes: `./logs:/app/logs`, `./rag_index:/app/rag_index`
- Healthcheck: interval 30s, timeout 10s, 3 retries

## Browser Extension
- Type: Chrome/Chromium Manifest V3
- Providers: Foundry Local, Gemini, OpenAI-compatible, OpenRouter
- Languages: en, ru, de, fr, es, ja, zh
- Entry: `extentions/browser-extention-summarizer/manifest.json`
