# this_file: src/vexy_pdf_werk/utils/validation.py
"""Input validation utilities for Vexy PDF Werk."""

import shutil
from pathlib import Path

import pikepdf
from loguru import logger

# Constants
MIN_DISK_SPACE_WARNING_MB = 500


def validate_pdf_file(pdf_path: Path) -> None:
    """
    Validate that a PDF file is readable and not corrupted.

    Args:
        pdf_path: Path to PDF file

    Raises:
        ValueError: If the file is not a valid PDF
        FileNotFoundError: If the file doesn't exist
        PermissionError: If file access is denied
    """
    if not pdf_path.exists():
        msg = f"PDF file not found: {pdf_path}\n" \
              f"Please check the file path and ensure the file exists."
        raise FileNotFoundError(msg)

    if not pdf_path.is_file():
        if pdf_path.is_dir():
            msg = f"Path is a directory, not a file: {pdf_path}\n" \
                  f"Please specify a PDF file, not a directory."
        else:
            msg = f"Path is not a regular file: {pdf_path}\n" \
                  f"Please specify a valid PDF file path."
        raise ValueError(msg)

    if pdf_path.suffix.lower() != '.pdf':
        msg = f"File must have .pdf extension: {pdf_path}\n" \
              f"Current extension: {pdf_path.suffix or '(none)'}\n" \
              f"Please specify a file with .pdf extension."
        raise ValueError(msg)

    # Check file size - warn if very large or very small
    try:
        file_size = pdf_path.stat().st_size
        if file_size == 0:
            msg = f"PDF file is empty: {pdf_path}\n" \
                  f"Please provide a valid PDF file with content."
            raise ValueError(msg)
        if file_size < 100:  # Very small for a PDF
            logger.warning(f"PDF file is very small ({file_size} bytes): {pdf_path}")
        elif file_size > 100 * 1024 * 1024:  # > 100MB
            logger.warning(f"PDF file is very large ({file_size / (1024*1024):.1f} MB): {pdf_path}")
    except (OSError, PermissionError) as e:
        msg = f"Cannot access PDF file {pdf_path}: {e}\n" \
              f"Please check file permissions and try again."
        raise PermissionError(msg)

    # Try to open with pikepdf to validate structure
    try:
        with pikepdf.open(pdf_path) as pdf:
            # Basic validation - check if we can read the page count
            page_count = len(pdf.pages)

            if page_count == 0:
                msg = f"PDF file has no pages: {pdf_path}\n" \
                      f"Please provide a PDF with at least one page."
                raise ValueError(msg)

            logger.debug(f"PDF validation passed: {pdf_path} ({page_count} pages)")

    except pikepdf.PasswordError:
        msg = f"PDF file is password protected: {pdf_path}\n" \
              f"Password-protected PDFs are not currently supported.\n" \
              f"Please provide an unprotected PDF file."
        raise ValueError(msg)
    except pikepdf.PdfError as e:
        # More specific error messages for different PDF errors
        error_str = str(e).lower()
        if "damaged" in error_str or "corrupt" in error_str:
            msg = f"PDF file appears to be corrupted: {pdf_path}\n" \
                  f"Error: {e}\n" \
                  f"Please try with a different PDF file or repair the current one."
        elif "not a pdf" in error_str:
            msg = f"File is not a valid PDF: {pdf_path}\n" \
                  f"The file may have a .pdf extension but is not actually a PDF.\n" \
                  f"Please check the file content and try again."
        else:
            msg = f"PDF structure error in {pdf_path}: {e}\n" \
                  f"The PDF file may be malformed or use unsupported features."
        raise ValueError(msg)
    except MemoryError:
        msg = f"PDF file is too large to process: {pdf_path}\n" \
              f"The system does not have enough memory to open this file.\n" \
              f"Please try with a smaller PDF file."
        raise ValueError(msg)
    except Exception as e:
        msg = f"Unexpected error opening PDF file {pdf_path}: {e}\n" \
              f"Please check the file and try again."
        raise ValueError(msg)


def validate_output_directory(output_path: Path, create_if_missing: bool = True,
                             min_free_space_mb: int = 50) -> None:
    """
    Validate output directory and optionally create it.

    Args:
        output_path: Path to output directory
        create_if_missing: Whether to create the directory if it doesn't exist
        min_free_space_mb: Minimum free space required in MB

    Raises:
        ValueError: If the path exists but is not a directory
        PermissionError: If unable to create or write to directory
        OSError: If insufficient disk space
    """
    if output_path.exists() and not output_path.is_dir():
        if output_path.is_file():
            msg = f"Output path is a file, not a directory: {output_path}\n" \
                  f"Please specify a directory path or use a different name."
        else:
            msg = f"Output path exists but is not a directory: {output_path}\n" \
                  f"Please specify a valid directory path."
        raise ValueError(msg)

    # Create directory if needed
    if not output_path.exists() and create_if_missing:
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created output directory: {output_path}")
        except PermissionError as e:
            msg = (f"Cannot create output directory {output_path}: {e}\n"
                   f"Please check directory permissions or choose a different location.")
            raise PermissionError(msg) from e
        except OSError as e:
            msg = (f"Failed to create output directory {output_path}: {e}\n"
                   f"Please check the path and try again.")
            raise OSError(msg) from e

    # Test write permissions
    if output_path.exists():
        test_file = output_path / ".vpw_write_test"
        try:
            test_file.touch()
            test_file.unlink()
            logger.debug(f"Write permission verified for: {output_path}")
        except PermissionError as e:
            msg = (f"No write permission in output directory {output_path}: {e}\n"
                   f"Please check directory permissions or choose a different location.")
            raise PermissionError(msg) from e
        except OSError as e:
            msg = (f"Cannot write to output directory {output_path}: {e}\n"
                   f"Please check the directory and try again.")
            raise OSError(msg) from e

    # Check available disk space
    try:
        # Get disk usage statistics
        _total, _used, free = shutil.disk_usage(output_path)
        free_mb = free // (1024 * 1024)

        if free_mb < min_free_space_mb:
            msg = (f"Insufficient disk space in output directory: {output_path}\n"
                   f"Available: {free_mb} MB, Required: {min_free_space_mb} MB\n"
                   f"Please free up disk space or choose a different location.")
            raise OSError(msg)

        logger.debug(f"Disk space check passed: {free_mb} MB available in {output_path}")

        # Warn if low on space
        if free_mb < MIN_DISK_SPACE_WARNING_MB:
            logger.warning(f"Low disk space warning: only {free_mb} MB available in {output_path}")

    except OSError as e:
        # Don't fail if we can't check disk space, just warn
        logger.warning(f"Could not check disk space for {output_path}: {e}")


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

