# this_file: src/vexy_pdf_werk/core/epub_creator.py
"""ePub creation functionality from Markdown content."""

import asyncio
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from ebooklib import epub  # type: ignore[import-untyped]
from loguru import logger

from vexy_pdf_werk.core.markdown_converter import MarkdownPage, MarkdownResult


@dataclass
class EpubCreationResult:
    """Result of ePub creation."""
    success: bool
    output_path: Path | None = None
    error: str | None = None
    processing_time: float = 0.0


class EpubCreator:
    """Creates ePub files from Markdown content."""

    def __init__(self, book_title: str | None = None, author: str | None = None):
        """
        Initialize the ePub creator.

        Args:
            book_title: Title for the ePub book
            author: Author of the book
        """
        self.book_title = book_title or "Converted PDF Document"
        self.author = author or "VPW User"

    async def create_epub(
        self,
        markdown_result: MarkdownResult,
        output_path: Path,
        source_pdf_path: Path | None = None
    ) -> EpubCreationResult:
        """
        Create an ePub file from markdown content.

        Args:
            markdown_result: Result from markdown conversion
            output_path: Path where to save the ePub file
            source_pdf_path: Original PDF path for metadata

        Returns:
            Result of ePub creation
        """
        start_time = time.time()

        if not markdown_result.success or not markdown_result.pages:
            processing_time = time.time() - start_time
            return EpubCreationResult(
                success=False,
                error="No valid markdown content to convert to ePub",
                processing_time=processing_time
            )

        try:
            # Calculate total content size for logging context
            total_content_chars = sum(len(page.content) for page in markdown_result.pages)

            logger.info(
                "Starting ePub creation from markdown pages",
                extra={
                    "output_path": str(output_path),
                    "total_pages": len(markdown_result.pages),
                    "total_content_chars": total_content_chars,
                    "source_pdf": str(source_pdf_path) if source_pdf_path else None,
                    "process_stage": "epub_start"
                }
            )

            # Create ePub book
            book = epub.EpubBook()

            # Set metadata
            book_title = self._determine_book_title(markdown_result, source_pdf_path)
            book.set_identifier(str(uuid.uuid4()))
            book.set_title(book_title)
            book.set_language('en')
            book.add_author(self.author)

            # Create chapters from markdown pages
            chapters = []
            spine = ['nav']  # Start with navigation

            for page in markdown_result.pages:
                logger.debug(
                    "Creating ePub chapter from markdown page",
                    extra={
                        "page_number": page.page_number + 1,
                        "page_title": page.title,
                        "page_slug": page.slug,
                        "content_chars": len(page.content),
                        "content_preview": page.content[:100] if page.content else "",
                        "process_stage": "epub_chapter_creation"
                    }
                )
                chapter = self._create_chapter_from_page(page)
                book.add_item(chapter)
                chapters.append(chapter)
                spine.append(chapter)

            logger.debug(
                "ePub chapters created successfully",
                extra={
                    "total_chapters": len(chapters),
                    "process_stage": "epub_chapters_complete"
                }
            )

            # Define Table of Contents
            book.toc = chapters

            # Add navigation files
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            # Define spine (reading order)
            book.spine = spine

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write ePub file
            epub.write_epub(str(output_path), book)

            # Get file size for logging context
            file_size_mb = output_path.stat().st_size / (1024 * 1024)

            logger.success(
                "ePub creation completed successfully",
                extra={
                    "output_path": str(output_path),
                    "file_size_mb": round(file_size_mb, 2),
                    "total_chapters": len(chapters),
                    "total_pages": len(markdown_result.pages),
                    "book_title": book_title,
                    "process_stage": "epub_success"
                }
            )
            processing_time = time.time() - start_time
            return EpubCreationResult(
                success=True,
                output_path=output_path,
                processing_time=processing_time
            )

        except Exception as e:
            error_msg = f"ePub creation failed: {e}"
            logger.error(
                "ePub creation failed",
                extra={
                    "output_path": str(output_path),
                    "total_pages": len(markdown_result.pages),
                    "source_pdf": str(source_pdf_path) if source_pdf_path else None,
                    "error_message": str(e),
                    "error_type": type(e).__name__,
                    "process_stage": "epub_error"
                }
            )
            processing_time = time.time() - start_time
            return EpubCreationResult(
                success=False,
                error=error_msg,
                processing_time=processing_time
            )

    def _determine_book_title(
        self,
        markdown_result: MarkdownResult,
        source_pdf_path: Path | None
    ) -> str:
        """Determine the best title for the book."""
        # Try to use first page title if available
        if markdown_result.pages and markdown_result.pages[0].title:
            return markdown_result.pages[0].title

        # Use provided book title
        if self.book_title and self.book_title != "Converted PDF Document":
            return self.book_title

        # Use source filename as fallback
        if source_pdf_path:
            return source_pdf_path.stem.replace('_', ' ').replace('-', ' ').title()

        return "Converted PDF Document"

    def _create_chapter_from_page(self, page: MarkdownPage) -> epub.EpubHtml:
        """
        Create an ePub chapter from a markdown page.

        Args:
            page: Markdown page to convert

        Returns:
            ePub HTML chapter
        """
        # Generate chapter filename
        chapter_filename = f"page_{page.page_number:03d}.xhtml"
        if page.slug:
            chapter_filename = f"page_{page.page_number:03d}_{page.slug}.xhtml"

        # Convert markdown to HTML (basic conversion)
        html_content = self._markdown_to_html(page.content, page.title)
        logger.debug(
            "Generated HTML content for ePub chapter",
            extra={
                "page_number": page.page_number + 1,
                "html_content_chars": len(html_content),
                "chapter_filename": chapter_filename,
                "process_stage": "epub_html_conversion"
            }
        )

        # Create chapter
        chapter = epub.EpubHtml(
            title=page.title or f"Page {page.page_number}",
            file_name=chapter_filename,
            lang='en'
        )

        chapter.content = html_content.encode('utf-8')
        logger.debug(
            "ePub chapter content finalized",
            extra={
                "page_number": page.page_number + 1,
                "chapter_title": chapter.title,
                "content_bytes": len(chapter.content) if chapter.content else 0,
                "process_stage": "epub_chapter_finalized"
            }
        )
        return chapter

    def _markdown_to_html(self, markdown_content: str, title: str | None = None) -> str:
        """
        Convert markdown content to HTML.

        This is a basic conversion. In the future, this could be enhanced
        with a proper markdown parser like `markdown` or `mistune`.

        Args:
            markdown_content: Markdown content to convert
            title: Optional title for the HTML

        Returns:
            HTML content
        """
        # Basic markdown-to-HTML conversion
        # For now, we'll do simple replacements
        html_content = markdown_content

        # Convert headers
        html_content = html_content.replace('# ', '<h1>').replace('\n# ', '\n<h1>')
        html_content = html_content.replace('## ', '<h2>').replace('\n## ', '\n<h2>')
        html_content = html_content.replace('### ', '<h3>').replace('\n### ', '\n<h3>')

        # Close header tags (simple approach)
        lines = html_content.split('\n')
        processed_lines = []

        for line in lines:
            if line.startswith('<h1>'):
                processed_lines.append(line + '</h1>')
            elif line.startswith('<h2>'):
                processed_lines.append(line + '</h2>')
            elif line.startswith('<h3>'):
                processed_lines.append(line + '</h3>')
            elif line.strip():
                # Regular paragraph
                processed_lines.append(f'<p>{line}</p>')
            else:
                # Empty line
                processed_lines.append('<br/>')

        html_body = '\n'.join(processed_lines)

        # Create complete HTML document
        return f'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title or "Chapter"}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
</head>
<body>
{html_body}
</body>
</html>'''



def create_epub_from_markdown(
    markdown_result: MarkdownResult,
    output_path: Path,
    book_title: str | None = None,
    author: str | None = None,
    source_pdf_path: Path | None = None
) -> EpubCreationResult:
    """
    Convenience function to create ePub from markdown result.

    Args:
        markdown_result: Result from markdown conversion
        output_path: Path where to save the ePub file
        book_title: Title for the ePub book
        author: Author of the book
        source_pdf_path: Original PDF path for metadata

    Returns:
        Result of ePub creation
    """
    creator = EpubCreator(book_title=book_title, author=author)
    return asyncio.run(creator.create_epub(markdown_result, output_path, source_pdf_path))
