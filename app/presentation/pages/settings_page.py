"""Learner account settings with operator-managed AI configuration."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fasthtml.common import Div, H3, H4, P, Span, Form
from faststrap import Alert, Badge, Button, Card, Col, Icon, Input, PageHeader, Row


def render_settings_page(
    current_settings: Dict[str, Any],
    success_message: Optional[str] = None,
    error_message: Optional[str] = None,
) -> list:
    """Show account controls and a non-sensitive AI service status."""
    alerts = []
    if success_message:
        alerts.append(
            Alert(
                Div(Icon("check-circle-fill", cls="me-2 text-success"), Span(success_message)),
                variant="success",
                cls="mb-4",
            )
        )
    if error_message:
        alerts.append(
            Alert(
                Div(Icon("exclamation-triangle-fill", cls="me-2 text-danger"), Span(error_message)),
                variant="danger",
                cls="mb-4",
            )
        )

    provider = current_settings.get("llm_provider", "AI tutor")
    model = current_settings.get("llm_model", "")
    configured = current_settings.get("provider_configured", False)
    service_card = Card(
        Div(
            PageHeader(
                title="AI Study Service",
                subtitle="Provider credentials and model settings are managed by the app owner.",
            ),
            Row(
                Col(
                    H4("Provider", cls="h6 text-muted mb-1"),
                    P(provider.capitalize(), cls="fw-semibold mb-0"),
                    span=12,
                    md=4,
                ),
                Col(
                    H4("Model", cls="h6 text-muted mb-1"),
                    P(model or "Configured by app owner", cls="fw-semibold mb-0"),
                    span=12,
                    md=4,
                ),
                Col(
                    H4("Availability", cls="h6 text-muted mb-1"),
                    Badge("Ready" if configured else "Temporarily unavailable", variant="success" if configured else "secondary"),
                    span=12,
                    md=4,
                ),
                cls="g-3",
            ),
            P("Contact the app owner if the tutor is unavailable or you need help.", cls="small text-muted mt-3 mb-0"),
            cls="p-4",
        ),
        cls="mb-4 shadow-sm",
    )

    account_card = Card(
        Div(
            PageHeader(
                title="Account Credentials",
                subtitle="Change the email address or password used to sign in.",
            ),
            Form(
                Row(
                    Col(
                        Input(
                            "email",
                            input_type="email",
                            label="New Email Address",
                            placeholder="Leave blank to keep the current email",
                            cls="mb-3",
                        ),
                        span=12,
                        md=6,
                    ),
                    Col(
                        Input(
                            "new_password",
                            input_type="password",
                            label="New Password",
                            placeholder="At least 12 characters; leave blank to keep current",
                            minlength="12",
                            autocomplete="new-password",
                            cls="mb-3",
                        ),
                        span=12,
                        md=6,
                    ),
                ),
                Button(
                    "Update Account",
                    variant="primary",
                    icon="shield-lock",
                    type="submit",
                    data_loading_text="Updating account...",
                ),
                method="post",
                action="/settings/account",
                data_loading_text="Updating account...",
            ),
            cls="p-4",
        ),
        cls="mb-4 shadow-sm",
    )
    return [*alerts, service_card, account_card]
