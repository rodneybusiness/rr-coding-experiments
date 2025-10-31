"""
Core Configuration Module

Loads environment variables and provides application settings.
Uses Pydantic Settings for type-safe configuration with validation.
"""

from typing import List, Optional, Any
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator, PostgresDsn, model_validator
import secrets


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Film Financing Navigator"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Animation Film Financing Optimization Platform"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: PostgresDsn
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS - stored as string, parsed in model_validator
    _BACKEND_CORS_ORIGINS: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: List[str] = []

    @model_validator(mode="before")
    @classmethod
    def parse_cors_origins(cls, values: dict) -> dict:
        """Parse CORS origins from comma-separated string."""
        cors_str = values.get("_BACKEND_CORS_ORIGINS") or values.get("BACKEND_CORS_ORIGINS", "http://localhost:3000")
        if isinstance(cors_str, str):
            values["BACKEND_CORS_ORIGINS"] = [origin.strip() for origin in cors_str.split(",")]
        elif isinstance(cors_str, list):
            values["BACKEND_CORS_ORIGINS"] = cors_str
        return values

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    LOGIN_RATE_LIMIT_PER_15_MIN: int = 5

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENVIRONMENT: str = "development"

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "noreply@filmfinance.com"
    EMAILS_FROM_NAME: str = "Film Financing Navigator"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from env


# Create global settings instance
settings = Settings()
