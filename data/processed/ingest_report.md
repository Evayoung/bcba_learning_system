# PTB ingestion quality report

- source pages: 400
- transcribed: 400 (100.0%)
- missing: 0 []
- blank pages (from image analysis): [107, 108, 109, 240, 241, 245]

## Printed page mapping

- pages with a printed number: 393
- pages without a printed number: 7 (numbered inserts + blanks) [29, 107, 108, 109, 240, 241, 245]
- offset drift: min=2 max=76 spread=74
- non-monotonic entries: none

Printed != PDF index and the offset is not constant, so the printed number must be
carried per chunk from OCR; never computed from the PDF index.

## Content types

- prose: 290
- review_questions: 25
- list: 20
- answer_key: 17
- table: 16
- quick_guide: 8
- blank_page: 7
- domain_divider: 6
- diagram: 6
- other: 4
- copyright_page: 1

## Domain tags found in page headers

- domains: {'A': 11, 'B': 75, 'C': 41, 'D': 38, 'E': 33, 'F': 45, 'G': 71, 'H': 26, 'I': 30}
- distinct task codes seen: 101 ['A.1', 'A.2', 'A.3', 'A.4', 'A.5', 'B.1', 'B.10', 'B.11', 'B.12', 'B.13', 'B.14', 'B.16', 'B.17', 'B.18'] ...

## Review queue

- flagged needs_review by the model: 15 [29, 33, 56, 69, 93, 99, 209, 290, 304, 107, 108, 109, 240, 241, 245]
- contains [unclear] markers: 0 []
- confidence < 0.8: 0 []
- very short transcripts (0-120 chars): [(23, 75), (97, 73), (107, 12), (108, 12), (109, 12), (240, 12), (241, 12), (245, 12)]

## Engines used

- gemini/gemini-3.1-flash-lite: 205 pages
- gemini/gemini-flash-lite-latest: 128 pages
- openai/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free: 35 pages
- gemini/gemini-3.7-flash: 19 pages
- gemini/gemini-3.6-flash: 6 pages
- None/None: 6 pages
- rapidocr-onnxruntime/rapidocr-onnxruntime: 1 pages

## Size

- transcript characters: min=12 median=2097 max=3289 total=783354

Status: this file is the original machine-ingestion baseline. Its status predates
the completed human review of flagged pages and the project owner's confirmation
that available transcripts match the scanned source. See
`source_quality_manifest.json` and `docs/08_EXTRACTION_QA.md` for current
source-fidelity status and the four missing question pages.
