# this_file: TODO.md
---

# Vexy PDF Werk - TODO

## Phase 1: Advanced AI-Powered PDF Structure Enhancement ✅ COMPLETE

- [x] Create `qdf_processor.py` module.
- [x] Implement PDF to QDF/JSON conversion.
- [x] Implement extraction of "mini version" (text streams) from QDF/JSON.
- [x] Create `enhance_pdf_structure` function in `ai_services.py`.
- [x] Implement prompt for LLM to correct text, improve structure, and suggest PDF/A tags.
- [x] Instruct LLM to return a unified diff.
- [x] Implement a diff parser for the LLM output.
- [x] Implement logic to apply the parsed diff to the "mini version".
- [ ] Research and implement merging of changes back into the "full" QDF/JSON. (Note: Diff application complete, QDF-to-PDF merging is placeholder)
- [x] Add `ai.structure_enhancement_enabled` flag to `config.py`.
- [x] Integrate the new enhancement step into the `PDFProcessor` pipeline.
- [x] Create unit tests for QDF/JSON processing.
- [x] Create unit tests for diff parsing and application.
- [x] Create integration tests for the end-to-end page enhancement flow (mocking LLM).

## Phase 2: Advanced Markdown Converters & Testing

- [ ] Implement `MarkerConverter` in `src/vexy_pdf_werk/core/markdown_converter.py`.
- [ ] Implement `MarkItDownConverter` in `src/vexy_pdf_werk/core/markdown_converter.py`.
- [ ] Enhance `MarkdownGenerator` to select the best available converter.
- [ ] Create unit tests for `BasicConverter`.
- [ ] Create integration tests for `MarkerConverter`.
- [ ] Create integration tests for `MarkItDownConverter`.

## Phase 3: Quality, Reliability & Robustness

- [x] Fix the 5 failing metadata extractor tests.
- [x] Clean up ruff issues in test files. (COMPLETED: Fixed 4/6 test files with significant linting improvements)
- [ ] Improve async test patterns and mock configurations.
- [x] Implement structured logging for all processing stages.
- [ ] Add timing metrics for performance monitoring.
- [ ] Add resource usage monitoring (memory, disk space).
- [ ] Add disk space validation before processing.
- [ ] Add comprehensive file permission validation.
- [ ] Investigate and improve memory management for large PDFs.

## Phase 4: Release Preparation

- [ ] Update `README.md` to include new features.
- [ ] Update `CHANGELOG.md` with all changes since the last release.
- [ ] Perform a final round of testing on all features.
- [ ] Tag a new version and create a GitHub release.
