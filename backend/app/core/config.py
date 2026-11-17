import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AbleConnect"
    PROJECT_TAGLINE: str = "Better Understanding. Easier Communication. Inclusive Education."
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    
    # Database configuration
    # Defaults to local SQLite for instant zero-dependency setup, easily overridden with PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ableconnect.db")
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "ableconnect-dev-super-secure-key-2026-inclusive-education")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # External AI configuration (optional)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
