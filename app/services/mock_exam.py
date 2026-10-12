"""Mock exam service: session creation, per-question navigation, timed submission, and results scoring."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session

from app.models import Domain, Task, Question, Attempt, StudySession


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


EXAM_CONFIG = {
    "mini":   {"label": "Quick Check",       "count": 13,  "minutes": 30},
    "domain": {"label": "Domain Sprint",     "count": 13,  "minutes": 45},
    "full":   {"label": "Full Practice Exam","count": 13,  "minutes": 60},
}


def create_mock_session(
    db: Session,
    exam_mode: str = "mini",
    domain_filter: str = "all",
) -> Dict[str, Any]:
    """
    Create a new mock exam study session and select eligible verified questions.
    Returns session_id and ordered question IDs.
    """
    cfg = EXAM_CONFIG.get(exam_mode, EXAM_CONFIG["mini"])

    # Select eligible verified questions
    q_query = db.query(Question).filter(Question.verification_status == "verified")

    if domain_filter == "foundation":
        domain_codes = ["A", "B", "C", "D"]
        domains = db.query(Domain).filter(Domain.code.in_(domain_codes)).all()
        task_ids = [t.id for d in domains for t in d.tasks]
        q_query = q_query.filter(Question.task_id.in_(task_ids))
    elif domain_filter == "applications":
        domain_codes = ["E", "F", "G", "H", "I"]
        domains = db.query(Domain).filter(Domain.code.in_(domain_codes)).all()
        task_ids = [t.id for d in domains for t in d.tasks]
        q_query = q_query.filter(Question.task_id.in_(task_ids))

    all_questions = q_query.all()
    count = min(cfg["count"], len(all_questions))

    if count == 0:
        return {"error": "No verified questions available for this configuration."}

    selected = random.sample(all_questions, count)
    question_ids = [q.id for q in selected]

    # Create StudySession record
    session = StudySession(
        mode="mock",
        started_at=_utc_now(),
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "question_ids": question_ids,
        "exam_mode": exam_mode,
        "label": cfg["label"],
        "count": count,
        "minutes": cfg["minutes"],
        "domain_filter": domain_filter,
    }


def get_mock_question(db: Session, question_id: int) -> Optional[Question]:
    return db.query(Question).filter(
        Question.id == question_id,
        Question.verification_status == "verified",
    ).first()


def submit_mock_answer(
    db: Session,
    session_id: int,
    question_id: int,
    selected_option: str,
) -> Dict[str, Any]:
    """
    Record a mock exam attempt. Returns is_correct and the question object.
    Server-side validates selected_option and correctness — never trusts client.
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError(f"Question {question_id} not found.")

    selected = selected_option.strip().upper()
    if selected not in ("A", "B", "C", "D"):
        raise ValueError(f"Invalid option '{selected_option}'.")

    is_correct = (selected == question.correct_option.strip().upper())

    # Check for duplicate submission in this session
    existing = (
        db.query(Attempt)
        .filter(Attempt.session_id == session_id, Attempt.question_id == question_id)
        .first()
    )
    if existing:
        return {
            "already_answered": True,
            "is_correct": existing.is_correct,
            "correct_option": question.correct_option,
        }

    attempt = Attempt(
        question_id=question_id,
        session_id=session_id,
        selected_option=selected,
        is_correct=is_correct,
        answered_at=_utc_now(),
    )
    db.add(attempt)
    db.commit()

    return {
        "already_answered": False,
        "is_correct": is_correct,
        "correct_option": question.correct_option,
    }


def score_mock_session(db: Session, session_id: int) -> Dict[str, Any]:
    """
    Score a completed mock session. Returns overall and per-domain breakdown.
    All scoring is deterministic and based solely on server-stored attempt records.
    """
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not session:
        return {"error": "Session not found."}

    # Mark session complete
    if session.status == "active":
        session.status = "completed"
        session.ended_at = _utc_now()
        db.commit()

    attempts = db.query(Attempt).filter(Attempt.session_id == session_id).all()
    total = len(attempts)
    correct = sum(1 for a in attempts if a.is_correct)
    score_pct = round((correct / total) * 100, 1) if total > 0 else 0.0

    # Domain breakdown
    domain_results: Dict[str, Dict] = {}
    for attempt in attempts:
        q = db.query(Question).filter(Question.id == attempt.question_id).first()
        if not q or not q.task or not q.task.domain:
            continue
        d = q.task.domain
        key = d.code
        if key not in domain_results:
            domain_results[key] = {
                "code": d.code,
                "title": d.title,
                "weight": d.exam_weight,
                "total": 0,
                "correct": 0,
            }
        domain_results[key]["total"] += 1
        if attempt.is_correct:
            domain_results[key]["correct"] += 1

    for v in domain_results.values():
        v["accuracy"] = round((v["correct"] / v["total"]) * 100, 1) if v["total"] > 0 else 0.0

    duration_seconds = None
    if session.ended_at and session.started_at:
        duration_seconds = int((session.ended_at - session.started_at).total_seconds())

    return {
        "session_id": session_id,
        "total": total,
        "correct": correct,
        "score_pct": score_pct,
        "passed": score_pct >= 70.0,
        "duration_seconds": duration_seconds,
        "domains": sorted(domain_results.values(), key=lambda x: x["code"]),
        "attempts": [
            {
                "question_id": a.question_id,
                "selected": a.selected_option,
                "is_correct": a.is_correct,
            }
            for a in attempts
        ],
    }
