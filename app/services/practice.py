"""Practice service managing question selection, answer verification, attempt logging, and progress stats."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_

from app.models import Domain, Task, Question, Attempt, StudySession, ReviewItem
from app.schemas.question import QuestionSchema, AttemptSubmissionSchema
from data.processed.adapted_practice_questions import ADAPTED_PRACTICE_QUESTIONS


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def seed_verified_questions(db: Session, force: bool = False) -> Dict[str, int]:
    """Seed verified practice questions into the questions table."""
    existing_count = db.query(Question).count()
    if existing_count > 0 and not force:
        _sync_question_provenance(db)
        return {"questions_seeded": 0, "total_questions": existing_count}

    if force:
        db.query(Question).delete()
        db.commit()

    tasks_by_code = {t.code: t for t in db.query(Task).all()}
    seeded_count = 0

    for q_data in ADAPTED_PRACTICE_QUESTIONS:
        # Validate schema
        validated = QuestionSchema(**q_data)
        task_obj = tasks_by_code.get(validated.task_code) if validated.task_code else None

        question = Question(
            task_id=task_obj.id if task_obj else None,
            stem=validated.stem,
            options=json.dumps([opt.model_dump() for opt in validated.options]),
            correct_option=validated.correct_option,
            rationale=validated.rationale,
            distractor_rationales=json.dumps(validated.distractor_rationales),
            difficulty=validated.difficulty,
            source=validated.source,
            origin_type=validated.origin_type,
            verification_status=validated.verification_status,
        )
        db.add(question)
        seeded_count += 1

    db.commit()
    return {"questions_seeded": seeded_count, "total_questions": db.query(Question).count()}


def _sync_question_provenance(db: Session) -> None:
    """Correct legacy labels for the existing adapted scenario questions."""
    current_by_stem = {item["stem"]: item for item in ADAPTED_PRACTICE_QUESTIONS}
    changed = False
    for question in db.query(Question).filter(Question.origin_type == "extracted").all():
        source_item = current_by_stem.get(question.stem)
        if source_item is None:
            continue
        question.origin_type = source_item["origin_type"]
        question.source = source_item["source"]
        changed = True
    if changed:
        db.commit()


def get_practice_question(
    db: Session,
    question_id: Optional[int] = None,
    domain_code: Optional[str] = None,
    task_code: Optional[str] = None,
) -> Optional[Question]:
    """Select a specific question or the next eligible verified practice item."""
    query = db.query(Question).filter(Question.verification_status == "verified")

    if question_id:
        return query.filter(Question.id == question_id).first()

    if task_code:
        task = db.query(Task).filter(Task.code == task_code).first()
        if task:
            query = query.filter(Question.task_id == task.id)
    elif domain_code and domain_code != "all":
        domain = db.query(Domain).filter(Domain.code == domain_code).first()
        if domain:
            task_ids = [t.id for t in domain.tasks]
            query = query.filter(Question.task_id.in_(task_ids))

    return query.order_by(Question.id.asc()).first()


def record_attempt(
    db: Session,
    submission: AttemptSubmissionSchema,
    session_id: Optional[int] = None,
) -> Tuple[Attempt, Question, bool]:
    """Record a practice attempt and calculate correctness deterministically."""
    question = db.query(Question).filter(Question.id == submission.question_id).first()
    if not question:
        raise ValueError(f"Question with ID {submission.question_id} does not exist.")

    is_correct = (submission.selected_option.strip().upper() == question.correct_option.strip().upper())

    now = _utc_now()
    attempt = Attempt(
        question_id=question.id,
        session_id=session_id,
        selected_option=submission.selected_option.strip().upper(),
        is_correct=is_correct,
        confidence=submission.confidence,
        response_time_seconds=submission.response_time_seconds,
        answered_at=now,
    )
    db.add(attempt)

    # Update or insert Spaced Repetition ReviewItem for this task
    if question.task_id:
        review_item = db.query(ReviewItem).filter(ReviewItem.task_id == question.task_id).first()
        if not review_item:
            interval_days = _review_interval_days(is_correct, submission.confidence)
            review_item = ReviewItem(
                task_id=question.task_id,
                concept_name=question.task.official_description if question.task else None,
                interval_days=interval_days,
                consecutive_correct=1 if is_correct else 0,
                last_reviewed_at=now,
                due_date=now + timedelta(days=interval_days),
            )
            db.add(review_item)
        else:
            review_item.last_reviewed_at = now
            if is_correct:
                review_item.consecutive_correct += 1
                review_item.interval_days = _review_interval_days(
                    True, submission.confidence, review_item.interval_days
                )
            else:
                review_item.consecutive_correct = 0
                review_item.interval_days = _review_interval_days(False, submission.confidence)
            review_item.due_date = now + timedelta(days=review_item.interval_days)

    db.commit()
    db.refresh(attempt)
    return attempt, question, is_correct


def _review_interval_days(is_correct: bool, confidence: str, previous: Optional[int] = None) -> int:
    """Use modest review intervals; low confidence slows progression even when correct."""
    if not is_correct:
        return 1
    if confidence == "low":
        return min(3, max(2, previous or 2))
    if previous is None:
        return 4 if confidence == "high" else 3
    return min(30, max(1, previous) * 2)


def repair_legacy_review_dates(db: Session) -> None:
    """Move stale legacy due dates forward from their last recorded review."""
    items = db.query(ReviewItem).filter(ReviewItem.last_reviewed_at.isnot(None)).all()
    changed = False
    for item in items:
        last_reviewed = item.last_reviewed_at
        due_date = item.due_date
        if last_reviewed and due_date:
            # SQLite may return naive datetimes for values originally stored in UTC.
            if last_reviewed.tzinfo is None:
                last_reviewed = last_reviewed.replace(tzinfo=timezone.utc)
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
            if due_date <= last_reviewed:
                item.due_date = last_reviewed + timedelta(days=max(1, item.interval_days or 1))
                changed = True
    if changed:
        db.commit()


def get_practice_statistics(db: Session) -> Dict[str, Any]:
    """Calculate progress only from verified questions, with task and review signals."""
    verified_attempts = db.query(Attempt).join(Question, Attempt.question_id == Question.id).filter(
        Question.verification_status == "verified"
    )
    total_attempts = verified_attempts.count()
    correct_attempts = verified_attempts.filter(Attempt.is_correct.is_(True)).count()
    overall_accuracy = round((correct_attempts / total_attempts) * 100, 1) if total_attempts > 0 else 0.0

    domain_rows = db.query(
        Domain.code, Domain.title, Domain.exam_weight,
        func.count(Attempt.id).label("attempts"),
        func.coalesce(func.sum(case((Attempt.is_correct.is_(True), 1), else_=0)), 0).label("correct"),
    ).outerjoin(Task, Task.domain_id == Domain.id).outerjoin(
        Question, and_(Question.task_id == Task.id, Question.verification_status == "verified")
    ).outerjoin(Attempt, Attempt.question_id == Question.id).group_by(
        Domain.id, Domain.code, Domain.title, Domain.exam_weight
    ).order_by(Domain.code.asc()).all()
    domain_stats = []
    for row in domain_rows:
        d_total, d_correct = row.attempts, int(row.correct)
        domain_stats.append({
            "code": row.code, "title": row.title, "weight": row.exam_weight,
            "attempts": d_total, "correct": d_correct,
            "accuracy": round((d_correct / d_total) * 100, 1) if d_total else 0.0,
        })

    task_rows = db.query(
        Task.code, Task.official_description, Domain.code.label("domain_code"),
        func.count(Attempt.id).label("attempts"),
        func.coalesce(func.sum(case((Attempt.is_correct.is_(True), 1), else_=0)), 0).label("correct"),
    ).join(Domain, Task.domain_id == Domain.id).outerjoin(
        Question, and_(Question.task_id == Task.id, Question.verification_status == "verified")
    ).outerjoin(Attempt, Attempt.question_id == Question.id).group_by(
        Task.id, Task.code, Task.official_description, Domain.code
    ).order_by(Task.code.asc()).all()
    task_stats = []
    for row in task_rows:
        if not row.attempts:
            continue
        correct = int(row.correct)
        task_stats.append({
            "code": row.code, "description": row.official_description,
            "domain_code": row.domain_code, "attempts": row.attempts,
            "correct": correct,
            "accuracy": round((correct / row.attempts) * 100, 1),
        })

    signals = db.query(Attempt, Question, Task, Domain).join(
        Question, Attempt.question_id == Question.id
    ).outerjoin(Task, Question.task_id == Task.id).outerjoin(
        Domain, Task.domain_id == Domain.id
    ).filter(
        Question.verification_status == "verified",
        or_(Attempt.is_correct.is_(False), Attempt.confidence == "low"),
    ).order_by(Attempt.answered_at.desc(), Attempt.id.desc()).limit(8).all()
    recent_signals = [{
        "question_id": attempt.question_id,
        "task_code": task.code if task else None,
        "domain_code": domain.code if domain else None,
        "stem": question.stem,
        "is_correct": attempt.is_correct,
        "confidence": attempt.confidence,
        "answered_at": attempt.answered_at,
    } for attempt, question, task, domain in signals]

    return {
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "overall_accuracy": overall_accuracy,
        "domains": domain_stats,
        "tasks": task_stats,
        "recent_signals": recent_signals,
    }
