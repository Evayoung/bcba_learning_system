# 03 — Curriculum and Content

## Objective

Represent the BCBA TCO as structured data and connect extracted content to domains/tasks. Do not attempt to automatically map every paragraph perfectly in the first iteration.

## Curriculum setup

- Add the nine domain records and their exam weighting.
- Add task records from a verified copy of the official 6th-edition TCO.
- Keep the official task code and exact official task description.
- Add indexes for task code, domain, content type, and source page.
- Keep the source manual and the official TCO as distinct source types.

## Content chunking

Create chunks at meaningful boundaries:
- heading/section
- definition or callout
- one concept explanation
- example or comparison
- table/figure description
- question and its options
- answer-key/rationale material

Avoid fixed-size splitting that separates a question from its options or separates a definition from its explanation.

Each chunk should preserve:
- document ID/title
- PDF page index
- printed page number if known
- section heading
- domain/task mapping if verified
- extraction status
- verification status
- raw extraction reference/path

## Search

Start with simple PostgreSQL full-text search or SQLite FTS if available and appropriate. A basic keyword search is enough for the first working version. Add embeddings only if testing shows that lexical search fails to retrieve relevant content.

## Retrieval rules

- Retrieve a small set of relevant chunks for the selected task/query.
- Pass those excerpts to the tutor.
- Show citations based only on metadata supplied by the application.
- Do not allow the LLM to make up page numbers or source references.
- If no useful source is found, label the answer as general supplementary explanation and avoid claiming it came from the manual.

## Acceptance checks

- A task can be selected and its linked content retrieved.
- Every extracted chunk has provenance.
- Unverified content is visible to the admin/developer for checking and is not treated as verified by default.
