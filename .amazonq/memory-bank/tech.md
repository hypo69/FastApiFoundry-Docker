# FastAPI Foundry - Technology Stack

## Programming Languages

### Python 3.8+
- **Primary Language**: All core application logic
- **Async/Await**: Modern asynchronous programming patterns
- **Type Hints**: Full type annotation for better IDE support and validation
- **Version Requirement**: Python 3.8 or higher for compatibility

### JavaScript (ES6+)
- **Frontend**: Web interface implementation in `static/app.js`
- **Modern Features**: Async/await, fetch API, ES6 modules
- **No Framework**: Vanilla JavaScript for minimal dependencies

### HTML5
- **Web Interface**: Single-page application in `static/index.html`
- **Responsive Design**: Mobile-friendly interface
- **Modern Standards**: Semantic HTML with accessibility considerations

## Core Dependencies

### Web Framework
```
fastapi>=0.104.1        # Modern async web framework
uvicorn[standard]>=0.24.0  # ASGI server with performance optimizations
```

### AI & ML Libraries
```
foundry-ml              # Local AI model integration
faiss-cpu>=1.7.4       # Vector similarity search for RAG
sentence-transformers   # Text embedding generation
numpy>=1.24.0          # Numerical computing
```

### Data & Validation
```
pydantic>=2.5.0        # Data validation and settings management
pydantic-settings      # Environment-based configuration
```

### Utilities
```
python-dotenv>=1.0.0   # Environment variable management
aiofiles>=23.2.1       # Async file operations
httpx>=0.25.0          # Async HTTP client
```

### Development & Testing
```
pytest>=7.4.0          # Testing framework
pytest-asyncio         # Async test support
black                  # Code formatting
flake8                 # Linting
```

## Build System & Package Management

### Requirements Management
- **requirements.txt**: Production dependencies
- **Pip**: Standard Python package manager
- **Virtual Environment**: Recommended for isolation

### Installation Scripts
- **install.py**: Cross-platform Python installer
- **install.bat**: Windows batch installer
- **install.sh**: Unix/Linux shell installer
- **install.ps1**: PowerShell installer

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py

# Run with auto-reload
python run.py --reload

# Run tests
python -m pytest tests/ -v

# Format code
black src/

# Lint code
flake8 src/ --max-line-length=120
```

### Production Commands
```bash
# Production server
python run.py --host 0.0.0.0 --port 8000

# Docker build
docker build -t fastapi-foundry .

# Docker compose
docker-compose up -d

# Health check
curl http://localhost:8000/api/v1/health
```

### RAG System Commands
```bash
# Build RAG index
python rag_indexer.py

# Rebuild index
python rag_indexer.py --rebuild

# Test RAG search
python rag_indexer.py --test "query text"
```

## Configuration Management

### Environment Variables
```bash
# Core Settings
FOUNDRY_HOST=localhost
FOUNDRY_PORT=8008
API_KEY=your-api-key-here

# RAG Configuration
RAG_ENABLED=true
RAG_INDEX_PATH=./rag_index
RAG_CHUNK_SIZE=1000

# Server Settings
HOST=0.0.0.0
PORT=8000
WORKERS=1
```

### Configuration Files
- **.env**: Local environment variables
- **.env.example**: Template for environment setup
- **models_config.json**: AI model configurations
- **config.json**: MCP server settings

## Deployment Technologies

### Containerization
```dockerfile
# Multi-stage Docker build
FROM python:3.11-slim
# Optimized for production deployment
```

### Process Management
```yaml
# Docker Compose services
version: '3.8'
services:
  fastapi-foundry:
    build: .
    ports:
      - "8000:8000"
```

### Reverse Proxy Support
- **Nginx**: Production reverse proxy configuration
- **Traefik**: Container-native load balancing
- **Apache**: Traditional web server integration

## Development Tools

### Code Quality
- **Black**: Automatic code formatting (line length: 88)
- **Flake8**: PEP 8 compliance checking
- **MyPy**: Static type checking (optional)
- **Pre-commit**: Git hooks for code quality

### Testing Framework
- **Pytest**: Unit and integration testing
- **Pytest-asyncio**: Async test support
- **Coverage**: Test coverage reporting
- **Factory Boy**: Test data generation

### IDE Support
- **VS Code**: Recommended with Python extension
- **PyCharm**: Full IDE support
- **Type Hints**: Complete type annotation for IntelliSense

## Performance Considerations

### Async Architecture
- **FastAPI**: Native async/await support
- **Uvicorn**: High-performance ASGI server
- **Async I/O**: Non-blocking file and network operations

### Caching Strategies
- **In-Memory**: Model and configuration caching
- **Redis**: Optional external caching (not included by default)
- **File System**: RAG index caching

### Monitoring & Logging
- **Structured Logging**: JSON-formatted logs
- **Health Endpoints**: Service monitoring
- **Metrics**: Request timing and error rates

## Security Features

### Authentication
- **API Keys**: Simple token-based authentication
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic model validation

### Production Security
- **HTTPS**: TLS/SSL support through reverse proxy
- **Rate Limiting**: Optional request throttling
- **Input Sanitization**: Automatic through FastAPI/Pydantic

## Version Requirements

### Minimum Versions
- **Python**: 3.8+
- **FastAPI**: 0.104.1+
- **Uvicorn**: 0.24.0+
- **Pydantic**: 2.5.0+

### Recommended Versions
- **Python**: 3.11+ (performance improvements)
- **Docker**: 20.10+ (for containerization)
- **Git**: 2.30+ (for development workflow)