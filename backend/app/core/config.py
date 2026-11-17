import os
from typing import List

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AbleConnect"
    PROJECT_TAGLINE: str = "Better Understanding. Easier Communication. Inclusive Education."
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite:///./ableconnect.db"
    JWT_SECRET_KEY: SecretStr = Field(validation_alias="JWT_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    SEED_DEMO_DATA: bool = False
    AUTO_CREATE_SCHEMA: bool = False
    CERTIFICATES_STORAGE_DIR: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "storage", "certificates")
    )
    MAX_CERTIFICATE_SIZE_BYTES: int = Field(default=10 * 1024 * 1024, ge=1024, le=20 * 1024 * 1024)

    GEMINI_API_KEY: str = ""

    @property
    def secret_key(self) -> str:
        return self.JWT_SECRET_KEY.get_secret_value()

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip().rstrip("/") for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_runtime_security(self):
        secret = self.secret_key.encode("utf-8")
        if len(secret) < 32 or len(set(secret)) < 12 or any(marker in self.secret_key.lower() for marker in ("replace-with", "example-secret", "your-secret")):
            raise ValueError("JWT_SECRET_KEY must be at least 32 bytes and contain sufficient entropy.")

        if self.ENVIRONMENT.lower() == "production":
            if len(secret) < 43:
                raise ValueError("Production JWT_SECRET_KEY must be at least 43 characters (about 256 random bits).")
            if not self.DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg://")):
                raise ValueError("Production requires PostgreSQL through DATABASE_URL.")
            if not self.cors_origins or any(origin == "*" or not origin.startswith("https://") for origin in self.cors_origins):
                raise ValueError("Production CORS_ORIGINS must list explicit HTTPS frontend origins.")
            if self.SEED_DEMO_DATA or self.AUTO_CREATE_SCHEMA:
                raise ValueError("Production cannot seed demo data or auto-create database schema.")
            if not os.getenv("CERTIFICATES_STORAGE_DIR"):
                raise ValueError("Production requires CERTIFICATES_STORAGE_DIR on private persistent storage.")
        return self

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


settings = Settings()
