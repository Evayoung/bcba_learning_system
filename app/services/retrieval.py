"""Retrieval service for RAG.

Provides keyword, full-text search (SQLite FTS5), and task/domain filtering over ContentChunk records.
Returns ranked, citation-rich source excerpts for the AI Tutor and practice interfaces.
"""

from __future__ import annotations

import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import ContentChunk, Domain, Task


class RetrievalResult:
    """A single retrieved excerpt with full provenance metadata."""

    def __init__(
        self,
        chunk_id: int,
        title: str,
        body: str,
        printed_page_number: Optional[int],
        pdf_page_index: Optional[int],
        section_heading: Optional[str],
        domain_code: Optional[str],
        domain_title: Optional[str],
        task_code: Optional[str],
        task_description: Optional[str],
        content_type: str,
        verification_status: str,
        score: float = 0.0,
    ):
        self.chunk_id = chunk_id
        self.title = title
        self.body = body
        self.printed_page_number = printed_page_number
        self.pdf_page_index = pdf_page_index
        self.section_heading = section_heading
        self.domain_code = domain_code
        self.domain_title = domain_title
        self.task_code = task_code
        self.task_description = task_description
        self.content_type = content_type
        self.verification_status = verification_status
        self.score = score

    @property
    def citation_label(self) -> str:
        """Formatted human-readable citation."""
        page_str = f"Page {self.printed_page_number}" if self.printed_page_number else f"PDF p. {self.pdf_page_index + 1 if self.pdf_page_index is not None else '?'}"
        task_str = f"Task {self.task_code}" if self.task_code else (f"Domain {self.domain_code}" if self.domain_code else "PTB Manual")
        return f"PTB ABA Study Manual • {page_str} ({task_str})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "title": self.title,
            "body": self.body,
            "printed_page_number": self.printed_page_number,
            "pdf_page_index": self.pdf_page_index,
            "section_heading": self.section_heading,
            "domain_code": self.domain_code,
            "domain_title": self.domain_title,
            "task_code": self.task_code,
            "task_description": self.task_description,
            "content_type": self.content_type,
            "verification_status": self.verification_status,
            "citation": self.citation_label,
            "score": self.score,
        }


def _clean_fts_query(query: str) -> str:
    """Sanitize user input query for SQLite FTS5 MATCH syntax."""
    # Remove FTS operators that could cause syntax errors
    cleaned = re.sub(r'[*"\'^:()\-+]', ' ', query)
    tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
    if not tokens:
        return ""
    # Join with OR or NEAR for relaxed matching
    return " OR ".join(f'"{t}"*' for t in tokens)


def retrieve_content(
    db: Session,
    query: Optional[str] = None,
    task_code: Optional[str] = None,
    domain_code: Optional[str] = None,
    limit: int = 5,
    content_types: Optional[List[str]] = None,
) -> List[RetrievalResult]:
    """Retrieve relevant ContentChunk records using SQLite FTS5 and metadata filters.
    
    Order of preference:
    1. If task_code is supplied, prioritize chunks mapped to that exact task.
    2. If query is supplied, match using SQLite FTS5 bm25 ranking.
    3. If neither, return top domain/task chunks.
    """
    results: List[RetrievalResult] = []

    # 1. Exact Task lookup
    if task_code and not query:
        task = db.query(Task).filter(Task.code == task_code).first()
        if task:
            chunks = (
                db.query(ContentChunk)
                .filter(ContentChunk.task_id == task.id)
                .order_by(ContentChunk.printed_page_number.asc())
                .limit(limit)
                .all()
            )
            for c in chunks:
                results.append(
                    RetrievalResult(
                        chunk_id=c.id,
                        title=c.title or "",
                        body=c.body,
                        printed_page_number=c.printed_page_number,
                        pdf_page_index=c.pdf_page_index,
                        section_heading=c.section_heading,
                        domain_code=task.domain.code if task.domain else None,
                        domain_title=task.domain.title if task.domain else None,
                        task_code=task.code,
                        task_description=task.official_description,
                        content_type=c.content_type or "prose",
                        verification_status=c.verification_status or "unverified",
                        score=1.0,
                    )
                )
            if results:
                return results

    # 2. SQLite FTS5 Query
    if query:
        fts_match = _clean_fts_query(query)
        if fts_match:
            sql = """
            SELECT
                c.id,
                c.title,
                c.body,
                c.printed_page_number,
                c.pdf_page_index,
                c.section_heading,
                c.content_type,
                c.verification_status,
                d.code as domain_code,
                d.title as domain_title,
                t.code as task_code,
                t.official_description as task_description,
                bm25(content_chunks_fts) as rank
            FROM content_chunks_fts fts
            JOIN content_chunks c ON fts.rowid = c.id
            LEFT JOIN domains d ON c.domain_id = d.id
            LEFT JOIN tasks t ON c.task_id = t.id
            WHERE content_chunks_fts MATCH :match_query
            """
            params: Dict[str, Any] = {"match_query": fts_match, "limit": limit}

            if domain_code and domain_code != "all":
                sql += " AND (d.code = :domain_code OR fts.domain_code = :domain_code)"
                params["domain_code"] = domain_code

            if task_code:
                sql += " AND (t.code = :task_code OR fts.task_code = :task_code)"
                params["task_code"] = task_code

            sql += " ORDER BY rank ASC LIMIT :limit"

            try:
                rows = db.execute(text(sql), params).fetchall()
                for r in rows:
                    results.append(
                        RetrievalResult(
                            chunk_id=r.id,
                            title=r.title or "",
                            body=r.body,
                            printed_page_number=r.printed_page_number,
                            pdf_page_index=r.pdf_page_index,
                            section_heading=r.section_heading,
                            domain_code=r.domain_code,
                            domain_title=r.domain_title,
                            task_code=r.task_code,
                            task_description=r.task_description,
                            content_type=r.content_type or "prose",
                            verification_status=r.verification_status or "unverified",
                            score=float(r.rank) if r.rank is not None else 0.0,
                        )
                    )
            except Exception:
                # Fallback to standard LIKE if FTS fails for any reason
                pass

    # 3. Fallback to SQL LIKE if FTS returned nothing
    if not results and (query or domain_code or task_code):
        q = db.query(ContentChunk)
        if domain_code and domain_code != "all":
            domain = db.query(Domain).filter(Domain.code == domain_code).first()
            if domain:
                q = q.filter(ContentChunk.domain_id == domain.id)
        if task_code:
            task = db.query(Task).filter(Task.code == task_code).first()
            if task:
                q = q.filter(ContentChunk.task_id == task.id)
        if query:
            q = q.filter(ContentChunk.body.ilike(f"%{query}%"))

        chunks = q.order_by(ContentChunk.printed_page_number.asc()).limit(limit).all()
        for c in chunks:
            results.append(
                RetrievalResult(
                    chunk_id=c.id,
                    title=c.title or "",
                    body=c.body,
                    printed_page_number=c.printed_page_number,
                    pdf_page_index=c.pdf_page_index,
                    section_heading=c.section_heading,
                    domain_code=c.domain.code if c.domain else None,
                    domain_title=c.domain.title if c.domain else None,
                    task_code=c.task.code if c.task else None,
                    task_description=c.task.official_description if c.task else None,
                    content_type=c.content_type or "prose",
                    verification_status=c.verification_status or "unverified",
                    score=0.5,
                )
            )

    return results
