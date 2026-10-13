"""Progress and review routes wired to live attempt data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from app.db import get_db
from app.models import ReviewItem, Task, Domain
from app.presentation.shell import page_frame
from app.presentation.pages.progress import progress_page
from app.services.practice import get_practice_statistics, repair_legacy_review_dates


def register_progress_routes(app: Any) -> None:
    @app.get("/progress")
    def progress():
        db = next(get_db())
        repair_legacy_review_dates(db)
        stats = get_practice_statistics(db)

        # Count items due for review
        now = datetime.now(timezone.utc)
        due_query = db.query(ReviewItem, Task, Domain).join(
            Task, ReviewItem.task_id == Task.id
        ).join(Domain, Task.domain_id == Domain.id).filter(
            ReviewItem.due_date <= now
        ).order_by(ReviewItem.due_date.asc())
        due_rows = due_query.all()
        stats["due_reviews"] = [{
            "task_code": task.code,
            "domain_code": domain.code,
            "description": task.official_description,
            "due_date": item.due_date,
            "interval_days": item.interval_days,
        } for item, task, domain in due_rows[:8]]
        due_count = len(due_rows)
        stats["due_review_count"] = due_count

        return page_frame(
            *progress_page(stats=stats),
            current="/progress",
            title="Progress",
        )
