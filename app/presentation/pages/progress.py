"""Progress presentation components using real attempt data from the database."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from fasthtml.common import Div, H3, H4, P, Span, A
from faststrap import Badge, Button, Card, Col, Icon, ProgressBar, Row


MASTERY_LABELS = {
    "not_started": ("Not Started", "secondary"),
    "practising": ("Practising", "warning"),
    "needs_review": ("Needs Review", "danger"),
    "consistently_correct": ("Consistently Correct", "success"),
}


def _mastery_label(attempts: int, accuracy: float) -> tuple[str, str]:
    """Return (label_text, badge_variant) using transparent documented thresholds."""
    if attempts == 0:
        return MASTERY_LABELS["not_started"]
    if accuracy < 60:
        return MASTERY_LABELS["needs_review"]
    if attempts < 5:
        return MASTERY_LABELS["practising"]
    if accuracy >= 80:
        return MASTERY_LABELS["consistently_correct"]
    return MASTERY_LABELS["practising"]


def progress_page(stats: Optional[Dict[str, Any]] = None) -> list:
    """Progress & Revision analysis view backed by live attempt data."""
    total_attempts = stats.get("total_attempts", 0) if stats else 0
    correct_attempts = stats.get("correct_attempts", 0) if stats else 0
    overall_accuracy = stats.get("overall_accuracy", 0.0) if stats else 0.0
    domains = stats.get("domains", []) if stats else []
    due_review = stats.get("due_review_count", 0) if stats else 0

    accuracy_display = f"{overall_accuracy}%" if total_attempts >= 5 else "—"
    accuracy_note = "Will calculate automatically after 5+ attempts" if total_attempts < 5 else f"{correct_attempts} of {total_attempts} correct"

    # Summary card
    summary_card = Card(
        Div(
            Row(
                Col(
                    Span("Questions Answered", cls="app-metric-label"),
                    Div(str(total_attempts), cls="app-metric-value mt-1"),
                    P("Practice attempts logged across all sessions", cls="text-muted small mb-0"),
                    span=12, md=4, cls="mb-3 mb-md-0",
                ),
                Col(
                    Span("Overall Accuracy", cls="app-metric-label"),
                    Div(accuracy_display, cls=f"app-metric-value mt-1 {'text-success' if overall_accuracy >= 70 else 'text-warning' if overall_accuracy >= 50 else 'text-danger' if total_attempts >= 5 else 'text-muted'}"),
                    P(accuracy_note, cls="text-muted small mb-0"),
                    span=12, md=4, cls="mb-3 mb-md-0",
                ),
                Col(
                    Span("Items Due for Review", cls="app-metric-label"),
                    Div(str(due_review) if due_review > 0 else "0", cls="app-metric-value mt-1 text-primary"),
                    P("Based on spaced repetition and incorrect answers", cls="text-muted small mb-0"),
                    span=12, md=4,
                ),
            ),
            cls="p-3",
        ),
        cls="mb-4",
    )

    # Domain breakdown rows
    domain_progress_rows = []
    for d in domains:
        d_attempts = d.get("attempts", 0)
        d_accuracy = d.get("accuracy", 0.0)
        d_correct = d.get("correct", 0)
        label_text, label_variant = _mastery_label(d_attempts, d_accuracy)
        bar_value = int(d_accuracy) if d_attempts > 0 else 0
        bar_variant = "success" if d_accuracy >= 80 else "warning" if d_accuracy >= 60 else "danger" if d_attempts > 0 else "light"

        domain_progress_rows.append(
            Div(
                Div(
                    Div(
                        Span(f"Domain {d['code']}: {d['title']}", cls="fw-semibold text-dark small"),
                        Div(
                            Badge(label_text, variant=label_variant, cls="me-1"),
                            Span(
                                f"{d_correct}/{d_attempts} correct" if d_attempts > 0 else f"{d.get('weight', 0)}% exam weight",
                                cls="text-muted small",
                            ),
                            cls="d-flex align-items-center gap-2",
                        ),
                        cls="d-flex justify-content-between align-items-center mb-2",
                    ),
                    ProgressBar(bar_value, variant=bar_variant, height="6px", cls="mb-1"),
                    Span(f"{d_accuracy}% accuracy" if d_attempts > 0 else "No attempts yet", cls="text-muted" + " small"),
                    cls="flex-grow-1 w-100",
                ),
                cls="py-3 border-bottom",
            )
        )

    breakdown_card = Card(
        Div(
            H3("Domain Performance Breakdown", cls="h6 fw-bold mb-3 text-dark"),
            P("Mastery labels: Not Started → Practising → Needs Review → Consistently Correct (≥80%, 5+ attempts)", cls="text-muted small mb-3"),
            *domain_progress_rows,
            cls="p-3",
        ),
        cls="mb-4",
    )

    # Quick action card
    actions_card = Card(
        Div(
            Row(
                Col(
                    A(
                        Button("Practice Questions", variant="primary", icon="check2-square", cls="w-100"),
                        href="/practice",
                        cls="text-decoration-none",
                    ),
                    span=12, md=4, cls="mb-2 mb-md-0",
                ),
                Col(
                    A(
                        Button("Study the Manual", variant="outline-primary", icon="journal-bookmark", cls="w-100"),
                        href="/learn",
                        cls="text-decoration-none",
                    ),
                    span=12, md=4, cls="mb-2 mb-md-0",
                ),
                Col(
                    A(
                        Button("Take Mock Exam", variant="outline-secondary", icon="stopwatch", cls="w-100"),
                        href="/mock",
                        cls="text-decoration-none",
                    ),
                    span=12, md=4,
                ),
            ),
            cls="p-3",
        ),
        cls="mb-4 bg-light border-0",
    )

    return [summary_card, breakdown_card, actions_card]
