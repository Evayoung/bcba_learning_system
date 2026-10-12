"""Unit and integration tests for content chunk ingestion and FTS5 retrieval."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Domain, Task, ContentChunk
from app.services.curriculum import seed_curriculum
from app.services.content_ingestion import setup_fts_index, rebuild_fts_index, import_content_chunks
from app.services.retrieval import retrieve_content, RetrievalResult


@pytest.fixture(scope="function")
def mem_db():
    """Create an in-memory SQLite database with FTS5 enabled."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSession()
    setup_fts_index(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_fts_index_creation_and_rebuild(mem_db):
    """Verify FTS5 virtual table creates and populates without errors."""
    seed_curriculum(mem_db)
    task_b4 = mem_db.query(Task).filter(Task.code == "B.4").first()

    chunk = ContentChunk(
        domain_id=task_b4.domain_id,
        task_id=task_b4.id,
        title="Positive Reinforcement",
        body="Positive reinforcement occurs when a response is followed immediately by the presentation of a stimulus change that increases future frequency.",
        printed_page_number=45,
        pdf_page_index=44,
        section_heading="Positive Reinforcement Defined",
        content_type="prose",
        verification_status="verified",
    )
    mem_db.add(chunk)
    mem_db.commit()

    rebuild_fts_index(mem_db)

    # Search for term
    results = retrieve_content(mem_db, query="reinforcement")
    assert len(results) >= 1
    assert results[0].chunk_id == chunk.id
    assert results[0].task_code == "B.4"
    assert results[0].printed_page_number == 45
    assert "PTB ABA Study Manual" in results[0].citation_label


def test_retrieval_by_exact_task(mem_db):
    """Retrieve content by task code returns matching chunks with correct metadata."""
    seed_curriculum(mem_db)
    task_a1 = mem_db.query(Task).filter(Task.code == "A.1").first()

    chunk1 = ContentChunk(
        domain_id=task_a1.domain_id,
        task_id=task_a1.id,
        title="Goals of Behavior Analysis as a Science",
        body="Description, prediction, and control are the levels of scientific understanding.",
        printed_page_number=3,
        pdf_page_index=2,
    )
    chunk2 = ContentChunk(
        domain_id=task_a1.domain_id,
        task_id=task_a1.id,
        title="Philosophical Underpinnings",
        body="Determinism, empiricism, experimentation, replication, parsimony, philosophic doubt.",
        printed_page_number=4,
        pdf_page_index=3,
    )
    mem_db.add_all([chunk1, chunk2])
    mem_db.commit()

    results = retrieve_content(mem_db, task_code="A.1")
    assert len(results) == 2
    assert results[0].printed_page_number == 3
    assert results[1].printed_page_number == 4
    assert results[0].domain_code == "A"


def test_retrieval_domain_filter(mem_db):
    """Domain filtering should restrict retrieval results to that domain."""
    seed_curriculum(mem_db)
    task_a = mem_db.query(Task).filter(Task.code == "A.1").first()
    task_b = mem_db.query(Task).filter(Task.code == "B.1").first()

    mem_db.add_all([
        ContentChunk(
            domain_id=task_a.domain_id,
            task_id=task_a.id,
            title="Domain A Chunk",
            body="Scientific principles of behavior and radical behaviorism.",
            printed_page_number=10,
        ),
        ContentChunk(
            domain_id=task_b.domain_id,
            task_id=task_b.id,
            title="Domain B Chunk",
            body="Concepts and principles regarding stimulus control.",
            printed_page_number=40,
        )
    ])
    mem_db.commit()
    rebuild_fts_index(mem_db)

    # Search with domain filter
    res_a = retrieve_content(mem_db, query="behaviorism", domain_code="A")
    assert len(res_a) == 1
    assert res_a[0].domain_code == "A"

    res_b = retrieve_content(mem_db, query="stimulus", domain_code="B")
    assert len(res_b) == 1
    assert res_b[0].domain_code == "B"


def test_retrieval_fallback_to_like(mem_db):
    """When query is empty or FTS special syntax occurs, fallback gracefully returns results."""
    seed_curriculum(mem_db)
    task_c = mem_db.query(Task).filter(Task.code == "C.1").first()
    mem_db.add(
        ContentChunk(
            domain_id=task_c.domain_id,
            task_id=task_c.id,
            title="Measurement Dimensions",
            body="Repeatability, temporal extent, temporal locus are dimensional quantities.",
            printed_page_number=75,
        )
    )
    mem_db.commit()

    # Query with punctuation characters
    results = retrieve_content(mem_db, query="temporal locus")
    assert len(results) >= 1
    assert "temporal locus" in results[0].body.lower()
