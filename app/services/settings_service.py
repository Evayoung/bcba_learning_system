"""Runtime settings service for persistent API keys and provider configuration.

Allows the candidate to easily update, test, and switch API keys directly from
the application UI, storing them persistently in local JSON storage with fallback
to environment variables.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional

from app.config import settings

SETTINGS_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "runtime_settings.json"


def _load_settings_file() -> Dict[str, Any]:
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_settings_file(data: Dict[str, Any]) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_runtime_settings() -> Dict[str, Any]:
    """Retrieve effective settings, overlaying saved user settings on top of defaults."""
    user_data = _load_settings_file()
    return {
        "llm_provider": user_data.get("llm_provider") or settings.llm_provider or "gemini",
        "llm_model": user_data.get("llm_model") or settings.llm_model or "gemini-2.5-flash",
        "gemini_api_key": user_data.get("gemini_api_key") or settings.gemini_api_key or "",
        "groq_api_key": user_data.get("groq_api_key") or settings.groq_api_key or "",
        "openrouter_api_key": user_data.get("openrouter_api_key") or "",
    }


def update_runtime_settings(
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    groq_api_key: Optional[str] = None,
    openrouter_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Update runtime settings persistently."""
    data = _load_settings_file()

    if llm_provider is not None:
        data["llm_provider"] = llm_provider.strip().lower()
    if llm_model is not None:
        data["llm_model"] = llm_model.strip()
    if gemini_api_key is not None:
        data["gemini_api_key"] = gemini_api_key.strip()
    if groq_api_key is not None:
        data["groq_api_key"] = groq_api_key.strip()
    if openrouter_api_key is not None:
        data["openrouter_api_key"] = openrouter_api_key.strip()

    _save_settings_file(data)
    return get_runtime_settings()


def mask_key(key: str) -> str:
    """Safely mask an API key for display (e.g. AIzaSy...8eS_Pto)."""
    if not key:
        return "Not configured"
    if len(key) <= 8:
        return "••••••••"
    return f"{key[:6]}...{key[-4:]}"
