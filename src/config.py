"""Application configuration loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Required secrets fail fast at load time."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    anthropic_api_key: str
    github_token: str
    db_path: str = "./reviewer.db"
    log_level: str = "INFO"
    model_default: str = "claude-haiku-4-5-20251001"
    model_deep: str = "claude-opus-4-8"


@lru_cache
def load_settings() -> Settings:
    """Load and cache settings. Raises ValidationError if required vars missing."""
    return Settings()
