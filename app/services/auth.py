"""Authentication service: password hashing, verification, user lookup, and seeder."""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User

# Standard PBKDF2-HMAC-SHA256 for secure, zero-dependency password storage
SALT = b"bcba_prep_secure_salt_v1"


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-SHA256."""
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), SALT, 100_000)
    return key.hex()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password hash with constant-time comparison."""
    return hmac.compare_digest(hash_password(password), hashed)


DEFAULT_EMAIL = "student@bcba.prep"
DEFAULT_PASSWORD = "bcba2026password"


def seed_default_user(db: Session) -> User:
    """Ensure at least one candidate user exists."""
    user = db.query(User).filter(User.email == DEFAULT_EMAIL).first()
    if not user:
        # Check if any user exists
        any_user = db.query(User).first()
        if not any_user:
            user = User(
                email=DEFAULT_EMAIL,
                password_hash=hash_password(DEFAULT_PASSWORD),
                name="BCBA Candidate",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        return any_user
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Verify credentials and return User if valid."""
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        return None
    if verify_password(password, user.password_hash):
        return user
    return None


def update_user_credentials(
    db: Session,
    user_id: int,
    new_email: Optional[str] = None,
    new_password: Optional[str] = None,
) -> User:
    """Update user email and/or password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    if new_email and new_email.strip():
        user.email = new_email.strip().lower()
    if new_password and new_password.strip():
        user.password_hash = hash_password(new_password.strip())

    db.commit()
    db.refresh(user)
    return user
