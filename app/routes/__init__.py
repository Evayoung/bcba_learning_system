"""Route registry for the application."""

from __future__ import annotations

from typing import Any


def setup_routes(app: Any) -> None:
    """Register all route modules."""
    from .dashboard import register_dashboard_routes
    from .learn import register_learn_routes
    from .practice import register_practice_routes
    from .progress import register_progress_routes
    from .mock import register_mock_routes
    from .settings_route import register_settings_routes
    from .auth_route import register_auth_routes

    register_auth_routes(app)
    register_dashboard_routes(app)
    register_learn_routes(app)
    register_practice_routes(app)
    register_progress_routes(app)
    register_mock_routes(app)
    register_settings_routes(app)
