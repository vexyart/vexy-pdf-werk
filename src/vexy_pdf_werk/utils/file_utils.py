# this_file: src/vexy_pdf_werk/utils/file_utils.py
"""File operation utilities for Vexy PDF Werk."""

import shutil
from pathlib import Path
from typing import Optional

from loguru import logger


def ensure_directory(directory: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to directory

    Returns:
        The directory path

    Raises:
        PermissionError: If unable to create directory
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")
        return directory
    except PermissionError as e:
        logger.error(f"Cannot create directory {directory}: {e}")
        raise


def safe_copy_file(src: Path, dst: Path, preserve_metadata: bool = True) -> Path:
    """
    Safely copy a file, handling errors and ensuring destination directory exists.

    Args:
        src: Source file path
        dst: Destination file path
        preserve_metadata: Whether to preserve file metadata

    Returns:
        The destination path

    Raises:
        FileNotFoundError: If source file doesn't exist
        PermissionError: If unable to copy file
    """
    if not src.exists():
        msg = f"Source file not found: {src}"
        raise FileNotFoundError(msg)

    # Ensure destination directory exists
    ensure_directory(dst.parent)

    try:
        if preserve_metadata:
            shutil.copy2(src, dst)
        else:
            shutil.copy(src, dst)
        logger.debug(f"Copied file: {src} -> {dst}")
        return dst
    except Exception as e:
        logger.error(f"Failed to copy file {src} to {dst}: {e}")
        raise


def generate_output_filename(
    input_path: Path,
    output_format: str,
    suffix: str | None = None
) -> str:
    """
    Generate standardized output filename.

    Args:
        input_path: Original input file path
        output_format: Output format (pdfa, markdown, epub, yaml)
        suffix: Optional suffix to add

    Returns:
        Generated filename
    """
    stem = input_path.stem

    # Format-specific extensions
    format_extensions = {
        'pdfa': '.pdf',
        'markdown': '.md',
        'epub': '.epub',
        'yaml': '.yaml'
    }

    extension = format_extensions.get(output_format, f'.{output_format}')

    if suffix:
        return f"{stem}_{suffix}{extension}"
    if output_format == 'pdfa':
        return f"{stem}_enhanced{extension}"
    return f"{stem}{extension}"


def cleanup_temp_files(*paths: Path) -> None:
    """
    Clean up temporary files and directories.

    Args:
        *paths: Paths to clean up
    """
    for path in paths:
        if not path.exists():
            continue

        try:
            if path.is_file():
                path.unlink()
                logger.debug(f"Cleaned up temp file: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                logger.debug(f"Cleaned up temp directory: {path}")
        except Exception as e:
            logger.warning(f"Failed to clean up {path}: {e}")


def find_tool_path(tool_name: str) -> str | None:
    """
    Find external tool in PATH.

    Args:
        tool_name: Name of the tool to find

    Returns:
        Full path to tool, or None if not found
    """
    path = shutil.which(tool_name)
    if path:
        logger.debug(f"Found tool {tool_name} at: {path}")
    else:
        logger.warning(f"Tool {tool_name} not found in PATH")
    return path

