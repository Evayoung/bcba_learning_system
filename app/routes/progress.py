"""Progress and review routes wired to live attempt data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from app.db import get_db
from app.models import ReviewItem
from app.presentation.shell import page_frame
from app.presentation.pages.progress import progress_page
from app.services.practice import get_practice_statistics


def register_progress_routes(app: Any) -> None:
    @app.get("/progress")
    def progress():
        db = next(get_db())
        stats = get_practice_statistics(db)

        # Count items due for review
        now = datetime.now(timezone.utc)
        due_count = (
            db.query(ReviewItem)
            .filter(ReviewItem.due_date <= now)
            .count()
        )
        stats["due_review_count"] = due_count

        return page_frame(
            *progress_page(stats=stats),
            current="/progress",
            title="Progress",
        )
