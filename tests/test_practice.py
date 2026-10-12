"""Unit and integration tests for Practice service: seeding, submission, scoring, and spaced repetition."""

from __future__ import annotations

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Domain, Task, Question, Attempt, ReviewItem
from app.services.curriculum import seed_curriculum
from app.services.practice import (
    seed_verified_questions,
    get_practice_question,
    record_attempt,
    get_practice_statistics,
)
from app.schemas.question import QuestionSchema, AttemptSubmissionSchema


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def mem_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    seed_curriculum(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# ─── Schema validation ────────────────────────────────────────────────────────


def test_question_schema_validates_correct_structure():
    """QuestionSchema accepts a valid 4-option question."""
    q = QuestionSchema(
        stem="What is positive reinforcement?",
        options=[
            {"id": "A", "text": "Removal of an aversive stimulus."},
            {"id": "B", "text": "Presentation of a stimulus that increases future frequency."},
            {"id": "C", "text": "Decrease in future probability of behavior."},
            {"id": "D", "text": "Neither increases nor decreases behavior."},
        ],
        correct_option="B",
        rationale="Positive reinforcement involves stimulus presentation following behavior that increases its future frequency.",
        task_code="B.4",
        domain_code="B",
    )
    assert q.correct_option == "B"
    assert len(q.options) == 4


def test_question_schema_rejects_wrong_correct_option():
    """Schema must reject a correct_option not present in options."""
    with pytest.raises(Exception):
        QuestionSchema(
            stem="A question?",
            options=[
                {"id": "A", "text": "Option A"},
                {"id": "B", "text": "Option B"},
                {"id": "C", "text": "Option C"},
                {"id": "D", "text": "Option D"},
            ],
            correct_option="E",  # not in options
            rationale="Some rationale.",
        )


def test_question_schema_rejects_duplicate_option_ids():
    """Schema must reject options with duplicate IDs."""
    with pytest.raises(Exception):
        QuestionSchema(
            stem="A question?",
            options=[
                {"id": "A", "text": "Option A"},
                {"id": "A", "text": "Duplicate A"},  # duplicate
                {"id": "C", "text": "Option C"},
                {"id": "D", "text": "Option D"},
            ],
            correct_option="A",
            rationale="Some rationale.",
        )


def test_question_schema_rejects_short_stem():
    """Schema must reject stems that are too short."""
    with pytest.raises(Exception):
        QuestionSchema(
            stem="Short?",  # too short
            options=[
                {"id": "A", "text": "Option A"},
                {"id": "B", "text": "Option B"},
                {"id": "C", "text": "Option C"},
                {"id": "D", "text": "Option D"},
            ],
            correct_option="A",
            rationale="Some rationale.",
        )


# ─── Seeding ──────────────────────────────────────────────────────────────────


def test_seed_verified_questions_is_idempotent(mem_db):
    """Seeding questions twice should not create duplicates."""
    res1 = seed_verified_questions(mem_db)
    res2 = seed_verified_questions(mem_db)
    assert res1["questions_seeded"] > 0
    assert res2["questions_seeded"] == 0  # idempotent
    assert res1["total_questions"] == res2["total_questions"]


def test_seed_creates_all_verified_questions(mem_db):
    """All VERIFIED_MANUAL_QUESTIONS must seed successfully."""
    result = seed_verified_questions(mem_db)
    assert result["questions_seeded"] >= 13
    assert result["total_questions"] >= 13

    qs = mem_db.query(Question).all()
    for q in qs:
        opts = json.loads(q.options)
        assert len(opts) == 4
        ids = {o["id"] for o in opts}
        assert q.correct_option in ids
        assert q.verification_status == "verified"


# ─── Retrieval ────────────────────────────────────────────────────────────────


def test_get_practice_question_returns_verified_item(mem_db):
    """get_practice_question should only return verified questions."""
    seed_verified_questions(mem_db)
    q = get_practice_question(mem_db)
    assert q is not None
    assert q.verification_status == "verified"


def test_get_practice_question_domain_filter(mem_db):
    """Domain filter should restrict returned question to that domain."""
    seed_verified_questions(mem_db)
    q = get_practice_question(mem_db, domain_code="B")
    assert q is not None
    assert q.task is not None
    assert q.task.domain.code == "B"


# ─── Submission ───────────────────────────────────────────────────────────────


def test_correct_attempt_scoring(mem_db):
    """A correct answer must be scored True deterministically."""
    seed_verified_questions(mem_db)
    q = mem_db.query(Question).first()
    submission = AttemptSubmissionSchema(
        question_id=q.id,
        selected_option=q.correct_option,
        confidence="high",
    )
    attempt, _, is_correct = record_attempt(mem_db, submission)
    assert is_correct is True
    assert attempt.is_correct is True
    assert attempt.selected_option == q.correct_option


def test_incorrect_attempt_scoring(mem_db):
    """An incorrect answer must be scored False deterministically."""
    seed_verified_questions(mem_db)
    q = mem_db.query(Question).first()
    # Pick a wrong option
    opts = json.loads(q.options)
    wrong_opt = next(o["id"] for o in opts if o["id"] != q.correct_option)

    submission = AttemptSubmissionSchema(
        question_id=q.id,
        selected_option=wrong_opt,
        confidence="low",
    )
    attempt, _, is_correct = record_attempt(mem_db, submission)
    assert is_correct is False
    assert attempt.is_correct is False


def test_attempt_saved_exactly_once(mem_db):
    """Submitting once must create exactly one Attempt record."""
    seed_verified_questions(mem_db)
    q = mem_db.query(Question).first()
    submission = AttemptSubmissionSchema(
        question_id=q.id,
        selected_option=q.correct_option,
    )
    record_attempt(mem_db, submission)
    total_attempts = mem_db.query(Attempt).count()
    assert total_attempts == 1


def test_spaced_repetition_correct_extends_interval(mem_db):
    """Correct answers should increase the review interval for the task."""
    seed_verified_questions(mem_db)
    q = mem_db.query(Question).filter(Question.task_id.isnot(None)).first()

    submission = AttemptSubmissionSchema(
        question_id=q.id,
        selected_option=q.correct_option,
        confidence="high",
    )
    record_attempt(mem_db, submission)
    review_item = mem_db.query(ReviewItem).filter(ReviewItem.task_id == q.task_id).first()
    assert review_item is not None
    assert review_item.interval_days >= 3
    assert review_item.consecutive_correct >= 1


def test_spaced_repetition_incorrect_resets_interval(mem_db):
    """Incorrect answers should reset interval to 1 day."""
    seed_verified_questions(mem_db)
    q = mem_db.query(Question).filter(Question.task_id.isnot(None)).first()

    opts = json.loads(q.options)
    wrong_opt = next(o["id"] for o in opts if o["id"] != q.correct_option)

    submission = AttemptSubmissionSchema(
        question_id=q.id,
        selected_option=wrong_opt,
        confidence="low",
    )
    record_attempt(mem_db, submission)
    review_item = mem_db.query(ReviewItem).filter(ReviewItem.task_id == q.task_id).first()
    assert review_item is not None
    assert review_item.interval_days == 1
    assert review_item.consecutive_correct == 0


# ─── Progress statistics ──────────────────────────────────────────────────────


def test_progress_statistics_reflect_attempts(mem_db):
    """get_practice_statistics must accurately count correct vs total attempts."""
    seed_verified_questions(mem_db)
    qs = mem_db.query(Question).limit(3).all()

    # Submit 2 correct + 1 incorrect
    record_attempt(mem_db, AttemptSubmissionSchema(question_id=qs[0].id, selected_option=qs[0].correct_option))
    record_attempt(mem_db, AttemptSubmissionSchema(question_id=qs[1].id, selected_option=qs[1].correct_option))
    opts = json.loads(qs[2].options)
    wrong = next(o["id"] for o in opts if o["id"] != qs[2].correct_option)
    record_attempt(mem_db, AttemptSubmissionSchema(question_id=qs[2].id, selected_option=wrong))

    stats = get_practice_statistics(mem_db)
    assert stats["total_attempts"] == 3
    assert stats["correct_attempts"] == 2
    assert stats["overall_accuracy"] == pytest.approx(66.7, abs=0.5)
