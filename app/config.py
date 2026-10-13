"""Application configuration for BCBA AI Learning Assistant."""

from __future__ import annotations

import secrets
from pathlib import Path
from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Environment and runtime settings."""

    database_url: str = "sqlite:///./bcba_assistant.db"
    port: int = 5001
    secret_key: str = Field(
        default="",
        validation_alias=AliasChoices("SESSION_SECRET", "SECRET_KEY"),
    )
    app_env: str = Field(
        default_factory=lambda: "development" if (BASE_DIR / ".env").exists() else "production"
    )
    app_base_url: str = ""
    candidate_email: str = ""
    candidate_password: str = ""
    candidate_name: str = "BCBA Candidate"
    use_cdn: bool = True

    # LLM Settings (Task 5)
    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.8-flash"
    llm_timeout_seconds: int = 45
    groq_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def validate_session_configuration(self) -> "Settings":
        environment = self.app_env.strip().lower()
        self.app_env = environment
        if environment in {"prod", "production"}:
            if len(self.secret_key) < 32:
                raise ValueError("SESSION_SECRET must be set to at least 32 characters in production.")
            if not self.app_base_url.strip().lower().startswith("https://"):
                raise ValueError("APP_BASE_URL must use https:// in production.")
        elif not self.secret_key:
            self.secret_key = secrets.token_urlsafe(48)
        return self


settings = Settings()
