"""Learner account settings; LLM credentials remain operator-managed."""

from __future__ import annotations

from typing import Any
from fasthtml.common import Redirect
from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal
from app.models import User
from app.presentation.pages.settings_page import render_settings_page
from app.presentation.shell import page_frame
from app.services.auth import update_user_credentials
from app.services.settings_service import get_public_runtime_settings


def register_settings_routes(app: Any) -> None:
    @app.get("/settings")
    def settings_view():
        return page_frame(
            *render_settings_page(current_settings=get_public_runtime_settings()),
            current="/settings",
            title="Account Settings",
        )

    @app.post("/settings/account")
    def settings_account(session, email: str = "", new_password: str = ""):
        user_id = session.get("user_id")
        if not user_id:
            return Redirect("/login")

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                session.clear()
                return Redirect("/login")
            if not email.strip() and not new_password.strip():
                message = "Enter a new email or password to update your account."
                return page_frame(
                    *render_settings_page(
                        current_settings=get_public_runtime_settings(),
                        error_message=message,
                    ),
                    current="/settings",
                    title="Account Settings",
                )
            try:
                updated_user = update_user_credentials(
                    db=db,
                    user_id=user.id,
                    new_email=email if email.strip() else None,
                    new_password=new_password if new_password.strip() else None,
                )
                updated_email = updated_user.email
            except ValueError as error:
                return page_frame(
                    *render_settings_page(
                        current_settings=get_public_runtime_settings(),
                        error_message=str(error),
                    ),
                    current="/settings",
                    title="Account Settings",
                )
            except IntegrityError:
                db.rollback()
                return page_frame(
                    *render_settings_page(
                        current_settings=get_public_runtime_settings(),
                        error_message="That email address is already in use.",
                    ),
                    current="/settings",
                    title="Account Settings",
                )

        session["user_email"] = updated_email
        return page_frame(
            *render_settings_page(
                current_settings=get_public_runtime_settings(),
                success_message="Account credentials updated.",
            ),
            current="/settings",
            title="Account Settings",
        )
