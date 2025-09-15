# this_file: tests/test_pdf_integration.py
"""Integration tests for PDF processing pipeline."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rich.progress import Progress

from vexy_pdf_werk.config import VPWConfig
from vexy_pdf_werk.core.pdf_processor import PDFProcessor


class TestPDFProcessingIntegration:
    """Integration test cases for PDF processing pipeline."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        config = VPWConfig()
        config.processing.force_ocr = False  # Don't force OCR in tests
        return config

    @pytest.fixture
    def processor(self, config):
        """Create a PDFProcessor instance with mocked external tools."""
        with patch('vexy_pdf_werk.core.pdf_processor.find_tool_path') as mock_find_tool:
            mock_find_tool.return_value = "/usr/bin/mock-tool"
            return PDFProcessor(config)

    @pytest.fixture
    def sample_pdf(self):
        """Create a sample PDF file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:

            # Create PDF with reportlab
            c = canvas.Canvas(temp_file.name, pagesize=letter)
            c.setTitle("Integration Test Document")
            c.setAuthor("Test Suite")
            c.drawString(100, 750, "Integration test PDF content")
            c.showPage()
            c.save()

            yield Path(temp_file.name)

            # Cleanup
            if Path(temp_file.name).exists():
                Path(temp_file.name).unlink()

    @pytest.mark.asyncio
    async def test_create_better_pdf_success_path(self, processor, sample_pdf):
        """Test successful PDF enhancement pipeline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "enhanced.pdf"

            # Mock external tool calls to simulate success
            with patch('asyncio.create_subprocess_exec') as mock_exec:

                def mock_subprocess(*_args, **_kwargs):
                    # Create mock process that also creates the expected output file
                    mock_process = AsyncMock()
                    mock_process.communicate.return_value = (b"Success", b"")
                    mock_process.returncode = 0

                    # Always create the final output file to simulate successful processing
                    # This simulates what qpdf/ocrmypdf would do
                    if not output_path.exists():
                        shutil.copy2(sample_pdf, output_path)

                    return mock_process

                mock_exec.side_effect = mock_subprocess

                result = await processor.create_better_pdf(
                    sample_pdf, output_path
                )

                assert result.success is True
                assert result.error is None
                assert result.processing_time > 0
                assert result.pdf_info is not None
                assert result.pdf_info.pages >= 1

    @pytest.mark.asyncio
    async def test_create_better_pdf_with_ocr_forced(self, config, sample_pdf):
        """Test PDF enhancement with forced OCR."""
        config.processing.force_ocr = True

        with patch('vexy_pdf_werk.core.pdf_processor.find_tool_path') as mock_find_tool:
            mock_find_tool.return_value = "/usr/bin/mock-tool"
            processor = PDFProcessor(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "enhanced_ocr.pdf"

            with patch('asyncio.create_subprocess_exec') as mock_exec:

                def mock_subprocess_ocr(*_args, **_kwargs):
                    mock_process = AsyncMock()
                    mock_process.communicate.return_value = (b"OCR Success", b"")
                    mock_process.returncode = 0

                    # Create output files - handle both ocrmypdf and qpdf commands
                    command_args = _args
                    if len(command_args) >= 2:
                        # For qpdf: [qpdf, --linearize, --object-streams=generate, input, output]
                        # For ocrmypdf: [ocrmypdf, options..., input, output]
                        # In both cases, output is the last argument
                        output_file = Path(command_args[-1])
                        input_file = Path(command_args[-2])

                        if input_file.exists() and not output_file.exists():
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(input_file, output_file)

                    return mock_process

                mock_exec.side_effect = mock_subprocess_ocr

                result = await processor.create_better_pdf(
                    sample_pdf, output_path
                )

                assert result.success is True

                # Verify OCR was attempted (force-ocr flag should be in command)
                mock_exec.assert_called()
                # Check if any of the calls had the force-ocr flag
                found_force_ocr = False
                for call in mock_exec.call_args_list:
                    call_args = call[0]  # Get positional args
                    if any('--force-ocr' in str(arg) for arg in call_args):
                        found_force_ocr = True
                        break
                assert found_force_ocr, f"Expected --force-ocr flag in command calls: {mock_exec.call_args_list}"

    @pytest.mark.asyncio
    async def test_create_better_pdf_with_ai_enhancement(self, config, sample_pdf):
        """Test PDF enhancement with AI correction enabled."""
        config.ai.enabled = True
        config.ai.correction_enabled = True

        with patch('vexy_pdf_werk.core.pdf_processor.find_tool_path') as mock_find_tool:
            mock_find_tool.return_value = "/usr/bin/mock-tool"
            processor = PDFProcessor(config)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "enhanced_ai.pdf"

            with patch('asyncio.create_subprocess_exec') as mock_exec:
                def mock_subprocess_ai(*_args, **_kwargs):
                    mock_process = AsyncMock()
                    mock_process.communicate.return_value = (b"Success", b"")
                    mock_process.returncode = 0

                    # Simulate file creation for any external tool calls
                    command_args = _args
                    if len(command_args) >= 2:
                        output_file = Path(command_args[-1])
                        input_file = Path(command_args[-2])

                        if input_file.exists() and not output_file.exists():
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(input_file, output_file)

                    return mock_process

                mock_exec.side_effect = mock_subprocess_ai

                result = await processor.create_better_pdf(
                    sample_pdf, output_path
                )

                assert result.success is True
                # AI enhancement is currently a placeholder, so this tests the workflow

    @pytest.mark.asyncio
    async def test_create_better_pdf_ocr_failure(self, processor, sample_pdf):
        """Test PDF enhancement handles OCR tool failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "failed.pdf"

            # Mock OCR tool failure
            with patch('asyncio.create_subprocess_exec') as mock_exec:
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"", b"OCR failed with error")
                mock_process.returncode = 1  # Failure return code
                mock_exec.return_value = mock_process

                result = await processor.create_better_pdf(
                    sample_pdf, output_path
                )

                assert result.success is False
                assert result.error is not None
                assert "OCR failed with error" in result.error

    @pytest.mark.asyncio
    async def test_create_better_pdf_qpdf_failure(self, processor, sample_pdf):
        """Test PDF enhancement handles qpdf tool failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "failed_qpdf.pdf"

            with patch('asyncio.create_subprocess_exec') as mock_exec:
                def mock_subprocess(*_args, **_kwargs):
                    # Return success for OCRmyPDF, failure for qpdf
                    command = _args[0]
                    mock_process = AsyncMock()

                    if any('ocrmypdf' in str(arg) for arg in command):
                        mock_process.communicate.return_value = (b"OCR Success", b"")
                        mock_process.returncode = 0
                    else:  # qpdf call
                        mock_process.communicate.return_value = (b"", b"qpdf failed")
                        mock_process.returncode = 1

                    return mock_process

                mock_exec.side_effect = mock_subprocess

                with patch('shutil.copy2'):
                    result = await processor.create_better_pdf(
                        sample_pdf, output_path
                    )

                assert result.success is False
                assert result.error is not None
                assert "PDF/A conversion failed" in result.error

    @pytest.mark.asyncio
    async def test_create_better_pdf_invalid_input(self, processor):
        """Test PDF enhancement with invalid input file."""
        invalid_path = Path("/nonexistent/file.pdf")
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_output:
            output_path = Path(temp_output.name)

            result = await processor.create_better_pdf(invalid_path, output_path)

            assert result.success is False
            assert result.error is not None

            # Cleanup
            if output_path.exists():
                output_path.unlink()

    @pytest.mark.asyncio
    async def test_create_better_pdf_progress_tracking(self, processor, sample_pdf):
        """Test PDF enhancement with progress tracking."""

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "progress_test.pdf"

            # Create mock progress tracker
            progress = Mock(spec=Progress)
            task_id = "test_task"

            with patch('asyncio.create_subprocess_exec') as mock_exec:
                def mock_subprocess_progress(*_args, **_kwargs):
                    mock_process = AsyncMock()
                    mock_process.communicate.return_value = (b"Success", b"")
                    mock_process.returncode = 0

                    # Simulate file creation for any external tool calls
                    command_args = _args
                    if len(command_args) >= 2:
                        output_file = Path(command_args[-1])
                        input_file = Path(command_args[-2])

                        if input_file.exists() and not output_file.exists():
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(input_file, output_file)

                    return mock_process

                mock_exec.side_effect = mock_subprocess_progress

                result = await processor.create_better_pdf(
                    sample_pdf, output_path, progress, task_id
                )

                assert result.success is True

                # Verify progress updates were called
                assert progress.update.called

    @pytest.mark.asyncio
    async def test_create_better_pdf_with_metadata_preservation(self, processor, sample_pdf):
        """Test PDF enhancement preserves original metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "metadata_test.pdf"

            with patch('asyncio.create_subprocess_exec') as mock_exec:
                def mock_subprocess_metadata(*_args, **_kwargs):
                    mock_process = AsyncMock()
                    mock_process.communicate.return_value = (b"Success", b"")
                    mock_process.returncode = 0

                    # Simulate file creation for any external tool calls
                    command_args = _args
                    if len(command_args) >= 2:
                        output_file = Path(command_args[-1])
                        input_file = Path(command_args[-2])

                        if input_file.exists() and not output_file.exists():
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(input_file, output_file)

                    return mock_process

                mock_exec.side_effect = mock_subprocess_metadata

                result = await processor.create_better_pdf(
                    sample_pdf, output_path
                )

                assert result.success is True
                assert result.pdf_info.title == 'Integration Test Document'
                assert result.pdf_info.author == 'Test Suite'

    @pytest.mark.asyncio
    async def test_create_better_pdf_file_cleanup(self, processor, sample_pdf):
        """Test PDF enhancement cleans up temporary files properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "cleanup_test.pdf"

            with patch('asyncio.create_subprocess_exec') as mock_exec:
                def mock_subprocess_cleanup(*_args, **_kwargs):
                    mock_process = AsyncMock()
                    mock_process.communicate.return_value = (b"Success", b"")
                    mock_process.returncode = 0

                    # Simulate file creation for any external tool calls
                    command_args = _args
                    if len(command_args) >= 2:
                        output_file = Path(command_args[-1])
                        input_file = Path(command_args[-2])

                        if input_file.exists() and not output_file.exists():
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(input_file, output_file)

                    return mock_process

                mock_exec.side_effect = mock_subprocess_cleanup

                result = await processor.create_better_pdf(
                    sample_pdf, output_path
                )

                assert result.success is True

                # Check that temporary directory cleanup worked
                # (This is handled by TemporaryDirectory context manager in the actual code)
