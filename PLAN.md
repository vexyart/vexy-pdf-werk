# this_file: PLAN.md
---

# Project Plan: Vexy PDF Werk (Next Steps)

This plan outlines the next phases of development for Vexy PDF Werk, focusing on completing the feature set as defined in `SPEC.md` and ensuring the package is fully functional and robust.

## Phase 1: Advanced AI-Powered PDF Structure Enhancement

This phase introduces a sophisticated workflow for improving PDF content and structure using LLMs and the QDF (qpdf data format).

1.  **QDF/JSON Representation**:
    -   Implement a new module, `qdf_processor.py`, to handle the conversion of a PDF page to its QDF/JSON representation using `pikepdf` or by calling `qpdf` directly (`qpdf --qdf --json`).
    -   Implement logic to extract a "mini version" containing only the text streams from the QDF/JSON.

2.  **LLM Integration for PDF Enhancement**:
    -   Create a new function in `ai_services.py` called `enhance_pdf_structure`.
    -   This function will take the "mini version" (text) of a page and send it to the LLM with a carefully crafted prompt.
    -   The prompt will instruct the LLM to:
        -   Correct orthographical and logical errors in the text.
        -   Suggest structural improvements.
        -   Provide suggestions for PDF/A tagging.
        -   Return the changes in a unified diff format.

3.  **Diff Application and Merging**:
    -   Implement a diff parser to handle the LLM's output.
    -   Implement logic to apply the parsed diff to the "mini version" of the text.
    -   Research and implement a method to merge the changes from the updated "mini version" back into the "full" QDF/JSON version. This is a complex task that may involve replacing text streams or updating object properties in the QDF/JSON structure.

4.  **Integration into the Main Pipeline**:
    -   Integrate this new enhancement step into the `PDFProcessor`'s `create_better_pdf` method.
    -   This will be an optional step, enabled by a new configuration flag in `config.py` (e.g., `ai.structure_enhancement_enabled`).

5.  **Testing**:
    -   Create unit tests for the QDF/JSON processing.
    -   Create unit tests for the diff parsing and application.
    -   Create integration tests (mocking the LLM) to test the end-to-end flow for a single page.

## Phase 2: Advanced Markdown Converters & Testing

This phase focuses on implementing the optional, high-fidelity Markdown converters and ensuring the entire conversion system is well-tested.

1.  **Implement Advanced Converters**:
    -   **Marker Converter**: Implement the `MarkerConverter` class in `src/vexy_pdf_werk/core/markdown_converter.py`. This should be a lazy-loaded implementation that is only used if the `marker-pdf` package is installed.
    -   **MarkItDown Converter**: Implement the `MarkItDownConverter` class, also as a lazy-loaded optional backend.
    -   **Converter Selection Logic**: Enhance the `MarkdownGenerator` to intelligently select the best available converter, with a clear fallback mechanism (`Marker` > `MarkItDown` > `Basic`).

2.  **Testing**:
    -   **Unit Tests for `BasicConverter`**: Create comprehensive unit tests for the existing `BasicConverter` to ensure its reliability as the fallback.
    -   **Integration Tests for Advanced Converters**: Add integration tests for `MarkerConverter` and `MarkItDownConverter`. These tests should be marked appropriately (e.g., `@pytest.mark.requires_marker`) and only run if the respective packages are installed.

## Phase 3: Quality, Reliability & Robustness

This phase focuses on improving the overall quality and reliability of the package.

1.  **Fix Remaining Test Suite Issues**:
    -   Address the 5 failing metadata extractor tests related to `Path.stat()` mocking.
    -   Clean up test files to reduce Ruff issues.
    -   Improve the reliability of async tests and mock configurations.

2.  **Enhanced Logging & Monitoring**:
    -   Implement structured logging with detailed progress information for each processing stage.
    -   Add timing metrics for performance monitoring.
    -   Add resource usage monitoring (memory, disk space) with warnings.

3.  **Comprehensive Input Validation & Edge Case Handling**:
    -   Add disk space validation before processing large PDFs.
    -   Add comprehensive file permission validation.
    -   Improve memory management for very large PDF files (e.g., chunked processing).

## Phase 4: Release Preparation

This phase prepares the project for a new release.

1.  **Final Documentation Updates**:
    -   Update `README.md` and other documentation to reflect the new features (advanced converters, AI integration).
    -   Ensure the `CHANGELOG.md` is up-to-date.

2.  **Tag and Release**:
    -   Perform a final round of testing.
    -   Tag a new version (e.g., `v1.2.0`) and create a release on GitHub.
