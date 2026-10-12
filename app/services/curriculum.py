"""Curriculum seed data and seeding service for BCBA TCO 6th Edition."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models import Domain, Task

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TCO_SEED_FILE = BASE_DIR / "data" / "processed" / "tco_6th_edition_tasks.json"

# Official BACB 6th Edition Domains with question counts and percentage weights
DOMAINS_SEED_DATA = [
    {
        "code": "A",
        "title": "Behaviorism and Philosophical Foundations",
        "question_count": 8,
        "exam_weight": 5,
    },
    {
        "code": "B",
        "title": "Concepts and Principles",
        "question_count": 24,
        "exam_weight": 14,
    },
    {
        "code": "C",
        "title": "Measurement, Data Display, and Interpretation",
        "question_count": 21,
        "exam_weight": 12,
    },
    {
        "code": "D",
        "title": "Experimental Design",
        "question_count": 13,
        "exam_weight": 7,
    },
    {
        "code": "E",
        "title": "Ethical and Professional Issues",
        "question_count": 22,
        "exam_weight": 13,
    },
    {
        "code": "F",
        "title": "Behavior Assessment",
        "question_count": 23,
        "exam_weight": 13,
    },
    {
        "code": "G",
        "title": "Behavior-Change Procedures",
        "question_count": 25,
        "exam_weight": 14,
    },
    {
        "code": "H",
        "title": "Selecting and Implementing Interventions",
        "question_count": 20,
        "exam_weight": 11,
    },
    {
        "code": "I",
        "title": "Personnel Supervision and Management",
        "question_count": 19,
        "exam_weight": 11,
    },
]


def load_tco_tasks() -> List[Dict[str, Any]]:
    """Load verified TCO task records from the seed file."""
    if not TCO_SEED_FILE.exists():
        raise FileNotFoundError(f"TCO seed file not found at {TCO_SEED_FILE}")
    with open(TCO_SEED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_curriculum(db: Session) -> Dict[str, int]:
    """Seed Domain and Task records into the database idempotently.
    
    Returns count of domains and tasks seeded.
    """
    domain_map: Dict[str, Domain] = {}
    domains_created = 0
    tasks_created = 0

    # 1. Seed or retrieve domains
    for d_data in DOMAINS_SEED_DATA:
        domain = db.query(Domain).filter(Domain.code == d_data["code"]).first()
        if not domain:
            domain = Domain(
                code=d_data["code"],
                title=d_data["title"],
                question_count=d_data["question_count"],
                exam_weight=d_data["exam_weight"],
            )
            db.add(domain)
            db.flush()
            domains_created += 1
        else:
            # Update weights/counts if needed
            domain.title = d_data["title"]
            domain.question_count = d_data["question_count"]
            domain.exam_weight = d_data["exam_weight"]
        domain_map[d_data["code"]] = domain

    # 2. Seed verified tasks
    tco_tasks = load_tco_tasks()
    for t_data in tco_tasks:
        domain = domain_map.get(t_data["domain_code"])
        if not domain:
            continue
        task = db.query(Task).filter(Task.code == t_data["code"]).first()
        if not task:
            task = Task(
                code=t_data["code"],
                domain_id=domain.id,
                official_description=t_data["description"],
            )
            db.add(task)
            tasks_created += 1
        else:
            task.official_description = t_data["description"]
            task.domain_id = domain.id

    db.commit()
    return {"domains_seeded": domains_created, "tasks_seeded": tasks_created}
