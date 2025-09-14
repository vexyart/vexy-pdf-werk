# Utilities

This section describes the utility functions used in the Vexy PDF Werk package.

## `file_utils.py`

-   `ensure_directory(directory: Path) -> Path`: Ensures a directory exists, creating it if necessary.
-   `safe_copy_file(src: Path, dst: Path, preserve_metadata: bool = True) -> Path`: Safely copies a file, handling errors and ensuring the destination directory exists.
-   `generate_output_filename(input_path: Path, output_format: str, suffix: str | None = None) -> str`: Generates a standardized output filename.
-   `cleanup_temp_files(*paths: Path) -> None`: Cleans up temporary files and directories.
-   `find_tool_path(tool_name: str) -> str | None`: Finds an external tool in the system's PATH.

## `slug_utils.py`

-   `generate_page_slug(content: str, max_length: int = 50) -> str`: Generates a URL-friendly slug from page content.
-   `sanitize_file_slug(filename: str) -> str`: Sanitizes a filename for safe filesystem usage.

## `validation.py`

-   `validate_pdf_file(pdf_path: Path) -> None`: Validates that a PDF file is readable and not corrupted.
-   `validate_output_directory(output_path: Path, create_if_missing: bool = True, min_free_space_mb: int = 50) -> None`: Validates the output directory and optionally creates it.
-   `validate_formats(formats: list[str]) -> list[str]`: Validates and normalizes the list of output formats.
