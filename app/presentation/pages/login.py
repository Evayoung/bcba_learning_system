"""Login presentation page using FastStrap AuthLayout / Card components."""

from __future__ import annotations

from typing import Optional
from fasthtml.common import Div, H2, P, Span, Form
from faststrap import Alert, Button, Card, Icon, Input


def render_login_page(
    error: Optional[str] = None,
    setup_required: bool = False,
) -> list:
    """Render the clean, secure candidate sign-in page."""

    alert = None
    if error:
        alert = Alert(
            Div(
                Icon("exclamation-circle-fill", cls="text-danger me-2"),
                Span(error, cls="fw-semibold text-danger"),
                cls="d-flex align-items-center",
            ),
            variant="danger",
            cls="mb-3",
        )

    login_card = Card(
        Div(
            # Brand mark
            Div(
                Div(
                    Span("BCBA", cls="app-brand-badge fs-6 px-3 py-2"),
                    cls="mb-3",
                ),
                H2("BCBA Study Assistant", cls="h4 fw-bold text-dark mb-1"),
                P("Sign in to continue your study session.", cls="text-muted small mb-4"),
                cls="text-center",
            ),
            alert if alert else None,
            # Form
            Form(
                Input(
                    "email",
                    input_type="email",
                    label="Email Address",
                    required=True,
                    placeholder="you@domain.com",
                    cls="mb-3",
                ),
                Input(
                    "password",
                    input_type="password",
                    label="Password",
                    required=True,
                    placeholder="Enter password",
                    cls="mb-4",
                ),
                Button(
                    "Sign In to Workspace",
                    variant="primary",
                    type="submit",
                    icon="box-arrow-in-right",
                    cls="w-100 py-2 fw-semibold",
                ),
                method="post",
                action="/login",
                data_loading_text="Signing in...",
            ),
            P(
                "No account has been created yet. Contact the app owner for access."
                if setup_required
                else "For account access, contact the app owner.",
                cls="text-center text-muted small mt-3 mb-0",
            ),
            cls="p-4",
        ),
        cls="shadow-sm border bg-white mx-auto",
        style="max-width: 440px;",
    )

    return [
        Div(
            login_card,
            cls="d-flex align-items-center justify-content-center min-vh-100 p-3 bg-light",
        )
    ]
