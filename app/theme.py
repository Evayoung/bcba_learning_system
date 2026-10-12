"""Theme and component styling defaults for BCBA AI Learning Assistant."""

from __future__ import annotations

from faststrap import create_theme, set_component_defaults

# Palette optimized for a focused, accessible learning interface
BRAND_COLORS = {
    "primary": "#1E3A8A",      # Deep Academic Navy
    "secondary": "#D97706",    # Warm Amber
    "accent": "#3B82F6",       # Cobalt Blue
    "success": "#059669",      # Emerald Green
    "info": "#0284C7",         # Sky Blue
    "warning": "#D97706",      # Amber
    "danger": "#DC2626",       # Crimson Red
    "light": "#F8FAFC",        # Crisp Slate
    "dark": "#0F172A",         # Deep Slate
}

BCBA_THEME = create_theme(
    primary=BRAND_COLORS["primary"],
    secondary=BRAND_COLORS["secondary"],
    success=BRAND_COLORS["success"],
    info=BRAND_COLORS["info"],
    warning=BRAND_COLORS["warning"],
    danger=BRAND_COLORS["danger"],
    light=BRAND_COLORS["light"],
    dark=BRAND_COLORS["dark"],
)


def setup_theme_defaults() -> None:
    """Apply global FastStrap component defaults."""
    set_component_defaults("Button", variant="primary", size="md")
    set_component_defaults("Card", cls="border-0 shadow-sm")
    set_component_defaults("Badge", pill=True)
    set_component_defaults("Input", size="md")
    set_component_defaults("Alert", dismissible=True)
