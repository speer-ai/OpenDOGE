from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "OpenDOGE"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "opendoge"
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # USAspending API settings
    USASPENDING_API_URL: str = "https://api.usaspending.gov/api/v2"
    TREASURY_API_URL: str = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1"
    SAM_API_KEY: str = ""
    SAM_API_URL: str = "https://api.sam.gov/entity-information/v1"
    
    # New API settings
    FPDS_API_URL: str = "https://api.fpds.gov/api/v1"
    FPDS_API_KEY: str = ""
    
    FBO_API_URL: str = "https://api.sam.gov/opportunities/v1"
    FBO_API_KEY: str = ""
    
    FSRS_API_URL: str = "https://api.fsrs.gov/api/v1"
    FSRS_API_KEY: str = ""
    
    FRED_API_URL: str = "https://api.stlouisfed.org/fred/v1"
    FRED_API_KEY: str = ""
    
    SEC_EDGAR_API_URL: str = "https://data.sec.gov/api"
    SEC_USER_AGENT: str = "OpenDOGE/1.0.0"
    
    # Data collection settings
    COLLECTION_INTERVAL: int = 3600  # 1 hour in seconds
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 300  # 5 minutes in seconds

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 