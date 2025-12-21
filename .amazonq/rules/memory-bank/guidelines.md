# FastAPI Foundry - Development Guidelines

## Code Quality Standards

### File Headers and Documentation
- **Mandatory Headers**: All Python files use standardized hypo69/AiStros headers with UTF-8 encoding declaration
- **Header Structure**: Includes process name, description, examples, file metadata, project info, author, and license
- **License Standard**: CC BY-NC-SA 4.0 consistently applied across all files
- **Encoding Declaration**: `# -*- coding: utf-8 -*-` at file start

### Python Code Formatting
- **Line Length**: No strict enforcement observed, varies by context
- **Import Organization**: Grouped imports (standard library, third-party, local modules)
- **Type Hints**: Comprehensive typing with `Optional`, `List`, `Dict`, `Any` from typing module
- **Async Patterns**: Extensive use of `async`/`await` for I/O operations
- **Error Handling**: Try-catch blocks with detailed logging

### Documentation Standards
- **Docstrings**: Triple-quoted strings with detailed parameter and return descriptions
- **Russian Comments**: Mixed Russian/English documentation (Russian for descriptions, English for technical terms)
- **Inline Comments**: Technical explanations in Russian with English technical terms
- **API Documentation**: Pydantic models with Field descriptions for automatic OpenAPI docs

## Structural Conventions

### Class Design Patterns
- **Singleton Pattern**: Used in ModelManager and RAGSystem with global instances
- **Manager Classes**: Centralized management (ModelManager, RAGSystem) with comprehensive CRUD operations
- **Configuration Classes**: Pydantic BaseSettings for environment-based configuration
- **Async Initialization**: `async def initialize()` pattern for setup operations

### Data Validation Patterns
- **Pydantic Models**: Extensive use for request/response validation
- **Field Validation**: Comprehensive constraints (min_length, max_length, ge, le, pattern)
- **Optional Fields**: Proper use of `Optional` with default values
- **Nested Models**: Complex data structures with proper typing

### Error Handling Conventions
- **Structured Responses**: Consistent success/error response format with timestamps
- **Logging Integration**: Comprehensive logging with different levels (info, warning, error)
- **Exception Propagation**: Proper exception handling with user-friendly error messages
- **Timeout Handling**: Configurable timeouts for external service calls

## Semantic Patterns

### Async/Await Implementation
- **Non-blocking I/O**: All external API calls use aiohttp with async/await
- **Thread Pool Execution**: CPU-intensive operations (model loading, FAISS operations) use `loop.run_in_executor()`
- **Lock Management**: `asyncio.Lock()` for thread-safe operations
- **Concurrent Processing**: Proper async patterns for multiple simultaneous requests

### Configuration Management
- **Environment Variables**: Pydantic Settings with Field defaults and env variable mapping
- **Validation**: Built-in validation with constraints (ge, le, pattern matching)
- **Type Safety**: Strong typing for all configuration parameters
- **Default Values**: Sensible defaults for all configuration options

### API Design Patterns
- **RESTful Endpoints**: Clear resource-based URL structure
- **Request/Response Models**: Dedicated Pydantic models for each endpoint
- **Status Responses**: Consistent success/error response structure
- **Batch Operations**: Support for batch processing with individual result tracking

## Internal API Usage Patterns

### Model Management
```python
# Model connection pattern
model_config = {
    "model_id": model_id,
    "provider": provider,
    "endpoint_url": endpoint_url,
    "status": "unknown",
    "created_at": datetime.now()
}
```

### RAG System Integration
```python
# RAG search pattern
results = await rag_system.search(query, top_k=5)
context = rag_system.format_context(results)
```

### Configuration Access
```python
# Settings usage pattern
from config import settings
url = settings.foundry_base_url
model = settings.foundry_default_model
```

### HTTP Client Patterns
```python
# Async HTTP client pattern
async with aiohttp.ClientSession() as session:
    async with session.post(url, json=payload, timeout=30) as response:
        if response.status == 200:
            data = await response.json()
```

## Frequently Used Code Idioms

### Dictionary Updates with Timestamps
```python
model_config["updated_at"] = datetime.now()
model_config["last_check"] = datetime.now()
```

### Conditional Field Updates
```python
if "field_name" in update_data:
    config["field_name"] = update_data["field_name"]
```

### Response Format Standardization
```python
return {
    "success": True/False,
    "message": "Description",
    "error": error_string_or_none,
    "timestamp": datetime.now()
}
```

### Async Initialization Pattern
```python
async def initialize(self) -> bool:
    async with self._lock:
        return await self._load_resources()
```

## Popular Annotations and Patterns

### Pydantic Field Annotations
- `Field(..., description="...")` - Required fields with descriptions
- `Field(default_value, description="...")` - Optional fields with defaults
- `Field(ge=0, le=100)` - Numeric constraints
- `Field(min_length=1, max_length=1000)` - String length constraints
- `Field(pattern="^regex$")` - Pattern validation

### Type Annotations
- `Optional[str] = None` - Optional string fields
- `List[Dict[str, Any]]` - Lists of dictionaries
- `Dict[str, Any]` - Generic dictionaries
- `datetime = Field(default_factory=datetime.now)` - Auto-timestamp fields

### Async Method Signatures
- `async def method_name(self, param: Type) -> ReturnType:`
- `async with aiohttp.ClientSession() as session:`
- `await loop.run_in_executor(None, sync_function, args)`

### Error Response Patterns
```python
{
    "success": False,
    "model_id": model_id,
    "message": "User-friendly message",
    "error": "Technical error details"
}
```

## Frontend Integration Patterns

### JavaScript API Communication
- **Fetch API**: Modern async/await patterns for API calls
- **Error Handling**: Comprehensive try-catch with user feedback
- **Status Updates**: Real-time status checking with intervals
- **Progress Tracking**: Simulated progress bars for long operations

### UI State Management
- **Global State**: Simple global variables for application state
- **DOM Manipulation**: Direct DOM updates without frameworks
- **Event Handling**: Modern event listener patterns
- **Bootstrap Integration**: Consistent UI components and styling

### WebSocket-like Patterns
- **Polling**: Regular status updates using setInterval
- **Real-time Updates**: Automatic refresh of system status
- **Progress Simulation**: Client-side progress tracking for downloads

## Testing and Validation Patterns

### Model Testing
- **Connection Testing**: Standardized test prompts for model validation
- **Response Time Tracking**: Performance monitoring with averages
- **Health Checks**: Regular automated health verification
- **Provider-Specific Testing**: Different test patterns per provider type

### Configuration Validation
- **Pydantic Validation**: Automatic validation on configuration load
- **Environment Variable Mapping**: Seamless env var to config mapping
- **Type Coercion**: Automatic type conversion with validation
- **Constraint Enforcement**: Built-in validation rules