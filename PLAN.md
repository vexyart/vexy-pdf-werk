# this_file: PLAN.md
---

# Project Plan: Vexy PDF Werk (Next Steps)

This plan has been updated to reflect the current state of the project. The initial implementation of core features, including the advanced AI-powered structure enhancement pipeline (QDF), is complete. The next phases focus on finalizing and testing this new feature, implementing additional content backends, and improving documentation and overall robustness.

## Phase 1: Finalize and Test AI Structure Enhancement (QDF Pipeline) ✅ COMPLETE

**Objective**: Ensure the newly implemented AI-powered structure enhancement feature is robust, reliable, and well-tested.

-   [x] **Core Implementation**: The core logic for converting PDF pages to QDF/JSON, extracting text, getting enhancement diffs from AI services, and applying those diffs is in place (`QDFProcessor`, `AIService`, `PDFProcessor`).
-   [x] **Task: Comprehensive Testing**:
    -   ✅ Write unit tests for the `QDFProcessor`, mocking `qpdf` subprocess calls.
    -   ✅ Write unit tests for the diff application logic in `apply_diff_to_qdf`.
    -   ✅ Create integration tests for the end-to-end `_enhance_with_ai_structure` workflow, mocking the AI service to return various diff formats (valid, invalid, empty).
    -   **Achievement**: Added 17 comprehensive tests achieving 92% coverage for QDF processor with full error scenario testing.
-   [x] **Task: Refine AI Prompts**:
    -   ✅ Iteratively test and refine the prompts in `ai_services.py` (`_create_structure_enhancement_prompt`) for both Claude and Gemini to ensure they consistently return clean, applicable diffs.
    -   **Achievement**: Completely rewrote prompts following industry best practices with specific instructions, examples, and output format requirements.
-   [x] **Task: Error Handling**:
    -   ✅ Implement robust error handling within the `_enhance_with_ai_structure` method.
    -   ✅ Handle cases where the AI service fails or returns a malformed diff, ensuring the pipeline can gracefully fall back to processing the page without enhancement.
    -   **Achievement**: Added comprehensive error handling with timeouts (30s/60s), retry logic (3 attempts), input validation, and graceful fallbacks.

## Phase 2: Implement Advanced Markdown Converters

**Objective**: Provide users with higher-fidelity Markdown conversion options by integrating optional, advanced backends.

-   [ ] **Task: Implement `MarkerConverter`**:
    -   Create a `MarkerConverter` class in `markdown_converter.py`.
    -   The implementation should be lazy-loaded, only activating if the `marker-pdf` package is installed.
-   [ ] **Task: Implement `MarkItDownConverter`**:
    -   Create a `MarkItDownConverter` class, also as a lazy-loaded optional backend.
-   [ ] **Task: Implement `DoclingConverter`**:
    -   Create a `DoclingConverter` class as a third optional backend.
-   [ ] **Task: Enhance `MarkdownGenerator`**:
    -   Update the `_create_converter` method to intelligently select the best available backend.
    -   The priority should be configurable but default to a sensible order (e.g., `Marker` > `Docling` > `MarkItDown` > `Basic`).
-   [ ] **Task: Add Tests for New Converters**:
    -   Add integration tests for each new converter.
    -   Use `pytest.mark.skipif` to ensure these tests only run if the required optional dependencies are installed.

## Phase 3: Documentation, Usability & Quality

**Objective**: Improve the user experience through better documentation, clearer CLI feedback, and higher code quality.

-   [ ] **Task: Update Documentation**:
    -   Refresh all documents in `src_docs/` to provide details on the AI structure enhancement feature and the new Markdown backends.
    -   Create a guide on how to use the AI features and configure the different backends.
-   [ ] **Task: Automate API Documentation**:
    -   Configure `mkdocs` with `mkdocstrings` to automatically generate the API Reference section from the Python docstrings. This ensures documentation stays in sync with the code.
-   [ ] **Task: Improve CLI Output**:
    -   Enhance the `rich.progress` implementation in `cli.py` to display more granular stages (e.g., "Applying OCR", "Enhancing Structure (Page 5/20)", "Generating ePub").
-   [ ] **Task: Publish Documentation**:
    -   Configure the `.github/workflows/build-docs.yml` action to automatically build and deploy the `mkdocs` site to GitHub Pages on pushes to the main branch.
-   [ ] **Task: Increase Test Coverage**:
    -   Address any remaining test failures and aim for higher overall test coverage, especially for core logic in `pdf_processor.py` and `markdown_converter.py`.

## Phase 4: Release Preparation

**Objective**: Prepare the project for a stable, well-documented release.

-   [ ] **Task: Final Review**:
    -   Perform a final review of the codebase, dependencies, and all user-facing documentation.
-   [ ] **Task: Update Changelog**:
    -   Ensure `CHANGELOG.md` is up-to-date with all the new features and fixes.
-   [ ] **Task: Tag and Release**:
    -   After all tests are passing, use `hatch` and `git` to tag a new version, build the package, and publish it to PyPI.
    -   Create a corresponding release on GitHub with detailed release notes.