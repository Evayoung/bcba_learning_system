"""Authentication service: password hashing, verification, user lookup, and seeder."""

from __future__ import annotations

import hashlib
import hmac
import os
import base64
from typing import Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models import User

PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 600_000
PASSWORD_SALT_BYTES = 16
LEGACY_SALT = b"bcba_prep_secure_salt_v1"
LEGACY_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """Hash with a unique random salt and a self-describing PBKDF2 format."""
    salt = os.urandom(PASSWORD_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    return f"{PASSWORD_ALGORITHM}${PASSWORD_ITERATIONS}${encoded_salt}${derived.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify current hashes and the former fixed-salt digest during migration."""
    parts = hashed.split("$")
    if len(parts) == 4 and parts[0] == PASSWORD_ALGORITHM:
        try:
            iterations = int(parts[1])
            if iterations < 100_000 or iterations > 2_000_000:
                return False
            padding = "=" * (-len(parts[2]) % 4)
            salt = base64.urlsafe_b64decode(parts[2] + padding)
            expected = bytes.fromhex(parts[3])
            if len(salt) != PASSWORD_SALT_BYTES or len(expected) != 32:
                return False
        except (ValueError, TypeError):
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)

    # Old accounts are upgraded to a random per-user salt after successful login.
    legacy = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), LEGACY_SALT, LEGACY_ITERATIONS)
    try:
        expected = bytes.fromhex(hashed)
    except ValueError:
        return False
    return hmac.compare_digest(legacy, expected)


def create_user(db: Session, email: str, password: str, name: Optional[str] = None) -> User:
    """Create a candidate account after validating its operator-supplied credentials."""
    normalized_email = email.strip().lower()
    if len(normalized_email) > 255 or normalized_email.count("@") != 1 or "." not in normalized_email.rsplit("@", 1)[1]:
        raise ValueError("Enter a valid email address.")
    _validate_password(password)
    user = User(email=normalized_email, password_hash=hash_password(password), name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def remove_legacy_demo_account(db: Session) -> bool:
    """Remove the public seeded demo login while leaving study records intact."""
    user = db.query(User).filter(User.email == "student@bcba.prep").first()
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True


def seed_initial_user(db: Session, email: str, password: str, name: str = "BCBA Candidate") -> Optional[User]:
    """Create the first candidate account from operator-provided environment settings.

    Existing accounts are preserved. A fresh database requires credentials so
    the application never creates a predictable shared login.
    """
    existing_user = db.query(User).first()
    if existing_user is not None:
        return existing_user
    if not email.strip() or not password:
        raise RuntimeError(
            "No candidate account exists. Set CANDIDATE_EMAIL and CANDIDATE_PASSWORD "
            "in the environment before starting the application."
        )
    try:
        return create_user(db, email=email, password=password, name=name.strip() or "BCBA Candidate")
    except ValueError as error:
        raise RuntimeError(f"Could not create the initial candidate account: {error}") from error


def _validate_password(password: str) -> None:
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long.")
    if len(password) > 1024:
        raise ValueError("Password must be no longer than 1024 characters.")


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Verify credentials and return User if valid."""
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user:
        return None
    if verify_password(password, user.password_hash):
        if "$" not in user.password_hash:
            user.password_hash = hash_password(password)
            db.commit()
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
        normalized_email = new_email.strip().lower()
        if len(normalized_email) > 255 or normalized_email.count("@") != 1 or "." not in normalized_email.rsplit("@", 1)[1]:
            raise ValueError("Enter a valid email address.")
        duplicate = db.query(User.id).filter(and_(User.email == normalized_email, User.id != user_id)).first()
        if duplicate:
            raise ValueError("That email address is already in use.")
        user.email = normalized_email
    if new_password and new_password.strip():
        _validate_password(new_password.strip())
        user.password_hash = hash_password(new_password.strip())

    db.commit()
    db.refresh(user)
    return user
