# Codex Tasks — Run One at a Time

**Instructions:** Give Codex the relevant task below, one at a time. After each task, inspect the diff and run tests. Do not ask Codex to continue to the next task automatically.

## Task 1 — Repository reconnaissance and foundation

Read `docs/PROJECT_BRIEF.md` and `docs/01_SETUP_AND_PROJECT_STRUCTURE.md`. Inspect the existing repository and FastStrap version/docs. Implement only the runnable application shell, configuration, database setup, navigation, placeholder routes, and smoke tests. Do not implement AI features yet. Run tests and report changed files, commands run, and remaining issues.

## Task 2 — Curriculum and database models

Read `docs/03_CURRICULUM_AND_CONTENT.md`. Implement the domain/task models and seed the nine domain records using the supplied counts/weights. Do not invent official task descriptions; provide an import path for a verified TCO source. Add ContentChunk, Question, Attempt, StudySession, and ReviewItem models with sensible relationships and constraints. Add tests and migrations/initialization. Keep the model scope minimal.

## Task 3 — PDF sample extraction tool

Read `docs/02_SCANNED_PDF_INGESTION.md`. Implement a separate CLI for extracting a selected page range from a scanned PDF using the chosen parser. Start with Marker if its installed version and CPU setup support the planned command. Do not process the full manual by default. Save raw output, per-page metadata, parser version, and a report. Add resume/error handling and instructions for using Colab if local CPU processing is too slow. Do not call an LLM for every page automatically.

## Task 4 — Content import and retrieval

Implement import of validated extraction outputs into ContentChunk records. Preserve PDF page index, printed page number when known, headings, source IDs, and verification status. Add simple keyword/full-text search and task filters. Do not add embeddings unless a test demonstrates that keyword search is inadequate.

## Task 5 — AI tutor

Read `docs/04_AI_TUTOR.md`. Add a provider adapter configured through environment variables. Implement explain, simplify, example, compare, and Socratic modes using retrieved source excerpts. Do not invent citations or claim that supplementary examples came from the manual. Add tests for provider failures and missing evidence. Use structured outputs where appropriate.

## Task 6 — Practice and question import

Read `docs/05_QUESTIONS_PRACTICE_PROGRESS.md`. Build the multiple-choice practice flow, answer submission, rationale display, attempt recording, and import of extracted review questions. Keep uncertain answer-key matches out of verified practice. Add tests for scoring, duplicate submissions, and option validation.

## Task 7 — Progress and revision

Implement domain/task accuracy, recent mistakes, confidence tracking, and a simple due-review queue. Use documented transparent rules rather than a complex mastery model. Add tests for calculations and review scheduling.

## Task 8 — Mock exam and release

Read `docs/06_MOCK_EXAM_AND_RELEASE.md`. Implement timed practice only after verified question selection, attempt persistence, and scoring work. Add final reliability/security checks, update README and environment example, run the full test suite, and document deployment requirements.

## Mandatory instruction for every task

Before coding, inspect existing code and current library APIs. Make the smallest coherent change. Do not silently replace unrelated code. Run the relevant tests. If an assumption is unverified, report it instead of inventing behavior. Finish by summarizing what works, what was tested, and the next task.
