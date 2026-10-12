# 05 — Questions, Practice, and Progress

## Objective

Deliver a trustworthy practice loop before building advanced adaptive features.

## Question record

Each question should include:
- stem
- exactly four options when matching the intended BCBA-style format
- correct option identifier
- rationale for the correct answer
- rationale for each distractor when available
- domain/task mapping
- difficulty (optional and clearly heuristic)
- source type: manual, human-authored, or AI-generated
- source page/reference when applicable
- verification status
- creation/model metadata for AI-generated content

Validate with Pydantic and database constraints. Ensure the correct option exists among the options and option IDs are unique.

## Import existing review questions

- Extract questions separately from explanations.
- Keep question numbers and source pages.
- Parse the answer key as a separate step.
- Match question number and answer key only when unambiguous.
- Flag uncertain matches for manual review.
- Never infer a missing answer from model confidence.
- Preserve the original extracted text for auditing.

## Practice flow

1. Candidate selects domain/task and number of questions.
2. Server selects eligible verified questions.
3. Candidate submits an option and optional confidence (e.g. 1–5).
4. Save the attempt.
5. Show correctness, rationale, and distractor explanations.
6. Offer a targeted follow-up question.
7. Update domain/task statistics.

Do not expose the answer before submission in practice mode.

## AI-generated questions

- Mark generated questions as `unverified` by default.
- Validate schema and check that only one answer is defensibly best.
- Require a rationale for the correct answer and distractors.
- Verify alignment to the task and supplied source material.
- Do not mix unverified questions into scored progress or exam simulations unless the candidate explicitly chooses an experimental practice mode.
- Human review is preferred before calling a question verified.

## Progress calculations

Start simple:
- domain accuracy = correct eligible attempts / eligible answered attempts;
- task accuracy = same calculation grouped by task;
- track total attempts and recent attempts separately;
- show confidence alongside accuracy where collected;
- flag repeated incorrect answers and low-confidence correct answers.

Do not label a topic mastered based on one correct response. Use transparent labels such as `Not started`, `Practising`, `Needs review`, and `Consistently correct`, with simple documented thresholds.

## Spaced repetition

Use a simple schedule initially:
- wrong or low-confidence answer: review soon;
- correct but low-confidence: review in a short interval;
- correct and confident: increase interval gradually;
- update due date after each review.

Make intervals configurable; don't present them as a scientifically validated prediction.

## Acceptance checks

- Attempt is saved exactly once per submission.
- Repeated refreshes do not accidentally double-submit.
- Scoring is deterministic and tested.
- Progress ignores invalid/unverified question keys.
- Candidate can review past incorrect answers.
