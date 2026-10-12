# 08 — Extraction QA (sampling and verification)

Doc 02 requires OCR output to be inspected against the original page images
before it is trusted. This is the record of that check, run on the completed
400-page transcription.

## Method

Two independent signals, so a single engine's confidence score is not the only
evidence:

1. **Cross-engine agreement.** `scripts/cross_check.py` compares each vision
   transcript with the RapidOCR baseline (`scripts/ocr_local.py`) produced by a
   completely different engine. Comparison is order-insensitive (bag of words,
   `SequenceMatcher(..., autojunk=False)`) because the two engines order
   two-column pages differently, which is exactly the failure mode we want to
   detect rather than reward.
2. **Manual visual inspection.** Page images were read next to their
   transcripts for the page types most likely to fail: dense tables, diagrams,
   callout boxes, review questions, answer keys, and every page the model
   itself flagged.

## Pages inspected manually

| PDF page | printed | type | engine | result |
|---|---:|---|---|---|
| 61 | 84 | two-column + table | gemini-3.6-flash | 6-row table exact, caption kept |
| 84 | 109 | two-column + `[THINK]` callouts | flash-lite-latest | column order correct, all callouts kept |
| 151 | 185 | numbered definitions | 3.1-flash-lite | numbering and order correct |
| 211 | 259 | callout + funnel diagram | flash-lite-latest | funnel order and captions correct |
| 204 | 250 | review questions | — | task codes (E.3, E.7 …) and blanks kept |
| 398 | 474 | answer key | — | question-numbered answers kept |
| 33 | 50 | callout "Breakdown" boxes | nemotron | content exact (1 artifact, fixed) |
| 4 | 11 | quick-guide prose | nemotron | content exact |

## Cross-engine agreement

13 of 14 comparable pages scored 0.71–0.96 bag-of-words similarity against the
independent engine (`data/processed/cross_check.json`). The single low score
(page 137, 0.29) is the *local* engine failing on a near-blank page (86
characters extracted against the vision model's 214); the vision transcript is
the better one there.

## Issues found, and what was done

| Issue | Extent | Action |
|---|---|---|
| LaTeX emitted instead of printed symbols (`\neq`, `\cdot`, `\frac`) | 3 pages (33, 128, 284) | symbol repair in `clean_transcripts.py`, re-run |
| Mojibake / smart quotes / spacing noise | 0 in raw data; console display only | normalisation pass still runs |
| Placeholder transcript `<the markdown string>` | 2 pages (44, 89) | detected by validation, re-transcribed |
| Vision models returned empty output | 1 page (29, ABC-chart graphic) | local RapidOCR fallback, `needs_review` |
| Blank pages | 6 (107, 108, 109, 240, 241, 245) | recorded as `blank_page` from image analysis, no API spent |
| Near-empty pages (header only, "my Notes" page) | 4 | correctly reported as near-blank with header/footer text |
| Printed page number unreadable | 0 of 393 non-blank pages | all read from footers; monotonic, no gaps |

## Verdict

The transcription is **usable for content retrieval**: reading order, tables,
callouts, headings, task codes and page numbers all survived, and an
independent engine agrees on content for 13/14 sampled pages.

It remains **unverified as a source of truth**. Everything still has to be read
against the page image before it becomes curriculum or an answer key, and the
15 pages flagged `needs_review` (plus the 1 RapidOCR page) need that pass
first.

## Review queue (from `data/processed/ingest_report.json`)

`needs_review`: 29, 33, 56, 69, 93, 99, 209, 290, 304 and the 6 blank inserts.
No page contains `[unclear]` markers and no page has confidence below 0.8.

## Human review pass (complete)

Every flagged page was re-read against its page image and corrected. Ten pages
needed changes; six blanks were confirmed. Corpus-wide scans now show **zero
`<unk>` runs, zero literal `\n` sequences, zero placeholder transcripts and zero
repeating-digit degeneration** across all 400 pages.

| PDF page | Defect found | Fix |
|---|---|---|
| 29 | RapidOCR fallback: fragmented, wrong order, ABC charts flattened | retranscribed from the image |
| 33 | LaTeX `\neq`, Breakdown callouts flattened | symbol + callouts restored |
| 56 | graphic as `![Owl](unclear)`, `$S^D$` math | graphic described, notation `S^D`/`S^Δ` |
| 69 | 116 `<unk>` tokens, everything after them lost | retranscribed from the image |
| 93 | (none — verified correct) | task codes and 2x8 matching verified |
| 99 | model degenerated into `3.14159…`, whole Topographical section lost | restored from the image |
| 209 | 17 literal `\n`, column merge, `E.11` misread as `E.II` | all three fixed |
| 290 | `S^d` misread as "SPs" | notation fixed |
| 304 | 101 `<unk>` tokens, pro/con table and procedure list lost | retranscribed from the image |
| 325 | 15 literal `\n`, icon as a star glyph | fixed, icon labelled |
| 107, 108, 109, 240, 241, 245 | flagged blank | confirmed blank on the image |

Each corrected page keeps the engine output in `engine_transcript` and records
`qa_status: human_reviewed`, `qa_reviewer` and `qa_notes`.

## Review questions and answer keys

Parsed by `scripts/parse_questions.py` into `data/processed/questions_draft.json`.
Questions and keys live on separate pages, so each side is parsed on its own and
then matched strictly by (domain, question number) — never by position, and never
by inference.

- 235 questions parsed, 280 key entries, **230 matched pairs**.
- Types: 190 fill-in-the-blank, 19 true/false, 14 matching, 12 short answer.
- All 14 matching questions have a complete answer map (`1: B, G` style), and 11
  also have item/option pairs where the transcript allowed them.
- Every entry carries question and answer page provenance (pdf + printed page).

### The source scan is missing four pages

Fifty questions have a keyed answer but no question text, because the pages that
carried them are **not in the scanned PDF**:

| Domain | Missing question numbers | Printed page absent |
|---|---|---|
| B | 25–37 | 121 |
| E | 20–32 | 249 |
| F | 1–12 | 301 |
| G | 1–12 | 379 |

These are reported as `answer_only` with the gap documented in `source_gaps`;
the missing text is not reconstructed. Domain E also has questions 36–40 with no
answer in the key (the E key ends at 35).

### Status

Question text and answers are machine-parsed and human-reviewed where
indicated, but the set is **not verified curriculum**. Nothing here should be
presented to a learner as a verified question until the pairs are checked
against the pages named in each entry's provenance.
