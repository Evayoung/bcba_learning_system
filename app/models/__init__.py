"""SQLAlchemy ORM models for the BCBA Assistant.

Minimal scope conforming to docs/00_PROJECT_BRIEF.md & docs/03_CURRICULUM_AND_CONTENT.md:
- Domain
- Task
- ContentChunk
- Question
- Attempt
- StudySession
- ReviewItem
"""

from __future__ import annotations

import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db import Base


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class Domain(Base):
    """The 9 BCBA Test Content Outline (TCO) Domains."""

    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(5), unique=True, nullable=False, index=True)  # e.g., 'A', 'B'
    title = Column(String(255), nullable=False)
    question_count = Column(Integer, nullable=False, default=0)
    exam_weight = Column(Integer, nullable=False, default=0)  # percentage, e.g. 14 for 14%

    tasks = relationship("Task", back_populates="domain", cascade="all, delete-orphan")
    chunks = relationship("ContentChunk", back_populates="domain")

    def __repr__(self) -> str:
        return f"<Domain {self.code}: {self.title}>"


class Task(Base):
    """Specific task items within a domain (e.g., A.1, B.4)."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # e.g., 'A.1', 'B.4'
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False, index=True)
    official_description = Column(Text, nullable=False)

    domain = relationship("Domain", back_populates="tasks")
    chunks = relationship("ContentChunk", back_populates="task")
    questions = relationship("Question", back_populates="task")
    review_items = relationship("ReviewItem", back_populates="task")

    def __repr__(self) -> str:
        return f"<Task {self.code}>"


class ContentChunk(Base):
    """Extracted study manual passages, definitions, and review sections."""

    __tablename__ = "content_chunks"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)

    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    content_type = Column(String(50), default="prose", index=True)  # prose, definition, table, question, rationale

    source_document = Column(String(255), default="PTB ABA Exam Study Manual 6th Edition")
    pdf_page_index = Column(Integer, nullable=True, index=True)  # 0-indexed
    printed_page_number = Column(Integer, nullable=True, index=True)  # printed on page footer
    section_heading = Column(String(255), nullable=True)
    raw_reference = Column(String(255), nullable=True)  # e.g. data/processed/pages_clean/page_0004.md

    extraction_status = Column(String(50), default="extracted")  # extracted, normalized, flagged
    verification_status = Column(String(50), default="unverified", index=True)  # unverified, verified, rejected

    created_at = Column(DateTime, default=_utc_now)

    domain = relationship("Domain", back_populates="chunks")
    task = relationship("Task", back_populates="chunks")

    __table_args__ = (
        Index("ix_chunks_domain_task", "domain_id", "task_id"),
        Index("ix_chunks_page", "pdf_page_index", "printed_page_number"),
    )

    def __repr__(self) -> str:
        return f"<ContentChunk id={self.id} page={self.printed_page_number} type={self.content_type}>"


class Question(Base):
    """Multiple-choice practice items."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)

    stem = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON-encoded list of strings or dicts
    correct_option = Column(String(10), nullable=False)  # e.g. "A", "B", "C", "D"

    rationale = Column(Text, nullable=True)
    distractor_rationales = Column(Text, nullable=True)  # JSON-encoded dict: {"A": "...", ...}

    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    source = Column(String(255), default="PTB Study Manual Review Questions")
    origin_type = Column(String(50), default="extracted")  # extracted, generated, custom
    verification_status = Column(String(50), default="unverified", index=True)  # unverified, verified

    created_at = Column(DateTime, default=_utc_now)

    task = relationship("Task", back_populates="questions")
    attempts = relationship("Attempt", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Question id={self.id} task_id={self.task_id}>"


class StudySession(Base):
    """A timed or untimed study / practice session."""

    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String(50), default="practice")  # practice, tutor, mock
    started_at = Column(DateTime, default=_utc_now)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")  # active, completed, abandoned

    attempts = relationship("Attempt", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StudySession id={self.id} mode={self.mode} status={self.status}>"


class Attempt(Base):
    """Candidate's response attempt for a question."""

    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=True, index=True)

    selected_option = Column(String(10), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    confidence = Column(String(20), nullable=True)  # low, medium, high
    response_time_seconds = Column(Float, nullable=True)
    answered_at = Column(DateTime, default=_utc_now, index=True)

    question = relationship("Question", back_populates="attempts")
    session = relationship("StudySession", back_populates="attempts")

    def __repr__(self) -> str:
        return f"<Attempt id={self.id} q={self.question_id} correct={self.is_correct}>"


class ReviewItem(Base):
    """Spaced repetition item for revision queues."""

    __tablename__ = "review_items"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    concept_name = Column(String(255), nullable=True)

    due_date = Column(DateTime, default=_utc_now, index=True)
    interval_days = Column(Integer, default=1)
    consecutive_correct = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime, nullable=True)

    task = relationship("Task", back_populates="review_items")

    def __repr__(self) -> str:
        return f"<ReviewItem id={self.id} task_id={self.task_id} due={self.due_date}>"


class User(Base):
    """Candidate user account with password hash."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=_utc_now)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
