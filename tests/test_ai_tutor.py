"""Unit and integration tests for AI Tutor provider adapter and grounded prompt generation."""

from __future__ import annotations

import pytest
from app.services.llm_provider import LLMProviderAdapter, LLMResponse, MODE_INSTRUCTIONS, TUTOR_SYSTEM_PROMPT


def test_missing_api_key_returns_graceful_error():
    """Adapter should report missing API key without raising unhandled exceptions."""
    adapter = LLMProviderAdapter(provider="gemini", api_key="", model="gemini-2.5-flash")
    response = adapter.generate_tutoring_response("What is operant conditioning?", mode="explain")

    assert not response.success
    assert "No API key configured" in response.error_message
    assert response.provider == "gemini"


def test_unsupported_provider_handled_gracefully():
    """Adapter should handle unknown provider names gracefully."""
    adapter = LLMProviderAdapter(provider="unknown_llm", api_key="secret-key", model="dummy")
    response = adapter.generate_tutoring_response("Explain extinction", mode="explain")

    assert not response.success
    assert "Unsupported provider" in response.error_message


def test_mode_instructions_exist():
    """All 5 specified tutor modes must have dedicated prompt directives."""
    expected_modes = ["explain", "simplify", "example", "compare", "socratic"]
    for m in expected_modes:
        assert m in MODE_INSTRUCTIONS
        assert len(MODE_INSTRUCTIONS[m]) > 20


def test_tutor_system_prompt_mandates_fidelity_and_disclaimers():
    """System prompt must strictly forbid citation hallucinations and mandate disclaimers."""
    assert "NEVER invent page numbers" in TUTOR_SYSTEM_PROMPT
    assert "CLEARLY DISTINGUISH content from the PTB Study Manual" in TUTOR_SYSTEM_PROMPT
    assert "Never provide real-world clinical advice" in TUTOR_SYSTEM_PROMPT
    assert "NEVER claim that any question or example is an official BACB exam item" in TUTOR_SYSTEM_PROMPT


def test_empty_retrieval_adds_notice_to_prompt():
    """When no source excerpts are provided, prompt includes notice regarding lack of evidence."""
    adapter = LLMProviderAdapter(provider="mock")
    # Test internal helper without calling network
    adapter.api_key = "test"
    # Overwrite _call_gemini / _call_groq to inspect constructed messages
    captured_messages = []
    adapter._call_groq = lambda msgs: captured_messages.extend(msgs) or LLMResponse(content="OK", success=True)
    adapter.provider = "groq"

    adapter.generate_tutoring_response(
        user_message="Explain something",
        mode="explain",
        source_excerpts=None,
    )

    sys_content = captured_messages[0]["content"]
    assert "No manual excerpts were retrieved for this query" in sys_content


def test_live_gemini_generation_with_source_excerpts():
    """Live call with actual API key produces grounded response referencing the manual excerpt."""
    adapter = LLMProviderAdapter()
    if not adapter.api_key:
        pytest.skip("No API key available for live test")

    excerpts = [
        {
            "citation": "PTB ABA Study Manual • Page 45 (Task B.4)",
            "title": "Positive Reinforcement Defined",
            "body": "Positive reinforcement occurs when a behavior is immediately followed by the presentation of a stimulus that increases future frequency.",
        }
    ]

    response = adapter.generate_tutoring_response(
        user_message="Define positive reinforcement in 2 sentences",
        mode="explain",
        source_excerpts=excerpts,
        task_code="B.4",
        task_description="Define and provide examples of positive reinforcement",
    )

    if not response.success and response.error_message:
        if "429" in response.error_message or "quota" in response.error_message.lower():
            pytest.skip(f"Gemini API quota exceeded: {response.error_message}")
        if "API_KEY_INVALID" in response.error_message or "400" in response.error_message:
            pytest.skip(f"Gemini API key expired/invalid: {response.error_message}")

    assert response.success is True
    assert len(response.content) > 30
    assert response.provider in ("gemini", "groq")
