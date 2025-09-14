# this_file: src/vexy_pdf_werk/core/markdown_converter.py
"""Markdown conversion functionality for PDF documents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

import pypdf
from loguru import logger

from ..config import ConversionConfig
from ..utils.slug_utils import generate_page_slug, sanitize_file_slug


@dataclass
class MarkdownPage:
    """Represents a single page converted to markdown."""
    page_number: int
    content: str
    title: Optional[str] = None
    slug: Optional[str] = None


@dataclass
class MarkdownResult:
    """Result of markdown conversion."""
    success: bool
    pages: List[MarkdownPage]
    error: Optional[str] = None
    total_pages: int = 0


class MarkdownConverter(ABC):
    """Abstract base class for PDF to Markdown converters."""

    def __init__(self, config: ConversionConfig):
        """Initialize the converter."""
        self.config = config

    @abstractmethod
    async def convert_pdf(self, pdf_path: Path) -> MarkdownResult:
        """
        Convert PDF to markdown pages.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Conversion result with markdown pages
        """
        pass

    def _generate_page_filename(self, page_number: int, content: str, total_pages: int) -> str:
        """
        Generate a filename for a markdown page.

        Args:
            page_number: Page number (0-based)
            content: Page content for slug generation
            total_pages: Total number of pages for padding

        Returns:
            Generated filename
        """
        # Generate slug from content
        slug = generate_page_slug(content)

        # Create zero-padded page number
        padding = len(str(total_pages - 1))  # 0-based indexing
        page_num_str = str(page_number).zfill(padding)

        # Sanitize slug for filesystem safety
        safe_slug = sanitize_file_slug(slug)

        return f"{page_num_str}--{safe_slug}.md"


class BasicConverter(MarkdownConverter):
    """Basic PDF to Markdown converter using PyPDF."""

    async def convert_pdf(self, pdf_path: Path) -> MarkdownResult:
        """
        Convert PDF to markdown using PyPDF extraction.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Conversion result with markdown pages
        """
        logger.info(f"Converting PDF to Markdown: {pdf_path}")

        try:
            pages = []

            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                total_pages = len(pdf_reader.pages)

                logger.debug(f"Processing {total_pages} pages")

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        # Extract text from page
                        text = page.extract_text()

                        if not text.strip():
                            # Create placeholder for empty pages
                            text = f"[Page {page_num + 1} appears to be empty or contains only images]"

                        # Clean up text formatting
                        cleaned_text = self._clean_extracted_text(text)

                        # Generate title from first line if available
                        title = self._extract_page_title(cleaned_text)

                        # Generate slug for filename
                        slug = generate_page_slug(cleaned_text)

                        page_md = MarkdownPage(
                            page_number=page_num,
                            content=cleaned_text,
                            title=title,
                            slug=slug
                        )

                        pages.append(page_md)
                        logger.debug(f"Processed page {page_num + 1}/{total_pages}")

                    except Exception as e:
                        logger.warning(f"Failed to process page {page_num + 1}: {e}")
                        # Create error page
                        error_content = f"[Error processing page {page_num + 1}: {str(e)}]"
                        pages.append(MarkdownPage(
                            page_number=page_num,
                            content=error_content,
                            title=f"Page {page_num + 1} (Error)",
                            slug=f"page-{page_num + 1}-error"
                        ))

                logger.success(f"Converted {len(pages)} pages to markdown")

                return MarkdownResult(
                    success=True,
                    pages=pages,
                    total_pages=total_pages
                )

        except Exception as e:
            logger.error(f"Failed to convert PDF to markdown: {e}")
            return MarkdownResult(
                success=False,
                pages=[],
                error=str(e)
            )

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and format extracted text for markdown output.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text suitable for markdown
        """
        if not text.strip():
            return text

        # Split into lines for processing
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # Strip excessive whitespace
            line = line.strip()

            # Skip completely empty lines in sequence (keep max 2)
            if not line:
                if len(cleaned_lines) >= 2 and cleaned_lines[-1] == "" and cleaned_lines[-2] == "":
                    continue  # Skip third+ empty line
                cleaned_lines.append("")
                continue

            # Basic formatting improvements
            line = self._improve_line_formatting(line)
            cleaned_lines.append(line)

        # Join back together
        result = '\n'.join(cleaned_lines)

        # Final cleanup
        result = result.strip()

        return result

    def _improve_line_formatting(self, line: str) -> str:
        """
        Apply basic formatting improvements to a line of text.

        Args:
            line: Single line of text

        Returns:
            Formatted line
        """
        # Remove excessive spaces
        import re
        line = re.sub(r' {3,}', '  ', line)  # Max 2 spaces between words

        # Detect potential headers (ALL CAPS lines, or lines ending with specific patterns)
        if self._looks_like_header(line):
            # Convert to markdown header
            line = f"## {line}"

        return line

    def _looks_like_header(self, line: str) -> bool:
        """
        Determine if a line looks like a section header.

        Args:
            line: Line of text to check

        Returns:
            True if line appears to be a header
        """
        if len(line) < 3:  # Too short to be meaningful header
            return False

        # Check for ALL CAPS (with some tolerance for punctuation)
        words = line.split()
        caps_words = [w for w in words if w.isupper() or not w.isalpha()]
        caps_ratio = len(caps_words) / len(words) if words else 0

        # If most words are caps and line is reasonably short
        if caps_ratio > 0.7 and len(line) < 80:
            return True

        # Check for numbered sections
        import re
        if re.match(r'^\d+\.?\s+[A-Z]', line):  # "1. Title" or "1 Title"
            return True

        return False

    def _extract_page_title(self, content: str) -> Optional[str]:
        """
        Extract a title from page content.

        Args:
            content: Page content

        Returns:
            Extracted title or None
        """
        if not content.strip():
            return None

        # Get first meaningful line
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return None

        first_line = lines[0]

        # Remove markdown header formatting if present
        if first_line.startswith('## '):
            first_line = first_line[3:].strip()

        # If line is reasonably short and not just numbers/symbols, use as title
        if 5 < len(first_line) < 100 and any(c.isalpha() for c in first_line):
            return first_line

        return None


class MarkdownGenerator:
    """Manages markdown generation from PDFs."""

    def __init__(self, config: ConversionConfig):
        """Initialize the generator."""
        self.config = config
        self.converter = self._create_converter()

    def _create_converter(self) -> MarkdownConverter:
        """Create appropriate converter based on configuration."""
        backend = self.config.markdown_backend.lower()

        if backend == "basic" or backend == "auto":
            # For now, always use basic converter
            # TODO: Add other converters (Marker, MarkItDown, Docling) later
            return BasicConverter(self.config)
        else:
            logger.warning(f"Unknown markdown backend '{backend}', falling back to basic")
            return BasicConverter(self.config)

    async def generate_markdown(self, pdf_path: Path, output_dir: Path) -> MarkdownResult:
        """
        Generate markdown files from PDF.

        Args:
            pdf_path: Input PDF path
            output_dir: Output directory for markdown files

        Returns:
            Conversion result
        """
        # Convert PDF to markdown
        result = await self.converter.convert_pdf(pdf_path)

        if not result.success:
            return result

        # Write markdown files if successful
        if self.config.paginate_markdown:
            await self._write_paginated_files(result.pages, output_dir)
        else:
            await self._write_single_file(result.pages, output_dir, pdf_path.stem)

        logger.success(f"Generated markdown files in {output_dir}")
        return result

    async def _write_paginated_files(self, pages: List[MarkdownPage], output_dir: Path) -> None:
        """Write separate markdown file for each page."""
        output_dir.mkdir(parents=True, exist_ok=True)

        total_pages = len(pages)

        for page in pages:
            filename = self.converter._generate_page_filename(
                page.page_number, page.content, total_pages
            )

            file_path = output_dir / filename

            # Create frontmatter
            frontmatter = self._create_frontmatter(page, total_pages)

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
                f.write(page.content)

            logger.debug(f"Wrote {file_path}")

    async def _write_single_file(self, pages: List[MarkdownPage], output_dir: Path, base_name: str) -> None:
        """Write all pages to a single markdown file."""
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / f"{base_name}.md"

        with open(file_path, 'w', encoding='utf-8') as f:
            # Write document header
            f.write(f"# {base_name}\n\n")

            for i, page in enumerate(pages):
                if i > 0:
                    f.write("\n---\n\n")  # Page separator

                f.write(f"## Page {page.page_number + 1}\n\n")
                f.write(page.content)
                f.write("\n\n")

        logger.debug(f"Wrote single file: {file_path}")

    def _create_frontmatter(self, page: MarkdownPage, total_pages: int) -> str:
        """Create YAML frontmatter for a markdown page."""
        frontmatter = "---\n"
        frontmatter += f"page: {page.page_number + 1}\n"
        frontmatter += f"total_pages: {total_pages}\n"

        if page.title:
            frontmatter += f"title: \"{page.title}\"\n"

        if page.slug:
            frontmatter += f"slug: \"{page.slug}\"\n"

        frontmatter += "---\n\n"
        return frontmatter