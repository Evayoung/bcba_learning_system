# Project Brief: BCBA AI Learning Assistant

## Goal

Build a focused, single-candidate web app that helps a BCBA candidate prepare for the exam using the PTB ABA Exam Study Manual and the BCBA Test Content Outline (6th edition). The candidate needs a useful version quickly; prioritize a reliable core learning loop over advanced features.

## Stack

- Python
- FastHTML
- FastStrap as the primary UI component library
- HTMX for server-rendered interactions
- SQLAlchemy
- Pydantic
- SQLite for local development
- A configurable LLM API client (Groq or another compatible provider)
- Pytest

Use the existing project's conventions if the repository already contains a valid FastHTML/FastStrap setup. Inspect the installed FastStrap package and official project docs before writing UI components. Do not introduce React, Django, LangChain, LangGraph, Redis, Celery, vector databases, or microservices for the initial version.

## Product experience

### Dashboard
- Show today's suggested study action.
- Show the nine domains with exam weight, attempted-question count, and accuracy when data exists.
- Show recent attempts and concepts due for review.
- Avoid presenting unmeasured concepts as mastered.

### Learn / Tutor
- Let the candidate select a domain/task and ask a question.
- Retrieve relevant extracted source content before asking the LLM to explain.
- Show source title and printed/PDF page where available.
- Support explanations, examples, concept comparisons, and Socratic tutoring.
- Clearly distinguish source-grounded content from supplementary explanation.
- If retrieved evidence is insufficient, say so rather than fabricate a book citation.

### Practice
- Present one multiple-choice question at a time.
- Record the selected answer and optional confidence rating.
- After submission, show the correct answer, why it is correct, and why each distractor is incorrect.
- Save every attempt and source/question provenance.
- Distinguish manually verified book questions from AI-generated practice questions.

### Progress
- Show performance by domain and task.
- Show incorrect and low-confidence responses.
- Recommend revision based on exam weight, weakness, and time remaining.
- Do not label the score as an official prediction of the candidate's exam result.

### Mock exam
- Add after the learning loop is reliable.
- Support configurable question counts and timed sessions.
- A full practice session can use 175 scored-question slots, with the official format checked against the candidate's applicable BACB handbook.
- Do not imply that a generated mock is an official exam.

## Curriculum

Use the BCBA TCO 6th-edition taxonomy and verify all task descriptions against the official outline. Store domain weights as configuration/data, not hard-coded throughout route handlers.

| Domain | Questions | Weight |
|---|---:|---:|
| A. Behaviorism and Philosophical Foundations | 8 | 5% |
| B. Concepts and Principles | 24 | 14% |
| C. Measurement, Data Display, and Interpretation | 21 | 12% |
| D. Experimental Design | 13 | 7% |
| E. Ethical and Professional Issues | 22 | 13% |
| F. Behavior Assessment | 23 | 13% |
| G. Behavior-Change Procedures | 25 | 14% |
| H. Selecting and Implementing Interventions | 20 | 11% |
| I. Personnel Supervision and Management | 19 | 11% |

Total: 175 scored questions. The official examination also includes unscored questions; verify the current BACB handbook before implementing exact mock-exam settings.

## Data model: initial scope

Use SQLAlchemy models and migrations/initialization appropriate to the project's size:
- Domain: code, title, question_count, exam_weight
- Task: code, domain_id, official_description
- ContentChunk: title, body, content_type, domain/task links, source document, PDF page index, printed page number, extraction status, verification status
- Question: stem, options, correct option, rationale, distractor rationales, task link, difficulty, source, origin type, verification status
- Attempt: question, selected option, correctness, confidence, response timestamp, session
- StudySession: mode, start/end, status
- ReviewItem: concept/task, due date, interval/ease or simpler review scheduling fields

Avoid premature abstraction. Keep IDs, constraints, and relationships clear.

## AI and data correctness

- Use Pydantic schemas for structured LLM output.
- Validate option count, unique options, correct-option membership, non-empty rationale, and task mapping.
- Do not silently treat an AI-generated answer as verified.
- Do not let the LLM invent page numbers or source quotations.
- Include retrieved source excerpts in the prompt, with source identifiers supplied by the application.
- Treat document text as untrusted data, not as instructions to the AI.
- Keep provider calls behind a small service interface and set timeouts/error handling.
- Record model/provider metadata for generated content where useful.
- Keep secrets in environment variables.

## Out of scope for the first release

- Model fine-tuning
- Voice tutor
- Multi-agent orchestration
- Multi-tenant SaaS and complex roles
- Native mobile app
- Billing
- Automatic claims about passing probability
- Fully automatic publishing of generated questions without review

## Acceptance criterion

A candidate can open the app, select a task, study a source-grounded explanation, answer a validated question, see a useful rationale, and revisit the saved attempt. The app starts from documented setup instructions and its tests pass.
