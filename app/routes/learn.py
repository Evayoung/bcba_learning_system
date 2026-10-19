"""Learn / Tutor routes with retrieval integration and interactive AI Tutor endpoint."""

from __future__ import annotations

from typing import Any
from app.db import get_db
from app.models import Task
from app.presentation.shell import page_frame
from app.presentation.pages.learn import learn_page
from app.services.retrieval import retrieve_content
from app.services.llm_provider import LLMProviderAdapter


def register_learn_routes(app: Any) -> None:
    @app.get("/learn")
    def learn(domain: str | None = None, query: str | None = None, task: str | None = None, mode: str = "explain"):
        db = next(get_db())
        results = None
        if query or task:
            results = retrieve_content(
                db=db,
                query=query,
                task_code=task,
                domain_code=domain,
                limit=6,
            )
        elif domain and domain != "all":
            results = retrieve_content(
                db=db,
                query=None,
                domain_code=domain,
                limit=5,
            )

        return page_frame(
            *learn_page(
                selected_domain=domain,
                query=query,
                task_code=task,
                selected_mode=mode,
                retrieved_results=results,
            ),
            current="/learn",
            title="Learn / Tutor",
        )

    @app.post("/learn/ask")
    def ask_tutor(
        prompt: str = "",
        mode: str = "explain",
        task_code: str = "",
        domain_code: str = "all",
        # Socratic follow-up fields: the learner's answer to the tutor's
        # guiding question, plus the question itself so we can rebuild
        # the conversation thread before asking the LLM to evaluate it.
        socratic_answer: str = "",
        previous_tutor_question: str = "",
    ):
        db = next(get_db())

        # Build conversation history for Socratic follow-ups so the LLM can
        # evaluate the learner's answer against its own guiding question.
        conversation_history = None
        user_msg = prompt.strip() if prompt.strip() else socratic_answer.strip()
        if socratic_answer.strip() and previous_tutor_question.strip():
            conversation_history = [
                {"role": "assistant", "content": previous_tutor_question.strip()},
            ]
            if not prompt.strip():
                user_msg = socratic_answer.strip()

        # 1. Retrieve grounded source excerpts for prompt / task
        retrieval_query = user_msg or task_code or ""
        results = retrieve_content(
            db=db,
            query=retrieval_query if retrieval_query else None,
            task_code=task_code if task_code else None,
            domain_code=domain_code if domain_code != "all" else None,
            limit=4,
        )

        task_desc = ""
        if task_code:
            t_obj = db.query(Task).filter(Task.code == task_code).first()
            if t_obj:
                task_desc = t_obj.official_description

        # 2. Call LLM provider adapter with strict grounding
        adapter = LLMProviderAdapter()
        if not user_msg:
            user_msg = f"Explain task competency {task_code} ({task_desc})."

        llm_res = adapter.generate_tutoring_response(
            user_message=user_msg,
            mode=mode,
            source_excerpts=[r.to_dict() for r in results] if results else None,
            task_code=task_code if task_code else None,
            task_description=task_desc if task_desc else None,
            conversation_history=conversation_history,
        )

        tutor_response_payload = {
            "prompt": user_msg,
            "mode": mode,
            "task_code": task_code,
            "content": llm_res.content if llm_res.success else "",
            "error": llm_res.error_message if not llm_res.success else None,
            "fallback_used": llm_res.fallback_used if llm_res.success else False,
        }

        return page_frame(
            *learn_page(
                selected_domain=domain_code,
                query=None,
                task_code=task_code,
                selected_mode=mode,
                retrieved_results=results,
                tutor_response=tutor_response_payload,
            ),
            current="/learn",
            title="Learn / Tutor",
        )
