"""Application configuration loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Required values fail fast at load time."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    github_token: str = ""
    db_path: Path = Path("./reviewer.db")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    ollama_host: str = "http://localhost:11434"
    model_default: str = "qwen2.5-coder:7b"
    model_deep: str = "qwen2.5-coder:14b"
    webhook_secret: str = ""

    @field_validator("github_token")
    @classmethod
    def require_github_token(cls, v: str) -> str:
        if not v:
            raise ValueError("GITHUB_TOKEN must be set in .env")
        return v

    @field_validator("webhook_secret")
    @classmethod
    def require_webhook_secret(cls, v: str) -> str:
        if not v:
            raise ValueError(
                "WEBHOOK_SECRET must be set in .env -- "
                "generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v


@lru_cache
def load_settings() -> Settings:
    """Load and cache settings. Call load_settings.cache_clear() in test teardown."""
    return Settings()
