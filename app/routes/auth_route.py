"""Authentication routes: GET /login, POST /login, GET /logout."""

from __future__ import annotations

from typing import Any
from fasthtml.common import Redirect
from app.db import get_db
from app.presentation.pages.login import render_login_page
from app.services.auth import authenticate_user, seed_default_user, DEFAULT_EMAIL, DEFAULT_PASSWORD


def register_auth_routes(app: Any) -> None:

    @app.get("/login")
    def login_view(session):
        # If already logged in, redirect to dashboard
        if session.get("user_id"):
            return Redirect("/")

        db = next(get_db())
        seed_default_user(db)

        return render_login_page(
            default_email=DEFAULT_EMAIL,
            default_password=DEFAULT_PASSWORD,
        )

    @app.post("/login")
    def login_action(session, email: str = "", password: str = ""):
        db = next(get_db())
        seed_default_user(db)

        user = authenticate_user(db, email=email, password=password)
        if not user:
            return render_login_page(
                error="Invalid email or password. Please check your credentials.",
                default_email=email or DEFAULT_EMAIL,
                default_password="",
            )

        # Set session cookie
        session["user_id"] = user.id
        session["user_email"] = user.email

        return Redirect("/")

    @app.get("/logout")
    def logout_action(session):
        session.clear()
        return Redirect("/login")
