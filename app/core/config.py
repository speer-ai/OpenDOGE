from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "OpenDOGE"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://opendoge:opendoge123@localhost:5432/opendoge"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # Cache time to live in seconds (1 hour)
    
    # USAspending API settings
    USASPENDING_API_BASE_URL: str = "https://api.usaspending.gov/api/v2"
    USASPENDING_API_TIMEOUT: int = 30
    
    # API Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "opendoge"
    POSTGRES_PASSWORD: str = "opendoge123"
    POSTGRES_DB: str = "opendoge"
    POSTGRES_PORT: str = "5432"
    
    # MongoDB Settings
    MONGODB_URL: str
    MONGODB_DB: str
    
    # External API Settings
    SAM_API_KEY: str
    XAI_API_KEY: str  # XAI API key for smart search functionality
    OPENAI_API_KEY: str = ""  # Optional OpenAI API key for fallback

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 