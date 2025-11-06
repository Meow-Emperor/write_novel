from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_DEFAULT_SECRET_KEY = "your-secret-key-change-in-production-please-make-it-secure-and-random"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./ai_novel.db"

    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    CUSTOM_API_URL: str = ""
    CUSTOM_API_KEY: str = ""

    # CORS (comma-separated string in env)
    ALLOWED_ORIGINS: str = (
        "http://localhost:5173,"
        "http://localhost:3000,"
        "http://127.0.0.1:5173,"
        "http://127.0.0.1:3000,"
        "http://host.docker.internal:5173"
    )

    # App meta
    APP_NAME: str = "AI Novel Platform"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Admin
    ADMIN_DEFAULT_USERNAME: str = "admin"
    ADMIN_DEFAULT_PASSWORD: str = "admin123"
    ALLOW_USER_REGISTRATION: bool = False

    # Quota
    DAILY_REQUEST_LIMIT: int = 100

    # Caching (Redis)
    AI_CACHE_ENABLED: bool = False
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    model_config = SettingsConfigDict(
        env_file=(
            # Project root .env
            Path(__file__).resolve().parents[3] / ".env",
            # backend/.env
            Path(__file__).resolve().parents[2] / ".env",
            # backend/app/.env
            Path(__file__).resolve().parents[1] / ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Backward compatible accessor for legacy code."""
        return [o.strip() for o in (self.ALLOWED_ORIGINS or "").split(",") if o.strip()]

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        """Ensure SECRET_KEY is provided and sufficiently strong."""
        if not value:
            raise ValueError("SECRET_KEY must be set to a secure random value")
        if value == _DEFAULT_SECRET_KEY:
            raise ValueError("SECRET_KEY must not use the insecure default value")
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value


settings = Settings()
