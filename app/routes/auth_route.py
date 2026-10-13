"""Authentication routes: GET /login, POST /login, GET /logout."""

from __future__ import annotations

from typing import Any
from fasthtml.common import Redirect
from app.db import SessionLocal
from app.models import User
from app.presentation.pages.login import render_login_page
from app.services.auth import authenticate_user


def register_auth_routes(app: Any) -> None:

    @app.get("/login")
    def login_view(session):
        # If already logged in, redirect to dashboard
        if session.get("user_id"):
            return Redirect("/")

        with SessionLocal() as db:
            setup_required = db.query(User.id).first() is None
        return render_login_page(setup_required=setup_required)

    @app.post("/login")
    def login_action(session, email: str = "", password: str = ""):
        with SessionLocal() as db:
            setup_required = db.query(User.id).first() is None
            user = authenticate_user(db, email=email, password=password)
            user_id = user.id if user else None
            user_email = user.email if user else None
        if not user:
            return render_login_page(
                error=None if setup_required else "Invalid email or password. Please check your credentials.",
                setup_required=setup_required,
            )

        # Set session cookie
        session["user_id"] = user_id
        session["user_email"] = user_email

        return Redirect("/")

    @app.get("/logout")
    def logout_action(session):
        session.clear()
        return Redirect("/login")
