# this_file: TODO.md
---

# Vexy PDF Werk - TODO

## Phase 1: Solidify Foundation & Configuration ✅ COMPLETE

- [x] Verify `uv run pytest`, `ruff`, and `mypy` run cleanly.
- [x] Validate `hatch build` generates version file correctly.
- [x] Implement dynamic configuration loading in `src/vexy_pdf_werk/config.py`.
- [x] Integrate `load_config` into `src/vexy_pdf_werk/cli.py`.
- [x] Implement `vpw config --show` command.
- [x] Implement `vpw config --init` command.

## Phase 2: Core PDF Processing Pipeline

- [x] Implement `PDFInfo` dataclass in `core/pdf_processor.py`.
- [x] Implement `PDFProcessor.analyze_pdf` method.
- [x] Implement `PDFProcessor.create_better_pdf` orchestration method.
- [x] Implement `_enhance_with_ocr` helper using `ocrmypdf`.
- [x] Implement `_convert_to_pdfa` helper using `qpdf`.
- [x] Add error handling and logging for external tools.
- [ ] Add unit tests for `analyze_pdf`.
- [ ] Add integration tests for `create_better_pdf`.

## Phase 3: Content Conversion to Markdown

- [ ] Define `MarkdownConverter` ABC and result dataclasses.
- [ ] Implement `BasicConverter` using `PyMuPDF`.
- [ ] Implement `MarkerConverter` (optional, lazy-loaded).
- [ ] Implement `MarkItDownConverter` (optional, lazy-loaded).
- [ ] Implement `MarkdownGenerator` to select and run converters.
- [ ] Implement `_write_markdown_files` with slug naming and frontmatter.
- [ ] Add unit tests for `BasicConverter`.
- [ ] Add integration tests for optional converters.

## Phase 4: Additional Format Generators

- [ ] Implement `MetadataExtractor` in `core/metadata_extractor.py`.
- [ ] Implement logic to generate `metadata.yaml`.
- [ ] Implement `EpubCreator` in `core/epub_creator.py`.
- [ ] Implement ePub generation from Markdown using `ebooklib`.

## Phase 5: AI Integration (Optional)

- [ ] Define `AIService` ABC in `integrations/ai_services.py`.
- [ ] Implement `ClaudeCLIService` using `claude` CLI.
- [ ] Implement `AIServiceFactory` to select AI provider.
- [ ] Implement `_enhance_with_ai` in `PDFProcessor`.

## Phase 6: Finalize CLI and Release Prep

- [ ] Implement the full `process` command logic in `cli.py`.
- [ ] Integrate `rich.progress` for user feedback.
- [ ] Implement graceful error handling in the CLI.
- [ ] Update `README.md` with full usage instructions.
- [ ] Update `CHANGELOG.md` for `v0.1.0`.
- [ ] Tag and prepare for `v0.1.0` release.

## Completed

- [x] Initial project scaffolding and foundation.
- [x] Detailed specification (`SPEC.md`).
- [x] Minimal CLI skeleton.
- [x] **Phase 1 Complete**: Foundation & Configuration system with CLI interface
- [x] **Phase 2 Core**: PDF processing pipeline foundation (missing tests)