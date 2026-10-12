"""Settings presentation page using FastStrap components.

Allows candidate to configure AI providers (Gemini, Groq, OpenRouter), enter/replace
API keys, select models, and test connections with real-time feedback.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from fasthtml.common import Div, H3, H4, P, Span, Form, A, Small
from faststrap import (
    Alert, Badge, BadgeGroup, Button, Card, Col, Icon, Input,
    PageHeader, Row, Select, StatCard, StatusBadge,
)
from app.services.settings_service import mask_key


def render_settings_page(
    current_settings: Dict[str, Any],
    success_message: Optional[str] = None,
    error_message: Optional[str] = None,
    test_result: Optional[Dict[str, Any]] = None,
) -> list:
    """Render the AI Key & Model Configuration page."""

    active_provider = current_settings.get("llm_provider", "gemini")
    active_model = current_settings.get("llm_model", "gemini-2.5-flash")
    gemini_key = current_settings.get("gemini_api_key", "")
    groq_key = current_settings.get("groq_api_key", "")
    openrouter_key = current_settings.get("openrouter_api_key", "")
    model_summary = active_model if len(active_model) <= 22 else f"{active_model[:19]}..."

    # Notifications
    alerts = []
    if success_message:
        alerts.append(
            Alert(
                Div(Icon("check-circle-fill", cls="me-2 text-success"), Span(success_message, cls="fw-semibold")),
                variant="success",
                cls="mb-4",
            )
        )
    if error_message:
        alerts.append(
            Alert(
                Div(Icon("exclamation-triangle-fill", cls="me-2 text-danger"), Span(error_message, cls="fw-semibold")),
                variant="danger",
                cls="mb-4",
            )
        )

    # Status overview cards
    overview_row = Row(
        Col(
            StatCard(
                "Active Provider",
                active_provider.capitalize(),
                icon=Icon("cpu-fill"),
                trend="Ready" if (gemini_key if active_provider == "gemini" else groq_key) else "No Key",
                trend_type="up" if (gemini_key if active_provider == "gemini" else groq_key) else "down",
            ),
            span=12, md=4,
        ),
        Col(
            StatCard(
                "Active Model",
                model_summary,
                icon=Icon("robot"),
                trend_type="neutral",
            ),
            span=12, md=4,
        ),
        Col(
            StatCard(
                "Gemini Status",
                "Configured" if gemini_key else "Missing",
                icon=Icon("key-fill"),
                trend_type="up" if gemini_key else "down",
            ),
            span=12, md=4,
        ),
        cls="mb-4 g-3",
    )

    # Provider & Model Settings Form
    provider_options = [
        ("gemini", "Google Gemini (Recommended for BCBA Tutor)", active_provider == "gemini"),
        ("groq", "Groq (High Speed)", active_provider == "groq"),
        ("openrouter", "OpenRouter (Multi-model aggregator)", active_provider == "openrouter"),
    ]

    model_options = [
        ("gemini-flash-latest", "gemini-flash-latest (Google Gemini - Verified Active)", active_model == "gemini-flash-latest"),
        ("gemini-2.5-flash-lite", "gemini-2.5-flash-lite (Google Gemini Lite)", active_model == "gemini-2.5-flash-lite"),
        ("gemini-2.5-pro", "gemini-2.5-pro (Google Gemini Deep Reasoning)", active_model == "gemini-2.5-pro"),
        ("qwen/qwen3.8-27b", "qwen/qwen3.8-27b (Groq - Fast & Capable 27B)", active_model == "qwen/qwen3.8-27b"),
        ("openai/gpt-oss-120b", "openai/gpt-oss-120b (Groq - 120B Flagship)", active_model == "openai/gpt-oss-120b"),
        ("nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", "nvidia/nemotron-3-nano-omni-30b-reasoning (OpenRouter Free Reasoning)", active_model == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"),
        ("nvidia/nemotron-3-super-120b-a12b:free", "nvidia/nemotron-3-super-120b (OpenRouter Free 120B)", active_model == "nvidia/nemotron-3-super-120b-a12b:free"),
    ]

    config_form = Card(
        Div(
            PageHeader(
                title="AI Keys & Provider Configuration",
                subtitle="Easily update your Google Gemini or Groq API keys if a key expires or runs out of quota.",
            ),
            Form(
                Row(
                    Col(
                        Select(
                            "llm_provider",
                            *provider_options,
                            label="Active AI Provider",
                            help_text="Select which provider the AI Tutor will query.",
                            cls="mb-3",
                        ),
                        span=12, md=6,
                    ),
                    Col(
                        Select(
                            "llm_model",
                            *model_options,
                            label="Model Name",
                            help_text="Choose the default LLM model identifier.",
                            cls="mb-3",
                        ),
                        span=12, md=6,
                    ),
                ),
                Div(
                    H4("API Keys", cls="h6 fw-bold mb-3 text-dark border-top pt-3"),
                    Row(
                        Col(
                            Input(
                                "gemini_api_key",
                                input_type="password",
                                placeholder="AIzaSy... (leave blank to keep current key)",
                                label="Google Gemini API Key",
                                help_text=f"Current key: {mask_key(gemini_key)}. Get a free key at aistudio.google.com",
                                cls="mb-3",
                            ),
                            span=12, md=6,
                        ),
                        Col(
                            Input(
                                "groq_api_key",
                                input_type="password",
                                placeholder="gsk_... (leave blank to keep current key)",
                                label="Groq API Key (Optional)",
                                help_text=f"Current key: {mask_key(groq_key)}. Get a key at console.groq.com",
                                cls="mb-3",
                            ),
                            span=12, md=6,
                        ),
                        Col(
                            Input(
                                "openrouter_api_key",
                                input_type="password",
                                placeholder="sk-or-... (optional)",
                                label="OpenRouter API Key (Optional)",
                                help_text=f"Current key: {mask_key(openrouter_key)}. Get a key at openrouter.ai",
                                cls="mb-3",
                            ),
                            span=12, md=6,
                        ),
                    ),
                    cls="mb-3",
                ),
                Div(
                    Button("Save API Settings", variant="primary", icon="check2", size="md", type="submit"),
                    A(
                        Button("Test Connection", variant="outline-primary", icon="broadcast-pin", size="md", cls="ms-2"),
                        href="/settings/test",
                        cls="text-decoration-none",
                        data_loading_text="Testing provider connection...",
                    ),
                    cls="d-flex align-items-center flex-wrap pt-2",
                ),
                method="post",
                action="/settings/save",
                data_loading_text="Saving AI settings...",
            ),
            cls="p-4",
        ),
        cls="mb-4 shadow-sm",
    )

    # Test connection card if triggered
    test_card = None
    if test_result:
        is_success = test_result.get("success", False)
        test_card = Card(
            Div(
                Div(
                    Icon("check-circle-fill" if is_success else "x-circle-fill", size="1.25rem", cls=f"{'text-success' if is_success else 'text-danger'} me-2"),
                    H4("Connection Diagnostic Results", cls=f"h6 fw-bold mb-0 {'text-success' if is_success else 'text-danger'}"),
                    cls="d-flex align-items-center mb-2",
                ),
                P(
                    test_result.get("message", ""),
                    cls="small mb-2",
                ),
                Div(
                    Badge(f"Provider: {test_result.get('provider')}", variant="primary", cls="me-1"),
                    Badge(f"Model: {test_result.get('model')}", variant="secondary", cls="me-1"),
                    StatusBadge("Connected" if is_success else "Error", status="success" if is_success else "danger", show_dot=True),
                    cls="d-flex align-items-center gap-1",
                ),
                cls="p-3",
            ),
            cls=f"mb-4 border-start border-4 {'border-success' if is_success else 'border-danger'} bg-light",
        )

    # Account credentials card
    account_card = Card(
        Div(
            PageHeader(
                title="Account Credentials",
                subtitle="Change your login email and password anytime.",
            ),
            Form(
                Row(
                    Col(
                        Input(
                            "email",
                            input_type="email",
                            label="New Email Address",
                            placeholder="Enter new email (leave blank to keep current)",
                            cls="mb-3",
                        ),
                        span=12, md=6,
                    ),
                    Col(
                        Input(
                            "new_password",
                            input_type="password",
                            label="New Password",
                            placeholder="Enter new password (leave blank to keep current)",
                            cls="mb-3",
                        ),
                        span=12, md=6,
                    ),
                ),
                Button("Update Account Credentials", variant="primary", icon="shield-lock", size="md", type="submit", data_loading_text="Updating account..."),
                method="post",
                action="/settings/account",
                data_loading_text="Updating account...",
            ),
            cls="p-4",
        ),
        cls="mb-4 shadow-sm",
    )

    items = [*alerts, overview_row]
    if test_card:
        items.append(test_card)
    items.append(config_form)
    items.append(account_card)
    return items
