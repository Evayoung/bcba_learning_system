"""FastHTML application entrypoint and configuration."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
from fasthtml.common import Beforeware, FastHTML, Link, Redirect
from faststrap import add_bootstrap, mount_assets

from app.config import settings
from app.db import init_db
from app.routes import setup_routes
from app.theme import BCBA_THEME, setup_theme_defaults

BASE_DIR = Path(__file__).resolve().parent.parent


def _require_login(req, session):
    """Protect app routes: redirect to /login if unauthenticated."""
    if session.get("user_id"):
        return None
    return Redirect("/login")


# Create FastHTML instance with route guard
app = FastHTML(secret_key=settings.secret_key)
app.before.append(
    Beforeware(
        _require_login,
        skip=[
            r"^/login",
            r"^/logout",
            r"^/assets/.*",
            r"^/favicon\.ico",
        ],
    )
)

# Configure FastStrap with brand theme
add_bootstrap(app, theme=BCBA_THEME, mode="light", use_cdn=settings.use_cdn)
setup_theme_defaults()

# Mount local assets for custom CSS and static resources
mount_assets(app, str(BASE_DIR / "assets"), url_path="/assets")

# Append headers (Fonts and custom stylesheet)
app.hdrs = app.hdrs + [
    Link(rel="preconnect", href="https://fonts.googleapis.com"),
    Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin="anonymous"),
    Link(
        rel="stylesheet",
        href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
    ),
    Link(rel="stylesheet", href="/assets/css/custom.css"),
]

# Initialize database schema and seed data
init_db()

# Idempotent startup seeding
from app.db import SessionLocal as _SessionLocal
from app.services.curriculum import seed_curriculum as _seed_curriculum
from app.services.practice import seed_verified_questions as _seed_questions
from app.services.auth import seed_default_user as _seed_user
from app.services.content_ingestion import import_content_chunks as _import_chunks
_startup_db = _SessionLocal()
try:
    _seed_curriculum(_startup_db)
    _import_chunks(_startup_db)
    _seed_questions(_startup_db)
    _seed_user(_startup_db)
finally:
    _startup_db.close()

# Register all application routes
setup_routes(app)

if __name__ == "__main__":
    from fasthtml.common import serve
    serve(port=settings.port)
