"""Entrypoint for the BCBA AI Learning Assistant."""

from __future__ import annotations

from fasthtml.common import serve

from app.config import settings
from app.main import app

__all__ = ["app"]


if __name__ == "__main__":
    serve(port=settings.port)
