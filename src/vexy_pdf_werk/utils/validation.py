# this_file: src/vexy_pdf_werk/utils/validation.py
"""Input validation utilities for Vexy PDF Werk."""

from pathlib import Path
from typing import Optional

import pikepdf
from loguru import logger


def validate_pdf_file(pdf_path: Path) -> None:
    """
    Validate that a PDF file is readable and not corrupted.

    Args:
        pdf_path: Path to PDF file

    Raises:
        ValueError: If the file is not a valid PDF
        FileNotFoundError: If the file doesn't exist
    """
    if not pdf_path.exists():
        msg = f"PDF file not found: {pdf_path}"
        raise FileNotFoundError(msg)

    if not pdf_path.is_file():
        msg = f"Path is not a file: {pdf_path}"
        raise ValueError(msg)

    if pdf_path.suffix.lower() != '.pdf':
        msg = f"File must have .pdf extension: {pdf_path}"
        raise ValueError(msg)

    # Try to open with pikepdf to validate structure
    try:
        with pikepdf.open(pdf_path) as pdf:
            # Basic validation - check if we can read the page count
            page_count = len(pdf.pages)
            logger.debug(f"PDF validation passed: {pdf_path} ({page_count} pages)")
    except pikepdf.PdfError as e:
        msg = f"Invalid or corrupted PDF file {pdf_path}: {e}"
        raise ValueError(msg)
    except Exception as e:
        msg = f"Cannot open PDF file {pdf_path}: {e}"
        raise ValueError(msg)


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
        msg = f"Output path exists but is not a directory: {output_path}"
        raise ValueError(msg)

    if not output_path.exists() and create_if_missing:
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created output directory: {output_path}")
        except PermissionError as e:
            msg = f"Cannot create output directory {output_path}: {e}"
            raise PermissionError(msg)

    # Test write permissions
    if output_path.exists():
        test_file = output_path / ".vpw_write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except PermissionError as e:
            msg = f"No write permission in output directory {output_path}: {e}"
            raise PermissionError(msg)


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
            msg = f"Invalid output format: {fmt}. Valid formats: {', '.join(valid_formats)}"
            raise ValueError(msg)
        if fmt_clean not in normalized_formats:  # Avoid duplicates
            normalized_formats.append(fmt_clean)

    if not normalized_formats:
        msg = "At least one output format must be specified"
        raise ValueError(msg)

    return normalized_formats

