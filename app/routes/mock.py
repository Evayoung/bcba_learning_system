"""Mock exam routes: setup, per-question flow, answer recording, and results."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db import get_db
from app.models import Question, StudySession, Attempt
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
    sign_mock_state,
    verify_mock_state,
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
    def mock_start(
        exam_mode: str = "mini",
        domain_filter: str = "all",
        question_count: int = 13,
        time_limit_minutes: int = -1,
    ):
        db = next(get_db())
        result = create_mock_session(
            db, exam_mode=exam_mode, domain_filter=domain_filter,
            question_count=question_count,
            time_limit_minutes=None if time_limit_minutes == -1 else time_limit_minutes,
        )

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
        state_token = sign_mock_state(session_id, question_ids, time_limit, exam_label)

        # Show first question
        q = get_mock_question(db, question_ids[0])
        return page_frame(
            *mock_question_page(
                question=q,
                question_index=0,
                total_questions=len(question_ids),
                session_id=session_id,
                time_limit_minutes=time_limit,
                exam_label=exam_label,
                state_token=state_token,
                remaining_seconds=time_limit * 60 if time_limit else None,
            ),
            current="/mock",
            title=f"{exam_label} — Question 1",
        )

    @app.post("/mock/answer")
    def mock_answer(
        session_id: int,
        question_id: int,
        question_index: int,
        selected_option: str = "",
        action: str = "next",
        state_token: str = "",
    ):
        db = next(get_db())
        state = verify_mock_state(state_token, session_id)
        if not state:
            from faststrap import Alert
            return page_frame(Alert("This exam link is invalid. Start a new practice set.", variant="danger"), *mock_setup_page(), current="/mock", title="Practice Exam")
        q_ids = state["question_ids"]
        if question_index < 0 or question_index >= len(q_ids) or q_ids[question_index] != question_id:
            from faststrap import Alert
            return page_frame(Alert("The question sequence is invalid. Start a new practice set.", variant="danger"), *mock_setup_page(), current="/mock", title="Practice Exam")
        total = len(q_ids)
        answered_count = db.query(Attempt).filter(
            Attempt.session_id == session_id,
            Attempt.question_id.in_(q_ids),
        ).count()
        if question_index > answered_count:
            from faststrap import Alert
            return page_frame(Alert("This question was already answered or the sequence is out of date. Start a new practice set to continue.", variant="warning"), *mock_setup_page(), current="/mock", title="Practice Exam")
        if action not in {"previous", "next", "finish"}:
            action = "next"
        session = db.query(StudySession).filter(StudySession.id == session_id).first()
        if not session or session.mode != "mock" or session.status != "active":
            from faststrap import Alert
            return page_frame(Alert("This practice set has ended. Start a new one to continue.", variant="warning"), *mock_setup_page(), current="/mock", title="Practice Exam")
        started_at = session.started_at
        if started_at and started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        elapsed_seconds = int((datetime.now(timezone.utc) - started_at).total_seconds()) if started_at else 0
        remaining_seconds = max(0, state["minutes"] * 60 - elapsed_seconds) if state["minutes"] else None
        if remaining_seconds == 0:
            results = score_mock_session(db, session_id, q_ids)
            return page_frame(*mock_results_page(results, exam_label=state["label"]), current="/mock", title=f"{state['label']} — Results")

        # Save or update an answer before moving. Previous can be used without changing it.
        is_last = question_index == total - 1
        saved_attempt = db.query(Attempt).filter(
            Attempt.session_id == session_id,
            Attempt.question_id == question_id,
        ).first()
        if action == "previous" and question_index == 0:
            action = "next"
        if action == "finish" and not is_last:
            action = "next"
        if not selected_option and not saved_attempt and action not in {"previous", "finish"}:
            q = get_mock_question(db, question_id)
            return page_frame(
                *mock_question_page(q, question_index, total, session_id,
                    time_limit_minutes=state["minutes"], exam_label=state["label"],
                    state_token=state_token, error_message="Choose an answer before continuing. Use Previous to revisit an earlier question.",
                    remaining_seconds=remaining_seconds),
                current="/mock", title=f"{state['label']} — Question {question_index + 1}",
            )
        if selected_option:
            try:
                submit_mock_answer(db, session_id, question_id, selected_option)
            except ValueError as exc:
                q = get_mock_question(db, question_id)
                return page_frame(
                    *mock_question_page(q, question_index, total, session_id,
                        time_limit_minutes=state["minutes"], exam_label=state["label"],
                        state_token=state_token, error_message=str(exc),
                        selected_option=saved_attempt.selected_option if saved_attempt else "",
                        remaining_seconds=remaining_seconds),
                    current="/mock", title=f"{state['label']} — Question {question_index + 1}",
                )

        # Navigate backward and forward through saved answers.
        next_index = question_index - 1 if action == "previous" else question_index + 1
        if action == "previous":
            previous_question = get_mock_question(db, q_ids[next_index])
            previous_attempt = db.query(Attempt).filter(
                Attempt.session_id == session_id,
                Attempt.question_id == q_ids[next_index],
            ).first()
            return page_frame(
                *mock_question_page(
                    question=previous_question, question_index=next_index,
                    total_questions=total, session_id=session_id,
                    time_limit_minutes=state["minutes"], exam_label=state["label"],
                    state_token=state_token,
                    selected_option=previous_attempt.selected_option if previous_attempt else "",
                    remaining_seconds=remaining_seconds,
                ),
                current="/mock", title=f"{state['label']} — Question {next_index + 1}",
            )
        is_last = (next_index >= total) or (action == "finish" and question_index == total - 1)

        if is_last:
            # Score and show results
            results = score_mock_session(db, session_id, q_ids)
            return page_frame(
                *mock_results_page(results, exam_label=state["label"]),
                current="/mock",
                title=f"{state['label']} — Results",
            )

        # Advance to next question
        next_q = get_mock_question(db, q_ids[next_index])
        next_attempt = db.query(Attempt).filter(
            Attempt.session_id == session_id,
            Attempt.question_id == q_ids[next_index],
        ).first()
        return page_frame(
            *mock_question_page(
                question=next_q,
                question_index=next_index,
                total_questions=total,
                session_id=session_id,
                time_limit_minutes=state["minutes"],
                exam_label=state["label"],
                state_token=state_token,
                selected_option=next_attempt.selected_option if next_attempt else "",
                remaining_seconds=remaining_seconds,
            ),
            current="/mock",
            title=f"{state['label']} — Question {next_index + 1}",
        )
