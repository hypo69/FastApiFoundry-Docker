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
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT", ge=1, le=65535)
    api_reload: bool = Field(default=False, env="API_RELOAD")
    api_workers: int = Field(default=1, env="API_WORKERS", ge=1)
    api_key: str = Field(default="", env="API_KEY")

    # HTTPS settings
    https_enabled: bool = Field(default=False)
    ssl_cert_file: str = Field(default="~/.ssl/cert.pem")
    ssl_key_file: str = Field(default="~/.ssl/key.pem")

    # Foundry
    foundry_base_url: str = Field(default="http://localhost:50477/v1/", env="FOUNDRY_BASE_URL")
    foundry_default_model: str = Field(default="deepseek-r1-distill-qwen-7b-generic-cpu:3", env="FOUNDRY_DEFAULT_MODEL")
    foundry_temperature: float = Field(default=0.6, env="FOUNDRY_TEMPERATURE", ge=0.0, le=2.0)
    foundry_top_p: float = Field(default=0.9, env="FOUNDRY_TOP_P", ge=0.0, le=1.0)
    foundry_top_k: int = Field(default=40, env="FOUNDRY_TOP_K", ge=1)
    foundry_max_tokens: int = Field(default=2048, env="FOUNDRY_MAX_TOKENS", ge=1)
    foundry_timeout: int = Field(default=300, env="FOUNDRY_TIMEOUT", ge=1)

    # RAG
    rag_enabled: bool = Field(default=True, env="RAG_ENABLED")
    rag_index_dir: str = Field(default="./rag_index", env="RAG_INDEX_DIR")
    rag_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="RAG_MODEL")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/fastapi-foundry.log", env="LOG_FILE")

    # CORS
    cors_origins: str = Field(default='["*"]', env="CORS_ORIGINS")

    def __init__(self, **kwargs):
        # Загружаем значения из config.json если они есть
        if config_data:
            # FastAPI Server
            if 'fastapi_server' in config_data:
                fs = config_data['fastapi_server']
                kwargs.setdefault('api_host', fs.get('host', '0.0.0.0'))
                kwargs.setdefault('api_port', fs.get('port', 8000))
                kwargs.setdefault('api_reload', fs.get('reload', False))
                kwargs.setdefault('api_workers', fs.get('workers', 1))
                kwargs.setdefault('cors_origins', json.dumps(fs.get('cors_origins', ['*'])))
            
            # Security
            if 'security' in config_data:
                sec = config_data['security']
                kwargs.setdefault('api_key', sec.get('api_key', ''))
                kwargs.setdefault('https_enabled', sec.get('https_enabled', False))
                kwargs.setdefault('ssl_cert_file', sec.get('ssl_cert_file', '~/.ssl/cert.pem'))
                kwargs.setdefault('ssl_key_file', sec.get('ssl_key_file', '~/.ssl/key.pem'))
            
            # Foundry AI
            if 'foundry_ai' in config_data:
                fa = config_data['foundry_ai']
                kwargs.setdefault('foundry_base_url', fa.get('base_url', 'http://localhost:50477/v1/'))
                kwargs.setdefault('foundry_default_model', fa.get('default_model', 'deepseek-r1-distill-qwen-7b-generic-cpu:3'))
                kwargs.setdefault('foundry_temperature', fa.get('temperature', 0.6))
                kwargs.setdefault('foundry_top_p', fa.get('top_p', 0.9))
                kwargs.setdefault('foundry_top_k', fa.get('top_k', 40))
                kwargs.setdefault('foundry_max_tokens', fa.get('max_tokens', 2048))
                kwargs.setdefault('foundry_timeout', fa.get('timeout', 300))
            
            # RAG System
            if 'rag_system' in config_data:
                rag = config_data['rag_system']
                kwargs.setdefault('rag_enabled', rag.get('enabled', True))
                kwargs.setdefault('rag_index_dir', rag.get('index_dir', './rag_index'))
                kwargs.setdefault('rag_model', rag.get('model', 'sentence-transformers/all-MiniLM-L6-v2'))
            
            # Logging
            if 'logging' in config_data:
                log = config_data['logging']
                kwargs.setdefault('log_level', log.get('level', 'INFO'))
                kwargs.setdefault('log_file', log.get('file', 'logs/fastapi-foundry.log'))
        
        super().__init__(**kwargs)

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

_settings = None

def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Создаем глобальный экземпляр
settings = get_settings()