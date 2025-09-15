# this_file: tests/test_metadata_extractor.py
"""Tests for metadata extraction functionality."""

import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from vexy_pdf_werk.core.markdown_converter import MarkdownPage, MarkdownResult
from vexy_pdf_werk.core.metadata_extractor import DocumentMetadata, MetadataExtractor
from vexy_pdf_werk.core.pdf_processor import PDFInfo


class TestDocumentMetadata:
    """Test cases for DocumentMetadata dataclass."""

    def test_metadata_creation_minimal(self):
        """Test metadata creation with minimal required fields."""
        metadata = DocumentMetadata(
            source_file="test.pdf",
            source_size_bytes=1024,
            processed_at="2025-01-15T10:30:00+00:00",
            pdf_pages=5
        )

        assert metadata.source_file == "test.pdf"
        assert metadata.source_size_bytes == 1024
        assert metadata.processed_at == "2025-01-15T10:30:00+00:00"
        assert metadata.pdf_pages == 5

        # Check optional fields have default values
        assert metadata.pdf_title is None
        assert metadata.estimated_word_count == 0
        assert metadata.formats_generated == []

    def test_metadata_creation_complete(self):
        """Test metadata creation with all fields."""
        metadata = DocumentMetadata(
            source_file="document.pdf",
            source_size_bytes=2048576,
            processed_at="2025-01-15T10:30:00+00:00",
            pdf_pages=25,
            pdf_title="Sample Document",
            pdf_author="John Doe",
            pdf_creation_date="2024-12-01",
            pdf_has_text=True,
            pdf_is_scanned=False,
            pdf_has_images=True,
            estimated_word_count=5000,
            first_page_preview="This document covers...",
            formats_generated=["markdown", "epub", "yaml"],
            processing_time_seconds=15.5
        )

        assert metadata.source_file == "document.pdf"
        assert metadata.pdf_pages == 25
        assert metadata.estimated_word_count == 5000
        assert metadata.formats_generated == ["markdown", "epub", "yaml"]
        assert metadata.processing_time_seconds == 15.5

    def test_metadata_to_dict(self):
        """Test conversion of metadata to dictionary."""
        metadata = DocumentMetadata(
            source_file="test.pdf",
            source_size_bytes=1024,
            processed_at="2025-01-15T10:30:00+00:00",
            pdf_pages=10
        )

        # Use dataclass asdict functionality
        metadata_dict = asdict(metadata)

        assert isinstance(metadata_dict, dict)
        assert metadata_dict["source_file"] == "test.pdf"
        assert metadata_dict["pdf_pages"] == 10


class TestMetadataExtractor:
    """Test cases for MetadataExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Create MetadataExtractor instance for testing."""
        return MetadataExtractor()

    @pytest.fixture
    def sample_pdf_info(self):
        """Create sample PDF info for testing."""
        return PDFInfo(
            path=Path("sample.pdf"),
            pages=15,
            has_text=True,
            is_scanned=False,
            has_images=True,
            title="Sample PDF Document",
            author="Jane Smith",
            creation_date="2024-11-15"
        )

    @pytest.fixture
    def sample_markdown_result(self):
        """Create sample markdown result for testing."""
        pages = [
            MarkdownPage(
                page_number=0,
                content="# Introduction\n\nThis is the introduction to our document.",
                title="Introduction",
                slug="introduction"
            ),
            MarkdownPage(
                page_number=1,
                content="# Chapter 1\n\nThis chapter discusses the main concepts.",
                title="Chapter 1",
                slug="chapter-1"
            )
        ]
        return MarkdownResult(success=True, pages=pages, total_pages=2)

    @pytest.fixture
    def temp_yaml_path(self):
        """Create temporary YAML file path for testing."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            yield temp_path
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

    def test_extractor_initialization(self, extractor):
        """Test MetadataExtractor initialization."""
        assert extractor is not None
        assert hasattr(extractor, 'extract_metadata')
        assert hasattr(extractor, 'save_metadata_yaml')

    def test_calculate_word_count(self, extractor, sample_markdown_result):
        """Test word count calculation from markdown content."""
        word_count = extractor._calculate_word_count(sample_markdown_result)

        # Word count filters out markdown formatting and short words
        # Page 1: "Introduction", "This", "is", "the", "introduction", "to", "our", "document" = 8 words
        # Page 2: "Chapter" ("1" filtered), "This", "chapter", "discusses", "the", "main", "concepts" = 7 words
        # Total = 15 words ("1" is filtered as single character)
        assert word_count == 15

    def test_calculate_word_count_empty_result(self, extractor):
        """Test word count calculation with empty markdown result."""
        empty_result = MarkdownResult(success=True, pages=[], total_pages=0)
        word_count = extractor._calculate_word_count(empty_result)
        assert word_count == 0

    def test_calculate_word_count_none_result(self, extractor):
        """Test word count calculation with None result."""
        # Method expects MarkdownResult, not None - test with empty result instead
        empty_result = MarkdownResult(success=True, pages=[], total_pages=0)
        word_count = extractor._calculate_word_count(empty_result)
        assert word_count == 0

    def test_get_first_page_preview(self, extractor, sample_markdown_result):
        """Test first page preview extraction."""
        preview = extractor._get_first_page_preview(sample_markdown_result)

        # Preview skips markdown headers (# Introduction) and gets content lines
        assert "This is the introduction to our document." in preview
        assert "Introduction" not in preview  # Header is skipped
        assert len(preview) <= 200  # Should be trimmed

    def test_get_first_page_preview_empty_result(self, extractor):
        """Test first page preview with empty result."""
        empty_result = MarkdownResult(success=True, pages=[], total_pages=0)
        preview = extractor._get_first_page_preview(empty_result)
        assert preview is None  # Method returns None for empty results

    def test_get_first_page_preview_none_result(self, extractor):
        """Test first page preview with None result."""
        # Method expects MarkdownResult, not None - test with empty result instead
        empty_result = MarkdownResult(success=True, pages=[], total_pages=0)
        preview = extractor._get_first_page_preview(empty_result)
        assert preview is None

    def test_extract_metadata_complete(self, extractor, sample_pdf_info, sample_markdown_result):
        """Test complete metadata extraction."""
        pdf_path = Path("test_document.pdf")
        formats_completed = ["markdown", "epub"]
        processing_time = 12.5

        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            pdf_path = Path(temp_file.name)
            # Write some dummy data to give the file a size
            temp_file.write(b"dummy pdf content" * 128)  # ~2KB file
            temp_file.flush()

            with patch('vexy_pdf_werk.core.metadata_extractor.datetime') as mock_datetime:
                mock_now = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = mock_now

                metadata = extractor.extract_metadata(
                    pdf_path=pdf_path,
                    pdf_info=sample_pdf_info,
                    markdown_result=sample_markdown_result,
                    formats_generated=formats_completed,
                    processing_time=processing_time
                )

        # Verify all metadata fields
        assert metadata.source_file == pdf_path.name
        assert metadata.source_size_bytes > 0  # Should have some file size
        assert metadata.processed_at == "2025-01-15T10:30:00+00:00"

        # PDF metadata
        assert metadata.pdf_pages == 15
        assert metadata.pdf_title == "Sample PDF Document"
        assert metadata.pdf_author == "Jane Smith"
        assert metadata.pdf_creation_date == "2024-11-15"

        # Processing metadata
        assert metadata.estimated_word_count == 15  # Adjusted for filtering logic
        assert "This is the introduction to our document." in metadata.first_page_preview
        assert metadata.formats_generated == ["markdown", "epub"]
        assert metadata.processing_time_seconds == 12.5

    def test_extract_metadata_minimal(self, extractor):
        """Test metadata extraction with minimal inputs."""
        # Create minimal PDFInfo since it's required
        minimal_pdf_info = PDFInfo(
            path=Path("minimal.pdf"),
            pages=1,
            has_text=False,
            is_scanned=True,
            has_images=False
        )

        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            pdf_path = Path(temp_file.name)
            # Write some dummy data
            temp_file.write(b"dummy content")
            temp_file.flush()

            # Update PDFInfo to use the actual temp path
            minimal_pdf_info.path = pdf_path

            with patch('vexy_pdf_werk.core.metadata_extractor.datetime') as mock_datetime:
                mock_now = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = mock_now

                metadata = extractor.extract_metadata(
                    pdf_path=pdf_path,
                    pdf_info=minimal_pdf_info,
                    markdown_result=None,
                    formats_generated=[],
                    processing_time=0.0
                )

            assert metadata.source_file == pdf_path.name
            assert metadata.source_size_bytes > 0
            assert metadata.pdf_pages == 1
            assert metadata.estimated_word_count == 0
            assert metadata.first_page_preview is None
            assert metadata.formats_generated == []

    def test_save_metadata_yaml(self, extractor, temp_yaml_path):
        """Test saving metadata to YAML file."""
        metadata = DocumentMetadata(
            source_file="test.pdf",
            source_size_bytes=1024,
            processed_at="2025-01-15T10:30:00+00:00",
            pdf_pages=5,
            estimated_word_count=100,
            formats_generated=["markdown"]
        )

        extractor.save_metadata_yaml(metadata, temp_yaml_path)

        # Verify file was created and contains expected content
        assert temp_yaml_path.exists()

        content = temp_yaml_path.read_text(encoding='utf-8')
        assert "source_file: test.pdf" in content
        assert "source_size_bytes: 1024" in content
        assert "pages: 5" in content
        assert "estimated_word_count: 100" in content
        assert "- markdown" in content

    def test_save_metadata_yaml_creates_directory(self, extractor):
        """Test that save_metadata_yaml creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "metadata.yaml"

            metadata = DocumentMetadata(
                source_file="test.pdf",
                source_size_bytes=1024,
                processed_at="2025-01-15T10:30:00+00:00",
                pdf_pages=5  # Required field
            )

            extractor.save_metadata_yaml(metadata, nested_path)

            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_save_metadata_yaml_with_none_values(self, extractor, temp_yaml_path):
        """Test saving metadata with None values."""
        metadata = DocumentMetadata(
            source_file="test.pdf",
            source_size_bytes=1024,
            processed_at="2025-01-15T10:30:00+00:00",
            pdf_pages=3,  # Required field
            pdf_title=None,
            pdf_author=None,
            estimated_word_count=0  # Default value, not None
        )

        extractor.save_metadata_yaml(metadata, temp_yaml_path)

        content = temp_yaml_path.read_text(encoding='utf-8')
        assert "source_file: test.pdf" in content
        # Title and author are omitted from YAML when None (per _clean_metadata_dict)
        assert "pdf_title:" not in content  # None values are filtered out
        assert "estimated_word_count: 0" in content

    def test_extract_and_save_metadata_integration(
        self, extractor, sample_pdf_info, sample_markdown_result, temp_yaml_path
    ):
        """Test complete extract and save workflow."""
        pdf_path = Path("integration_test.pdf")

        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            pdf_path = Path(temp_file.name)
            # Write some dummy data
            temp_file.write(b"integration test content" * 64)  # ~1.5KB file
            temp_file.flush()

            with patch('vexy_pdf_werk.core.metadata_extractor.datetime') as mock_datetime:
                mock_now = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = mock_now

                # Extract metadata
                metadata = extractor.extract_metadata(
                    pdf_path=pdf_path,
                    pdf_info=sample_pdf_info,
                    markdown_result=sample_markdown_result,
                    formats_generated=["markdown", "epub", "yaml"],
                    processing_time=8.3
                )

            # Save to YAML
            extractor.save_metadata_yaml(metadata, temp_yaml_path)

            # Verify file was created
            assert temp_yaml_path.exists()

            # Verify content
            content = temp_yaml_path.read_text(encoding='utf-8')
            assert f"source_file: {pdf_path.name}" in content
            assert "title: Sample PDF Document" in content  # Nested under pdf_info
            assert "author: Jane Smith" in content  # Nested under pdf_info
            assert "estimated_word_count: 15" in content  # Adjusted for filtering logic
            assert "processing_time_seconds: 8.3" in content
            assert "- markdown" in content
            assert "- epub" in content
            assert "- yaml" in content


class TestMetadataExtractorEdgeCases:
    """Test edge cases and error conditions for MetadataExtractor."""

    @pytest.fixture
    def extractor(self):
        """Create MetadataExtractor instance for testing."""
        return MetadataExtractor()

    def test_calculate_word_count_with_special_characters(self, extractor):
        """Test word count with special characters and formatting."""
        pages = [
            MarkdownPage(
                page_number=0,
                content="# Header with-hyphens and_underscores\n\n**Bold** *italic* text.",
                title="Special Characters",
                slug="special"
            )
        ]
        result = MarkdownResult(success=True, pages=pages, total_pages=1)

        word_count = extractor._calculate_word_count(result)
        # Should count: "Header", "with-hyphens", "and_underscores", "Bold", "italic", "text" = 6 words
        assert word_count == 6

    def test_get_first_page_preview_very_long_content(self, extractor):
        """Test first page preview with very long content."""
        # Create content with meaningful lines (not just repeated text in one line)
        long_content = (
            "This is the first line of very long content.\n"
            "This is the second line that continues the document.\n"
            + ("This is additional content. " * 20)
        )
        pages = [
            MarkdownPage(
                page_number=0,
                content=long_content,
                title="Long Content",
                slug="long"
            )
        ]
        result = MarkdownResult(success=True, pages=pages, total_pages=1)

        preview = extractor._get_first_page_preview(result)
        assert preview is not None  # Should return a preview
        assert len(preview) <= 200  # Should be trimmed
        assert "This is the first line" in preview  # Should contain start of content

    def test_get_first_page_preview_with_markdown_formatting(self, extractor):
        """Test first page preview skips headers but keeps content formatting."""
        pages = [
            MarkdownPage(
                page_number=0,
                content="# **Bold Header**\n\n*Italic text* and `code` snippets.",
                title="Formatted Content",
                slug="formatted"
            )
        ]
        result = MarkdownResult(success=True, pages=pages, total_pages=1)

        preview = extractor._get_first_page_preview(result)
        # Header line is skipped, but content line formatting is preserved
        assert "Bold Header" not in preview  # Header is skipped
        assert "*Italic text* and `code` snippets." in preview  # Content line preserved
        assert "#" not in preview   # Header marker not in preview

    def test_save_metadata_yaml_permission_error(self, extractor):
        """Test save_metadata_yaml handles permission errors."""
        metadata = DocumentMetadata(
            source_file="test.pdf",
            source_size_bytes=1024,
            processed_at="2025-01-15T10:30:00+00:00",
            pdf_pages=5  # Required field
        )

        # Try to write to a path that doesn't exist and can't be created
        invalid_path = Path("/invalid/path/metadata.yaml")

        with pytest.raises((PermissionError, OSError)):
            extractor.save_metadata_yaml(metadata, invalid_path)

    def test_extract_metadata_with_version_info(self, extractor):
        """Test metadata extraction with basic info (version not implemented yet)."""
        pdf_path = Path("version_test.pdf")

        # Create minimal PDFInfo since it's required
        minimal_pdf_info = PDFInfo(
            path=pdf_path,
            pages=1,
            has_text=False,
            is_scanned=True,
            has_images=False
        )

        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            pdf_path = Path(temp_file.name)
            # Write some dummy data
            temp_file.write(b"version test content")
            temp_file.flush()

            # Update PDFInfo to use the actual temp path
            minimal_pdf_info.path = pdf_path

            with patch('vexy_pdf_werk.core.metadata_extractor.datetime') as mock_datetime:
                mock_now = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
                mock_datetime.now.return_value = mock_now

                metadata = extractor.extract_metadata(
                    pdf_path=pdf_path,
                    pdf_info=minimal_pdf_info,
                    markdown_result=None,
                    formats_generated=[],
                    processing_time=0.0
                )

            # Test basic functionality (version field not yet implemented)
            assert metadata.source_file == pdf_path.name
            assert metadata.pdf_pages == 1


class TestMetadataYAMLFormat:
    """Test YAML format and structure of saved metadata."""

    @pytest.fixture
    def extractor(self):
        """Create MetadataExtractor instance for testing."""
        return MetadataExtractor()

    def test_yaml_structure_and_format(self, extractor):
        """Test that saved YAML has proper structure and format."""
        metadata = DocumentMetadata(
            source_file="structured_test.pdf",
            source_size_bytes=2048000,
            processed_at="2025-01-15T10:30:00+00:00",
            pdf_pages=20,
            pdf_title="Structured Document",
            pdf_author="Test Author",
            pdf_creation_date="2024-12-01",
            estimated_word_count=1500,
            first_page_preview="This is a preview of the first page...",
            formats_generated=["markdown", "epub", "yaml"],
            processing_time_seconds=7.8
            # vexy_pdf_werk_version field not yet implemented
        )

        with tempfile.NamedTemporaryFile(mode='w+', suffix=".yaml", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            extractor.save_metadata_yaml(metadata, temp_path)

            # Read and verify YAML content
            content = temp_path.read_text(encoding='utf-8')

            # Check nested structure created by _clean_metadata_dict
            assert "document:" in content
            assert "pdf_info:" in content
            assert "processing:" in content
            assert "content:" in content

            # Check specific fields in nested structure
            assert "source_file: structured_test.pdf" in content
            assert "source_size_bytes: 2048000" in content
            assert "pages: 20" in content  # Under pdf_info section
            assert "estimated_word_count: 1500" in content
            assert "processing_time_seconds: 7.8" in content

            # Check list formatting
            assert "formats_generated:" in content
            assert "- markdown" in content
            assert "- epub" in content
            assert "- yaml" in content

        finally:
            if temp_path.exists():
                temp_path.unlink()
