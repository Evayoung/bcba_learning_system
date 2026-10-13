"""Mock exam service: session creation, per-question navigation, timed submission, and results scoring."""

from __future__ import annotations

import json
import random
import base64
import binascii
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session
from app.config import settings

from app.models import Domain, Task, Question, Attempt, StudySession


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


EXAM_CONFIG = {
    "mini":   {"label": "Quick Check",       "count": 13,  "minutes": 30},
    "domain": {"label": "Domain Sprint",     "count": 13,  "minutes": 45},
    "full":   {"label": "Extended Practice Set","count": 13,  "minutes": 60},
}


def sign_mock_state(session_id: int, question_ids: List[int], minutes: int, label: str) -> str:
    """Sign the browser-carried exam state so question order cannot be altered."""
    payload = json.dumps({
        "session_id": session_id, "question_ids": question_ids,
        "minutes": minutes, "label": label,
    }, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(settings.secret_key.encode("utf-8"), payload, hashlib.sha256).digest()
    payload_part = base64.urlsafe_b64encode(payload).decode("ascii")
    signature_part = base64.urlsafe_b64encode(signature).decode("ascii")
    return f"{payload_part}.{signature_part}"


def verify_mock_state(token: str, session_id: int) -> Optional[Dict[str, Any]]:
    try:
        payload_part, signature_part = token.split(".", 1)
        payload = base64.urlsafe_b64decode(payload_part.encode("ascii"))
        supplied_signature = base64.urlsafe_b64decode(signature_part.encode("ascii"))
        expected_signature = hmac.new(settings.secret_key.encode("utf-8"), payload, hashlib.sha256).digest()
        if not hmac.compare_digest(supplied_signature, expected_signature):
            return None
        state = json.loads(payload)
        if state.get("session_id") != session_id or not isinstance(state.get("question_ids"), list):
            return None
        if not state["question_ids"] or not all(isinstance(qid, int) for qid in state["question_ids"]):
            return None
        return state
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
        return None


def create_mock_session(
    db: Session,
    exam_mode: str = "mini",
    domain_filter: str = "all",
    question_count: int = 13,
    time_limit_minutes: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Create a new mock exam study session and select eligible verified questions.
    Returns session_id and ordered question IDs.
    """
    if exam_mode not in EXAM_CONFIG:
        exam_mode = "mini"
    if domain_filter not in {"all", "foundation", "applications"}:
        domain_filter = "all"
    cfg = EXAM_CONFIG[exam_mode]

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
    try:
        question_count = int(question_count)
    except (TypeError, ValueError):
        question_count = cfg["count"]
    if question_count not in {5, 10, 13}:
        question_count = cfg["count"]
    count = min(question_count, cfg["count"], len(all_questions))

    if count == 0:
        return {"error": "No verified questions available for this configuration."}

    if time_limit_minutes not in {None, 0, 30, 45, 60}:
        time_limit_minutes = None
    minutes = cfg["minutes"] if time_limit_minutes is None else time_limit_minutes
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
        "minutes": minutes,
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
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not session or session.mode != "mock" or session.status != "active":
        raise ValueError("This practice session is no longer active.")
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.verification_status == "verified",
    ).first()
    if not question:
        raise ValueError(f"Question {question_id} not found.")

    selected = selected_option.strip().upper()
    try:
        allowed_options = {str(option["id"]).strip().upper() for option in json.loads(question.options)}
    except (TypeError, KeyError, json.JSONDecodeError):
        allowed_options = set()
    if not allowed_options or selected not in allowed_options:
        raise ValueError(f"Invalid option '{selected_option}'.")

    is_correct = (selected == question.correct_option.strip().upper())

    # Check for duplicate submission in this session
    existing = (
        db.query(Attempt)
        .filter(Attempt.session_id == session_id, Attempt.question_id == question_id)
        .first()
    )
    if existing:
        existing.selected_option = selected
        existing.is_correct = is_correct
        existing.answered_at = _utc_now()
        db.commit()
        return {
            "already_answered": True,
            "is_correct": is_correct,
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


def score_mock_session(
    db: Session, session_id: int, question_ids: Optional[List[int]] = None
) -> Dict[str, Any]:
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

    attempts_query = db.query(Attempt).filter(Attempt.session_id == session_id)
    if question_ids is not None:
        attempts_query = attempts_query.filter(Attempt.question_id.in_(question_ids))
    attempts = attempts_query.all()
    total = len(question_ids) if question_ids is not None else len(attempts)
    correct = sum(1 for a in attempts if a.is_correct)
    attempts_by_question = {attempt.question_id: attempt for attempt in attempts}

    # Domain breakdown
    domain_results: Dict[str, Dict] = {}
    task_results: Dict[str, Dict] = {}
    result_question_ids = question_ids if question_ids is not None else [a.question_id for a in attempts]
    for question_id in result_question_ids:
        q = db.query(Question).filter(Question.id == question_id).first()
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
        attempt = attempts_by_question.get(question_id)
        if attempt and attempt.is_correct:
            domain_results[key]["correct"] += 1

        task_key = q.task.code
        if task_key not in task_results:
            task_results[task_key] = {
                "code": q.task.code,
                "description": q.task.official_description,
                "domain_code": d.code,
                "total": 0,
                "correct": 0,
            }
        task_results[task_key]["total"] += 1
        if attempt and attempt.is_correct:
            task_results[task_key]["correct"] += 1

    for v in domain_results.values():
        v["accuracy"] = round((v["correct"] / v["total"]) * 100, 1) if v["total"] > 0 else 0.0
    for v in task_results.values():
        v["accuracy"] = round((v["correct"] / v["total"]) * 100, 1) if v["total"] > 0 else 0.0

    duration_seconds = None
    if session.ended_at and session.started_at:
        ended_at = session.ended_at
        started_at = session.started_at
        if ended_at.tzinfo is None:
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        duration_seconds = max(0, int((ended_at - started_at).total_seconds()))

    review = []
    review_ids = result_question_ids
    for qid in review_ids:
        question = db.query(Question).filter(Question.id == qid).first()
        if not question:
            continue
        attempt = attempts_by_question.get(qid)
        review.append({
            "question_id": qid,
            "stem": question.stem,
            "options": json.loads(question.options) if question.options else [],
            "selected": attempt.selected_option if attempt else None,
            "is_correct": bool(attempt and attempt.is_correct),
            "correct_option": question.correct_option,
            "rationale": question.rationale,
            "distractor_rationales": json.loads(question.distractor_rationales) if question.distractor_rationales else {},
            "task_code": question.task.code if question.task else None,
        })

    return {
        "session_id": session_id,
        "total": total,
        "correct": correct,
        "score_pct": round((correct / total) * 100, 1) if total else 0.0,
        "duration_seconds": duration_seconds,
        "domains": sorted(domain_results.values(), key=lambda x: x["code"]),
        "tasks": sorted(task_results.values(), key=lambda x: x["code"]),
        "attempts": [
            {
                "question_id": a.question_id,
                "selected": a.selected_option,
                "is_correct": a.is_correct,
            }
            for a in attempts
        ],
        "review": review,
    }
