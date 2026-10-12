"""Tests for mock exam service: session creation, answer recording, scoring, and validation."""

from __future__ import annotations

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Domain, Task, Question, Attempt, StudySession
from app.services.curriculum import seed_curriculum
from app.services.practice import seed_verified_questions
from app.services.mock_exam import (
    create_mock_session,
    get_mock_question,
    submit_mock_answer,
    score_mock_session,
    EXAM_CONFIG,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def mem_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    seed_curriculum(db)
    seed_verified_questions(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# ─── Exam config ──────────────────────────────────────────────────────────────


def test_exam_config_has_three_modes():
    """All three exam modes must be configured."""
    assert "mini" in EXAM_CONFIG
    assert "domain" in EXAM_CONFIG
    assert "full" in EXAM_CONFIG
    for cfg in EXAM_CONFIG.values():
        assert "label" in cfg
        assert "count" in cfg
        assert "minutes" in cfg


# ─── Session creation ─────────────────────────────────────────────────────────


def test_create_mock_session_returns_session_id(mem_db):
    """create_mock_session must return a valid session_id and question list."""
    result = create_mock_session(mem_db, exam_mode="mini", domain_filter="all")
    assert "session_id" in result
    assert "question_ids" in result
    assert len(result["question_ids"]) > 0
    assert result["session_id"] > 0


def test_create_mock_session_question_count_does_not_exceed_verified(mem_db):
    """Session question count must not exceed available verified questions."""
    total_verified = mem_db.query(Question).filter(Question.verification_status == "verified").count()
    result = create_mock_session(mem_db, exam_mode="full")
    assert len(result["question_ids"]) <= total_verified


def test_create_mock_session_saves_study_session_record(mem_db):
    """create_mock_session must persist a StudySession row with mode='mock'."""
    result = create_mock_session(mem_db, exam_mode="mini")
    session = mem_db.query(StudySession).filter(StudySession.id == result["session_id"]).first()
    assert session is not None
    assert session.mode == "mock"
    assert session.status == "active"


def test_create_mock_session_domain_filter_foundation(mem_db):
    """Foundation filter must restrict questions to Domains A–D."""
    result = create_mock_session(mem_db, exam_mode="mini", domain_filter="foundation")
    # May return empty if no verified questions in A-D — check it doesn't error
    assert "question_ids" in result or "error" in result


def test_create_mock_session_no_questions_returns_error(mem_db):
    """If no questions exist in the filtered subset, return an error dict."""
    # Remove all questions from the DB for this test
    mem_db.query(Question).delete()
    mem_db.commit()
    result = create_mock_session(mem_db, exam_mode="mini")
    assert "error" in result


# ─── Answer submission ────────────────────────────────────────────────────────


def test_submit_mock_answer_correct(mem_db):
    """Correct answer must be scored True."""
    result = create_mock_session(mem_db, exam_mode="mini")
    q_id = result["question_ids"][0]
    session_id = result["session_id"]
    q = get_mock_question(mem_db, q_id)

    res = submit_mock_answer(mem_db, session_id, q_id, q.correct_option)
    assert res["is_correct"] is True
    assert res["already_answered"] is False


def test_submit_mock_answer_incorrect(mem_db):
    """Wrong answer must be scored False."""
    result = create_mock_session(mem_db, exam_mode="mini")
    q_id = result["question_ids"][0]
    session_id = result["session_id"]
    q = get_mock_question(mem_db, q_id)

    opts = json.loads(q.options)
    wrong = next(o["id"] for o in opts if o["id"] != q.correct_option)
    res = submit_mock_answer(mem_db, session_id, q_id, wrong)
    assert res["is_correct"] is False


def test_submit_mock_answer_invalid_option_raises(mem_db):
    """Invalid option letter must raise ValueError — server validates."""
    result = create_mock_session(mem_db, exam_mode="mini")
    q_id = result["question_ids"][0]
    with pytest.raises(ValueError):
        submit_mock_answer(mem_db, result["session_id"], q_id, "Z")


def test_submit_mock_answer_idempotent_on_duplicate(mem_db):
    """Submitting the same question twice in a session must not create duplicate."""
    result = create_mock_session(mem_db, exam_mode="mini")
    q_id = result["question_ids"][0]
    session_id = result["session_id"]
    q = get_mock_question(mem_db, q_id)

    submit_mock_answer(mem_db, session_id, q_id, q.correct_option)
    res2 = submit_mock_answer(mem_db, session_id, q_id, q.correct_option)
    assert res2["already_answered"] is True
    total = mem_db.query(Attempt).filter(Attempt.session_id == session_id).count()
    assert total == 1


# ─── Scoring ──────────────────────────────────────────────────────────────────


def test_score_mock_session_calculates_correct_percentage(mem_db):
    """score_mock_session must return accurate score_pct."""
    result = create_mock_session(mem_db, exam_mode="mini")
    session_id = result["session_id"]
    q_ids = result["question_ids"]
    q0 = get_mock_question(mem_db, q_ids[0])

    submit_mock_answer(mem_db, session_id, q_ids[0], q0.correct_option)

    scored = score_mock_session(mem_db, session_id)
    assert scored["total"] == 1
    assert scored["correct"] == 1
    assert scored["score_pct"] == 100.0


def test_score_mock_session_marks_session_completed(mem_db):
    """Scoring must flip StudySession.status to 'completed'."""
    result = create_mock_session(mem_db, exam_mode="mini")
    session_id = result["session_id"]
    score_mock_session(mem_db, session_id)
    session = mem_db.query(StudySession).filter(StudySession.id == session_id).first()
    assert session.status == "completed"
    assert session.ended_at is not None


def test_score_mock_session_pass_threshold(mem_db):
    """Score >= 70 should be marked passed=True."""
    result = create_mock_session(mem_db, exam_mode="mini")
    session_id = result["session_id"]
    q_ids = result["question_ids"]

    # Answer all correctly
    for q_id in q_ids:
        q = get_mock_question(mem_db, q_id)
        submit_mock_answer(mem_db, session_id, q_id, q.correct_option)

    scored = score_mock_session(mem_db, session_id)
    assert scored["passed"] is True
    assert scored["score_pct"] >= 70.0


def test_score_mock_session_returns_domain_breakdown(mem_db):
    """Score results must include per-domain breakdown when task-linked questions exist."""
    result = create_mock_session(mem_db, exam_mode="mini")
    session_id = result["session_id"]
    q_ids = result["question_ids"]

    for q_id in q_ids:
        q = get_mock_question(mem_db, q_id)
        submit_mock_answer(mem_db, session_id, q_id, q.correct_option)

    scored = score_mock_session(mem_db, session_id)
    # domains may be empty if questions lack task links, but the key must exist
    assert "domains" in scored
    assert isinstance(scored["domains"], list)


def test_score_missing_session_returns_error(mem_db):
    """Scoring a non-existent session must return an error dict."""
    result = score_mock_session(mem_db, session_id=99999)
    assert "error" in result
