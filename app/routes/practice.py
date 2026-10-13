"""Practice question routes with full session, submission, and navigation flow."""

from __future__ import annotations

from typing import Any, Optional
from app.db import get_db, init_db
from app.models import Question, Task, Domain
from app.presentation.shell import page_frame
from app.presentation.pages.practice import render_practice_view
from app.services.practice import (
    seed_verified_questions,
    get_practice_question,
    record_attempt,
)
from app.schemas.question import AttemptSubmissionSchema


DOMAIN_OPTIONS = [
    ("all", "All Domains (A - I)"),
    ("A", "Domain A: Behaviorism & Philosophical Foundations"),
    ("B", "Domain B: Concepts and Principles"),
    ("C", "Domain C: Measurement & Interpretation"),
    ("D", "Domain D: Experimental Design"),
    ("E", "Domain E: Ethical and Professional Issues"),
    ("F", "Domain F: Behavior Assessment"),
    ("G", "Domain G: Behavior-Change Procedures"),
    ("H", "Domain H: Selecting Interventions"),
    ("I", "Domain I: Personnel Supervision"),
]


def register_practice_routes(app: Any) -> None:
    @app.get("/practice")
    def practice(domain: str = "all", qid: Optional[int] = None, task: Optional[str] = None):
        db = next(get_db())

        # Ensure questions seeded
        seed_verified_questions(db)

        question = get_practice_question(
            db,
            question_id=qid,
            domain_code=domain if domain != "all" else None,
            task_code=task,
        )

        return page_frame(
            *render_practice_view(
                question=question,
                attempt=None,
                domain_code=domain,
                task_code=task,
                all_domains=DOMAIN_OPTIONS,
            ),
            current="/practice",
            title="Practice",
        )

    @app.post("/practice/submit")
    def practice_submit(
        question_id: int,
        selected_option: str = "",
        confidence: str = "medium",
        domain_code: str = "all",
        task_code: Optional[str] = None,
    ):
        db = next(get_db())

        if not selected_option:
            # No option selected; reload the same question
            question = get_practice_question(db, question_id=question_id)
            return page_frame(
                *render_practice_view(
                    question=question,
                    attempt=None,
                    domain_code=domain_code,
                    task_code=task_code,
                    all_domains=DOMAIN_OPTIONS,
                ),
                current="/practice",
                title="Practice",
            )

        submission = AttemptSubmissionSchema(
            question_id=question_id,
            selected_option=selected_option,
            confidence=confidence,
        )
        attempt, question, is_correct = record_attempt(db, submission)

        # Find the next question for the "Next Question" button
        next_query = db.query(Question).filter(
            Question.verification_status == "verified"
        )
        if task_code and question.task_id:
            next_query = next_query.filter(Question.task_id == question.task_id)
        elif domain_code != "all" and question.task and question.task.domain:
            domain_task_ids = [task.id for task in question.task.domain.tasks]
            next_query = next_query.filter(Question.task_id.in_(domain_task_ids))
        next_q = next_query.filter(Question.id > question_id).order_by(Question.id.asc()).first()
        if next_q is None:
            next_q = next_query.filter(Question.id <= question_id).order_by(Question.id.asc()).first()

        return page_frame(
            *render_practice_view(
                question=question,
                attempt=attempt,
                domain_code=domain_code,
                task_code=task_code,
                all_domains=DOMAIN_OPTIONS,
                next_question_id=next_q.id if next_q else None,
            ),
            current="/practice",
            title="Practice",
        )
