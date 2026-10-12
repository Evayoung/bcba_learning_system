"""Dashboard routes."""

from __future__ import annotations

from typing import Any
from app.presentation.shell import page_frame
from app.presentation.pages.dashboard import dashboard_page


def register_dashboard_routes(app: Any) -> None:
    @app.get("/")
    def dashboard():
        return page_frame(*dashboard_page(), current="/", title="Dashboard")
