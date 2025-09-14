# this_file: src/vexy_pdf_werk/utils/slug_utils.py
"""Slug generation utilities for Vexy PDF Werk."""

import re

from pathvalidate import sanitize_filename
from slugify import slugify  # type: ignore[import-untyped]


# Constants for slug generation
MIN_LINE_LENGTH_FOR_EXTRACTION = 10
MIN_SLUG_LENGTH = 3


def generate_page_slug(content: str, max_length: int = 50) -> str:
    """
    Generate a URL-friendly slug from page content using intelligent text extraction.

    This function implements a multi-stage algorithm to create meaningful, readable
    slugs from PDF page content:

    1. Extracts the first meaningful line (>10 chars) to avoid headers/page numbers
    2. Cleans markdown formatting that could interfere with slug generation
    3. Truncates at word boundaries to maintain readability
    4. Uses the `slugify` library for URL-safe conversion
    5. Applies fallback strategies for edge cases

    Args:
        content: Text content to generate slug from
        max_length: Maximum length of generated slug (default: 50)

    Returns:
        Generated slug suitable for filenames and URLs

    Examples:
        >>> generate_page_slug("Chapter 1: Introduction\\nThis is the content...")
        'chapter-1-introduction'
        >>> generate_page_slug("## Very Long Title That Exceeds Length")
        'very-long-title-that-exceeds'
    """
    # Handle empty or whitespace-only content
    if not content.strip():
        return "empty-page"

    # Stage 1: Extract first meaningful line/sentence
    # Split content into lines for processing
    lines = content.strip().split('\n')
    text = ""

    # Find the first line with substantial content (>10 characters)
    # This helps skip over page numbers, short headers, or formatting artifacts
    for line in lines:
        clean_line = line.strip()
        if clean_line and len(clean_line) > MIN_LINE_LENGTH_FOR_EXTRACTION:  # Skip very short lines
            text = clean_line
            break

    # Fallback: use first available line if no meaningful content found
    if not text:
        text = lines[0].strip() if lines else "page"

    # Stage 2: Clean markdown and formatting artifacts
    # Remove common markdown syntax that could interfere with slug generation
    text = re.sub(r'[#*_`\[\]()]', '', text)  # Remove markdown symbols
    text = re.sub(r'\s+', ' ', text).strip()   # Normalize whitespace

    # Stage 3: Intelligent truncation at word boundaries
    if len(text) > max_length:
        # First, truncate to max length
        text = text[:max_length]

        # Find the last space to avoid cutting words in half
        last_space = text.rfind(' ')

        # Only truncate at word boundary if we don't lose too much content
        # (at least half the max length should remain)
        if last_space > max_length // 2:
            text = text[:last_space]

    # Stage 4: Generate URL-safe slug using slugify library
    # This handles unicode, special characters, and creates web-safe URLs
    slug = str(slugify(text))

    # Stage 5: Final length validation and cleanup
    # Ensure slug doesn't exceed max length (slugify might add dashes)
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')  # Remove trailing dashes

    # Stage 6: Fallback for edge cases
    # If slug is empty or too short after processing, use a generic fallback
    if not slug or len(slug) < MIN_SLUG_LENGTH:
        return "page-content"

    return slug


def sanitize_file_slug(filename: str) -> str:
    """
    Sanitize a filename for safe filesystem usage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    return sanitize_filename(filename, replacement_text="-")

