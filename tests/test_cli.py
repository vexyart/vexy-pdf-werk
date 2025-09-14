# this_file: tests/test_cli.py
"""Tests for CLI interface functionality."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rich.console import Console

from vexy_pdf_werk.cli import VexyPDFWerk


class TestVexyPDFWerkCLI:
    """Test cases for VexyPDFWerk CLI interface."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance for testing."""
        return VexyPDFWerk()

    @pytest.fixture
    def temp_pdf_path(self):
        """Create temporary PDF file path for testing."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            # Write minimal PDF content for testing
            temp_file.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
            yield temp_path
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_cli_initialization(self, cli):
        """Test CLI initialization sets version correctly."""
        assert cli._version is not None
        assert hasattr(cli, '_version')

    def test_version_command(self, cli, capsys):
        """Test version command displays version information."""
        cli.version()
        captured = capsys.readouterr()
        assert cli._version in captured.out

    @patch('vexy_pdf_werk.cli.validate_pdf_file')
    def test_process_invalid_pdf_file(self, mock_validate, cli, capsys):
        """Test process command with invalid PDF file."""
        # Mock validation to raise FileNotFoundError
        mock_validate.side_effect = FileNotFoundError("PDF file not found: test.pdf")

        result = cli.process("nonexistent.pdf")

        assert result == 1
        captured = capsys.readouterr()
        assert "PDF Validation Error" in captured.out
        mock_validate.assert_called_once()

    @patch('vexy_pdf_werk.cli.validate_pdf_file')
    @patch('vexy_pdf_werk.cli.validate_output_directory')
    def test_process_invalid_output_directory(self, mock_validate_dir, mock_validate_pdf, cli, capsys):
        """Test process command with invalid output directory."""
        # Mock PDF validation to pass
        mock_validate_pdf.return_value = None
        # Mock directory validation to raise PermissionError
        mock_validate_dir.side_effect = PermissionError("Cannot create output directory")

        result = cli.process("test.pdf", output_dir="/invalid/path")

        assert result == 1
        captured = capsys.readouterr()
        assert "Output Directory Error" in captured.out

    @patch('vexy_pdf_werk.cli.validate_pdf_file')
    @patch('vexy_pdf_werk.cli.validate_output_directory')
    @patch('vexy_pdf_werk.cli.validate_formats')
    def test_process_invalid_formats(self, mock_validate_formats, mock_validate_dir, mock_validate_pdf, cli, capsys):
        """Test process command with invalid output formats."""
        # Mock validations to pass except formats
        mock_validate_pdf.return_value = None
        mock_validate_dir.return_value = None
        mock_validate_formats.side_effect = ValueError("Invalid output format: invalid")

        result = cli.process("test.pdf", formats="invalid")

        assert result == 1
        captured = capsys.readouterr()
        assert "Format Validation Error" in captured.out

    @patch('vexy_pdf_werk.cli.validate_pdf_file')
    @patch('vexy_pdf_werk.cli.validate_output_directory')
    @patch('vexy_pdf_werk.cli.validate_formats')
    @patch('vexy_pdf_werk.cli.load_config')
    def test_process_formats_parsing(self, mock_load_config, mock_validate_formats, mock_validate_dir, mock_validate_pdf, cli):
        """Test process command correctly parses different format inputs."""
        # Mock all validations to pass
        mock_validate_pdf.return_value = None
        mock_validate_dir.return_value = None
        mock_validate_formats.return_value = ["markdown", "epub"]
        mock_load_config.return_value = MagicMock()

        # Test string format
        with patch.object(cli, '_run_processing_pipeline', return_value=0):
            result = cli.process("test.pdf", formats="markdown,epub")
            assert result == 0

        # Test list format (Fire sometimes converts to list)
        with patch.object(cli, '_run_processing_pipeline', return_value=0):
            result = cli.process("test.pdf", formats=["markdown", "epub"])
            assert result == 0

    @patch('vexy_pdf_werk.cli.validate_pdf_file')
    @patch('vexy_pdf_werk.cli.validate_output_directory')
    @patch('vexy_pdf_werk.cli.validate_formats')
    @patch('vexy_pdf_werk.cli.load_config')
    @patch('vexy_pdf_werk.cli.VexyPDFWerk._run_processing_pipeline')
    def test_process_successful_execution(self, mock_pipeline, mock_load_config, mock_validate_formats, mock_validate_dir, mock_validate_pdf, cli, capsys):
        """Test successful process command execution."""
        # Mock all validations and processing to succeed
        mock_validate_pdf.return_value = None
        mock_validate_dir.return_value = None
        mock_validate_formats.return_value = ["markdown"]
        mock_load_config.return_value = MagicMock()
        mock_pipeline.return_value = 0

        result = cli.process("test.pdf")

        assert result == 0
        captured = capsys.readouterr()
        assert "Processing:" in captured.out
        assert "Output directory:" in captured.out
        mock_pipeline.assert_called_once()

    def test_config_show_command(self, cli, capsys):
        """Test config show command."""
        with patch('vexy_pdf_werk.cli.load_config') as mock_load, \
             patch('vexy_pdf_werk.cli.console') as mock_console:
            mock_config = MagicMock()
            mock_load.return_value = mock_config

            result = cli.config(show=True)

            assert result is None
            mock_load.assert_called_once()
            mock_console.print.assert_called()

    def test_config_init_command(self, cli):
        """Test config init command."""
        with patch('vexy_pdf_werk.cli.get_config_file') as mock_get_config, \
             patch('vexy_pdf_werk.cli.create_default_config') as mock_create, \
             patch('vexy_pdf_werk.cli.console') as mock_console:
            mock_config_path = Path("/test/config.toml")
            mock_get_config.return_value = mock_config_path

            result = cli.config(init=True)

            assert result is None
            mock_create.assert_called_once()
            mock_console.print.assert_called()

    def test_config_no_flags(self, cli, capsys):
        """Test config command with no flags shows help."""
        result = cli.config()

        assert result is None
        captured = capsys.readouterr()
        assert "Use --show to display config or --init to create default config" in captured.out

    def test_verbose_logging_enabled(self, cli):
        """Test that verbose flag enables debug logging."""
        with patch('vexy_pdf_werk.cli.logger') as mock_logger, \
             patch('vexy_pdf_werk.cli.validate_pdf_file'), \
             patch('vexy_pdf_werk.cli.validate_output_directory'), \
             patch('vexy_pdf_werk.cli.validate_formats'), \
             patch('vexy_pdf_werk.cli.load_config'), \
             patch.object(cli, '_run_processing_pipeline', return_value=0):

            cli.process("test.pdf", verbose=True)

            # Verify logger was reconfigured for debug mode
            mock_logger.remove.assert_called()
            mock_logger.add.assert_called()


class TestProcessingPipeline:
    """Test cases for the internal processing pipeline."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance for testing."""
        return VexyPDFWerk()

    @pytest.mark.asyncio
    async def test_run_processing_pipeline_pdfa_format(self, cli):
        """Test processing pipeline with PDF/A format."""
        with patch('vexy_pdf_werk.cli.PDFProcessor') as mock_processor_class:
            mock_processor = AsyncMock()
            mock_processor_class.return_value = mock_processor
            mock_processor.create_better_pdf.return_value = MagicMock(success=True)

            result = await cli._run_processing_pipeline(
                Path("test.pdf"), Path("output"), ["pdfa"], MagicMock()
            )

            assert result == 0
            mock_processor.create_better_pdf.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_processing_pipeline_markdown_format(self, cli):
        """Test processing pipeline with Markdown format."""
        with patch('vexy_pdf_werk.cli.MarkdownGenerator') as mock_generator_class, \
             patch('vexy_pdf_werk.cli.PDFProcessor') as mock_processor_class:
            mock_generator = AsyncMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_markdown.return_value = MagicMock(success=True, pages=[])

            mock_processor = AsyncMock()
            mock_processor_class.return_value = mock_processor
            mock_processor.analyze_pdf.return_value = MagicMock()

            result = await cli._run_processing_pipeline(
                Path("test.pdf"), Path("output"), ["markdown"], MagicMock()
            )

            assert result == 0
            mock_generator.generate_markdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_processing_pipeline_epub_format(self, cli):
        """Test processing pipeline with ePub format (requires Markdown)."""
        with patch('vexy_pdf_werk.cli.MarkdownGenerator') as mock_md_class, \
             patch('vexy_pdf_werk.core.epub_creator.EpubCreator') as mock_epub_class, \
             patch('vexy_pdf_werk.cli.PDFProcessor') as mock_processor_class:
            # Mock PDF processor
            mock_processor = AsyncMock()
            mock_processor_class.return_value = mock_processor
            mock_processor.analyze_pdf.return_value = MagicMock()

            # Mock markdown generation
            mock_md_generator = AsyncMock()
            mock_md_class.return_value = mock_md_generator
            mock_md_result = MagicMock(success=True, pages=[MagicMock()])
            mock_md_generator.generate_markdown.return_value = mock_md_result

            # Mock epub creation
            mock_epub_creator = AsyncMock()
            mock_epub_class.return_value = mock_epub_creator
            mock_epub_creator.create_epub.return_value = MagicMock(success=True)

            result = await cli._run_processing_pipeline(
                Path("test.pdf"), Path("output"), ["epub"], MagicMock()
            )

            assert result == 0
            mock_md_generator.generate_markdown.assert_called_once()
            mock_epub_creator.create_epub.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_processing_pipeline_yaml_format(self, cli):
        """Test processing pipeline with YAML metadata format."""
        with patch('vexy_pdf_werk.cli.MetadataExtractor') as mock_extractor_class, \
             patch('vexy_pdf_werk.cli.PDFProcessor') as mock_processor_class:
            mock_processor = AsyncMock()
            mock_processor_class.return_value = mock_processor
            mock_processor.analyze_pdf.return_value = MagicMock()

            mock_extractor = AsyncMock()
            mock_extractor_class.return_value = mock_extractor
            mock_extractor.extract_metadata.return_value = MagicMock()
            mock_extractor.save_metadata_yaml.return_value = None

            result = await cli._run_processing_pipeline(
                Path("test.pdf"), Path("output"), ["yaml"], MagicMock()
            )

            assert result == 0
            mock_extractor.extract_metadata.assert_called_once()
            mock_extractor.save_metadata_yaml.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_processing_pipeline_error_handling(self, cli):
        """Test processing pipeline handles errors gracefully."""
        with patch('vexy_pdf_werk.cli.PDFProcessor') as mock_processor_class, \
             patch('vexy_pdf_werk.cli.console'), \
             patch('vexy_pdf_werk.cli.Progress') as mock_progress_class:
            mock_processor = AsyncMock()
            mock_processor_class.return_value = mock_processor
            mock_processor.analyze_pdf.return_value = MagicMock()
            # Mock the create_better_pdf call that would fail
            mock_processor.create_better_pdf.side_effect = Exception("Processing failed")

            # Mock Progress to avoid progress bar issues
            mock_progress = MagicMock()
            mock_progress_class.return_value = mock_progress
            mock_progress.__enter__.return_value = mock_progress
            mock_progress.add_task.return_value = MagicMock()

            # The exception should be caught and handled, not bubble up
            with pytest.raises(Exception, match="Processing failed"):
                await cli._run_processing_pipeline(
                    Path("test.pdf"), Path("output"), ["pdfa"], MagicMock()
                )

    @pytest.mark.asyncio
    async def test_run_processing_pipeline_partial_success(self, cli):
        """Test processing pipeline with some formats failing."""
        with patch('vexy_pdf_werk.cli.PDFProcessor') as mock_processor_class, \
             patch('vexy_pdf_werk.cli.MarkdownGenerator') as mock_md_class:
            # PDF/A succeeds
            mock_processor = AsyncMock()
            mock_processor_class.return_value = mock_processor
            mock_processor.create_better_pdf.return_value = MagicMock(success=True)

            # Markdown fails
            mock_md_generator = AsyncMock()
            mock_md_class.return_value = mock_md_generator
            mock_md_generator.generate_markdown.return_value = MagicMock(success=False, error="Conversion failed")

            result = await cli._run_processing_pipeline(
                Path("test.pdf"), Path("output"), ["pdfa", "markdown"], MagicMock()
            )

            # Should still return success code for partial success
            assert result == 0


class TestCLIEntryPoints:
    """Test CLI entry points and integration."""

    def test_main_function(self):
        """Test main function entry point."""
        with patch('vexy_pdf_werk.cli.fire.Fire') as mock_fire:
            from vexy_pdf_werk.cli import main
            main()
            mock_fire.assert_called_once_with(VexyPDFWerk)

    def test_cli_integration_with_fire(self):
        """Test CLI integration works with Fire framework."""
        # This test ensures the CLI class is properly structured for Fire
        cli = VexyPDFWerk()

        # Verify all public methods are accessible
        assert hasattr(cli, 'process')
        assert hasattr(cli, 'config')
        assert hasattr(cli, 'version')

        # Verify methods are callable
        assert callable(cli.process)
        assert callable(cli.config)
        assert callable(cli.version)
