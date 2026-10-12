"""Tests for settings service and configuration management."""

from __future__ import annotations

import pytest
from app.services.settings_service import (
    get_runtime_settings,
    update_runtime_settings,
    mask_key,
)
from app.main import app
from starlette.testclient import TestClient

client = TestClient(app)
client.post("/login", data={"email": "student@bcba.prep", "password": "bcba2026password"})


def test_mask_key_formatting():
    """mask_key correctly obscures sensitive API key material."""
    assert mask_key("") == "Not configured"
    assert mask_key("12345") == "••••••••"
    masked = mask_key("AIzaSyB9tKis9HgTpjmyKh5Knj8DqRrm8eS_Pto")
    assert masked.startswith("AIzaSy")
    assert masked.endswith("_Pto")
    assert "..." in masked


def test_update_and_get_runtime_settings():
    """Updating runtime settings updates and persists values."""
    from pathlib import Path
    settings_file = Path(__file__).resolve().parent.parent / "data" / "runtime_settings.json"
    try:
        updated = update_runtime_settings(
            llm_provider="gemini",
            llm_model="gemini-2.5-flash",
            gemini_api_key="test-key-12345678",
        )
        assert updated["llm_provider"] == "gemini"
        assert updated["llm_model"] == "gemini-2.5-flash"
        assert updated["gemini_api_key"] == "test-key-12345678"

        # Verify retrieval
        read_back = get_runtime_settings()
        assert read_back["gemini_api_key"] == "test-key-12345678"
    finally:
        if settings_file.exists():
            settings_file.unlink()


def test_settings_route_renders():
    """GET /settings returns HTTP 200 with AI Keys & Provider Configuration form."""
    response = client.get("/settings")
    assert response.status_code == 200
    assert "Settings / AI" in response.text
    assert "AI Keys &amp; Provider Configuration" in response.text or "AI Keys" in response.text
    assert "Google Gemini API Key" in response.text


def test_settings_save_post():
    """POST /settings/save saves keys and returns success notice."""
    from pathlib import Path
    settings_file = Path(__file__).resolve().parent.parent / "data" / "runtime_settings.json"
    try:
        response = client.post(
            "/settings/save",
            data={
                "llm_provider": "gemini",
                "llm_model": "gemini-2.5-flash",
                "gemini_api_key": "AIzaSyNewTestKey123456",
                "groq_api_key": "",
                "openrouter_api_key": "",
            },
        )
        assert response.status_code == 200
        assert "updated successfully" in response.text
    finally:
        # Clean up so test dummy key does not pollute runtime
        if settings_file.exists():
            settings_file.unlink()
