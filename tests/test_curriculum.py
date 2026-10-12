"""Unit and integration tests for Curriculum & Database models."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import (
    Domain,
    Task,
    ContentChunk,
    Question,
    StudySession,
    Attempt,
    ReviewItem,
)
from app.services.curriculum import seed_curriculum, DOMAINS_SEED_DATA


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for test isolation."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_seed_curriculum_populates_all_9_domains(test_db):
    """Seed should insert exactly 9 domains with proper exam weights."""
    result = seed_curriculum(test_db)
    assert result["domains_seeded"] == 9

    domains = test_db.query(Domain).order_by(Domain.code).all()
    assert len(domains) == 9

    codes = [d.code for d in domains]
    assert codes == ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

    # Verify total question count equals 175
    total_questions = sum(d.question_count for d in domains)
    assert total_questions == 175

    # Verify total weights equal 100%
    total_weight = sum(d.exam_weight for d in domains)
    assert total_weight == 100


def test_seed_curriculum_populates_all_104_tasks(test_db):
    """Seed should insert all 104 verified TCO tasks under corresponding domains."""
    seed_curriculum(test_db)

    tasks = test_db.query(Task).all()
    assert len(tasks) == 104

    # Spot-check critical task descriptions
    a1 = test_db.query(Task).filter(Task.code == "A.1").first()
    assert a1 is not None
    assert "goals of behavior analysis as a science" in a1.official_description
    assert a1.domain.code == "A"

    b4 = test_db.query(Task).filter(Task.code == "B.4").first()
    assert b4 is not None
    assert "positive and negative reinforcement" in b4.official_description
    assert b4.domain.code == "B"

    i7 = test_db.query(Task).filter(Task.code == "I.7").first()
    assert i7 is not None
    assert "efficacy of supervisory practices" in i7.official_description
    assert i7.domain.code == "I"


def test_seed_curriculum_is_idempotent(test_db):
    """Running seed multiple times should not create duplicate records."""
    res1 = seed_curriculum(test_db)
    assert res1["domains_seeded"] == 9
    assert res1["tasks_seeded"] == 104

    # Run a second time
    res2 = seed_curriculum(test_db)
    assert res2["domains_seeded"] == 0
    assert res2["tasks_seeded"] == 0

    assert test_db.query(Domain).count() == 9
    assert test_db.query(Task).count() == 104


def test_content_chunk_model_relationships(test_db):
    """ContentChunk should link to Domain and Task properly."""
    seed_curriculum(test_db)
    task_b4 = test_db.query(Task).filter(Task.code == "B.4").first()

    chunk = ContentChunk(
        domain_id=task_b4.domain_id,
        task_id=task_b4.id,
        title="Positive Reinforcement Contingencies",
        body="A response-reinforcer relation where presentation increases future probability.",
        content_type="prose",
        pdf_page_index=25,
        printed_page_number=37,
        section_heading="B.4 Reinforcement",
        verification_status="unverified",
    )
    test_db.add(chunk)
    test_db.commit()

    saved = test_db.query(ContentChunk).first()
    assert saved.task.code == "B.4"
    assert saved.domain.code == "B"
    assert saved.printed_page_number == 37
    assert saved.verification_status == "unverified"


def test_question_attempt_and_review_item_relationships(test_db):
    """Question, Attempt, StudySession, and ReviewItem should associate cleanly."""
    seed_curriculum(test_db)
    task_b1 = test_db.query(Task).filter(Task.code == "B.1").first()

    session = StudySession(mode="practice", status="active")
    test_db.add(session)
    test_db.flush()

    question = Question(
        task_id=task_b1.id,
        stem="What distinguishes a response from a behavior?",
        options='["A single instance of behavior", "A collection of stimuli", "A class of antecedents", "An unconditioned reflex"]',
        correct_option="A",
        rationale="A response is a specific instance of a behavior.",
        origin_type="extracted",
        verification_status="unverified",
    )
    test_db.add(question)
    test_db.flush()

    attempt = Attempt(
        question_id=question.id,
        session_id=session.id,
        selected_option="A",
        is_correct=True,
        confidence="high",
        response_time_seconds=12.5,
    )
    test_db.add(attempt)

    review_item = ReviewItem(
        task_id=task_b1.id,
        concept_name="Response vs Behavior",
        interval_days=3,
        consecutive_correct=1,
    )
    test_db.add(review_item)
    test_db.commit()

    # Query checks
    saved_attempt = test_db.query(Attempt).first()
    assert saved_attempt.is_correct is True
    assert saved_attempt.question.stem.startswith("What distinguishes")
    assert saved_attempt.session.mode == "practice"

    saved_review = test_db.query(ReviewItem).first()
    assert saved_review.task.code == "B.1"
    assert saved_review.interval_days == 3
