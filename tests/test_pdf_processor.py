# this_file: tests/test_pdf_processor.py
"""Tests for PDF processor functionality."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pikepdf
import pytest

from vexy_pdf_werk.config import VPWConfig
from vexy_pdf_werk.core.pdf_processor import PDFInfo, PDFProcessor


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
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

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
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

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
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

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
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

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
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

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
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

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

    @pytest.mark.asyncio
    async def test_enhance_with_ai_structure_workflow(self, processor, sample_pdf, caplog):
        """Test the full workflow of _enhance_with_ai_structure."""
        from unittest.mock import AsyncMock, MagicMock

        output_path = Path(tempfile.mktemp(suffix=".pdf"))

        # Mock the AI Service
        mock_ai_service = AsyncMock()
        mock_ai_service.enhance_pdf_structure.return_value = "- old\n+ new"
        
        with patch('vexy_pdf_werk.core.pdf_processor.AIServiceFactory.create_service') as mock_create_service:
            mock_create_service.return_value = mock_ai_service

            # Mock the QDFProcessor methods
            with patch.object(processor.qdf_processor, 'pdf_to_qdf_json', new_callable=AsyncMock) as mock_to_json, \
                 patch.object(processor.qdf_processor, 'extract_text_from_qdf') as mock_extract_text, \
                 patch.object(processor.qdf_processor, 'apply_diff_to_qdf') as mock_apply_diff:

                # Setup mock return values
                mock_to_json.return_value = {"is_qdf": True}
                mock_extract_text.return_value = "some text"
                mock_apply_diff.return_value = {"is_updated_qdf": True}

                # Check that the placeholder warning is logged
                import logging
                from loguru import logger
                caplog.set_level(logging.WARNING)
                handler_id = logger.add(caplog.handler, format="{message}")

                # Call the method
                await processor._enhance_with_ai_structure(sample_pdf, output_path)

                logger.remove(handler_id)

                assert "QDF merging not yet implemented" in caplog.text

                # Assertions
                assert mock_create_service.called
                
                # With a 1-page PDF, these should be called once
                mock_to_json.assert_called_once_with(sample_pdf, 0)
                mock_extract_text.assert_called_once_with({"is_qdf": True})
                mock_ai_service.enhance_pdf_structure.assert_called_once_with("some text")
                mock_apply_diff.assert_called_once_with({"is_qdf": True}, "- old\n+ new")
                
                # Check that the final PDF was saved
                assert output_path.exists()

        if output_path.exists():
            output_path.unlink()

    @pytest.mark.asyncio
    async def test_enhance_with_ai_structure_no_ai_service(self, processor, sample_pdf):
        """Test that enhance_with_ai_structure handles unavailable AI service gracefully."""
        output_path = Path(tempfile.mktemp(suffix=".pdf"))

        with patch('vexy_pdf_werk.core.pdf_processor.AIServiceFactory.create_service') as mock_create_service:
            mock_create_service.return_value = None  # No AI service available

            await processor._enhance_with_ai_structure(sample_pdf, output_path)

            # Should just copy the input to output
            assert output_path.exists()
            assert output_path.stat().st_size > 0

        if output_path.exists():
            output_path.unlink()

    @pytest.mark.asyncio
    async def test_enhance_with_ai_structure_empty_diff(self, processor, sample_pdf):
        """Test handling when AI service returns empty diff."""
        from unittest.mock import AsyncMock

        output_path = Path(tempfile.mktemp(suffix=".pdf"))

        # Mock AI service to return empty diff
        mock_ai_service = AsyncMock()
        mock_ai_service.enhance_pdf_structure.return_value = ""

        with patch('vexy_pdf_werk.core.pdf_processor.AIServiceFactory.create_service') as mock_create_service:
            mock_create_service.return_value = mock_ai_service

            # Mock QDF processor methods
            with patch.object(processor.qdf_processor, 'pdf_to_qdf_json', new_callable=AsyncMock) as mock_to_json, \
                 patch.object(processor.qdf_processor, 'extract_text_from_qdf') as mock_extract_text, \
                 patch.object(processor.qdf_processor, 'apply_diff_to_qdf') as mock_apply_diff:

                mock_to_json.return_value = {"test": "qdf"}
                mock_extract_text.return_value = "some text content"
                mock_apply_diff.return_value = {"test": "qdf"}

                await processor._enhance_with_ai_structure(sample_pdf, output_path)

                # Should process but not apply diff due to empty response
                mock_ai_service.enhance_pdf_structure.assert_called_once()
                # apply_diff should not be called with empty diff
                mock_apply_diff.assert_not_called()

        if output_path.exists():
            output_path.unlink()

    @pytest.mark.asyncio
    async def test_enhance_with_ai_structure_no_text_content(self, processor, sample_pdf):
        """Test handling when PDF page has no extractable text."""
        from unittest.mock import AsyncMock

        output_path = Path(tempfile.mktemp(suffix=".pdf"))

        mock_ai_service = AsyncMock()
        mock_ai_service.enhance_pdf_structure.return_value = "+ new content"

        with patch('vexy_pdf_werk.core.pdf_processor.AIServiceFactory.create_service') as mock_create_service:
            mock_create_service.return_value = mock_ai_service

            with patch.object(processor.qdf_processor, 'pdf_to_qdf_json', new_callable=AsyncMock) as mock_to_json, \
                 patch.object(processor.qdf_processor, 'extract_text_from_qdf') as mock_extract_text:

                mock_to_json.return_value = {"test": "qdf"}
                mock_extract_text.return_value = ""  # No text content

                await processor._enhance_with_ai_structure(sample_pdf, output_path)

                # Should not call AI service for pages with no text
                mock_ai_service.enhance_pdf_structure.assert_not_called()

        if output_path.exists():
            output_path.unlink()

    @pytest.mark.asyncio
    async def test_enhance_with_ai_structure_ai_service_error(self, processor, sample_pdf, caplog):
        """Test handling when AI service throws an exception."""
        from unittest.mock import AsyncMock
        import logging
        from loguru import logger

        output_path = Path(tempfile.mktemp(suffix=".pdf"))

        # Mock AI service to throw exception
        mock_ai_service = AsyncMock()
        mock_ai_service.enhance_pdf_structure.side_effect = Exception("AI service error")

        caplog.set_level(logging.ERROR)
        handler_id = logger.add(caplog.handler, format="{message}")

        with patch('vexy_pdf_werk.core.pdf_processor.AIServiceFactory.create_service') as mock_create_service:
            mock_create_service.return_value = mock_ai_service

            with patch.object(processor.qdf_processor, 'pdf_to_qdf_json', new_callable=AsyncMock) as mock_to_json, \
                 patch.object(processor.qdf_processor, 'extract_text_from_qdf') as mock_extract_text:

                mock_to_json.return_value = {"test": "qdf"}
                mock_extract_text.return_value = "some text"

                await processor._enhance_with_ai_structure(sample_pdf, output_path)

                logger.remove(handler_id)

                # Should handle error gracefully and continue processing
                assert "AI service failed for page 1 after" in caplog.text
                assert output_path.exists()

        if output_path.exists():
            output_path.unlink()

    @pytest.mark.asyncio
    async def test_enhance_with_ai_structure_qdf_conversion_error(self, processor, sample_pdf, caplog):
        """Test handling when QDF conversion fails."""
        from unittest.mock import AsyncMock
        import logging
        from loguru import logger

        output_path = Path(tempfile.mktemp(suffix=".pdf"))

        mock_ai_service = AsyncMock()
        mock_ai_service.enhance_pdf_structure.return_value = "+ enhanced content"

        caplog.set_level(logging.ERROR)
        handler_id = logger.add(caplog.handler, format="{message}")

        with patch('vexy_pdf_werk.core.pdf_processor.AIServiceFactory.create_service') as mock_create_service:
            mock_create_service.return_value = mock_ai_service

            # Mock QDF processor to throw exception
            with patch.object(processor.qdf_processor, 'pdf_to_qdf_json', new_callable=AsyncMock) as mock_to_json:
                mock_to_json.side_effect = RuntimeError("QDF conversion failed")

                await processor._enhance_with_ai_structure(sample_pdf, output_path)

                logger.remove(handler_id)

                # Should handle QDF error and still produce output
                assert "QDF conversion failed for page 1:" in caplog.text
                assert output_path.exists()

        if output_path.exists():
            output_path.unlink()
