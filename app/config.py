"""Application configuration for BCBA AI Learning Assistant."""

from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Environment and runtime settings."""

    database_url: str = "sqlite:///./bcba_assistant.db"
    port: int = 5001
    secret_key: str = "bcba-study-assistant-secret-key-local"
    app_env: str = "development"
    use_cdn: bool = True

    # LLM Settings (Task 5)
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-flash"
    llm_timeout_seconds: int = 45
    groq_api_key: str = ""
    gemini_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
