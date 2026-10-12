"""Shared responsive layout shell for BCBA AI Learning Assistant.

Follows FastStrap standards and adopts the proven production shell structure from sj_admin:
- Fixed desktop sidebar (.app-sidebar) positioned at viewport top-left
- Non-scrolling sidebar when content is short; auto overflow with thin scrollbar only when needed
- Offset main layout (.app-main) that scrolls independently
"""

from __future__ import annotations

from fasthtml.common import (
    A, Aside, Div, Footer, H1, Main, Nav, P, Small, Span,
)
from faststrap import (
    BottomNav, BottomNavItem, Container, Drawer, Icon,
    SidebarNavbar, SidebarNavItem,
)
from faststrap.components.feedback.modern_toast import ModernToastStack, ToastPlacement

NAV_ITEMS = (
    ("Dashboard", "/", "grid"),
    ("Learn / Tutor", "/learn", "book"),
    ("Practice", "/practice", "check2-square"),
    ("Progress", "/progress", "graph-up"),
    ("Mock Exam", "/mock", "stopwatch"),
    ("Settings / AI", "/settings", "gear"),
)

PAGE_SUBTITLES = {
    "/": "Track your exam readiness, review weighted domains, and follow today's study plan.",
    "/learn": "Explore verified concepts from the PTB Study Manual with source citations and AI guidance.",
    "/practice": "Test your mastery with active recall, rationale explanations, and distractor analysis.",
    "/progress": "Inspect domain-by-domain accuracy, review queue status, and identify learning gaps.",
    "/mock": "Full-length and domain-focused timed practice sessions aligned with the 6th Edition TCO.",
    "/settings": "Configure Google Gemini, Groq, or OpenRouter API keys and adjust active models.",
}


def app_logo() -> Span:
    """Branded BCBA logo badge."""
    return Span(
        Span("BCBA", cls="app-brand-badge"),
        Div(
            Span("Study Assistant", cls="app-brand-title"),
            Span("6th Edition TCO", cls="app-brand-subtitle"),
            cls="d-flex flex-column",
        ),
        cls="d-flex align-items-center gap-2",
    )


def app_sidebar(current: str = "/") -> Aside:
    """Desktop fixed sidebar — modeled after sj_admin production architecture."""
    nav_links = [
        A(
            Icon(icon, cls="me-2 fs-6"),
            Span(label),
            href=href,
            cls=f"app-nav-link {'active' if href == current else ''}",
        )
        for label, href, icon in NAV_ITEMS
    ]

    return Aside(
        Div(
            A(
                app_logo(),
                href="/",
                cls="app-brand text-decoration-none",
            ),
            Div(
                Span("Navigation", cls="app-sidebar-kicker"),
                Nav(*nav_links, cls="d-flex flex-column gap-1"),
                cls="mb-3",
            ),
            Div(
                Div(
                    Div(
                        Span("Exam Outline", cls="fw-bold d-block text-white mb-1"),
                        Span("BACB 6th Edition • 175 Scored Qs", cls="d-block text-muted small"),
                        Span("PTB Manual 400p Ingested", cls="d-block text-info small mt-1"),
                        cls="app-exam-pill mb-2",
                    ),
                    A(
                        Icon("box-arrow-right", cls="me-2"),
                        "Sign Out",
                        href="/logout",
                        cls="btn btn-outline-light btn-sm w-100 text-decoration-none d-flex align-items-center justify-content-center",
                    ),
                    cls="app-sidebar-panel",
                ),
                cls="mt-auto",
            ),
            cls="app-sidebar-inner",
        ),
        cls="app-sidebar d-none d-lg-flex",
    )


def app_mobile_header(current: str = "/", title: str = "Dashboard") -> Div:
    """Top navigation bar for mobile / tablet viewports."""
    return Div(
        Container(
            Div(
                A(app_logo(), href="/", cls="text-decoration-none"),
                Span(title, cls="fw-bold text-dark"),
                cls="app-mobile-header-row",
            ),
        ),
        cls="app-mobile-header d-lg-none",
    )


def app_bottom_nav(current: str = "/") -> Div:
    """Bottom navigation bar for mobile devices."""
    return BottomNav(
        *[
            BottomNavItem(
                label,
                href=href,
                icon=icon,
                active=(href == current),
                cls="admin-bottom-link",
            )
            for label, href, icon in NAV_ITEMS[:4]
        ],
        A(
            Icon("list", size="1.25em", cls="mb-1"),
            Small("Menu", cls="d-block"),
            href="#",
            data_bs_toggle="offcanvas",
            data_bs_target="#appMobileDrawer",
            aria_label="Open navigation drawer",
            cls="nav-link d-flex flex-column align-items-center justify-content-center w-100 flex-grow-1 py-2 text-decoration-none text-muted",
        ),
        variant="light",
        cls="app-bottom-nav d-lg-none",
        id="app-bottom-nav",
    )


def app_mobile_drawer(current: str = "/") -> Div:
    """Offcanvas navigation drawer for mobile devices."""
    links = [
        A(
            Icon(icon, cls="me-2 text-primary"),
            Span(label),
            href=href,
            cls=f"d-flex align-items-center p-2 rounded text-decoration-none {'bg-light fw-bold text-primary' if href == current else 'text-dark'}",
        )
        for label, href, icon in NAV_ITEMS
    ]

    return Drawer(
        Div(
            P("Study Workspaces", cls="text-muted small fw-bold text-uppercase mb-3"),
            Div(*links, cls="d-flex flex-column gap-2"),
            Div(
                A(
                    Icon("box-arrow-right", cls="me-2 text-danger"),
                    Span("Sign Out", cls="text-danger fw-semibold"),
                    href="/logout",
                    cls="d-flex align-items-center p-2 rounded text-decoration-none bg-light",
                ),
                Span("BACB 6th Edition TCO • 175 Questions", cls="text-muted small d-block mt-3"),
                cls="mt-4 pt-3 border-top",
            ),
        ),
        drawer_id="appMobileDrawer",
        title="Navigation",
        placement="start",
        cls="app-mobile-drawer d-lg-none",
    )


def page_frame(
    *children,
    current: str = "/",
    title: str = "Dashboard",
    subtitle: str | None = None,
):
    """Full-page responsive layout wrapper."""
    effective_subtitle = subtitle or PAGE_SUBTITLES.get(
        current, "Prepare for the BCBA Exam with evidence-grounded active learning."
    )

    return (
        app_mobile_header(current, title),
        Div(
            app_sidebar(current),
            Main(
                Div(
                    Container(
                        Div(
                            P("BCBA Exam Preparation", cls="app-kicker"),
                            H1(title, cls="app-page-title"),
                            P(effective_subtitle, cls="app-page-copy"),
                            cls="app-page-header",
                        ),
                        *children,
                        cls="app-shell",
                    ),
                    Footer(
                        Container(
                            Div(
                                Span("BCBA Study Assistant • 6th Edition TCO", cls="small text-muted"),
                                Span("·", cls="mx-2 text-muted"),
                                Span("PTB Manual Grounded", cls="small text-muted"),
                                cls="d-flex align-items-center justify-content-center",
                            ),
                        ),
                        cls="app-footer",
                    ),
                    cls="app-content-wrap",
                ),
                cls="app-main",
            ),
            cls="app-layout",
        ),
        app_bottom_nav(current),
        app_mobile_drawer(current),
        ModernToastStack(placement=ToastPlacement("top-end"), gap=2, id="toast-container"),
        Div(cls="app-loading-bar", id="app-loading-bar"),
    )
