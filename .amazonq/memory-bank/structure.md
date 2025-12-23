# FastAPI Foundry - Project Structure

## Directory Organization

### Core Application (`src/`)
```
src/
├── api/              # FastAPI application layer
│   ├── endpoints/    # API route handlers
│   ├── middleware/   # Request/response middleware
│   ├── app.py       # Application factory
│   ├── main.py      # Entry point
│   └── models.py    # Pydantic data models
├── core/            # Configuration management
│   └── config.py    # Settings and environment variables
├── models/          # AI model integration
│   ├── foundry_client.py  # Foundry API client
│   └── model_manager.py   # Model lifecycle management
├── rag/             # Retrieval-Augmented Generation
│   └── rag_system.py      # RAG implementation with FAISS
└── utils/           # Shared utilities
```

### MCP Integration (`mcp-servers/`)
```
mcp-servers/
└── aistros-foundry/     # Model Context Protocol server
    ├── src/
    │   └── server.py    # MCP server implementation
    ├── config.json      # MCP configuration
    └── README.md        # MCP setup instructions
```

### Documentation (`docs/`)
```
docs/
├── installation.md      # Setup and requirements
├── configuration.md     # Environment configuration
├── usage.md            # API and web interface usage
├── examples.md         # Code examples and tutorials
├── development.md      # Development guidelines
├── deployment.md       # Production deployment
└── mcp_integration.md  # MCP server setup
```

### Web Interface (`static/`)
```
static/
├── index.html          # Main web interface
└── app.js             # Frontend JavaScript application
```

### Deployment & Scripts
```
Root Level:
├── run.py                    # Main application launcher
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-service deployment
├── .env.example            # Environment template
├── install.py              # Cross-platform installer
├── rag_indexer.py          # RAG index builder
└── tunnel_manager.py       # Public access tunneling
```

## Core Components & Relationships

### API Layer Architecture
- **FastAPI Application**: Modern async web framework with automatic OpenAPI docs
- **Endpoint Handlers**: Modular route organization in `endpoints/` directory
- **Pydantic Models**: Type-safe request/response validation
- **Middleware Stack**: CORS, authentication, and request logging

### AI Model Integration
- **Foundry Client**: Direct integration with local Foundry model server
- **Model Manager**: Handles model loading, switching, and lifecycle
- **Async Processing**: Non-blocking model inference for better performance
- **Error Handling**: Robust error recovery and model fallbacks

### RAG System Architecture
- **FAISS Vector Store**: High-performance similarity search
- **Document Indexing**: Automated processing of project documentation
- **Context Retrieval**: Relevant document chunks for enhanced responses
- **Embedding Generation**: Vector representations for semantic search

### MCP Server Integration
- **Protocol Compliance**: Full MCP specification implementation
- **Claude Desktop**: Direct integration with Anthropic's desktop client
- **Tool Registration**: Exposes AI capabilities as MCP tools
- **Bidirectional Communication**: Real-time model interaction

## Architectural Patterns

### Dependency Injection
- Configuration through environment variables and `.env` files
- Service layer separation for testability
- Factory pattern for application initialization

### Async/Await Pattern
- Non-blocking I/O for model inference
- Concurrent request handling
- Streaming response support

### Modular Design
- Clear separation of concerns across modules
- Plugin-style architecture for extending functionality
- Interface-based design for model abstraction

### Configuration Management
- Environment-based configuration
- Validation through Pydantic settings
- Runtime configuration updates

## Data Flow

### Request Processing
1. **HTTP Request** → FastAPI router
2. **Validation** → Pydantic models
3. **Authentication** → API key verification
4. **Model Selection** → Model manager routing
5. **RAG Enhancement** → Context retrieval (if enabled)
6. **AI Processing** → Foundry client inference
7. **Response** → JSON/streaming output

### RAG Enhancement Flow
1. **Query Analysis** → Extract search terms
2. **Vector Search** → FAISS similarity matching
3. **Context Assembly** → Relevant document chunks
4. **Prompt Enhancement** → Inject context into model prompt
5. **Enhanced Response** → Context-aware AI output

### MCP Communication
1. **MCP Client** → Protocol message
2. **Server Handler** → Route to appropriate tool
3. **AI Processing** → Model inference
4. **Response Formatting** → MCP protocol compliance
5. **Client Delivery** → Structured response

## Scalability Considerations

### Horizontal Scaling
- Stateless application design
- Docker containerization ready
- Load balancer compatible

### Performance Optimization
- Async request handling
- Model caching strategies
- RAG index optimization
- Connection pooling