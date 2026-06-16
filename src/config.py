"""Application configuration loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Required values fail fast at load time."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    github_token: str
    db_path: str = "./reviewer.db"
    log_level: str = "INFO"
    ollama_host: str = "http://localhost:11434"
    model_default: str = "qwen2.5-coder:7b"
    model_deep: str = "qwen2.5-coder:14b"
    webhook_secret: str = ""


@lru_cache
def load_settings() -> Settings:
    """Load and cache settings. Raises ValidationError if required vars missing."""
    return Settings()
