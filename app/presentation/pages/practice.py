"""Practice presentation — proper FastStrap components throughout.

FastStrap mode: Hybrid (polished shell, dense functional interior).
Components: Card, Row, Col, Select, Button, Badge, BadgeGroup, StatusBadge,
            Radio, Icon, EmptyState, ProgressBar, Alert.
No native FastHTML Input/Label for radio buttons — uses FastStrap Radio component.
"""

from __future__ import annotations

import json
from typing import Optional, List, Any
from fasthtml.common import Div, H3, H4, P, Span, Form, Input, A
from faststrap import (
    Alert, Badge, BadgeGroup, Button, Card, Col, EmptyState,
    Icon, Markdown, Radio, Row, Select, StatusBadge,
)
from app.models import Question, Attempt


def render_practice_view(
    question: Optional[Question],
    attempt: Optional[Attempt] = None,
    domain_code: Optional[str] = None,
    all_domains: Optional[List[tuple]] = None,
    next_question_id: Optional[int] = None,
) -> list:
    """Render full practice session view with proper FastStrap components."""

    domain_options = all_domains or [
        ("all", "All Domains (A – I)"),
        ("A", "Domain A: Behaviorism"),
        ("B", "Domain B: Concepts and Principles"),
        ("C", "Domain C: Measurement"),
        ("D", "Domain D: Experimental Design"),
        ("G", "Domain G: Behavior-Change"),
    ]
    selected_domain = domain_code or "all"

    # ── Filter bar ─────────────────────────────────────────────────────────────
    filter_card = Card(
        Div(
            Form(
                Row(
                    Col(
                        Select(
                            "domain",
                            *domain_options,
                            label="Filter by Domain",
                            cls="mb-2",
                        ),
                        span=12, md=8,
                    ),
                    Col(
                        Button("Load Questions", variant="primary", type="submit", cls="w-100 mt-md-4 mb-2"),
                        span=12, md=4,
                    ),
                ),
                method="get",
                action="/practice",
            ),
            cls="p-3",
        ),
        cls="mb-4 shadow-sm",
    )

    # ── Empty state ────────────────────────────────────────────────────────────
    if not question:
        return [
            filter_card,
            Card(
                EmptyState(
                    icon="check2-circle",
                    title="All Questions Reviewed",
                    description="You have reviewed all verified questions for this domain. Try another domain or practise again.",
                    action=A(
                        Button("View Progress", variant="primary", icon="bar-chart-line"),
                        href="/progress",
                        cls="text-decoration-none",
                    ),
                ),
                cls="mb-4 py-4",
            ),
        ]

    # ── Parse question data ────────────────────────────────────────────────────
    options_data = json.loads(question.options) if question.options else []
    distractor_data = json.loads(question.distractor_rationales) if question.distractor_rationales else {}

    task_label = f"Task {question.task.code}" if question.task else "Verified Item"
    domain_label = f"Domain {question.task.domain.code}" if question.task and question.task.domain else "TCO"

    is_submitted = attempt is not None
    user_selected = attempt.selected_option if attempt else None
    is_correct = attempt.is_correct if attempt else False

    # ── Option elements ────────────────────────────────────────────────────────
    option_elements = []
    for opt in options_data:
        opt_id = opt["id"]
        opt_text = opt["text"]

        if is_submitted:
            if opt_id == question.correct_option:
                border_cls = "border-success border-2"
                bg_cls = "bg-success-subtle"
                status_icon = Icon("check-circle-fill", cls="text-success ms-auto flex-shrink-0")
            elif opt_id == user_selected and not is_correct:
                border_cls = "border-danger border-2"
                bg_cls = "bg-danger-subtle"
                status_icon = Icon("x-circle-fill", cls="text-danger ms-auto flex-shrink-0")
            else:
                border_cls = "border"
                bg_cls = "bg-light"
                status_icon = None

            option_elements.append(
                Div(
                    Div(
                        Span(
                            opt_id,
                            cls=(
                                "badge me-3 flex-shrink-0 "
                                + ("bg-success" if opt_id == question.correct_option
                                   else "bg-danger" if opt_id == user_selected
                                   else "bg-secondary")
                            ),
                        ),
                        Span(opt_text, cls="text-dark small fw-medium flex-grow-1"),
                        status_icon if status_icon else Div(),
                        cls="d-flex align-items-center w-100 gap-2",
                    ),
                    cls=f"p-3 mb-2 rounded {border_cls} {bg_cls}",
                )
            )
        else:
            option_elements.append(
                Div(
                    Radio(
                        "selected_option",
                        label=f"{opt_id}.  {opt_text}",
                        value=opt_id,
                        radio_id=f"opt_{opt_id}",
                        input_cls="me-2",
                        label_cls="text-dark small fw-medium",
                    ),
                    cls="p-3 mb-2 rounded border bg-white option-hover",
                )
            )

    # ── Confidence selector (before submit only) ───────────────────────────────
    confidence_group = Div(
        Span("Confidence:", cls="small fw-bold text-muted me-2"),
        Div(
            Radio("confidence", label="Low",    value="low",    radio_id="conf_low",    inline=True, input_cls="me-1"),
            Radio("confidence", label="Medium", value="medium", radio_id="conf_medium", inline=True, input_cls="me-1", checked=True),
            Radio("confidence", label="High",   value="high",   radio_id="conf_high",   inline=True, input_cls="me-1"),
            cls="d-flex gap-3",
        ),
        cls="d-flex align-items-center",
    )

    # ── Footer controls ────────────────────────────────────────────────────────
    if not is_submitted:
        footer = Div(
            confidence_group,
            Button("Submit Answer", variant="primary", type="submit", icon="check-lg"),
            cls="d-flex flex-wrap justify-content-between align-items-center pt-3 border-top gap-3",
        )
    else:
        result_badge = StatusBadge(
            "Correct Answer!" if is_correct else f"Incorrect — Correct answer is {question.correct_option}",
            status="success" if is_correct else "danger",
            show_dot=True,
            pill=True,
        )
        footer = Div(
            Div(result_badge, cls="mb-2 mb-md-0"),
            A(
                Button("Next Question →", variant="primary", icon="arrow-right"),
                href=(
                    f"/practice?domain={selected_domain}&qid={next_question_id}"
                    if next_question_id
                    else f"/practice?domain={selected_domain}"
                ),
                cls="text-decoration-none",
            ),
            cls="d-flex flex-wrap justify-content-between align-items-center pt-3 border-top gap-2",
        )

    # ── Question card header badges ────────────────────────────────────────────
    question_badges = Div(
        BadgeGroup(
            Badge(domain_label, variant="primary"),
            Badge(task_label, variant="info"),
            Badge(question.difficulty.capitalize(), variant="secondary"),
            Badge("Verified", variant="success"),
        ),
        cls="mb-3",
    )

    # ── Build question card content ────────────────────────────────────────────
    if not is_submitted:
        q_content = Form(
            Input(type="hidden", name="question_id",  value=str(question.id)),
            Input(type="hidden", name="domain_code",  value=selected_domain),
            Div(
                question_badges,
                H3(question.stem, cls="h5 fw-bold mb-4 text-dark lh-base"),
                Div(*option_elements, cls="mb-4"),
                footer,
                cls="p-4",
            ),
            method="post",
            action="/practice/submit",
        )
    else:
        q_content = Div(
            question_badges,
            H3(question.stem, cls="h5 fw-bold mb-4 text-dark lh-base"),
            Div(*option_elements, cls="mb-4"),
            footer,
            cls="p-4",
        )

    question_card = Card(q_content, cls="mb-4 shadow-sm bg-white")

    # ── Rationale card ─────────────────────────────────────────────────────────
    if is_submitted:
        distractor_rows = [
            Div(
                Span(f"Option {k}:", cls="fw-bold text-danger me-2"),
                Span(v, cls="text-muted small"),
                cls="mb-2 p-2 rounded bg-light border-start border-3 border-danger",
            )
            for k, v in distractor_data.items()
        ]

        rationale_card = Card(
            Div(
                Div(
                    Icon("check2-square", size="1.25rem", cls="text-success me-2"),
                    H4("Comprehensive Behavioral Rationale", cls="h6 fw-bold mb-0 text-success"),
                    cls="d-flex align-items-center mb-3",
                ),
                Div(
                    Markdown(question.rationale) if question.rationale else P("No rationale provided.", cls="text-muted small"),
                    cls="tutor-markdown-body mb-3",
                ),
                Div(
                    H4("Distractor Analysis — Why the other options are incorrect:", cls="h6 fw-bold mb-2 text-dark"),
                    *distractor_rows,
                    cls="mt-3 pt-3 border-top",
                ) if distractor_rows else Div(),
                Div(
                    Span(f"Source: {question.source}", cls="small text-muted fst-italic"),
                    cls="mt-3 pt-2 border-top",
                ),
                cls="p-4",
            ),
            cls="mb-4 border-start border-4 border-success shadow-sm bg-white",
        )
    else:
        rationale_card = Card(
            Div(
                Div(
                    Icon("info-circle", size="1.25rem", cls="text-primary me-2"),
                    Span("Rationale & Distractor Analysis", cls="fw-bold text-dark"),
                    cls="d-flex align-items-center mb-2",
                ),
                P(
                    "Select an answer and click 'Submit Answer' to reveal the full ABA rationale, "
                    "distractor breakdowns, and manual citations.",
                    cls="text-muted small mb-0",
                ),
                cls="p-3",
            ),
            cls="bg-light border-0 mb-4",
        )

    return [filter_card, question_card, rationale_card]
