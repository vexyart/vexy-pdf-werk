# this_file: src/vexy_pdf_werk/utils/slug_utils.py
"""Slug generation utilities for Vexy PDF Werk."""

import re

from pathvalidate import sanitize_filename
from slugify import slugify


def generate_page_slug(content: str, max_length: int = 50) -> str:
    """
    Generate a URL-friendly slug from page content.

    Args:
        content: Text content to generate slug from
        max_length: Maximum length of generated slug

    Returns:
        Generated slug
    """
    if not content.strip():
        return "empty-page"

    # Extract first meaningful line/sentence
    lines = content.strip().split('\n')
    text = ""

    for line in lines:
        clean_line = line.strip()
        if clean_line and len(clean_line) > 10:  # Skip very short lines
            text = clean_line
            break

    if not text:
        # Fallback to first line if no meaningful line found
        text = lines[0].strip() if lines else "page"

    # Remove markdown formatting
    text = re.sub(r'[#*_`\[\]()]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Truncate at word boundary
    if len(text) > max_length:
        text = text[:max_length]
        # Find last space to avoid cutting words
        last_space = text.rfind(' ')
        if last_space > max_length // 2:  # Only if we don't cut too much
            text = text[:last_space]

    # Generate slug
    slug = slugify(text)

    # Truncate slug if too long
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')

    # Fallback if slug is empty or too short
    if not slug or len(slug) < 3:
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

