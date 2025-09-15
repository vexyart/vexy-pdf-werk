# this_file: src/vexy_pdf_werk/core/markdown_converter.py
"""Markdown conversion functionality for PDF documents."""

import asyncio
import re
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import aiofiles
import pypdf
from loguru import logger

from vexy_pdf_werk.config import ConversionConfig
from vexy_pdf_werk.utils.slug_utils import generate_page_slug, sanitize_file_slug

# Text processing constants
MIN_LINE_LENGTH = 2
MIN_HEADER_LENGTH = 3
CAPS_RATIO_THRESHOLD = 0.7
MAX_HEADER_LENGTH = 80
MIN_PAGE_LINES = 5
MIN_CONTENT_LENGTH = 100


@dataclass
class MarkdownPage:
    """Represents a single page converted to markdown."""

    page_number: int
    content: str
    title: str | None = None
    slug: str | None = None


@dataclass
class MarkdownResult:
    """Result of markdown conversion."""

    success: bool
    pages: list[MarkdownPage]
    error: str | None = None
    total_pages: int = 0
    processing_time: float = 0.0


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
        start_time = time.time()

        # Get file size for logging context
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)

        logger.info(
            "Starting PDF to Markdown conversion",
            extra={
                "input_path": str(pdf_path),
                "file_size_mb": round(file_size_mb, 2),
                "converter": self.__class__.__name__,
                "process_stage": "markdown_start"
            }
        )

        try:
            pages = []

            # Run synchronous PDF reading in thread executor to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                pdf_reader = await loop.run_in_executor(executor, self._read_pdf_sync, pdf_path)

                total_pages = len(pdf_reader.pages)
                logger.info(
                    "PDF loaded for conversion",
                    extra={
                        "input_path": str(pdf_path),
                        "total_pages": total_pages,
                        "converter": self.__class__.__name__,
                        "process_stage": "markdown_loaded"
                    }
                )

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

                        page_md = MarkdownPage(page_number=page_num, content=cleaned_text, title=title, slug=slug)

                        pages.append(page_md)
                        logger.debug(f"Processed page {page_num + 1}/{total_pages}")

                    except Exception as e:
                        logger.warning(f"Failed to process page {page_num + 1}: {e}")
                        # Create error page
                        error_content = f"[Error processing page {page_num + 1}: {e!s}]"
                        pages.append(
                            MarkdownPage(
                                page_number=page_num,
                                content=error_content,
                                title=f"Page {page_num + 1} (Error)",
                                slug=f"page-{page_num + 1}-error",
                            )
                        )

                # Calculate total word count for logging
                total_words = sum(len(page.content.split()) for page in pages)

                logger.success(
                    "PDF to Markdown conversion completed successfully",
                    extra={
                        "input_path": str(pdf_path),
                        "total_pages": total_pages,
                        "pages_converted": len(pages),
                        "total_words": total_words,
                        "converter": self.__class__.__name__,
                        "file_size_mb": round(file_size_mb, 2),
                        "process_stage": "markdown_success"
                    }
                )

                processing_time = time.time() - start_time

                # Add timing to the success log
                logger.info(
                    f"PDF to Markdown conversion timing: {processing_time:.2f}s",
                    extra={
                        "input_path": str(pdf_path),
                        "processing_time_seconds": round(processing_time, 2),
                        "total_pages": total_pages,
                        "pages_converted": len(pages),
                        "process_stage": "markdown_timing"
                    }
                )

                return MarkdownResult(
                    success=True,
                    pages=pages,
                    total_pages=total_pages,
                    processing_time=processing_time
                )

        except Exception as e:
            logger.error(
                "PDF to Markdown conversion failed",
                extra={
                    "input_path": str(pdf_path),
                    "file_size_mb": round(file_size_mb, 2),
                    "converter": self.__class__.__name__,
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "process_stage": "markdown_error"
                }
            )
            processing_time = time.time() - start_time
            return MarkdownResult(
                success=False,
                pages=[],
                error=str(e),
                processing_time=processing_time
            )

    def _read_pdf_sync(self, pdf_path: Path) -> pypdf.PdfReader:
        """Synchronous PDF reading for use in thread executor."""
        import io
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        return pypdf.PdfReader(io.BytesIO(pdf_data))

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
        lines = text.split("\n")
        cleaned_lines: list[str] = []

        for raw_line in lines:
            # Strip excessive whitespace
            processed_line = raw_line.strip()

            # Skip completely empty lines in sequence (keep max 2)
            if not processed_line:
                if len(cleaned_lines) >= MIN_LINE_LENGTH and cleaned_lines[-1] == "" and cleaned_lines[-2] == "":
                    continue  # Skip third+ empty line
                cleaned_lines.append("")
                continue

            # Basic formatting improvements
            processed_line = self._improve_line_formatting(processed_line)
            cleaned_lines.append(processed_line)

        # Join back together
        result = "\n".join(cleaned_lines)

        # Final cleanup
        return result.strip()

    def _improve_line_formatting(self, line: str) -> str:
        """
        Apply basic formatting improvements to a line of text.

        Args:
            line: Single line of text

        Returns:
            Formatted line
        """
        # Remove excessive spaces
        line = re.sub(r" {3,}", "  ", line)  # Max 2 spaces between words

        # Detect potential headers (ALL CAPS lines, or lines ending with specific patterns)
        if self._looks_like_header(line):
            # Convert to markdown header
            line = f"## {line}"

        return line

    def _looks_like_header(self, line: str) -> bool:
        """
        Determine if a line looks like a section header using heuristic analysis.

        This method implements a two-stage heuristic algorithm to identify headers
        in PDF text that may not have explicit formatting:

        1. ALL CAPS detection: Identifies traditional document headers
        2. Numbered section detection: Catches formal document structure

        Args:
            line: Line of text to check

        Returns:
            True if line appears to be a header

        Examples:
            >>> converter._looks_like_header("CHAPTER ONE: INTRODUCTION")
            True
            >>> converter._looks_like_header("1. Introduction Section")
            True
            >>> converter._looks_like_header("This is normal text")
            False
        """
        # Basic length validation: headers should be substantial but not too long
        if len(line) < MIN_HEADER_LENGTH:  # Too short to be meaningful header
            return False

        # Pattern 1: ALL CAPS header detection with punctuation tolerance
        # Many PDF headers are in ALL CAPS (e.g., "CHAPTER ONE: INTRODUCTION")
        words = line.split()

        # Count words that are either uppercase or non-alphabetic (punctuation, numbers)
        # Non-alphabetic words are included because headers often contain colons,
        # numbers, and other formatting that shouldn't disqualify them
        caps_words = [w for w in words if w.isupper() or not w.isalpha()]
        caps_ratio = len(caps_words) / len(words) if words else 0

        # If 70%+ of words are caps/symbols and line is reasonably short
        # (80 chars max to avoid catching entire paragraphs in caps)
        if caps_ratio > CAPS_RATIO_THRESHOLD and len(line) < MAX_HEADER_LENGTH:
            return True

        # Pattern 2: Numbered section detection
        # Catches formal document structure like "1. Introduction" or "2 Main Content"
        # Pattern matches: digit(s) + optional period + whitespace + capital letter
        # Examples: "1. Title", "2 Title", "1.1 Subsection"
        return bool(re.match(r"^\d+\.?\s+[A-Z]", line))

    def _extract_page_title(self, content: str) -> str | None:
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
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        if not lines:
            return None

        first_line = lines[0]

        # Remove markdown header formatting if present
        if first_line.startswith("## "):
            first_line = first_line[3:].strip()

        # If line is reasonably short and not just numbers/symbols, use as title
        if MIN_PAGE_LINES < len(first_line) < MIN_CONTENT_LENGTH and any(c.isalpha() for c in first_line):
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
            # Currently using basic converter as the primary implementation
            # Advanced converters (Marker, MarkItDown, Docling) are planned for future versions
            return BasicConverter(self.config)
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

    async def _write_paginated_files(self, pages: list[MarkdownPage], output_dir: Path) -> None:
        """Write separate markdown file for each page."""
        output_dir.mkdir(parents=True, exist_ok=True)

        total_pages = len(pages)

        for page in pages:
            filename = self.converter._generate_page_filename(page.page_number, page.content, total_pages)

            file_path = output_dir / filename

            # Create frontmatter
            frontmatter = self._create_frontmatter(page, total_pages)

            # Write file
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(frontmatter)
                await f.write(page.content)

            logger.debug(f"Wrote {file_path}")

    async def _write_single_file(self, pages: list[MarkdownPage], output_dir: Path, base_name: str) -> None:
        """Write all pages to a single markdown file."""
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / f"{base_name}.md"

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            # Write document header
            await f.write(f"# {base_name}\n\n")

            for i, page in enumerate(pages):
                if i > 0:
                    await f.write("\n---\n\n")  # Page separator

                await f.write(f"## Page {page.page_number + 1}\n\n")
                await f.write(page.content)
                await f.write("\n\n")

        logger.debug(f"Wrote single file: {file_path}")

    def _create_frontmatter(self, page: MarkdownPage, total_pages: int) -> str:
        """Create YAML frontmatter for a markdown page."""
        frontmatter = "---\n"
        frontmatter += f"page: {page.page_number + 1}\n"
        frontmatter += f"total_pages: {total_pages}\n"

        if page.title:
            frontmatter += f'title: "{page.title}"\n'

        if page.slug:
            frontmatter += f'slug: "{page.slug}"\n'

        frontmatter += "---\n\n"
        return frontmatter
