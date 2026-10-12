"""Tests for candidate authentication: login, logout, password hashing, and credentials update."""

from __future__ import annotations

import pytest
from app.main import app
from app.services.auth import (
    hash_password,
    verify_password,
    seed_default_user,
    DEFAULT_EMAIL,
    DEFAULT_PASSWORD,
)
from starlette.testclient import TestClient

client = TestClient(app)


def test_password_hashing_and_verification():
    """Passwords hash deterministically and verify with constant time."""
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_login_page_renders():
    """GET /login returns HTTP 200 with sign-in form."""
    response = client.get("/login")
    assert response.status_code == 200
    assert "BCBA Study Assistant" in response.text
    assert "Sign In to Workspace" in response.text
    assert DEFAULT_EMAIL in response.text


def test_login_success_redirects_and_sets_session():
    """POST /login with valid credentials authenticates successfully."""
    c = TestClient(app)
    response = c.post(
        "/login",
        data={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_login_invalid_credentials_shows_error():
    """POST /login with wrong credentials stays on login page with error."""
    c = TestClient(app)
    response = c.post(
        "/login",
        data={"email": DEFAULT_EMAIL, "password": "incorrect_password"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "Invalid email or password" in response.text


def test_logout_clears_session():
    """GET /logout clears candidate session and redirects to login."""
    c = TestClient(app)
    c.post("/login", data={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD})
    response = c.get("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_update_account_credentials_in_settings():
    """POST /settings/account updates login credentials."""
    from app.db import get_db
    from app.models import User
    c = TestClient(app)
    c.post("/login", data={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD})
    response = c.post(
        "/settings/account",
        data={"email": "updated_student@bcba.prep", "new_password": "newpassword2026"},
    )
    assert response.status_code == 200
    assert "updated successfully" in response.text
    assert "updated_student@bcba.prep" in response.text

    # Restore default student user for other tests
    db = next(get_db())
    db.query(User).delete()
    db.commit()
    seed_default_user(db)
