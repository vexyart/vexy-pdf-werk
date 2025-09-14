##### PDF Processor Tests (`tests/unit/test_pdf_processor.py`)

```python
## 58. this_file: tests/unit/test_pdf_processor.py

"""Unit tests for PDF processor."""

import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest

from vexy_pdf_werk.core.pdf_processor import PDFProcessor, PDFInfo, ProcessingResult
from vexy_pdf_werk.config import VPWConfig


class TestPDFProcessor:
    """Test PDF processor functionality."""

    @pytest.fixture
    def pdf_processor(self, default_config):
        """Create PDF processor with mocked external tools."""
        with patch('shutil.which') as mock_which:
            # Mock external tools as available
            mock_which.side_effect = lambda tool: f"/usr/bin/{tool}"
            processor = PDFProcessor(default_config)
            return processor

    @pytest.mark.asyncio
    async def test_analyze_pdf_basic(self, pdf_processor, sample_pdf):
        """Test basic PDF analysis."""
        with patch('pikepdf.open') as mock_open:
            # Mock PDF structure
            mock_pdf = Mock()
            mock_pdf.pages = [Mock(), Mock()]  # 2 pages
            mock_pdf.docinfo = {
                '/Title': 'Test Document',
                '/Author': 'Test Author'
            }
            mock_open.return_value.__enter__.return_value = mock_pdf

            pdf_info = await pdf_processor.analyze_pdf(sample_pdf)

            assert pdf_info.path == sample_pdf
            assert pdf_info.pages == 2
            assert pdf_info.title == 'Test Document'
            assert pdf_info.author == 'Test Author'

    @pytest.mark.asyncio
    async def test_analyze_pdf_no_metadata(self, pdf_processor, sample_pdf):
        """Test PDF analysis without metadata."""
        with patch('pikepdf.open') as mock_open:
            mock_pdf = Mock()
            mock_pdf.pages = [Mock()]
            mock_pdf.docinfo = {}  # No metadata
            mock_open.return_value.__enter__.return_value = mock_pdf

            pdf_info = await pdf_processor.analyze_pdf(sample_pdf)

            assert pdf_info.pages == 1
            assert pdf_info.title is None
            assert pdf_info.author is None

    @pytest.mark.asyncio
    async def test_create_better_pdf_success(self, pdf_processor, sample_pdf, temp_dir):
        """Test successful PDF processing."""
        output_pdf = temp_dir / "output.pdf"

        # Mock the analyze_pdf method
        mock_pdf_info = PDFInfo(
            path=sample_pdf,
            pages=1,
            has_text=True,
            is_scanned=False,
            has_images=False,
            title="Test PDF"
        )

        with patch.object(pdf_processor, 'analyze_pdf', return_value=mock_pdf_info), \
             patch.object(pdf_processor, '_convert_to_pdfa', new_callable=AsyncMock) as mock_convert:

            # Mock successful conversion
            mock_convert.return_value = None

            # Create empty output file to simulate successful processing
            output_pdf.touch()

            result = await pdf_processor.create_better_pdf(sample_pdf, output_pdf)

            assert result.success is True
            assert result.output_path == output_pdf
            assert result.pdf_info == mock_pdf_info
            assert result.processing_time > 0

    @pytest.mark.asyncio
    async def test_create_better_pdf_failure(self, pdf_processor, sample_pdf, temp_dir):
        """Test PDF processing failure handling."""
        output_pdf = temp_dir / "output.pdf"

        with patch.object(pdf_processor, 'analyze_pdf', side_effect=RuntimeError("PDF corrupt")):
            result = await pdf_processor.create_better_pdf(sample_pdf, output_pdf)

            assert result.success is False
            assert result.error == "PDF corrupt"
            assert result.output_path is None

    @pytest.mark.asyncio
    async def test_enhance_with_ocr(self, pdf_processor, sample_pdf, temp_dir):
        """Test OCR enhancement process."""
        output_pdf = temp_dir / "ocr_output.pdf"
        pdf_info = PDFInfo(sample_pdf, 1, False, True, False)

        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock successful OCRmyPDF execution
            mock_process = Mock()
            mock_process.communicate.return_value = (b"Success", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Create output file to simulate OCRmyPDF success
            output_pdf.touch()

            await pdf_processor._enhance_with_ocr(sample_pdf, output_pdf, pdf_info)

            # Verify OCRmyPDF was called with correct arguments
            args, kwargs = mock_subprocess.call_args
            assert "ocrmypdf" in args[0]
            assert str(sample_pdf) in args[0]
            assert str(output_pdf) in args[0]

    @pytest.mark.asyncio
    async def test_enhance_with_ocr_failure(self, pdf_processor, sample_pdf, temp_dir):
        """Test OCR enhancement failure handling."""
        output_pdf = temp_dir / "ocr_output.pdf"
        pdf_info = PDFInfo(sample_pdf, 1, False, True, False)

        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock OCRmyPDF failure
            mock_process = Mock()
            mock_process.communicate.return_value = (b"", b"OCR failed")
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process

            with pytest.raises(RuntimeError, match="OCR processing failed"):
                await pdf_processor._enhance_with_ocr(sample_pdf, output_pdf, pdf_info)


class TestPDFInfo:
    """Test PDFInfo dataclass."""

    def test_pdf_info_creation(self):
        """Test PDFInfo object creation."""
        path = Path("test.pdf")
        info = PDFInfo(
            path=path,
            pages=10,
            has_text=True,
            is_scanned=False,
            has_images=True,
            title="Test Document"
        )

        assert info.path == path
        assert info.pages == 10
        assert info.has_text is True
        assert info.is_scanned is False
        assert info.has_images is True
        assert info.title == "Test Document"

    def test_pdf_info_defaults(self):
        """Test PDFInfo with default values."""
        info = PDFInfo(
            path=Path("test.pdf"),
            pages=1,
            has_text=False,
            is_scanned=True,
            has_images=False
        )

        assert info.title is None
        assert info.author is None
        assert info.creation_date is None
```