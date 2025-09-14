#!/usr/bin/env python3
# this_file: src/vexy_pdf_werk/vexy_pdf_werk.py

"""vexy_pdf_werk: Transform PDFs into high-quality, accessible formats.

This module provides core functionality for processing PDF documents using
modern tools and optional AI enhancement.
"""

import logging
from dataclasses import dataclass
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration settings for vexy_pdf_werk."""

    name: str
    value: str | int | float
    options: dict[str, Any] | None = None


def process_data(data: list[Any], config: Config | None = None, *, debug: bool = False) -> dict[str, Any]:
    """Process the input data according to configuration.

    Args:
        data: Input data to process
        config: Optional configuration settings
        debug: Enable debug mode

    Returns:
        Processed data as a dictionary

    Raises:
        ValueError: If input data is invalid
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    if not data:
        msg = "Input data cannot be empty"
        raise ValueError(msg)

    # Legacy interface: For full PDF processing, use the CLI
    # This function is kept for backward compatibility
    # The main processing pipeline is implemented in cli.py
    logger.warning("process_data() is a legacy interface. Use 'vpw process' CLI command for full functionality.")

    result: dict[str, Any] = {
        "status": "legacy_interface",
        "config_used": config is not None,
        "recommendation": "Use 'vpw process <pdf_path>' for full PDF processing"
    }
    return result


def main() -> None:
    """
    Main entry point for vexy_pdf_werk legacy interface.

    This function provides a legacy interface for basic processing.
    For full PDF processing functionality, use the CLI interface instead:

    Example:
        python -m vexy_pdf_werk.cli process document.pdf

    Raises:
        ValueError: If configuration or data validation fails
        RuntimeError: If processing encounters an unrecoverable error
    """
    try:
        # Example usage of legacy interface
        logger.info("Starting vexy_pdf_werk legacy interface")

        # Create example configuration
        config = Config(
            name="default",
            value="test",
            options={"mode": "legacy", "version": "1.0"}
        )

        # Process empty data as example (legacy behavior)
        try:
            result = process_data([], config=config, debug=True)
            logger.info("Legacy processing completed successfully: %s", result)

        except ValueError as e:
            logger.warning("Validation error in legacy processing: %s", e)
            logger.info("This is expected behavior for the legacy interface")
            logger.info("For PDF processing, use: python -m vexy_pdf_werk.cli process <pdf_file>")

    except Exception as e:
        logger.error("Unexpected error in legacy interface: %s", str(e))
        logger.error("For PDF processing, use the CLI: python -m vexy_pdf_werk.cli")
        msg = f"Legacy interface failed: {e}"
        raise RuntimeError(msg) from e


if __name__ == "__main__":
    main()
