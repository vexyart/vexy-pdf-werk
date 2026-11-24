# this_file: PLAN.md
---

# Remaining work

## Restore the Python test suite

Use the shared ReportLab fixture for tests that need a readable PDF. Keep malformed inputs in error-path tests. Check the failing async, EPUB, Markdown backend selection and pagination, metadata and AI workflow tests against the current APIs. Document how to use the fixture and rerun `PYTHONPATH=src python -m pytest tests/`.

Verify Marker, MarkItDown and Docling with their optional dependencies installed. The three real-conversion tests skip without them. Confirm that each backend produces Markdown from a known PDF without falling back to the basic converter.

## Clear the Ruff findings

Run `ruff check src/vexy_pdf_werk tests` and fix the reported violations. Preserve lazy imports for optional converters. Rerun Ruff and the Python suite after the fixes.

## Finish PDF edge-case coverage

Add regression tests for the input checks exercised manually, including password-protected, malformed and zero-page PDFs. Run the processor on an image-only PDF, a partially readable file and a PDF with unusual metadata. Check the OCR decision, recovered pages or reported errors, and the generated filenames when paths contain spaces or Unicode.
