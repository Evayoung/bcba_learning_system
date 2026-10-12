# 02 — Scanned PDF Ingestion: Practical Plan

## Objective

Extract the scanned PTB ABA Exam Study Manual into source-linked content that the tutor can retrieve. OCR quality must be checked before content is trusted.

## Important recommendation

Do not use a vision LLM API as the only OCR engine for all pages by default. A scanned book can contain hundreds of pages; one image request per page can be slow, consume API limits, and still misread tables or answer keys.

Use a document OCR/parser for bulk extraction, then use a vision-capable LLM selectively to re-check difficult pages or turn validated text into structured records.

### Preferred execution order

1. Keep the original PDF unchanged and never overwrite it.
2. Create a manifest with file name, page count, file size, extraction date, tool version, and output location.
3. Choose 12–20 representative pages: normal text, dense definitions, diagrams, tables, review questions, and answer-key pages.
4. Test Marker on the sample. On the 16 GB CPU laptop, use a small page range and one worker; expect CPU processing to be slower.
5. If local processing is impractical, use Google Colab for the one-off batch job. Colab resource availability is variable, so save progress and outputs to persistent storage regularly.
6. Inspect the output against the original page images.
7. If extraction is poor, test PaddleOCR/PP-Structure on the same sample rather than installing multiple stacks immediately.
8. Use a Groq vision model only on selected low-confidence pages, if the current Groq account/model supports image inputs. Check the current official model list and rate limits before implementation.
9. Store extracted Markdown/JSON plus page-level metadata. Do not discard raw outputs.
10. Import only validated chunks/questions into the app.

## Do not build the full OCR workflow into the web request

Create a CLI command/script, for example:

```bash
python -m scripts.ingest_manual --input data/source/manual.pdf --output data/processed/
```

Long-running OCR should not block a FastHTML request. The initial script can be synchronous and resumable; no queue infrastructure is necessary.

## Suggested page-level output metadata

```json
{
  "document_id": "ptb_aba_manual",
  "pdf_page_index": 30,
  "printed_page_number": 31,
  "parser": "marker",
  "parser_version": "record-the-installed-version",
  "extraction_status": "needs_review",
  "markdown_path": "pages/page_0031.md"
}
```

Use real values at runtime. Do not invent printed page numbers; leave them null when they cannot be read.

## Quality checks

For each sample page:
- Is the heading correct?
- Are columns in the right order?
- Are all options attached to the correct question?
- Are symbols, abbreviations, and negations preserved?
- Are table cells aligned correctly?
- Is the answer key mapped to the correct question?
- Can we locate the original PDF page from the extracted content?

Mark pages/questions `needs_review` when uncertain. Never silently repair a questionable answer key with an LLM guess.

## Using Groq or another vision API

A vision LLM can be useful for a few difficult page images, but:
- confirm that the selected model accepts image inputs;
- check current rate limits, context limits, pricing, and terms;
- resize/crop images sensibly without making text unreadable;
- send one page or a small related group at a time;
- ask for literal transcription and structured output, not an explanation;
- preserve the original image and the raw model response;
- validate returned JSON and compare important content with the page.

Do not rotate through multiple accounts to evade rate limits. Use each provider within its published limits. Do not send copyrighted material to a third-party API unless the candidate's use and the manual's terms permit it.

## Initial implementation deliverable

- A page-range extraction command.
- Output directory and manifest.
- Error logging and resumable page/chunk processing where possible.
- A short quality report for the sample pages.
- No automatic question publishing yet.
