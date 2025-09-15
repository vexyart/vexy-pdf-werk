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

from vexy_pdf_werk.config import ConversionConfig
from vexy_pdf_werk.utils.slug_utils import generate_page_slug, sanitize_file_slug
from vexy_pdf_werk.utils.validation import validate_pdf_file

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
        validate_pdf_file(pdf_path)

        try:
            pages = []

            # Run synchronous PDF reading in thread executor to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                pdf_reader = await loop.run_in_executor(executor, self._read_pdf_sync, pdf_path)
                total_pages = len(pdf_reader.pages)

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

                    except Exception as e:
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

                processing_time = time.time() - start_time

                return MarkdownResult(
                    success=True,
                    pages=pages,
                    total_pages=total_pages,
                    processing_time=processing_time
                )

        except Exception as e:
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


class MarkerConverter(MarkdownConverter):
    """Advanced converter using marker-pdf for high-quality PDF-to-Markdown conversion.

    Falls back to BasicConverter if dependency is missing.
    """

    def __init__(self, config: ConversionConfig):
        super().__init__(config)
        try:
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            from marker.output import text_from_rendered

            self._PdfConverter = PdfConverter
            self._create_model_dict = create_model_dict
            self._text_from_rendered = text_from_rendered
            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False

    async def convert_pdf(self, pdf_path: Path) -> MarkdownResult:
        if not self._available:
            return await BasicConverter(self.config).convert_pdf(pdf_path)

        start_time = time.time()
        validate_pdf_file(pdf_path)

        try:
            # Run marker conversion in thread executor to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                # Create marker converter with model artifacts
                marker_converter = self._PdfConverter(
                    artifact_dict=self._create_model_dict()
                )

                # Convert PDF using marker
                rendered = await loop.run_in_executor(
                    executor,
                    marker_converter,
                    str(pdf_path)
                )

                # Extract text and images from rendered output
                text, _, images = self._text_from_rendered(rendered)

                # Convert marker's full-document output to our paginated format
                pages = self._split_marker_output_to_pages(text, pdf_path)
                processing_time = time.time() - start_time

                return MarkdownResult(
                    success=True,
                    pages=pages,
                    total_pages=len(pages),
                    processing_time=processing_time
                )

        except Exception:
            # Fall back to BasicConverter on errors
            return await BasicConverter(self.config).convert_pdf(pdf_path)

    def _split_marker_output_to_pages(self, full_text: str, pdf_path: Path) -> list[MarkdownPage]:
        """
        Split marker's full-document output into pages.

        Marker typically outputs the entire document as one markdown string.
        We need to split it into logical pages for consistency with our interface.
        """
        # Split by major section headers (## or # level headers)
        # This is a heuristic approach since marker doesn't preserve exact page boundaries
        import re

        # Split on headers but preserve the headers
        header_pattern = r'^(#{1,2}\s+.+)$'
        sections = re.split(header_pattern, full_text, flags=re.MULTILINE)

        pages = []
        current_page_content = ""
        page_number = 0

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # Check if this is a header
            if re.match(header_pattern, section.strip(), re.MULTILINE):
                # If we have accumulated content, save it as a page
                if current_page_content.strip():
                    title = self._extract_page_title(current_page_content)
                    slug = generate_page_slug(current_page_content)

                    pages.append(MarkdownPage(
                        page_number=page_number,
                        content=current_page_content.strip(),
                        title=title,
                        slug=slug
                    ))
                    page_number += 1

                # Start new page with this header
                current_page_content = section + "\n"
            else:
                # Add content to current page
                current_page_content += section

        # Add final page if there's remaining content
        if current_page_content.strip():
            title = self._extract_page_title(current_page_content)
            slug = generate_page_slug(current_page_content)

            pages.append(MarkdownPage(
                page_number=page_number,
                content=current_page_content.strip(),
                title=title,
                slug=slug
            ))

        # If no logical sections found, treat as single page
        if not pages:
            title = self._extract_page_title(full_text)
            slug = generate_page_slug(full_text)

            pages.append(MarkdownPage(
                page_number=0,
                content=full_text.strip(),
                title=title,
                slug=slug
            ))

        return pages


class MarkItDownConverter(MarkdownConverter):
    """Advanced converter using Microsoft's markitdown for PDF-to-Markdown conversion.

    Falls back to BasicConverter if dependency is missing.
    """

    def __init__(self, config: ConversionConfig):
        super().__init__(config)
        try:
            from markitdown import MarkItDown
            self._MarkItDown = MarkItDown
            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False

    async def convert_pdf(self, pdf_path: Path) -> MarkdownResult:
        if not self._available:
            return await BasicConverter(self.config).convert_pdf(pdf_path)

        start_time = time.time()
        validate_pdf_file(pdf_path)

        try:
            # Run markitdown conversion in thread executor to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                # Create markitdown converter
                md_converter = self._MarkItDown()

                # Convert PDF using markitdown
                result = await loop.run_in_executor(
                    executor,
                    md_converter.convert,
                    str(pdf_path)
                )

                # Extract text content from markitdown result
                full_text = result.text_content

                # Convert markitdown's full-document output to our paginated format
                pages = self._split_markitdown_output_to_pages(full_text, pdf_path)
                processing_time = time.time() - start_time

                return MarkdownResult(
                    success=True,
                    pages=pages,
                    total_pages=len(pages),
                    processing_time=processing_time
                )

        except Exception:
            # Fall back to BasicConverter on errors
            return await BasicConverter(self.config).convert_pdf(pdf_path)

    def _split_markitdown_output_to_pages(self, full_text: str, pdf_path: Path) -> list[MarkdownPage]:
        """
        Split markitdown's full-document output into pages.

        MarkItDown typically outputs the entire document as one markdown string.
        We need to split it into logical pages for consistency with our interface.
        """
        # Split by major section headers (## or # level headers)
        # This is a heuristic approach since markitdown doesn't preserve exact page boundaries
        import re

        # Split on headers but preserve the headers
        header_pattern = r'^(#{1,3}\s+.+)$'
        sections = re.split(header_pattern, full_text, flags=re.MULTILINE)

        pages = []
        current_page_content = ""
        page_number = 0

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # Check if this is a header
            if re.match(header_pattern, section.strip(), re.MULTILINE):
                # If we have accumulated content, save it as a page
                if current_page_content.strip():
                    title = self._extract_page_title(current_page_content)
                    slug = generate_page_slug(current_page_content)

                    pages.append(MarkdownPage(
                        page_number=page_number,
                        content=current_page_content.strip(),
                        title=title,
                        slug=slug
                    ))
                    page_number += 1

                # Start new page with this header
                current_page_content = section + "\n"
            else:
                # Add content to current page
                current_page_content += section

        # Add final page if there's remaining content
        if current_page_content.strip():
            title = self._extract_page_title(current_page_content)
            slug = generate_page_slug(current_page_content)

            pages.append(MarkdownPage(
                page_number=page_number,
                content=current_page_content.strip(),
                title=title,
                slug=slug
            ))

        # If no logical sections found, treat as single page
        if not pages:
            title = self._extract_page_title(full_text)
            slug = generate_page_slug(full_text)

            pages.append(MarkdownPage(
                page_number=0,
                content=full_text.strip(),
                title=title,
                slug=slug
            ))

        return pages


class DoclingConverter(MarkdownConverter):
    """Advanced converter using IBM docling for sophisticated PDF document understanding.

    Falls back to BasicConverter if dependency is missing.
    """

    def __init__(self, config: ConversionConfig):
        super().__init__(config)
        try:
            from docling.document_converter import DocumentConverter
            self._DocumentConverter = DocumentConverter
            self._available = True
        except ImportError:
            self._available = False
        except Exception:
            self._available = False

    async def convert_pdf(self, pdf_path: Path) -> MarkdownResult:
        if not self._available:
            return await BasicConverter(self.config).convert_pdf(pdf_path)

        start_time = time.time()
        validate_pdf_file(pdf_path)

        try:
            # Run docling conversion in thread executor to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                # Create docling converter
                docling_converter = self._DocumentConverter()

                # Convert PDF using docling
                result = await loop.run_in_executor(
                    executor,
                    docling_converter.convert,
                    str(pdf_path)
                )

                # Extract markdown content from docling result
                full_text = result.document.export_to_markdown()

                # Convert docling's full-document output to our paginated format
                pages = self._split_docling_output_to_pages(full_text, pdf_path)
                processing_time = time.time() - start_time

                return MarkdownResult(
                    success=True,
                    pages=pages,
                    total_pages=len(pages),
                    processing_time=processing_time
                )

        except Exception:
            # Fall back to BasicConverter on errors
            return await BasicConverter(self.config).convert_pdf(pdf_path)

    def _split_docling_output_to_pages(self, full_text: str, pdf_path: Path) -> list[MarkdownPage]:
        """
        Split docling's full-document output into pages.

        Docling typically outputs the entire document as one markdown string.
        We need to split it into logical pages for consistency with our interface.
        """
        # Split by major section headers (## or # level headers)
        # This is a heuristic approach since docling doesn't preserve exact page boundaries
        import re

        # Split on headers but preserve the headers
        header_pattern = r'^(#{1,3}\s+.+)$'
        sections = re.split(header_pattern, full_text, flags=re.MULTILINE)

        pages = []
        current_page_content = ""
        page_number = 0

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # Check if this is a header
            if re.match(header_pattern, section.strip(), re.MULTILINE):
                # If we have accumulated content, save it as a page
                if current_page_content.strip():
                    title = self._extract_page_title(current_page_content)
                    slug = generate_page_slug(current_page_content)

                    pages.append(MarkdownPage(
                        page_number=page_number,
                        content=current_page_content.strip(),
                        title=title,
                        slug=slug
                    ))
                    page_number += 1

                # Start new page with this header
                current_page_content = section + "\n"
            else:
                # Add content to current page
                current_page_content += section

        # Add final page if there's remaining content
        if current_page_content.strip():
            title = self._extract_page_title(current_page_content)
            slug = generate_page_slug(current_page_content)

            pages.append(MarkdownPage(
                page_number=page_number,
                content=current_page_content.strip(),
                title=title,
                slug=slug
            ))

        # If no logical sections found, treat as single page
        if not pages:
            title = self._extract_page_title(full_text)
            slug = generate_page_slug(full_text)

            pages.append(MarkdownPage(
                page_number=0,
                content=full_text.strip(),
                title=title,
                slug=slug
            ))

        return pages


class MarkdownGenerator:
    """Manages markdown generation from PDFs."""

    def __init__(self, config: ConversionConfig):
        """Initialize the generator."""
        self.config = config
        self.converter = self._create_converter()

    def _create_converter(self) -> MarkdownConverter:
        """Create appropriate converter based on configuration and availability."""
        backend = (self.config.markdown_backend or "auto").lower()

        if backend == "basic":
            return BasicConverter(self.config)

        if backend == "marker":
            return MarkerConverter(self.config)
        if backend == "docling":
            return DoclingConverter(self.config)
        if backend == "markitdown":
            return MarkItDownConverter(self.config)

        if backend == "auto":
            # Default priority
            priority = ["marker", "docling", "markitdown", "basic"]
            for name in priority:
                if name == "marker":
                    conv = MarkerConverter(self.config)
                    if getattr(conv, "_available", False):
                        return conv
                elif name == "docling":
                    conv = DoclingConverter(self.config)
                    if getattr(conv, "_available", False):
                        return conv
                elif name == "markitdown":
                    conv = MarkItDownConverter(self.config)
                    if getattr(conv, "_available", False):
                        return conv
                else:
                    return BasicConverter(self.config)

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