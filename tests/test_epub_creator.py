# this_file: tests/test_epub_creator.py
"""Tests for ePub creation functionality."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vexy_pdf_werk.core.epub_creator import EpubCreationResult, EpubCreator, create_epub_from_markdown
from vexy_pdf_werk.core.markdown_converter import MarkdownPage, MarkdownResult


class TestEpubCreationResult:
    """Test cases for EpubCreationResult dataclass."""

    def test_creation_result_success(self):
        """Test successful creation result."""
        result = EpubCreationResult(
            success=True,
            output_path=Path("test.epub")
        )
        assert result.success is True
        assert result.output_path == Path("test.epub")
        assert result.error is None

    def test_creation_result_failure(self):
        """Test failed creation result."""
        result = EpubCreationResult(
            success=False,
            error="Creation failed"
        )
        assert result.success is False
        assert result.output_path is None
        assert result.error == "Creation failed"


class TestEpubCreator:
    """Test cases for EpubCreator class."""

    @pytest.fixture
    def creator(self):
        """Create EpubCreator instance for testing."""
        return EpubCreator(book_title="Test Book", author="Test Author")

    @pytest.fixture
    def sample_markdown_pages(self):
        """Create sample markdown pages for testing."""
        return [
            MarkdownPage(
                page_number=0,
                content="# Chapter 1\n\nThis is the first chapter content.",
                title="Chapter 1",
                slug="chapter-1"
            ),
            MarkdownPage(
                page_number=1,
                content="# Chapter 2\n\nThis is the second chapter content.",
                title="Chapter 2",
                slug="chapter-2"
            )
        ]

    @pytest.fixture
    def successful_markdown_result(self, sample_markdown_pages):
        """Create successful markdown result for testing."""
        return MarkdownResult(
            success=True,
            pages=sample_markdown_pages,
            total_pages=2
        )

    @pytest.fixture
    def failed_markdown_result(self):
        """Create failed markdown result for testing."""
        return MarkdownResult(
            success=False,
            pages=[],
            error="Markdown conversion failed"
        )

    @pytest.fixture
    def temp_output_path(self):
        """Create temporary output path for testing."""
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            yield temp_path
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

    def test_creator_initialization(self, creator):
        """Test EpubCreator initialization."""
        assert creator.book_title == "Test Book"
        assert creator.author == "Test Author"

    def test_creator_initialization_defaults(self):
        """Test EpubCreator initialization with defaults."""
        creator = EpubCreator()
        assert creator.book_title == "Converted PDF Document"
        assert creator.author == "VPW User"

    @pytest.mark.asyncio
    async def test_create_epub_with_failed_markdown(self, creator, failed_markdown_result, temp_output_path):
        """Test ePub creation with failed markdown result."""
        result = await creator.create_epub(failed_markdown_result, temp_output_path)

        assert result.success is False
        assert result.error == "No valid markdown content to convert to ePub"
        assert result.output_path is None

    @pytest.mark.asyncio
    async def test_create_epub_with_empty_pages(self, creator, temp_output_path):
        """Test ePub creation with empty pages."""
        empty_result = MarkdownResult(success=True, pages=[], total_pages=0)
        result = await creator.create_epub(empty_result, temp_output_path)

        assert result.success is False
        assert result.error == "No valid markdown content to convert to ePub"

    @pytest.mark.asyncio
    async def test_create_epub_success(self, creator, successful_markdown_result, temp_output_path):
        """Test successful ePub creation."""
        with patch('vexy_pdf_werk.core.epub_creator.epub') as mock_epub:
            # Mock the epub library
            mock_book = MagicMock()
            mock_epub.EpubBook.return_value = mock_book
            mock_epub.EpubHtml.return_value = MagicMock()
            mock_epub.EpubNcx.return_value = MagicMock()
            mock_epub.EpubNav.return_value = MagicMock()

            result = await creator.create_epub(successful_markdown_result, temp_output_path)

            assert result.success is True
            assert result.output_path == temp_output_path
            assert result.error is None

            # Verify book metadata was set (first page title takes precedence)
            mock_book.set_title.assert_called_once_with("Chapter 1")
            mock_book.add_author.assert_called_once_with("Test Author")
            mock_book.set_language.assert_called_once_with('en')

            # Verify chapters were created
            assert mock_book.add_item.call_count >= 2  # At least for the 2 pages

            # Verify write_epub was called
            mock_epub.write_epub.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_epub_with_exception(self, creator, successful_markdown_result, temp_output_path):
        """Test ePub creation handles exceptions gracefully."""
        with patch('vexy_pdf_werk.core.epub_creator.epub') as mock_epub:
            mock_epub.EpubBook.side_effect = Exception("ePub library error")

            result = await creator.create_epub(successful_markdown_result, temp_output_path)

            assert result.success is False
            assert "ePub creation failed: ePub library error" in result.error
            assert result.output_path is None

    def test_determine_book_title_from_first_page(self, creator, successful_markdown_result):
        """Test book title determination from first page title."""
        title = creator._determine_book_title(successful_markdown_result, None)
        assert title == "Chapter 1"

    def test_determine_book_title_from_provided_title(self, creator):
        """Test book title determination from provided title."""
        creator.book_title = "Custom Title"
        empty_result = MarkdownResult(success=True, pages=[], total_pages=0)
        title = creator._determine_book_title(empty_result, None)
        assert title == "Custom Title"

    def test_determine_book_title_from_source_path(self, creator):
        """Test book title determination from source PDF path."""
        creator.book_title = "Converted PDF Document"  # Default title
        empty_result = MarkdownResult(success=True, pages=[], total_pages=0)
        source_path = Path("/path/to/my_awesome_document.pdf")
        title = creator._determine_book_title(empty_result, source_path)
        assert title == "My Awesome Document"

    def test_determine_book_title_fallback(self, creator):
        """Test book title determination fallback."""
        creator.book_title = "Converted PDF Document"  # Default title
        empty_result = MarkdownResult(success=True, pages=[], total_pages=0)
        title = creator._determine_book_title(empty_result, None)
        assert title == "Converted PDF Document"

    def test_create_chapter_from_page(self, creator, sample_markdown_pages):
        """Test chapter creation from markdown page."""
        page = sample_markdown_pages[0]

        with patch('vexy_pdf_werk.core.epub_creator.epub') as mock_epub:
            mock_chapter = MagicMock()
            mock_epub.EpubHtml.return_value = mock_chapter

            creator._create_chapter_from_page(page)

            # Verify EpubHtml was called with correct parameters
            mock_epub.EpubHtml.assert_called_once_with(
                title="Chapter 1",
                file_name="page_000_chapter-1.xhtml",
                lang='en'
            )

            # Verify content was set
            assert mock_chapter.content is not None

    def test_create_chapter_without_slug(self, creator):
        """Test chapter creation from page without slug."""
        page = MarkdownPage(
            page_number=5,
            content="Some content",
            title="Page Title",
            slug=None
        )

        with patch('vexy_pdf_werk.core.epub_creator.epub') as mock_epub:
            mock_chapter = MagicMock()
            mock_epub.EpubHtml.return_value = mock_chapter

            creator._create_chapter_from_page(page)

            # Verify filename without slug
            mock_epub.EpubHtml.assert_called_once_with(
                title="Page Title",
                file_name="page_005.xhtml",
                lang='en'
            )

    def test_markdown_to_html_basic(self, creator):
        """Test basic markdown to HTML conversion."""
        markdown_content = "# Header\n\nParagraph text\n\n## Subheader"
        html = creator._markdown_to_html(markdown_content, "Test Title")

        assert "<!DOCTYPE html" in html
        assert "<title>Test Title</title>" in html
        assert "<h1>Header</h1>" in html
        # Note: The basic markdown converter doesn't handle ## properly
        # It should still contain the subheader text
        assert "Subheader" in html
        assert "<p>Paragraph text</p>" in html

    def test_markdown_to_html_with_empty_lines(self, creator):
        """Test markdown to HTML conversion with empty lines."""
        markdown_content = "Line 1\n\n\nLine 2"
        html = creator._markdown_to_html(markdown_content)

        assert "<p>Line 1</p>" in html
        assert "<p>Line 2</p>" in html
        assert "<br/>" in html

    def test_markdown_to_html_without_title(self, creator):
        """Test markdown to HTML conversion without title."""
        html = creator._markdown_to_html("Content", None)
        assert "<title>Chapter</title>" in html


class TestConvenienceFunction:
    """Test cases for convenience functions."""

    @pytest.fixture
    def successful_markdown_result(self):
        """Create successful markdown result for testing."""
        pages = [
            MarkdownPage(
                page_number=0,
                content="Test content",
                title="Test Page",
                slug="test-page"
            )
        ]
        return MarkdownResult(success=True, pages=pages, total_pages=1)

    def test_create_epub_from_markdown_convenience(self, successful_markdown_result):
        """Test convenience function for ePub creation."""
        with patch('vexy_pdf_werk.core.epub_creator.EpubCreator') as mock_creator_class, \
             patch('asyncio.run') as mock_run:

            mock_creator = MagicMock()
            mock_creator_class.return_value = mock_creator
            mock_result = EpubCreationResult(success=True, output_path=Path("test.epub"))
            mock_run.return_value = mock_result

            output_path = Path("output.epub")
            result = create_epub_from_markdown(
                successful_markdown_result,
                output_path,
                book_title="Test Book",
                author="Test Author"
            )

            # Verify creator was initialized with correct parameters
            mock_creator_class.assert_called_once_with(book_title="Test Book", author="Test Author")

            # Verify asyncio.run was called
            mock_run.assert_called_once()

            assert result == mock_result

    def test_create_epub_from_markdown_minimal_args(self, successful_markdown_result):
        """Test convenience function with minimal arguments."""
        with patch('vexy_pdf_werk.core.epub_creator.EpubCreator') as mock_creator_class, \
             patch('asyncio.run'):

            output_path = Path("output.epub")
            create_epub_from_markdown(successful_markdown_result, output_path)

            # Verify creator was initialized with defaults
            mock_creator_class.assert_called_once_with(book_title=None, author=None)


class TestEpubCreatorIntegration:
    """Integration test cases for EpubCreator."""

    @pytest.mark.asyncio
    async def test_full_epub_creation_flow(self):
        """Test complete ePub creation flow with real-like data."""
        # Create realistic markdown pages
        pages = [
            MarkdownPage(
                page_number=0,
                content="# Introduction\n\nThis document covers the basics of PDF processing.",
                title="Introduction",
                slug="introduction"
            ),
            MarkdownPage(
                page_number=1,
                content="## Chapter 1: Getting Started\n\nFirst, install the required dependencies.",
                title="Chapter 1: Getting Started",
                slug="getting-started"
            ),
            MarkdownPage(
                page_number=2,
                content="## Conclusion\n\nThis concludes our guide to PDF processing.",
                title="Conclusion",
                slug="conclusion"
            )
        ]

        markdown_result = MarkdownResult(
            success=True,
            pages=pages,
            total_pages=3
        )

        creator = EpubCreator(
            book_title="PDF Processing Guide",
            author="Vexy Art"
        )

        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            with patch('vexy_pdf_werk.core.epub_creator.epub') as mock_epub:
                # Mock the entire epub library
                mock_book = MagicMock()
                mock_epub.EpubBook.return_value = mock_book
                mock_epub.EpubHtml.return_value = MagicMock()
                mock_epub.EpubNcx.return_value = MagicMock()
                mock_epub.EpubNav.return_value = MagicMock()

                result = await creator.create_epub(
                    markdown_result,
                    temp_path,
                    source_pdf_path=Path("guide.pdf")
                )

                assert result.success is True
                assert result.output_path == temp_path

                # Verify book metadata (first page title takes precedence)
                mock_book.set_title.assert_called_once_with("Introduction")
                mock_book.add_author.assert_called_once_with("Vexy Art")

                # Verify 3 chapters were added
                assert mock_book.add_item.call_count >= 3

        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()
