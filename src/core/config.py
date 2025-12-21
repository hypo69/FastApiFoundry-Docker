from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Foundry
    foundry_base_url: str = Field(default="http://localhost:50477/v1/", env="FOUNDRY_BASE_URL")
    foundry_default_model: str = Field(default="deepseek-r1-distill-qwen-7b-generic-cpu:3", env="FOUNDRY_DEFAULT_MODEL")
    foundry_temperature: float = Field(default=0.6, env="FOUNDRY_TEMPERATURE", ge=0.0, le=2.0)
    foundry_top_p: float = Field(default=0.9, env="FOUNDRY_TOP_P", ge=0.0, le=1.0)
    foundry_top_k: int = Field(default=40, env="FOUNDRY_TOP_K", ge=1)
    foundry_max_tokens: int = Field(default=2048, env="FOUNDRY_MAX_TOKENS", ge=1)
    foundry_timeout: int = Field(default=300, env="FOUNDRY_TIMEOUT", ge=1)
    
    # API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT", ge=1, le=65535)
    api_reload: bool = Field(default=False, env="API_RELOAD")
    api_workers: int = Field(default=1, env="API_WORKERS", ge=1)
    api_key: str = Field(default="", env="API_KEY")
    cors_origins: str = Field(default='["*"]', env="CORS_ORIGINS")
    
    # RAG
    rag_enabled: bool = Field(default=True, env="RAG_ENABLED")
    rag_index_dir: str = Field(default="./rag_index", env="RAG_INDEX_DIR")
    rag_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="RAG_MODEL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/fastapi-foundry.log", env="LOG_FILE")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

settings = Settings()