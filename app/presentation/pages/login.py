"""Login presentation page using FastStrap AuthLayout / Card components."""

from __future__ import annotations

from typing import Optional
from fasthtml.common import Div, H2, H4, P, Span, Form, A, Small
from faststrap import (
    Alert, Button, Card, Col, Icon, Input, Row, StatusBadge,
)


def render_login_page(
    error: Optional[str] = None,
    default_email: str = "student@bcba.prep",
    default_password: str = "bcba2026password",
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
                P("Sign in to access your guided tutor, practice items, and mock exams.", cls="text-muted small mb-4"),
                cls="text-center",
            ),
            alert if alert else None,
            # Form
            Form(
                Input(
                    "email",
                    input_type="email",
                    label="Email Address",
                    value=default_email,
                    required=True,
                    placeholder="you@domain.com",
                    cls="mb-3",
                ),
                Input(
                    "password",
                    input_type="password",
                    label="Password",
                    value=default_password,
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
            # Default credential reminder pill
            Div(
                Div(
                    Icon("info-circle", cls="text-primary me-2"),
                    Span("Default Access:", cls="fw-bold small text-dark me-1"),
                    Span(f"{default_email} • {default_password}", cls="small text-muted font-monospace"),
                    cls="d-flex align-items-center justify-content-center flex-wrap pt-3 mt-4 border-top",
                ),
                P("You can update your email & password anytime in the Settings tab.", cls="text-center text-muted small mt-1 mb-0"),
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
