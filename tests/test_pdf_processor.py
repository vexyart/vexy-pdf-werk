# this_file: tests/test_pdf_processor.py
"""Tests for PDF processor functionality."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import pikepdf

from vexy_pdf_werk.config import VPWConfig
from vexy_pdf_werk.core.pdf_processor import PDFProcessor, PDFInfo


class TestPDFProcessor:
    """Test cases for PDFProcessor class."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return VPWConfig()

    @pytest.fixture
    def processor(self, config):
        """Create a PDFProcessor instance."""
        with patch('vexy_pdf_werk.core.pdf_processor.find_tool_path') as mock_find_tool:
            mock_find_tool.return_value = "/usr/bin/mock-tool"
            return PDFProcessor(config)

    @pytest.fixture
    def sample_pdf(self):
        """Create a sample PDF file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Create a minimal PDF using a simpler approach
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            # Create PDF with reportlab
            c = canvas.Canvas(temp_file.name, pagesize=letter)
            c.setTitle("Test Document")
            c.setAuthor("Test Author")
            c.drawString(100, 750, "Test PDF Content")
            c.showPage()
            c.save()

            yield Path(temp_file.name)

            # Cleanup
            Path(temp_file.name).unlink()

    @pytest.mark.asyncio
    async def test_analyze_pdf_basic_properties(self, processor, sample_pdf):
        """Test PDF analysis returns correct basic properties."""
        pdf_info = await processor.analyze_pdf(sample_pdf)

        assert isinstance(pdf_info, PDFInfo)
        assert pdf_info.path == sample_pdf
        assert pdf_info.pages >= 1
        assert pdf_info.title == 'Test Document'
        assert pdf_info.author == 'Test Author'
        assert pdf_info.creation_date is not None

    @pytest.mark.asyncio
    async def test_analyze_pdf_content_detection(self, processor, sample_pdf):
        """Test PDF analysis detects content characteristics."""
        pdf_info = await processor.analyze_pdf(sample_pdf)

        # These assertions depend on the PDF structure we created
        assert isinstance(pdf_info.has_text, bool)
        assert isinstance(pdf_info.is_scanned, bool)
        assert isinstance(pdf_info.has_images, bool)

    @pytest.mark.asyncio
    async def test_analyze_pdf_with_invalid_file(self, processor):
        """Test PDF analysis with invalid file raises appropriate error."""
        invalid_path = Path("/nonexistent/file.pdf")

        with pytest.raises((FileNotFoundError, RuntimeError)):
            await processor.analyze_pdf(invalid_path)

    @pytest.mark.asyncio
    async def test_analyze_pdf_with_corrupted_file(self, processor):
        """Test PDF analysis with corrupted file raises appropriate error."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Write invalid PDF content
            temp_file.write(b"Not a PDF file")
            temp_file.flush()

            corrupted_path = Path(temp_file.name)

            try:
                with pytest.raises((ValueError, RuntimeError)):
                    await processor.analyze_pdf(corrupted_path)
            finally:
                corrupted_path.unlink()

    @pytest.mark.asyncio
    async def test_analyze_pdf_with_metadata_missing(self, processor):
        """Test PDF analysis handles missing metadata gracefully."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Create PDF without metadata
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            c = canvas.Canvas(temp_file.name, pagesize=letter)
            # Don't set title/author to test missing metadata
            c.drawString(100, 750, "PDF without metadata")
            c.showPage()
            c.save()

            pdf_path = Path(temp_file.name)

            try:
                pdf_info = await processor.analyze_pdf(pdf_path)

                # Reportlab sets default metadata, so check for defaults or None
                assert pdf_info.title in [None, '', 'untitled']
                assert pdf_info.author in [None, '', 'anonymous']
                assert pdf_info.pages == 1
            finally:
                pdf_path.unlink()

    def test_processor_initialization_with_missing_tools(self, config):
        """Test processor initialization fails gracefully with missing external tools."""
        with patch('vexy_pdf_werk.core.pdf_processor.find_tool_path') as mock_find_tool:
            mock_find_tool.return_value = None  # Tool not found

            with pytest.raises(RuntimeError, match="Required tool.*not found"):
                PDFProcessor(config)

    def test_processor_initialization_with_custom_tool_paths(self):
        """Test processor initialization with custom tool paths in config."""
        config = VPWConfig()
        config.tesseract_path = "/custom/tesseract"
        config.qpdf_path = "/custom/qpdf"

        with patch('vexy_pdf_werk.core.pdf_processor.find_tool_path') as mock_find_tool:
            mock_find_tool.return_value = "/usr/bin/mock-tool"

            processor = PDFProcessor(config)
            assert processor.tesseract_cmd == "/custom/tesseract"

    @pytest.mark.asyncio
    async def test_analyze_pdf_performance_with_large_pdf(self, processor):
        """Test PDF analysis performs reasonably with larger PDFs."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Create PDF with multiple pages
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            c = canvas.Canvas(temp_file.name, pagesize=letter)
            c.setTitle('Large Test Document')

            # Add multiple pages to simulate larger document
            for i in range(10):
                c.drawString(100, 750, f"Page {i+1} content")
                c.showPage()

            c.save()

            pdf_path = Path(temp_file.name)

            try:
                import time
                start_time = time.time()

                pdf_info = await processor.analyze_pdf(pdf_path)

                end_time = time.time()
                analysis_time = end_time - start_time

                # Analysis should complete reasonably quickly (under 5 seconds)
                assert analysis_time < 5.0
                assert pdf_info.pages == 10

            finally:
                pdf_path.unlink()


class TestPDFInfoDataClass:
    """Test cases for PDFInfo dataclass."""

    def test_pdfinfo_creation(self):
        """Test PDFInfo can be created with all fields."""
        pdf_path = Path("/test/document.pdf")

        pdf_info = PDFInfo(
            path=pdf_path,
            pages=5,
            has_text=True,
            is_scanned=False,
            has_images=True,
            title="Test Document",
            author="Test Author",
            creation_date="2024-01-01"
        )

        assert pdf_info.path == pdf_path
        assert pdf_info.pages == 5
        assert pdf_info.has_text is True
        assert pdf_info.is_scanned is False
        assert pdf_info.has_images is True
        assert pdf_info.title == "Test Document"
        assert pdf_info.author == "Test Author"
        assert pdf_info.creation_date == "2024-01-01"

    def test_pdfinfo_optional_fields(self):
        """Test PDFInfo works with minimal required fields."""
        pdf_path = Path("/test/document.pdf")

        pdf_info = PDFInfo(
            path=pdf_path,
            pages=1,
            has_text=False,
            is_scanned=True,
            has_images=False
        )

        assert pdf_info.title is None
        assert pdf_info.author is None
        assert pdf_info.creation_date is None