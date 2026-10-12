"""Content ingestion and chunking service.

Reads validated markdown pages from data/processed/pages_clean/ and metadata from
data/processed/pages/, decomposes text at meaningful heading/conceptual boundaries,
and seeds ContentChunk records with domain/task mappings and page provenance.
"""

from __future__ import annotations

import glob
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Domain, Task, ContentChunk

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PAGES_CLEAN_DIR = BASE_DIR / "data" / "processed" / "pages_clean"
PAGES_META_DIR = BASE_DIR / "data" / "processed" / "pages"
SEED_JSON_PATH = BASE_DIR / "data" / "processed" / "seed_content_chunks.json"


def extract_task_codes(text_snippet: str, header_tag: Optional[str] = None) -> List[str]:
    """Extract all task codes (e.g. ['B.4'], ['A.1', 'A.2']) from text and header tags."""
    found: set[str] = set()
    pat = re.compile(r'\b([A-I]\.\d+)\b')

    if header_tag:
        for m in pat.findall(header_tag):
            found.add(m)

    # Check top few lines of text
    lines = text_snippet.splitlines()[:10]
    for line in lines:
        for m in pat.findall(line):
            found.add(m)

    return sorted(list(found))


def parse_page_chunks(page_num: int, md_text: str, meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Decompose page markdown into meaningful semantic chunks preserving metadata."""
    tr = meta.get("transcript", {})
    printed_page = tr.get("printed_page_number")
    header_tag = tr.get("header_domain_tag")
    content_type = tr.get("content_type", "prose")
    needs_review = tr.get("needs_review", False)
    verification_status = "flagged" if needs_review else "unverified"

    clean_text = md_text.strip()
    if not clean_text:
        return []

    # Split page at major markdown headers (# or ## or ###)
    sections = re.split(r'\n(?=#{1,3}\s+)', clean_text)
    chunks_data = []

    for idx, sec in enumerate(sections):
        sec = sec.strip()
        if not sec:
            continue

        lines = sec.splitlines()
        first_line = lines[0].strip()
        # Clean title from markdown header syntax
        heading = re.sub(r'^#+\s*', '', first_line).strip()[:200]
        if not heading:
            heading = f"Page {printed_page or page_num} Section {idx + 1}"

        # Detect domain and task codes from header or section
        sec_tasks = extract_task_codes(sec, header_tag)
        primary_task = sec_tasks[0] if sec_tasks else None

        domain_code = None
        if header_tag and "Domain" in header_tag:
            m_dom = re.search(r'Domain\s+([A-I])', header_tag, re.IGNORECASE)
            if m_dom:
                domain_code = m_dom.group(1).upper()
        elif primary_task:
            domain_code = primary_task.split(".")[0]

        chunks_data.append({
            "title": heading,
            "body": sec,
            "content_type": content_type,
            "source_document": "PTB ABA Exam Study Manual 6th Edition",
            "pdf_page_index": page_num - 1,
            "printed_page_number": printed_page,
            "section_heading": heading,
            "raw_reference": f"data/processed/pages_clean/page_{page_num:04d}.md",
            "extraction_status": "normalized",
            "verification_status": verification_status,
            "domain_code": domain_code,
            "task_code": primary_task,
        })

    return chunks_data


def setup_fts_index(db: Session) -> None:
    """Create or update SQLite FTS5 index for fast full-text search."""
    # Ensure SQLite FTS5 table exists as standalone table
    create_fts_sql = """
    CREATE VIRTUAL TABLE IF NOT EXISTS content_chunks_fts USING fts5(
        title,
        body,
        section_heading,
        task_code,
        domain_code,
        tokenize='unicode61'
    );
    """
    db.execute(text(create_fts_sql))

    # Create synchronization triggers
    trigger_insert = """
    CREATE TRIGGER IF NOT EXISTS content_chunks_ai AFTER INSERT ON content_chunks BEGIN
        INSERT INTO content_chunks_fts(rowid, title, body, section_heading, task_code, domain_code)
        VALUES (
            new.id,
            coalesce(new.title, ''),
            new.body,
            coalesce(new.section_heading, ''),
            (SELECT code FROM tasks WHERE id = new.task_id),
            (SELECT code FROM domains WHERE id = new.domain_id)
        );
    END;
    """

    trigger_delete = """
    CREATE TRIGGER IF NOT EXISTS content_chunks_ad AFTER DELETE ON content_chunks BEGIN
        DELETE FROM content_chunks_fts WHERE rowid = old.id;
    END;
    """

    trigger_update = """
    CREATE TRIGGER IF NOT EXISTS content_chunks_au AFTER UPDATE ON content_chunks BEGIN
        DELETE FROM content_chunks_fts WHERE rowid = old.id;
        INSERT INTO content_chunks_fts(rowid, title, body, section_heading, task_code, domain_code)
        VALUES (
            new.id,
            coalesce(new.title, ''),
            new.body,
            coalesce(new.section_heading, ''),
            (SELECT code FROM tasks WHERE id = new.task_id),
            (SELECT code FROM domains WHERE id = new.domain_id)
        );
    END;
    """

    db.execute(text(trigger_insert))
    db.execute(text(trigger_delete))
    db.execute(text(trigger_update))
    db.commit()


def rebuild_fts_index(db: Session) -> None:
    """Rebuild the FTS5 search index from scratch."""
    db.execute(text("DELETE FROM content_chunks_fts;"))
    populate_sql = """
    INSERT INTO content_chunks_fts(rowid, title, body, section_heading, task_code, domain_code)
    SELECT
        c.id,
        coalesce(c.title, ''),
        c.body,
        coalesce(c.section_heading, ''),
        coalesce(t.code, ''),
        coalesce(d.code, '')
    FROM content_chunks c
    LEFT JOIN tasks t ON c.task_id = t.id
    LEFT JOIN domains d ON c.domain_id = d.id;
    """
    db.execute(text(populate_sql))
    db.commit()


def _import_from_seed_json(db: Session, domains: Dict, tasks: Dict) -> Dict[str, int]:
    """Load ContentChunks from the pre-exported seed JSON file.

    Used by cloud/CI deployments where data/processed/pages_clean/ is absent.
    The seed file is data/processed/seed_content_chunks.json.
    """
    with open(SEED_JSON_PATH, "r", encoding="utf-8") as f:
        seed_data: List[Dict[str, Any]] = json.load(f)

    imported_count = 0
    for c_data in seed_data:
        domain_obj = domains.get(c_data.get("domain_code", ""))
        task_obj = tasks.get(c_data.get("task_code", ""))
        if task_obj and not domain_obj:
            domain_obj = task_obj.domain

        chunk = ContentChunk(
            domain_id=domain_obj.id if domain_obj else None,
            task_id=task_obj.id if task_obj else None,
            title=c_data.get("title"),
            body=c_data.get("body", ""),
            content_type=c_data.get("content_type", "prose"),
            source_document=c_data.get("source_document", "PTB ABA Exam Study Manual"),
            pdf_page_index=c_data.get("pdf_page_index"),
            printed_page_number=c_data.get("printed_page_number"),
            section_heading=c_data.get("section_heading"),
            raw_reference=c_data.get("raw_reference"),
            extraction_status=c_data.get("extraction_status", "exported"),
            verification_status=c_data.get("verification_status", "unverified"),
        )
        db.add(chunk)
        imported_count += 1

    db.commit()
    rebuild_fts_index(db)
    return {"chunks_imported": imported_count, "total_chunks": db.query(ContentChunk).count()}


def import_content_chunks(db: Session, force: bool = False) -> Dict[str, int]:
    """Import content chunks into the database.

    Primary path (local dev): reads validated markdown pages from
    data/processed/pages_clean/ + JSON metadata from data/processed/pages/.

    Cloud/deployment fallback: when pages_clean/ is absent, reads directly from
    data/processed/seed_content_chunks.json (committed to the repo).

    Idempotent by default unless force=True.
    """
    setup_fts_index(db)

    existing_count = db.query(ContentChunk).count()
    if existing_count > 0 and not force:
        return {"chunks_imported": 0, "total_chunks": existing_count}

    if force:
        db.query(ContentChunk).delete()
        db.commit()

    # Pre-load domains and tasks for quick lookups
    domains = {d.code: d for d in db.query(Domain).all()}
    tasks = {t.code: t for t in db.query(Task).all()}

    # ------------------------------------------------------------------ #
    # CLOUD / DEPLOYMENT FALLBACK: load from pre-exported seed JSON       #
    # ------------------------------------------------------------------ #
    md_files = sorted(glob.glob(str(PAGES_CLEAN_DIR / "page_*.md")))
    if not md_files and SEED_JSON_PATH.exists():
        return _import_from_seed_json(db, domains, tasks)

    imported_count = 0

    for md_path in md_files:
        filename = os.path.basename(md_path)
        m = re.search(r'page_(\d+)\.md', filename)
        if not m:
            continue
        page_num = int(m.group(1))

        json_path = PAGES_META_DIR / f"page_{page_num:04d}.json"
        meta: Dict[str, Any] = {}
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    meta = json.load(f)
                except Exception:
                    pass

        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        parsed_chunks = parse_page_chunks(page_num, md_text, meta)
        for c_data in parsed_chunks:
            domain_obj = domains.get(c_data["domain_code"]) if c_data.get("domain_code") else None
            task_obj = tasks.get(c_data["task_code"]) if c_data.get("task_code") else None

            # Fallback: if task is matched, use task's domain
            if task_obj and not domain_obj:
                domain_obj = task_obj.domain

            chunk = ContentChunk(
                domain_id=domain_obj.id if domain_obj else None,
                task_id=task_obj.id if task_obj else None,
                title=c_data["title"],
                body=c_data["body"],
                content_type=c_data["content_type"],
                source_document=c_data["source_document"],
                pdf_page_index=c_data["pdf_page_index"],
                printed_page_number=c_data["printed_page_number"],
                section_heading=c_data["section_heading"],
                raw_reference=c_data["raw_reference"],
                extraction_status=c_data["extraction_status"],
                verification_status=c_data["verification_status"],
            )
            db.add(chunk)
            imported_count += 1

    db.commit()
    rebuild_fts_index(db)

    return {"chunks_imported": imported_count, "total_chunks": db.query(ContentChunk).count()}
