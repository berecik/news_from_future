from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional, List
import os


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "News From Future"
    
    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # NewsAPI settings
    NEWSAPI_API_KEY: str
    NEWSAPI_BASE_URL: str = "https://newsapi.org/v2"
    NEWS_FETCH_INTERVAL_MINUTES: int = 30
    NEWS_SOURCES: str = "bbc-news,cnn,reuters,associated-press,the-washington-post"
    NEWS_CATEGORIES: str = "business,technology,science,health,politics"
    NEWS_HISTORY_DAYS: int = 1
    
    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"  # Default model for Nvidia 3090 with 24GB VRAM
    
    # Storage settings
    NEWS_STORAGE_FILE: str = "data/news_cache.json"
    
    @validator("NEWSAPI_API_KEY", pre=True)
    def validate_newsapi_key(cls, v: Optional[str]) -> str:
        if not v:
            raise ValueError("NEWSAPI_API_KEY is required")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
