"""Settings routes allowing candidates to view, update, and test AI API keys and models."""

from __future__ import annotations

from typing import Any
from app.presentation.shell import page_frame
from app.presentation.pages.settings_page import render_settings_page
from app.services.settings_service import get_runtime_settings, update_runtime_settings
from app.services.llm_provider import LLMProviderAdapter


def register_settings_routes(app: Any) -> None:

    @app.get("/settings")
    def settings_view():
        runtime = get_runtime_settings()
        return page_frame(
            *render_settings_page(current_settings=runtime),
            current="/settings",
            title="Settings & AI Keys",
        )

    @app.post("/settings/save")
    def settings_save(
        llm_provider: str = "gemini",
        llm_model: str = "gemini-2.5-flash",
        gemini_api_key: str = "",
        groq_api_key: str = "",
        openrouter_api_key: str = "",
    ):
        kwargs = {
            "llm_provider": llm_provider,
            "llm_model": llm_model,
        }
        # Only overwrite keys if candidate actually entered a new one
        if gemini_api_key.strip():
            kwargs["gemini_api_key"] = gemini_api_key.strip()
        if groq_api_key.strip():
            kwargs["groq_api_key"] = groq_api_key.strip()
        if openrouter_api_key.strip():
            kwargs["openrouter_api_key"] = openrouter_api_key.strip()

        updated = update_runtime_settings(**kwargs)

        return page_frame(
            *render_settings_page(
                current_settings=updated,
                success_message="AI settings and API keys updated successfully! New keys are now active for the AI Tutor.",
            ),
            current="/settings",
            title="Settings & AI Keys",
        )

    @app.get("/settings/test")
    def settings_test():
        runtime = get_runtime_settings()
        adapter = LLMProviderAdapter()

        # Send lightweight diagnostic ping
        test_res = adapter.generate_tutoring_response(
            user_message="Respond with 'Connection successful' in 3 words.",
            mode="simplify",
            source_excerpts=None,
        )

        diagnostic = {
            "success": test_res.success,
            "provider": adapter.provider,
            "model": adapter.model,
            "message": (
                f"Connected successfully! Received response: '{test_res.content[:100]}...'"
                if test_res.success
                else f"Connection error: {test_res.error_message or 'Unknown error'}"
            ),
        }

        return page_frame(
            *render_settings_page(
                current_settings=runtime,
                test_result=diagnostic,
            ),
            current="/settings",
            title="Settings & AI Keys",
        )

    @app.post("/settings/account")
    def settings_account(session, email: str = "", new_password: str = ""):
        from app.db import get_db
        from app.services.auth import update_user_credentials
        from app.models import User

        db = next(get_db())
        user_id = session.get("user_id")
        user = None
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = db.query(User).first()

        runtime = get_runtime_settings()
        if not user:
            return page_frame(
                *render_settings_page(current_settings=runtime, error_message="No user account found to update."),
                current="/settings",
                title="Settings & AI Keys",
            )

        if not email.strip() and not new_password.strip():
            return page_frame(
                *render_settings_page(current_settings=runtime, error_message="Please enter a new email or password to update."),
                current="/settings",
                title="Settings & AI Keys",
            )

        updated_user = update_user_credentials(
            db=db,
            user_id=user.id,
            new_email=email if email.strip() else None,
            new_password=new_password if new_password.strip() else None,
        )

        session["user_email"] = updated_user.email

        return page_frame(
            *render_settings_page(
                current_settings=runtime,
                success_message=f"Account credentials updated successfully! New login email is: {updated_user.email}",
            ),
            current="/settings",
            title="Settings & AI Keys",
        )
