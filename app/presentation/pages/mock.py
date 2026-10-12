"""Mock exam presentation components using proper FastStrap component API.

App mode: Hybrid (polished shell + dense functional interior).
Components used: StatCard, ProgressBar, Alert, Badge, BadgeGroup, ResultCard,
                 Card, Row, Col, Button, Select, Spinner, Icon, StatusBadge,
                 Radio, Stepper, StepperStep, PageHeader, EmptyState, DataTable.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from fasthtml.common import Div, H2, H3, H4, P, Span, Form, A, Input, Small
from faststrap import (
    Alert, Badge, BadgeGroup, Button, Card, Col, EmptyState,
    Icon, PageHeader, ProgressBar, Radio, ResultCard, Row,
    Select, Spinner, StatCard, StatusBadge, Input as FSInput,
)


def mock_setup_page(total_verified: int = 0) -> list:
    """Mock exam configuration page — first viewport has setup card + disclaimer."""

    disclaimer = Alert(
        Div(
            Span("Practice simulator only. ", cls="fw-bold"),
            "This tool is built on the PTB 6th Edition Study Manual and BACB TCO. "
            "It is not an official BACB exam and does not predict or guarantee exam outcomes. "
            "Question counts are limited to currently verified items.",
        ),
        variant="info",
        heading="Important Notice",
        cls="mb-4",
    )

    # Config form — POST to /mock/start
    config_card = Card(
        Div(
            PageHeader(
                title="Configure Practice Exam",
                subtitle="Simulate real exam timing and pacing across the weighted outline.",
            ),
            Form(
                Row(
                    Col(
                        Select(
                            "exam_mode",
                            ("mini", "Quick Check — up to 13 Qs • 30 min"),
                            ("domain", "Domain Sprint — up to 13 Qs • 45 min"),
                            ("full", "Full Practice — up to 13 Qs • 60 min"),
                            label="Exam Format",
                            cls="mb-3",
                        ),
                        span=12, md=6,
                    ),
                    Col(
                        Select(
                            "domain_filter",
                            ("all", "All Domains (Proportional Weight)"),
                            ("foundation", "Foundations Only (Domains A–D)"),
                            ("applications", "Applications Only (Domains E–I)"),
                            label="Domain Coverage",
                            cls="mb-3",
                        ),
                        span=12, md=6,
                    ),
                ),
                Div(
                    Button(
                        "Launch Practice Exam",
                        variant="primary",
                        icon="play-circle-fill",
                        size="lg",
                        type="submit",
                        data_loading_text="Preparing exam...",
                    ),
                    Span(
                        f"{total_verified} verified questions available",
                        cls="text-muted small ms-3",
                    ),
                    cls="d-flex align-items-center flex-wrap gap-3 mt-2",
                ),
                method="post",
                action="/mock/start",
            ),
            cls="p-4",
        ),
        cls="mb-4 shadow-sm",
    )

    # Stats row
    stats_row = Row(
        Col(StatCard("Verified Questions", str(total_verified), icon=Icon("patch-check-fill"), trend_type="up"), span=12, md=4),
        Col(StatCard("Domains Covered", "9", icon=Icon("grid-3x3-gap-fill"), trend_type="neutral"), span=12, md=4),
        Col(StatCard("Exam Weighting", "175 Scored Items", icon=Icon("bar-chart-fill"), trend_type="neutral"), span=12, md=4),
        cls="mb-4 g-3",
    )

    return [disclaimer, config_card, stats_row]


def mock_question_page(
    question: Any,
    question_index: int,
    total_questions: int,
    session_id: int,
    question_ids: List[int],
    time_limit_minutes: int = 30,
    exam_label: str = "Practice Exam",
) -> list:
    """Render a single in-exam question with progress, timer info, and navigation."""

    options_data = json.loads(question.options) if question.options else []
    task_label = f"Task {question.task.code}" if question.task else "TCO Item"
    domain_label = f"Domain {question.task.domain.code}" if question.task and question.task.domain else ""
    progress_pct = int((question_index / total_questions) * 100)

    # Exam header band
    exam_header = Card(
        Div(
            Row(
                Col(
                    Div(
                        Icon("stopwatch", cls="text-primary me-2"),
                        Span(f"{exam_label}", cls="fw-bold text-dark"),
                        cls="d-flex align-items-center",
                    ),
                    span=12, md=6,
                ),
                Col(
                    Div(
                        Badge(f"Question {question_index + 1} of {total_questions}", variant="primary", cls="me-2"),
                        Badge(f"{time_limit_minutes} min limit", variant="secondary"),
                        cls="d-flex align-items-center justify-content-md-end",
                    ),
                    span=12, md=6,
                ),
            ),
            Div(
                ProgressBar(progress_pct, variant="primary", striped=True, animated=True, height="6px"),
                Small(f"{progress_pct}% complete", cls="text-muted d-block mt-1"),
                cls="mt-3",
            ),
            cls="p-3",
        ),
        cls="mb-3 shadow-sm",
    )

    # Build radio options
    option_radios = []
    for opt in options_data:
        option_radios.append(
            Div(
                Radio(
                    "selected_option",
                    label=f"{opt['id']}.  {opt['text']}",
                    value=opt["id"],
                    radio_id=f"opt_{opt['id']}",
                    input_cls="me-2",
                    label_cls="text-dark",
                ),
                cls="p-3 mb-2 rounded border bg-white option-hover",
            )
        )

    # Hidden fields for session state
    hidden_fields = [
        Input(type="hidden", name="session_id", value=str(session_id)),
        Input(type="hidden", name="question_id", value=str(question.id)),
        Input(type="hidden", name="question_ids", value=json.dumps(question_ids)),
        Input(type="hidden", name="question_index", value=str(question_index)),
        Input(type="hidden", name="time_limit_minutes", value=str(time_limit_minutes)),
        Input(type="hidden", name="exam_label", value=exam_label),
    ]

    # Navigation footer
    is_last = (question_index >= total_questions - 1)
    nav_footer = Div(
        Div(
            BadgeGroup(
                Badge(domain_label, variant="primary") if domain_label else None,
                Badge(task_label, variant="info"),
                Badge(question.difficulty.capitalize(), variant="secondary"),
            ),
            cls="mb-3 mb-md-0",
        ),
        Div(
            Button(
                "Finish Exam" if is_last else "Save & Next →",
                variant="success" if is_last else "primary",
                icon="check-circle-fill" if is_last else "arrow-right",
                type="submit",
                name="action",
                value="finish" if is_last else "next",
                data_loading_text="Saving your answer...",
            ),
            cls="d-flex gap-2",
        ),
        cls="d-flex justify-content-between align-items-center pt-3 border-top flex-wrap gap-2",
    )

    question_card = Card(
        Form(
            *hidden_fields,
            Div(
                H3(question.stem, cls="h5 fw-bold mb-4 text-dark lh-base"),
                Div(*option_radios, cls="mb-3"),
                nav_footer,
                cls="p-4",
            ),
            method="post",
            action="/mock/answer",
            data_loading_text="Saving your answer...",
        ),
        cls="mb-4 shadow",
    )

    return [exam_header, question_card]


def mock_results_page(results: Dict[str, Any], exam_label: str = "Practice Exam") -> list:
    """Render post-exam results with score, domain breakdown, and review items."""

    score_pct = results.get("score_pct", 0)
    total = results.get("total", 0)
    correct = results.get("correct", 0)
    passed = results.get("passed", False)
    domains = results.get("domains", [])
    duration_seconds = results.get("duration_seconds")

    duration_str = ""
    if duration_seconds:
        mins, secs = divmod(duration_seconds, 60)
        duration_str = f"{mins}m {secs}s"

    # Result header card
    result_card = ResultCard(
        f"{'Congratulations!' if passed else 'Keep Practising!'} — You scored {score_pct}%",
        message=(
            f"You answered {correct} of {total} questions correctly."
            + (f" Completed in {duration_str}." if duration_str else "")
            + " This is a practice session only, not an official BACB score."
        ),
        status="success" if passed else "warning",
        icon="trophy-fill" if passed else "graph-up-arrow",
        action=A(
            Button("Practise Again", variant="primary", icon="arrow-repeat"),
            href="/mock",
            cls="text-decoration-none",
        ),
        cls="mb-4",
    )

    # Summary stat cards
    stat_row = Row(
        Col(
            StatCard(
                "Score",
                f"{score_pct}%",
                icon=Icon("percent"),
                trend=f"{'Pass' if passed else 'Below Pass'}",
                trend_type="up" if passed else "down",
            ),
            span=12, md=4,
        ),
        Col(
            StatCard("Correct", f"{correct}/{total}", icon=Icon("check2-circle"), trend_type="neutral"),
            span=12, md=4,
        ),
        Col(
            StatCard("Time Taken", duration_str or "—", icon=Icon("stopwatch"), trend_type="neutral"),
            span=12, md=4,
        ),
        cls="mb-4 g-3",
    )

    # Domain breakdown
    domain_rows = []
    for d in domains:
        d_acc = d.get("accuracy", 0)
        bar_variant = "success" if d_acc >= 80 else "warning" if d_acc >= 60 else "danger"
        domain_rows.append(
            Div(
                Div(
                    Div(
                        Span(f"Domain {d['code']}: {d['title']}", cls="fw-semibold small text-dark"),
                        Div(
                            StatusBadge(
                                f"{d_acc}%",
                                status="success" if d_acc >= 80 else "warning" if d_acc >= 60 else "danger",
                                show_dot=True,
                            ),
                            Span(f"{d['correct']}/{d['total']}", cls="text-muted small ms-2"),
                            cls="d-flex align-items-center gap-2",
                        ),
                        cls="d-flex justify-content-between align-items-center mb-2",
                    ),
                    ProgressBar(int(d_acc), variant=bar_variant, height="6px"),
                    cls="flex-grow-1 w-100",
                ),
                cls="py-3 border-bottom",
            )
        )

    breakdown_card = Card(
        Div(
            H3("Domain Performance Breakdown", cls="h6 fw-bold mb-1 text-dark"),
            P("Based on this practice session only. For progress over time, visit the Progress tab.", cls="text-muted small mb-3"),
            *domain_rows if domain_rows else [
                EmptyState(icon="bar-chart", title="No domain data", description="No task-linked questions in this session.")
            ],
            cls="p-4",
        ),
        cls="mb-4 shadow-sm",
    )

    # Review actions
    actions_card = Card(
        Div(
            Row(
                Col(
                    A(Button("Try Again", variant="primary", icon="arrow-repeat", cls="w-100"), href="/mock", cls="text-decoration-none"),
                    span=12, md=4, cls="mb-2 mb-md-0",
                ),
                Col(
                    A(Button("Targeted Practice", variant="outline-primary", icon="check2-square", cls="w-100"), href="/practice", cls="text-decoration-none"),
                    span=12, md=4, cls="mb-2 mb-md-0",
                ),
                Col(
                    A(Button("Study Manual", variant="outline-secondary", icon="journal-bookmark", cls="w-100"), href="/learn", cls="text-decoration-none"),
                    span=12, md=4,
                ),
            ),
            cls="p-4",
        ),
        cls="bg-light border-0",
    )

    return [result_card, stat_row, breakdown_card, actions_card]
