"""Learn / Tutor presentation components with live source retrieval, citations, and AI chat."""

from __future__ import annotations

from typing import List, Optional, Any
from fasthtml.common import Div, H3, H4, P, Span, Form, A, Textarea, Small
from faststrap import Badge, Button, Card, Col, Icon, Input, Markdown, Row, Select
from app.services.retrieval import RetrievalResult


def render_retrieval_card(res: RetrievalResult) -> Any:
    """Render a single retrieved source chunk with provenance badges."""
    clean_body = res.body[:600] + ("..." if len(res.body) > 600 else "")

    badges = [
        Badge(res.citation_label, variant="primary", cls="me-1 mb-1"),
    ]
    if res.task_code:
        badges.append(Badge(f"Task {res.task_code}", variant="info", cls="me-1 mb-1"))
    if res.domain_code:
        badges.append(Badge(f"Domain {res.domain_code}", variant="secondary", cls="me-1 mb-1"))
    if res.verification_status == "flagged":
        badges.append(Badge("Flagged for Review", variant="warning", cls="me-1 mb-1"))

    return Card(
        Div(
            Div(
                H4(res.title or res.section_heading or "Source Excerpt", cls="h6 fw-bold mb-1 text-primary"),
                Div(*badges, cls="d-flex flex-wrap align-items-center mb-2"),
                cls="d-flex flex-column",
            ),
            P(clean_body, cls="text-dark small mb-2", style="white-space: pre-wrap; line-height: 1.5;"),
            Div(
                Span(f"Score: {res.score:.2f}", cls="text-muted small"),
                Span(f"PDF p. {res.pdf_page_index + 1}" if res.pdf_page_index is not None else "", cls="text-muted small ms-2"),
                cls="d-flex justify-content-between align-items-center border-top pt-2",
            ),
            cls="p-3",
        ),
        cls="mb-3 border-start border-4 border-primary shadow-sm",
    )


def render_tutor_response_box(
    user_prompt: str,
    tutor_text: str,
    mode: str,
    task_code: Optional[str] = None,
    error: Optional[str] = None,
) -> Any:
    """Render the AI Tutor explanation box with strict provenance badge."""
    if error:
        is_quota_or_key = "429" in error or "quota" in error.lower() or "api key" in error.lower() or "unauthorized" in error.lower()
        return Card(
            Div(
                Div(
                    Icon("exclamation-triangle-fill", size="1.5rem", cls="text-warning me-2"),
                    H4("AI Tutor Response Notice", cls="h6 fw-bold mb-0 text-dark"),
                    cls="d-flex align-items-center mb-2",
                ),
                P(error, cls="small text-danger mb-3"),
                Div(
                    A(
                        Button("Update API Key in Settings →", variant="outline-primary", size="sm", icon="gear-fill"),
                        href="/settings",
                        cls="text-decoration-none",
                    ),
                    Span("You can easily paste a new Gemini or Groq key without restarting the app.", cls="text-muted small ms-2") if is_quota_or_key else None,
                    cls="d-flex align-items-center flex-wrap gap-2 pt-2 border-top",
                ) if is_quota_or_key else None,
                cls="p-3",
            ),
            cls="border-warning bg-light mb-4",
            id="tutor-output",
        )

    mode_labels = {
        "explain": "Comprehensive Explanation",
        "simplify": "Plain English / Layman",
        "example": "Applied Behavior Example",
        "compare": "Contrast vs Confusable Term",
        "socratic": "Socratic Guiding Question",
    }
    mode_label = mode_labels.get(mode, mode.capitalize())

    return Card(
        Div(
            Div(
                Div(
                    Icon("robot", size="1.4rem", cls="text-primary me-2"),
                    H4(f"AI Tutor — {mode_label}", cls="h6 fw-bold mb-0 text-primary"),
                    cls="d-flex align-items-center",
                ),
                Div(
                    Badge(f"Mode: {mode.upper()}", variant="primary", cls="me-1"),
                    Badge(f"Task: {task_code}" if task_code else "TCO Curriculum", variant="info", cls="me-1"),
                    Badge("Manual Grounded", variant="success"),
                    cls="d-flex flex-wrap align-items-center gap-1",
                ),
                cls="d-flex justify-content-between align-items-center flex-wrap gap-2 pb-2 mb-3 border-bottom",
            ),
            Div(
                Span(f'Prompt: "{user_prompt}"', cls="small text-muted fw-bold d-block mb-3 fst-italic"),
                Div(
                    Markdown(tutor_text) if tutor_text else P("No response text generated.", cls="text-muted small"),
                    cls="tutor-markdown-body mb-3",
                ),
                Small(
                    "Disclaimer: AI tutoring assistance is designed strictly for academic BACB exam prep. "
                    "Manual citations reference the PTB ABA Exam Study Manual 6th Edition.",
                    cls="text-muted d-block border-top pt-2",
                ),
            ),
            cls="p-3",
        ),
        cls="mb-4 border-start border-4 border-success shadow-sm bg-white",
        id="tutor-output",
    )


def learn_page(
    selected_domain: str | None = None,
    query: str | None = None,
    task_code: str | None = None,
    selected_mode: str = "explain",
    retrieved_results: list[RetrievalResult] | None = None,
    tutor_response: Optional[dict] = None,
) -> list:
    """Learn workspace view with interactive AI Tutor question form and manual excerpts."""
    modes = [
        ("explain", "Comprehensive"),
        ("simplify", "Plain English"),
        ("example", "Applied Example"),
        ("compare", "Compare Terms"),
        ("socratic", "Socratic Question"),
    ]

    domain_options = [
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

    selected_val = selected_domain if selected_domain in dict(domain_options) else "all"

    # Fetch task list for domain if selected
    task_items = []
    if selected_val != "all":
        try:
            from app.db import SessionLocal
            from app.models import Domain, Task
            db = SessionLocal()
            try:
                dom = db.query(Domain).filter(Domain.code == selected_val).first()
                if dom:
                    tasks = db.query(Task).filter(Task.domain_id == dom.id).order_by(Task.code).all()
                    for t in tasks:
                        is_active = (task_code == t.code)
                        task_items.append(
                            A(
                                Div(
                                    Badge(t.code, variant="primary" if is_active else "outline-primary", cls="me-2"),
                                    Span(t.official_description, cls="text-dark small"),
                                    cls="d-flex align-items-baseline",
                                ),
                                href=f"/learn?domain={selected_val}&task={t.code}",
                                cls=f"p-2 border-bottom text-decoration-none d-block {'bg-light rounded' if is_active else ''}",
                            )
                        )
            finally:
                db.close()
        except Exception:
            pass

    tasks_card = Card(
        Div(
            H4(f"Domain {selected_val} Task Competencies (Click to View Manual Excerpt)", cls="h6 fw-bold mb-3 text-primary"),
            Div(*task_items, cls="d-flex flex-column gap-1", style="max-height: 280px; overflow-y: auto;"),
            cls="p-3",
        ),
        cls="mb-4",
    ) if task_items else None

    # Search & Filter Controls
    controls_card = Card(
        Div(
            Form(
                Row(
                    Col(
                        Select("domain", *domain_options, label="Select Domain", selected=selected_val, cls="mb-2"),
                        span=12, md=5,
                    ),
                    Col(
                        Input("query", value=query or "", placeholder="Search keyword (e.g. reinforcement, extinction, IOA)...", label="Search Manual Concept", cls="mb-2"),
                        span=12, md=5,
                    ),
                    Col(
                        Button("Search", variant="primary", type="submit", cls="w-100 mt-md-4 mb-2"),
                        span=12, md=2,
                    ),
                ),
                method="get",
                action="/learn",
            ),
            cls="p-3",
        ),
        cls="mb-4",
    )

    # Interactive AI Tutor Query Box
    prompt_placeholder = f"Ask AI Tutor about {task_code or 'this topic'} (e.g. 'Can you explain the difference between negative reinforcement and punishment?')..."
    ai_tutor_card = Card(
        Div(
            Div(
                Div(
                    Icon("mortarboard-fill", size="1.3rem", cls="text-primary me-2"),
                    H4("Ask the AI Tutor", cls="h6 fw-bold mb-0 text-primary"),
                    cls="d-flex align-items-center",
                ),
                Span("Grounded in PTB 6th Edition Manual Excerpts", cls="text-muted small"),
                cls="d-flex justify-content-between align-items-center mb-3",
            ),
            Form(
                # Hidden inputs preserving current task and domain
                Input("task_code", value=task_code or "", type="hidden"),
                Input("domain_code", value=selected_val, type="hidden"),
                Div(
                    Span("Tutor Mode:", cls="small fw-bold text-muted me-2"),
                    Div(
                        *[
                            Button(
                                label,
                                variant="primary" if mode_val == selected_mode else "outline-primary",
                                size="sm",
                                name="mode",
                                value=mode_val,
                                type="submit",
                                cls="me-1 mb-1",
                                data_loading_text="Applying tutor mode...",
                            )
                            for mode_val, label in modes
                        ],
                        cls="d-inline-flex flex-wrap gap-1 mb-2",
                    ),
                ),
                Row(
                    Col(
                        Input(
                            "prompt",
                            placeholder=prompt_placeholder,
                            value="",
                            cls="mb-2",
                        ),
                        span=12, md=10,
                    ),
                    Col(
                        Button("Ask Tutor", variant="success", type="submit", cls="w-100 mb-2", data_loading_text="Searching the manual and asking AI..."),
                        span=12, md=2,
                    ),
                ),
                method="post",
                action="/learn/ask",
                data_loading_text="Searching the manual and asking AI...",
            ),
            cls="p-3",
        ),
        cls="mb-4 shadow-sm",
    )

    items = [controls_card]
    if tasks_card:
        items.append(tasks_card)

    items.append(ai_tutor_card)

    # If an AI tutor response exists, display it prominently
    if tutor_response:
        items.append(
            render_tutor_response_box(
                user_prompt=tutor_response.get("prompt", ""),
                tutor_text=tutor_response.get("content", ""),
                mode=tutor_response.get("mode", selected_mode),
                task_code=tutor_response.get("task_code"),
                error=tutor_response.get("error"),
            )
        )

    # Render retrieval results or manual overview
    if retrieved_results:
        results_header = Div(
            H3(f"Found {len(retrieved_results)} Source Excerpts from PTB Manual", cls="h5 fw-bold mb-3 text-primary"),
            cls="mb-2",
        )
        rendered_cards = [render_retrieval_card(r) for r in retrieved_results]
        items.append(Div(results_header, *rendered_cards, cls="mb-4"))
    elif query or task_code:
        no_res = Card(
            Div(
                Icon("search", size="2rem", cls="text-muted mb-2"),
                H4("No exact excerpts found", cls="h6 fw-bold text-muted"),
                P("Try adjusting your keyword query or selecting another domain task.", cls="small text-muted mb-0"),
                cls="d-flex flex-column align-items-center text-center p-4",
            ),
            cls="mb-4",
        )
        items.append(no_res)
    else:
        overview_card = Card(
            Div(
                Div(
                    Icon("journal-bookmark", size="2.5rem", cls="text-primary mb-3"),
                    H3("512 Semantic Chunks Indexed with SQLite FTS5", cls="h5 fw-bold mb-2"),
                    P(
                        "All 400 pages of the PTB 6th Edition Study Manual are indexed with full-text search, "
                        "task code mappings, and printed page numbers. Search above or click any task to review the exact source text.",
                        cls="text-muted small mb-3",
                        style="max-width: 600px;",
                    ),
                    Div(
                        Badge("512 Chunks Active", variant="success", cls="me-2"),
                        Badge("104 Tasks Mapped", variant="info", cls="me-2"),
                        Badge("FTS5 BM25 Ranked", variant="secondary"),
                        cls="mb-3",
                    ),
                    cls="d-flex flex-column align-items-center text-center p-4",
                ),
                cls="p-2",
            ),
            cls="bg-white",
        )
        items.append(overview_card)

    return items
