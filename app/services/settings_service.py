"""Operator-managed LLM configuration and legacy-key cleanup."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

from app.config import settings

SETTINGS_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "runtime_settings.json"
_LEGACY_KEY_FIELDS = {"gemini_api_key", "groq_api_key", "openrouter_api_key"}


def purge_legacy_provider_keys() -> None:
    """Remove provider credentials previously stored in plaintext JSON."""
    if not SETTINGS_FILE.exists():
        return
    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as settings_file:
            data = json.load(settings_file)
    except (OSError, json.JSONDecodeError):
        # This file contains only runtime provider preferences; discard an
        # unreadable version rather than risk leaving an unhandled secret file.
        SETTINGS_FILE.unlink(missing_ok=True)
        return

    if not isinstance(data, dict) or not (_LEGACY_KEY_FIELDS & data.keys()):
        return
    for key_name in _LEGACY_KEY_FIELDS:
        data.pop(key_name, None)

    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=SETTINGS_FILE.parent,
            prefix="runtime_settings_", suffix=".tmp", delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            json.dump(data, temp_file, indent=2)
        try:
            os.chmod(temp_path, 0o600)
        except OSError:
            pass
        os.replace(temp_path, SETTINGS_FILE)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def get_runtime_settings() -> Dict[str, Any]:
    """Return provider settings from environment configuration only."""
    provider = settings.llm_provider.strip().lower()
    keys = {
        "gemini": settings.gemini_api_key,
        "groq": settings.groq_api_key,
        "openrouter": settings.openrouter_api_key,
    }
    return {
        "llm_provider": provider,
        "llm_model": settings.llm_model,
        "gemini_api_key": settings.gemini_api_key,
        "groq_api_key": settings.groq_api_key,
        "openrouter_api_key": settings.openrouter_api_key,
        "provider_configured": bool(keys.get(provider)),
    }


def get_public_runtime_settings() -> Dict[str, Any]:
    """Return configuration safe to show on the learner-facing settings page."""
    runtime = get_runtime_settings()
    return {
        "llm_provider": runtime["llm_provider"],
        "llm_model": runtime["llm_model"],
        "provider_configured": runtime["provider_configured"],
    }
