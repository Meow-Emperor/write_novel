from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./ai_novel.db"

    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    CUSTOM_API_URL: str = ""
    CUSTOM_API_KEY: str = ""

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # App meta
    APP_NAME: str = "AI Novel Platform"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-please-make-it-secure-and-random"

    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parents[2] / ".env",
            Path(__file__).resolve().parents[1] / ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, value: List[str] | str) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        """Backward compatible accessor for legacy code."""
        return list(self.ALLOWED_ORIGINS)


settings = Settings()
