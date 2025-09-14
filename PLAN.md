# this_file: PLAN.md
---

# Project Plan: Vexy PDF Werk (Implementation Phase)

This plan outlines the implementation of the core features for Vexy PDF Werk, building upon the established foundation. The goal is to create a functional, robust, and extensible PDF processing pipeline as defined in `SPEC.md`.

## Phase 1: Solidify Foundation & Configuration (10%)

This phase ensures the project setup is complete and the configuration system is fully integrated.

1.  **Verify Toolchain and Environment**:
    -   [ ] Confirm `uv run pytest`, `uv run ruff check .`, and `uv run mypy src` execute cleanly.
    -   [ ] Validate that `hatch build` correctly generates `src/vexy_pdf_werk/_version.py` via `hatch-vcs`.

2.  **Implement Dynamic Configuration**:
    -   [ ] Implement the configuration loading logic in `src/vexy_pdf_werk/config.py` as specified.
    -   [ ] Integrate `load_config` into the CLI (`cli.py`) to load settings from `config.toml`, environment variables, and command-line arguments.
    -   [ ] Implement the `vpw config --show` and `vpw config --init` commands to manage the user configuration file.

## Phase 2: Core PDF Processing Pipeline (30%)

Implement the primary PDF enhancement workflow: analyzing, OCRing, and converting to a high-quality, archivable PDF/A format.

1.  **Implement PDF Analysis**:
    -   [ ] Implement the `PDFInfo` dataclass in `core/pdf_processor.py`.
    -   [ ] Implement the `PDFProcessor.analyze_pdf` method using `pikepdf` to extract metadata and determine content characteristics (e.g., text, images, scanned).

2.  **Implement OCR & PDF/A Workflow**:
    -   [ ] Implement the main `PDFProcessor.create_better_pdf` orchestration method.
    -   [ ] Implement `_enhance_with_ocr` helper using `ocrmypdf` via `asyncio.create_subprocess_exec`. Handle `force_ocr` and `skip-text` logic.
    -   [ ] Implement `_convert_to_pdfa` helper using `qpdf` for final optimization and linearization.
    -   [ ] Add robust error handling and logging for external tool failures.

3.  **Unit & Integration Testing**:
    -   [ ] Create unit tests for `analyze_pdf` with fixture PDFs (text-based, image-based, mixed).
    -   [ ] Create integration tests for `create_better_pdf` that call the actual external tools (`ocrmypdf`, `qpdf`) on small test PDFs. Mark as `@pytest.mark.slow`.

## Phase 3: Content Conversion to Markdown (30%)

Implement the flexible PDF-to-Markdown conversion system with multiple backends.

1.  **Implement Converter Abstraction**:
    -   [ ] Define the `MarkdownConverter` abstract base class in `core/markdown_generator.py`.
    -   [ ] Define `PageContent` and `MarkdownResult` dataclasses.

2.  **Implement Concrete Converters**:
    -   [ ] **Basic Converter**: Implement `BasicConverter` using `PyMuPDF` (`fitz`) for text and image extraction. This is the essential fallback.
    -   [ ] **Marker Converter (Optional)**: Implement `MarkerConverter`, including lazy import to prevent hard dependency. Handle paginated output.
    -   [ ] **MarkItDown Converter (Optional)**: Implement `MarkItDownConverter`, including logic to handle pagination by splitting the PDF.

3.  **Implement Markdown Generator**:
    -   [ ] Implement the `MarkdownGenerator` class to manage and select the appropriate converter (`_select_converter`).
    -   [ ] Implement `generate_markdown` to orchestrate the conversion and file writing.
    -   [ ] Implement `_write_markdown_files` to save content with proper naming (`001--slug.md`) and YAML frontmatter.

4.  **Testing**:
    -   [ ] Create unit tests for the `BasicConverter`.
    -   [ ] Create integration tests for `MarkerConverter` and `MarkItDownConverter` if they are installed, marked appropriately (e.g., `@pytest.mark.requires_marker`).

## Phase 4: Additional Format Generators (15%)

Create the remaining output formats: ePub and bibliographic YAML.

1.  **Implement Metadata Extractor**:
    -   [ ] Implement `MetadataExtractor` in `core/metadata_extractor.py`.
    -   [ ] The extractor should gather information from `PDFInfo` and potentially other sources.
    -   [ ] It should generate a `metadata.yaml` file with structured bibliographic data (title, author, etc.).

2.  **Implement ePub Creator**:
    -   [ ] Implement `EpubCreator` in `core/epub_creator.py`.
    -   [ ] Use the generated Markdown files as input.
    -   [ ] Use `ebooklib` to convert the collection of Markdown files into a single `.epub` file.

## Phase 5: AI Integration (Optional) (10%)

Implement the optional AI-based text correction and enhancement features.

1.  **Implement AI Service Abstraction**:
    -   [ ] Define the `AIService` abstract base class in `integrations/ai_services.py`.

2.  **Implement AI Services**:
    -   [ ] Implement `ClaudeCLIService` to interact with the `claude` CLI tool for text correction.
    -   [ ] Implement a similar service for Gemini if a CLI tool is available and specified.
    -   [ ] Implement the `AIServiceFactory` to select the configured AI provider.

3.  **Integrate into PDF Processor**:
    -   [ ] Implement the `_enhance_with_ai` method in `PDFProcessor`.
    -   [ ] This method will be called conditionally based on the `ai.enabled` configuration flag.

## Phase 6: Finalize CLI and Release Prep (5%)

Connect all pipeline components and prepare for an initial release.

1.  **Complete CLI `process` Command**:
    -   [ ] In `cli.py`, replace the stub `process` logic with a full call to the processing pipeline.
    -   [ ] Instantiate `PDFProcessor`, `MarkdownGenerator`, etc.
    -   [ ] Use `rich.progress` to display the status of each stage (Analyzing, OCR, Converting, etc.).
    -   [ ] Handle and display errors gracefully to the user.

2.  **Documentation and Release**:
    -   [ ] Update `README.md` with complete usage instructions for the functional CLI.
    -   [ ] Update `CHANGELOG.md` with all implemented features.
    -   [ ] Perform a final round of testing.
    -   [ ] Tag a `v0.1.0` release.