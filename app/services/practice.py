"""Practice service managing question selection, answer verification, attempt logging, and progress stats."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Domain, Task, Question, Attempt, StudySession, ReviewItem
from app.schemas.question import QuestionSchema, AttemptSubmissionSchema
from data.processed.verified_manual_questions import VERIFIED_MANUAL_QUESTIONS


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def seed_verified_questions(db: Session, force: bool = False) -> Dict[str, int]:
    """Seed verified practice questions into the questions table."""
    existing_count = db.query(Question).count()
    if existing_count > 0 and not force:
        return {"questions_seeded": 0, "total_questions": existing_count}

    if force:
        db.query(Question).delete()
        db.commit()

    tasks_by_code = {t.code: t for t in db.query(Task).all()}
    seeded_count = 0

    for q_data in VERIFIED_MANUAL_QUESTIONS:
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

    attempt = Attempt(
        question_id=question.id,
        session_id=session_id,
        selected_option=submission.selected_option.strip().upper(),
        is_correct=is_correct,
        confidence=submission.confidence,
        response_time_seconds=submission.response_time_seconds,
        answered_at=_utc_now(),
    )
    db.add(attempt)

    # Update or insert Spaced Repetition ReviewItem for this task
    if question.task_id:
        review_item = db.query(ReviewItem).filter(ReviewItem.task_id == question.task_id).first()
        if not review_item:
            review_item = ReviewItem(
                task_id=question.task_id,
                concept_name=question.task.official_description if question.task else None,
                interval_days=1 if not is_correct else 3,
                consecutive_correct=1 if is_correct else 0,
                last_reviewed_at=_utc_now(),
            )
            db.add(review_item)
        else:
            review_item.last_reviewed_at = _utc_now()
            if is_correct:
                review_item.consecutive_correct += 1
                review_item.interval_days = min(30, review_item.interval_days * 2)
            else:
                review_item.consecutive_correct = 0
                review_item.interval_days = 1

    db.commit()
    db.refresh(attempt)
    return attempt, question, is_correct


def get_practice_statistics(db: Session) -> Dict[str, Any]:
    """Calculate overall and domain accuracy from verified attempts."""
    total_attempts = db.query(Attempt).count()
    correct_attempts = db.query(Attempt).filter(Attempt.is_correct == True).count()
    overall_accuracy = round((correct_attempts / total_attempts) * 100, 1) if total_attempts > 0 else 0.0

    # Domain accuracy breakdown
    domain_stats = []
    domains = db.query(Domain).order_by(Domain.code.asc()).all()

    for d in domains:
        t_ids = [t.id for t in d.tasks]
        d_attempts = (
            db.query(Attempt)
            .join(Question, Attempt.question_id == Question.id)
            .filter(Question.task_id.in_(t_ids))
            .all()
        )
        d_total = len(d_attempts)
        d_correct = sum(1 for a in d_attempts if a.is_correct)
        d_acc = round((d_correct / d_total) * 100, 1) if d_total > 0 else 0.0

        domain_stats.append({
            "code": d.code,
            "title": d.title,
            "weight": d.exam_weight,
            "attempts": d_total,
            "correct": d_correct,
            "accuracy": d_acc,
        })

    return {
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "overall_accuracy": overall_accuracy,
        "domains": domain_stats,
    }
