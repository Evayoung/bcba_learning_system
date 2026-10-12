"""Smoke and sanity tests for BCBA AI Learning Assistant."""

from __future__ import annotations

import sys
from pathlib import Path
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from app.db import engine, Base

client = TestClient(app)
# Authenticate client with seeded default credentials for smoke tests
client.post("/login", data={"email": "student@bcba.prep", "password": "bcba2026password"})


def test_dashboard_route_renders():
    """Dashboard should return HTTP 200 with exam details."""
    response = client.get("/")
    assert response.status_code == 200
    assert "BCBA" in response.text
    assert "Dashboard" in response.text
    assert "Concepts and Principles" in response.text


def test_learn_route_renders():
    """Learn workspace should return HTTP 200."""
    response = client.get("/learn")
    assert response.status_code == 200
    assert "Learn / Tutor" in response.text
    assert "Semantic Chunks" in response.text


def test_learn_route_with_domain_filter():
    """Learn workspace with domain filter should show domain task competencies."""
    response = client.get("/learn?domain=B")
    assert response.status_code == 200
    assert "Domain B Task Competencies" in response.text
    assert "B.4" in response.text


def test_learn_post_ask_tutor_renders():
    """POST /learn/ask should return HTTP 200 with tutor response box."""
    response = client.post("/learn/ask", data={"prompt": "Explain B.4", "mode": "explain", "task_code": "B.4"})
    assert response.status_code == 200
    assert "AI Tutor" in response.text
    assert "tutor-output" in response.text



def test_practice_route_renders():
    """Practice question route should return HTTP 200."""
    response = client.get("/practice")
    assert response.status_code == 200
    assert "Practice" in response.text
    assert "Submit Answer" in response.text


def test_progress_route_renders():
    """Progress overview should return HTTP 200."""
    response = client.get("/progress")
    assert response.status_code == 200
    assert "Progress" in response.text
    assert "Domain Performance Breakdown" in response.text


def test_mock_route_renders():
    """Mock exam route should return HTTP 200."""
    response = client.get("/mock")
    assert response.status_code == 200
    assert "Mock Exam" in response.text
    assert "Configure Practice Exam" in response.text


def test_database_connection():
    """Database schema can be created and connected to without error."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        assert conn is not None
