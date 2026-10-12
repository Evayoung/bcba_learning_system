"""Mock exam routes: setup, per-question flow, answer recording, and results."""

from __future__ import annotations

import json
from typing import Any

from app.db import get_db
from app.models import Question
from app.presentation.shell import page_frame
from app.presentation.pages.mock import (
    mock_setup_page,
    mock_question_page,
    mock_results_page,
)
from app.services.mock_exam import (
    create_mock_session,
    get_mock_question,
    submit_mock_answer,
    score_mock_session,
    EXAM_CONFIG,
)
from app.services.practice import seed_verified_questions


def register_mock_routes(app: Any) -> None:

    @app.get("/mock")
    def mock():
        db = next(get_db())
        seed_verified_questions(db)
        total_verified = db.query(Question).filter(Question.verification_status == "verified").count()
        return page_frame(
            *mock_setup_page(total_verified=total_verified),
            current="/mock",
            title="Mock Exam",
        )

    @app.post("/mock/start")
    def mock_start(exam_mode: str = "mini", domain_filter: str = "all"):
        db = next(get_db())
        result = create_mock_session(db, exam_mode=exam_mode, domain_filter=domain_filter)

        if "error" in result:
            from faststrap import Alert
            return page_frame(
                Alert(result["error"], variant="danger", cls="mb-4"),
                *mock_setup_page(),
                current="/mock",
                title="Mock Exam",
            )

        session_id = result["session_id"]
        question_ids = result["question_ids"]
        time_limit = result["minutes"]
        exam_label = result["label"]

        # Show first question
        q = get_mock_question(db, question_ids[0])
        return page_frame(
            *mock_question_page(
                question=q,
                question_index=0,
                total_questions=len(question_ids),
                session_id=session_id,
                question_ids=question_ids,
                time_limit_minutes=time_limit,
                exam_label=exam_label,
            ),
            current="/mock",
            title=f"{exam_label} — Question 1",
        )

    @app.post("/mock/answer")
    def mock_answer(
        session_id: int,
        question_id: int,
        question_ids: str,
        question_index: int,
        selected_option: str = "",
        time_limit_minutes: int = 30,
        exam_label: str = "Practice Exam",
        action: str = "next",
    ):
        db = next(get_db())
        q_ids = json.loads(question_ids)
        total = len(q_ids)

        # Validate and record the answer if one was given
        if selected_option:
            try:
                submit_mock_answer(db, session_id, question_id, selected_option)
            except ValueError:
                pass  # invalid option — skip silently, still advance

        # Determine next action
        next_index = question_index + 1
        is_last = (next_index >= total) or (action == "finish")

        if is_last:
            # Score and show results
            results = score_mock_session(db, session_id)
            return page_frame(
                *mock_results_page(results, exam_label=exam_label),
                current="/mock",
                title=f"{exam_label} — Results",
            )

        # Advance to next question
        next_q = get_mock_question(db, q_ids[next_index])
        return page_frame(
            *mock_question_page(
                question=next_q,
                question_index=next_index,
                total_questions=total,
                session_id=session_id,
                question_ids=q_ids,
                time_limit_minutes=time_limit_minutes,
                exam_label=exam_label,
            ),
            current="/mock",
            title=f"{exam_label} — Question {next_index + 1}",
        )
