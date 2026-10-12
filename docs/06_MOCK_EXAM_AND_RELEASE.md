# 06 — Mock Exam and Release

## Build only after the core loop works

Mock-exam requirements:
- configurable question count;
- optional time limit;
- saved answers and clear question navigation;
- submit confirmation;
- scoring after submission;
- post-exam review with rationales;
- results by domain and task;
- clear statement that it is practice, not an official BACB exam or a pass prediction.

Check the applicable BACB handbook before setting exact timing and question counts. The TCO domain counts represent scored-question distribution; do not claim the app reproduces the real exam exactly.

## Reliability and security checklist

- API keys only in environment variables.
- `.env` excluded from version control.
- Validate all submitted question/option IDs server-side.
- Do not trust client-provided correctness values.
- Avoid logging API keys or full sensitive provider payloads.
- Use safe file paths for uploads/ingestion.
- Limit uploaded PDF size if uploads are enabled.
- Keep OCR outside normal web requests.
- Handle provider errors and rate limits.
- Provide a clear fallback message when the tutor API is unavailable.
- Back up the SQLite database and processed content.
- Check the manual's terms before external processing or redistribution.

## Deployment

Choose the simplest deployment supported by the project and budget. Keep the app configurable through environment variables and ensure persistent storage for the database and extracted content. If the hosting provider has ephemeral disk, do not rely on local SQLite/files without a persistent volume or external database/storage.

## Release acceptance test

A new user can:
1. open the dashboard;
2. choose a task;
3. read relevant content with source-page information;
4. answer a verified question;
5. see a correct explanation;
6. view the saved attempt and domain performance;
7. return later and continue studying.

All automated tests pass, and setup instructions work from a clean environment.
