"""Database configuration and session management."""

from __future__ import annotations

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import settings

# SQLite connection configuration
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency / context helper for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables and seed base curriculum data."""
    # Ensure all models are registered with Base metadata
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Seed curriculum domains & tasks idempotently
    from app.services.curriculum import seed_curriculum

    db = SessionLocal()
    try:
        seed_curriculum(db)
    finally:
        db.close()

