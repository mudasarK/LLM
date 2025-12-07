import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Deep Agents API"
    VERSION: str = "1.0.0"
    
    # LLM Configuration
    # Note: You only need ONE API key (OpenAI OR Anthropic)
    # Priority: OpenAI is checked first, then Anthropic
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Agent Configuration
    DEFAULT_MODEL: str = "gpt-4o"  # Used if OPENAI_API_KEY is set
    DEFAULT_ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20240620"  # Used if ANTHROPIC_API_KEY is set
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
