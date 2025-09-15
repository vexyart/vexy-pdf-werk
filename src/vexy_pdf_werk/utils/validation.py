# this_file: src/vexy_pdf_werk/utils/validation.py
"""Basic input validation utilities for Vexy PDF Werk."""

from pathlib import Path

import pikepdf


def validate_pdf_file(pdf_path: Path) -> None:
    """
    Validate that a PDF file exists and is readable.

    Args:
        pdf_path: Path to PDF file

    Raises:
        ValueError: If the file is not a valid PDF
        FileNotFoundError: If the file doesn't exist
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not pdf_path.is_file():
        raise ValueError(f"Path is not a file: {pdf_path}")

    if pdf_path.suffix.lower() != '.pdf':
        raise ValueError(f"File must have .pdf extension: {pdf_path}")

    if pdf_path.stat().st_size == 0:
        raise ValueError(f"PDF file is empty: {pdf_path}")

    # Try to open with pikepdf to validate structure
    try:
        with pikepdf.open(pdf_path) as pdf:
            if len(pdf.pages) == 0:
                raise ValueError(f"PDF file has no pages: {pdf_path}")
    except pikepdf.PasswordError:
        raise ValueError(f"PDF file is password protected: {pdf_path}")
    except pikepdf.PdfError as e:
        raise ValueError(f"PDF structure error: {e}")


def validate_output_directory(output_path: Path, create_if_missing: bool = True) -> None:
    """
    Validate output directory and optionally create it.

    Args:
        output_path: Path to output directory
        create_if_missing: Whether to create the directory if it doesn't exist

    Raises:
        ValueError: If the path exists but is not a directory
        PermissionError: If unable to create or write to directory
    """
    if output_path.exists() and not output_path.is_dir():
        raise ValueError(f"Output path exists but is not a directory: {output_path}")

    if not output_path.exists() and create_if_missing:
        output_path.mkdir(parents=True, exist_ok=True)


def validate_formats(formats: list[str]) -> list[str]:
    """
    Validate and normalize output format list.

    Args:
        formats: List of requested output formats

    Returns:
        Validated and normalized format list

    Raises:
        ValueError: If any format is invalid
    """
    valid_formats = {'pdfa', 'markdown', 'epub', 'yaml'}
    normalized_formats = []

    for fmt in formats:
        fmt_clean = fmt.strip().lower()
        if fmt_clean not in valid_formats:
            raise ValueError(f"Invalid output format: {fmt}")
        if fmt_clean not in normalized_formats:
            normalized_formats.append(fmt_clean)

    if not normalized_formats:
        raise ValueError("At least one output format must be specified")

    return normalized_formats

