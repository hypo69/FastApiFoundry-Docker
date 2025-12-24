import json
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Load config.json for application settings
config_file = Path(__file__).parent.parent / "config.json"
if config_file.exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
else:
    config_data = {}

class Settings(BaseSettings):
    # FastAPI Server (from config.json)
    api_host: str = Field(default=config_data.get('fastapi_server', {}).get('host', '0.0.0.0'), env="API_HOST")
    api_port: int = Field(default=config_data.get('fastapi_server', {}).get('port', 8000), env="API_PORT", ge=1, le=65535)
    api_reload: bool = Field(default=config_data.get('fastapi_server', {}).get('reload', False), env="API_RELOAD")
    api_workers: int = Field(default=config_data.get('fastapi_server', {}).get('workers', 1), env="API_WORKERS", ge=1)
    api_key: str = Field(default=config_data.get('security', {}).get('api_key', ''), env="API_KEY")

    # HTTPS settings (from config.json)
    https_enabled: bool = Field(default=config_data.get('security', {}).get('https_enabled', False))
    ssl_cert_file: str = Field(default=config_data.get('security', {}).get('ssl_cert_file', '~/.ssl/cert.pem'))
    ssl_key_file: str = Field(default=config_data.get('security', {}).get('ssl_key_file', '~/.ssl/key.pem'))

    # Foundry (from config.json with env override)
    foundry_base_url: str = Field(default=config_data.get('foundry_ai', {}).get('base_url', 'http://localhost:50477/v1/'), env="FOUNDRY_BASE_URL")
    foundry_default_model: str = Field(default=config_data.get('foundry_ai', {}).get('default_model', 'deepseek-r1-distill-qwen-7b-generic-cpu:3'), env="FOUNDRY_DEFAULT_MODEL")
    foundry_temperature: float = Field(default=config_data.get('foundry_ai', {}).get('temperature', 0.6), env="FOUNDRY_TEMPERATURE", ge=0.0, le=2.0)
    foundry_top_p: float = Field(default=config_data.get('foundry_ai', {}).get('top_p', 0.9), env="FOUNDRY_TOP_P", ge=0.0, le=1.0)
    foundry_top_k: int = Field(default=config_data.get('foundry_ai', {}).get('top_k', 40), env="FOUNDRY_TOP_K", ge=1)
    foundry_max_tokens: int = Field(default=config_data.get('foundry_ai', {}).get('max_tokens', 2048), env="FOUNDRY_MAX_TOKENS", ge=1)
    foundry_timeout: int = Field(default=config_data.get('foundry_ai', {}).get('timeout', 300), env="FOUNDRY_TIMEOUT", ge=1)

    # RAG (from config.json with env override)
    rag_enabled: bool = Field(default=config_data.get('rag_system', {}).get('enabled', True), env="RAG_ENABLED")
    rag_index_dir: str = Field(default=config_data.get('rag_system', {}).get('index_dir', './rag_index'), env="RAG_INDEX_DIR")
    rag_model: str = Field(default=config_data.get('rag_system', {}).get('model', 'sentence-transformers/all-MiniLM-L6-v2'), env="RAG_MODEL")

    # Logging (from config.json with env override)
    log_level: str = Field(default=config_data.get('logging', {}).get('level', 'INFO'), env="LOG_LEVEL")
    log_file: str = Field(default=config_data.get('logging', {}).get('file', 'logs/fastapi-foundry.log'), env="LOG_FILE")

    # CORS (from config.json)
    cors_origins: str = Field(default=json.dumps(config_data.get('fastapi_server', {}).get('cors_origins', ['*'])), env="CORS_ORIGINS")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()