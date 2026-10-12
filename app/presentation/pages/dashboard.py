"""Dashboard presentation components for the BCBA Assistant.

FastStrap mode: Hybrid — polished KPI summary + dense domain grid.
Uses: StatCard, MetricCard, PageHeader, Card, Badge, BadgeGroup,
      StatusBadge, Button, Row, Col, ProgressBar, Icon, EmptyState.
"""

from __future__ import annotations

from fasthtml.common import A, Div, H2, H3, H4, P, Span
from faststrap import (
    Badge, BadgeGroup, Button, Card, Col, Icon,
    MetricCard, PageHeader, ProgressBar, Row, StatCard, StatusBadge,
)

# Official 6th Edition BCBA Domains (static reference)
DOMAINS = [
    {"code": "A", "title": "Behaviorism and Philosophical Foundations",   "questions": 8,  "weight": 5},
    {"code": "B", "title": "Concepts and Principles",                     "questions": 24, "weight": 14},
    {"code": "C", "title": "Measurement, Data Display, and Interpretation","questions": 21, "weight": 12},
    {"code": "D", "title": "Experimental Design",                         "questions": 13, "weight": 7},
    {"code": "E", "title": "Ethical and Professional Issues",             "questions": 22, "weight": 13},
    {"code": "F", "title": "Behavior Assessment",                         "questions": 23, "weight": 13},
    {"code": "G", "title": "Behavior-Change Procedures",                  "questions": 25, "weight": 14},
    {"code": "H", "title": "Selecting and Implementing Interventions",    "questions": 20, "weight": 11},
    {"code": "I", "title": "Personnel Supervision and Management",        "questions": 19, "weight": 11},
]


def study_action_banner() -> Card:
    """Prominent today's recommended action banner with CTAs."""
    return Card(
        Div(
            PageHeader(
                title="Domain B: Concepts and Principles",
                eyebrow="Today's Recommended Study Focus",
                subtitle=(
                    "Domain B carries the highest exam weight (14% / 24 scored items). "
                    "Review reinforcement schedules, stimulus control, and extinction."
                ),
                actions=Div(
                    A(
                        Button("Start Concept Tutor", variant="primary", icon="book"),
                        href="/learn?domain=B",
                        cls="text-decoration-none",
                    ),
                    A(
                        Button("Practice Questions", variant="outline-primary", icon="check2-square"),
                        href="/practice?domain=B",
                        cls="text-decoration-none",
                    ),
                    cls="d-flex flex-wrap gap-2",
                ),
            ),
            cls="p-3",
        ),
        cls="mb-4 shadow-sm border-start border-primary border-4",
    )


def kpi_cards() -> Row:
    """Top-level stat cards using FastStrap StatCard component."""
    return Row(
        Col(
            StatCard("Scored Exam Items", "175", icon=Icon("file-earmark-check-fill"), trend_type="neutral"),
            span=12, sm=6, lg=3,
        ),
        Col(
            StatCard("TCO Domains", "9", icon=Icon("grid-3x3-gap-fill"), trend_type="neutral"),
            span=12, sm=6, lg=3,
        ),
        Col(
            StatCard("Manual Pages", "400", icon=Icon("journal-text"), trend_type="neutral"),
            span=12, sm=6, lg=3,
        ),
        Col(
            StatCard("Content Chunks (RAG)", "512", icon=Icon("lightning-charge-fill"), trend="Indexed", trend_type="up"),
            span=12, sm=6, lg=3,
        ),
        cls="mb-4 g-3",
    )


def domain_grid(db_domains: list | None = None) -> Div:
    """9 BCBA domains with exam weight, task count, progress bar, and study actions."""
    domains_list = []

    if db_domains is not None:
        domains_list = [
            {
                "code": d.code,
                "title": d.title,
                "questions": d.question_count,
                "weight": d.exam_weight,
                "tasks_count": len(d.tasks) if hasattr(d, "tasks") and d.tasks else 0,
            }
            for d in db_domains
        ]
    else:
        try:
            from sqlalchemy.orm import joinedload
            from app.db import SessionLocal
            from app.models import Domain
            db = SessionLocal()
            try:
                results = db.query(Domain).options(joinedload(Domain.tasks)).order_by(Domain.code).all()
                for d in results:
                    domains_list.append({
                        "code": d.code,
                        "title": d.title,
                        "questions": d.question_count,
                        "weight": d.exam_weight,
                        "tasks_count": len(d.tasks),
                    })
            finally:
                db.close()
        except Exception:
            domains_list = DOMAINS

    if not domains_list:
        domains_list = DOMAINS

    # Weight → bar variant mapping
    def _bar_variant(weight: int) -> str:
        if weight >= 14:
            return "primary"
        if weight >= 12:
            return "info"
        if weight >= 10:
            return "success"
        return "secondary"

    cols = []
    for d in domains_list:
        tasks_text = f" • {d['tasks_count']} Tasks" if d.get("tasks_count") else ""
        bar_v = _bar_variant(d["weight"])
        card = Card(
            Div(
                Div(
                    Div(d["code"], cls="domain-pill me-3"),
                    Div(
                        H4(d["title"], cls="h6 fw-bold mb-1 text-dark lh-sm"),
                        BadgeGroup(
                            Badge(f"{d['weight']}% weight", variant=bar_v, pill=True),
                            Badge(f"{d['questions']} items", variant="secondary", pill=True),
                        ),
                    ),
                    cls="d-flex align-items-start mb-3",
                ),
                Div(
                    ProgressBar(d["weight"] * (100 // 14), variant=bar_v, height="4px"),
                    Span(f"Exam weight: {d['weight']}%{tasks_text}", cls="text-muted small mt-1 d-block"),
                    cls="mb-3",
                ),
                A(
                    "Study Domain →",
                    href=f"/learn?domain={d['code']}",
                    cls="small fw-semibold text-primary text-decoration-none",
                ),
                cls="p-3",
            ),
            cls="h-100 card-hover",
        )
        cols.append(Col(card, span=12, md=6, lg=4, cls="mb-3"))

    return Div(
        Div(
            H3("Exam Domains — 6th Edition TCO", cls="h5 fw-bold mb-1"),
            P(
                "Nine domains covering 175 scored multiple-choice items and 104 verified task competencies.",
                cls="text-muted small mb-3",
            ),
            cls="mb-2",
        ),
        Row(*cols, cls="g-3"),
    )


def dashboard_page() -> list:
    """Composite dashboard view: action banner → KPI stats → domain grid."""
    return [
        study_action_banner(),
        kpi_cards(),
        domain_grid(),
    ]
