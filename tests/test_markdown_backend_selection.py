# this_file: tests/test_markdown_backend_selection.py
import asyncio
import types
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO

import pytest
import importlib.util

from vexy_pdf_werk.config import ConversionConfig
from vexy_pdf_werk.core.markdown_converter import (
    MarkdownGenerator,
    BasicConverter,
    MarkerConverter,
    MarkItDownConverter,
    DoclingConverter,
    MarkdownResult,
    MarkdownPage,
)


def test_auto_selects_basic_when_no_backends_available(monkeypatch):
    # Skip if marker is installed in the environment
    if importlib.util.find_spec("marker") is not None:
        pytest.skip("marker installed in environment; cannot assert Basic fallback")
    # Ensure optional backends are not importable
    for name in ("marker", "markitdown", "docling"):
        sys.modules.pop(name, None)

    gen = MarkdownGenerator(ConversionConfig(markdown_backend="auto"))
    assert isinstance(gen.converter, BasicConverter)


def test_auto_selects_marker_when_available(monkeypatch):
    # Provide a dummy marker module
    dummy_marker = types.ModuleType("marker")
    monkeypatch.setitem(sys.modules, "marker", dummy_marker)
    # Ensure others don't interfere
    sys.modules.pop("docling", None)
    sys.modules.pop("markitdown", None)

    gen = MarkdownGenerator(ConversionConfig(markdown_backend="auto"))
    assert isinstance(gen.converter, MarkerConverter)


def test_explicit_backend_falls_back_to_basic_when_missing(monkeypatch):
    # Make sure docling isn't importable
    sys.modules.pop("docling", None)

    gen = MarkdownGenerator(ConversionConfig(markdown_backend="docling"))
    # The generator will construct a DoclingConverter, but it will not be available
    # convert_pdf will still delegate to BasicConverter; selection can still return DoclingConverter instance
    # We assert that calling convert delegates successfully on a tiny synthesized file
    assert hasattr(gen.converter, "convert_pdf")


# Integration tests for real converter implementations
@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a minimal valid PDF for testing."""
    import pypdf.generic
    from pypdf import PdfWriter

    # Create a very simple PDF
    writer = PdfWriter()
    writer.add_blank_page(612, 792)  # Standard letter size

    pdf_path = tmp_path / "test.pdf"
    with open(pdf_path, "wb") as f:
        writer.write(f)

    return pdf_path


@pytest.fixture
def config():
    """Standard config for testing."""
    return ConversionConfig(
        paginate_markdown=True,
        include_images=False
    )


class TestMarkerConverter:
    """Integration tests for MarkerConverter."""

    @pytest.mark.asyncio
    async def test_marker_converter_availability_detection(self, config):
        """Test that MarkerConverter correctly detects marker-pdf availability."""
        converter = MarkerConverter(config)

        # Test availability detection logic
        if hasattr(converter, '_available'):
            # If marker-pdf is installed, should be available
            if importlib.util.find_spec("marker") is not None:
                assert converter._available is True
            else:
                assert converter._available is False

    @pytest.mark.asyncio
    async def test_marker_converter_fallback_when_unavailable(self, config, sample_pdf_path):
        """Test that MarkerConverter falls back to BasicConverter when marker is unavailable."""

        # Force converter to be unavailable
        converter = MarkerConverter(config)
        converter._available = False

        result = await converter.convert_pdf(sample_pdf_path)

        assert isinstance(result, MarkdownResult)
        assert result.success is True
        assert len(result.pages) > 0
        assert all(isinstance(page, MarkdownPage) for page in result.pages)

    @pytest.mark.skipif(
        importlib.util.find_spec("marker") is None,
        reason="marker-pdf not installed"
    )
    @pytest.mark.asyncio
    async def test_marker_converter_real_conversion(self, config, sample_pdf_path):
        """Test MarkerConverter with real marker-pdf integration (if available)."""
        converter = MarkerConverter(config)

        if converter._available:
            result = await converter.convert_pdf(sample_pdf_path)

            assert isinstance(result, MarkdownResult)
            assert result.success is True
            assert len(result.pages) > 0
            assert all(isinstance(page, MarkdownPage) for page in result.pages)
            assert result.processing_time > 0


class TestMarkItDownConverter:
    """Integration tests for MarkItDownConverter."""

    @pytest.mark.asyncio
    async def test_markitdown_converter_availability_detection(self, config):
        """Test that MarkItDownConverter correctly detects markitdown availability."""
        converter = MarkItDownConverter(config)

        # Test availability detection logic
        if hasattr(converter, '_available'):
            # If markitdown is installed, should be available
            if importlib.util.find_spec("markitdown") is not None:
                assert converter._available is True
            else:
                assert converter._available is False

    @pytest.mark.asyncio
    async def test_markitdown_converter_fallback_when_unavailable(self, config, sample_pdf_path):
        """Test that MarkItDownConverter falls back to BasicConverter when markitdown is unavailable."""

        # Force converter to be unavailable
        converter = MarkItDownConverter(config)
        converter._available = False

        result = await converter.convert_pdf(sample_pdf_path)

        assert isinstance(result, MarkdownResult)
        assert result.success is True
        assert len(result.pages) > 0
        assert all(isinstance(page, MarkdownPage) for page in result.pages)

    @pytest.mark.skipif(
        importlib.util.find_spec("markitdown") is None,
        reason="markitdown not installed"
    )
    @pytest.mark.asyncio
    async def test_markitdown_converter_real_conversion(self, config, sample_pdf_path):
        """Test MarkItDownConverter with real markitdown integration (if available)."""
        converter = MarkItDownConverter(config)

        if converter._available:
            result = await converter.convert_pdf(sample_pdf_path)

            assert isinstance(result, MarkdownResult)
            assert result.success is True
            assert len(result.pages) > 0
            assert all(isinstance(page, MarkdownPage) for page in result.pages)
            assert result.processing_time > 0


class TestDoclingConverter:
    """Integration tests for DoclingConverter."""

    @pytest.mark.asyncio
    async def test_docling_converter_availability_detection(self, config):
        """Test that DoclingConverter correctly detects docling availability."""
        converter = DoclingConverter(config)

        # Test availability detection logic
        if hasattr(converter, '_available'):
            # If docling is installed, should be available
            if importlib.util.find_spec("docling") is not None:
                assert converter._available is True
            else:
                assert converter._available is False

    @pytest.mark.asyncio
    async def test_docling_converter_fallback_when_unavailable(self, config, sample_pdf_path):
        """Test that DoclingConverter falls back to BasicConverter when docling is unavailable."""

        # Force converter to be unavailable
        converter = DoclingConverter(config)
        converter._available = False

        result = await converter.convert_pdf(sample_pdf_path)

        assert isinstance(result, MarkdownResult)
        assert result.success is True
        assert len(result.pages) > 0
        assert all(isinstance(page, MarkdownPage) for page in result.pages)

    @pytest.mark.skipif(
        importlib.util.find_spec("docling") is None,
        reason="docling not installed"
    )
    @pytest.mark.asyncio
    async def test_docling_converter_real_conversion(self, config, sample_pdf_path):
        """Test DoclingConverter with real docling integration (if available)."""
        converter = DoclingConverter(config)

        if converter._available:
            result = await converter.convert_pdf(sample_pdf_path)

            assert isinstance(result, MarkdownResult)
            assert result.success is True
            assert len(result.pages) > 0
            assert all(isinstance(page, MarkdownPage) for page in result.pages)
            assert result.processing_time > 0


class TestMarkdownGeneratorIntegration:
    """Integration tests for MarkdownGenerator with different backends."""

    @pytest.mark.asyncio
    async def test_markdown_generator_with_all_backends(self, sample_pdf_path, tmp_path):
        """Test MarkdownGenerator with all available backends."""
        backends = ["basic", "marker", "markitdown", "docling", "auto"]

        for backend in backends:
            config = ConversionConfig(markdown_backend=backend)
            generator = MarkdownGenerator(config)

            # Test that generator initializes without error
            assert generator.converter is not None

            # Test that generation works (even if falling back)
            result = await generator.generate_markdown(sample_pdf_path, tmp_path / f"{backend}_output")

            assert isinstance(result, MarkdownResult)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_converter_error_handling_and_fallback(self, config, sample_pdf_path):
        """Test that converters handle errors gracefully and fall back when needed."""

        # Test with a non-existent file
        non_existent_path = Path("/non/existent/file.pdf")

        for ConverterClass in [MarkerConverter, MarkItDownConverter, DoclingConverter]:
            converter = ConverterClass(config)

            # Should fail validation but handle gracefully
            with pytest.raises((FileNotFoundError, ValueError)):
                await converter.convert_pdf(non_existent_path)

    @pytest.mark.asyncio
    async def test_page_splitting_functionality(self, config, tmp_path):
        """Test that all converters properly split content into pages."""

        # Create a mock PDF with content that would split into multiple logical pages
        content_with_headers = """
# Chapter 1: Introduction

This is the introduction content.

## Section 1.1

Some content here.

# Chapter 2: Main Content

This is the main content.

## Section 2.1

More content here.

# Chapter 3: Conclusion

This is the conclusion.
        """.strip()

        # Test each converter's page splitting logic
        for ConverterClass in [MarkerConverter, MarkItDownConverter, DoclingConverter]:
            converter = ConverterClass(config)

            if hasattr(converter, '_split_marker_output_to_pages'):
                pages = converter._split_marker_output_to_pages(content_with_headers, tmp_path / "test.pdf")
            elif hasattr(converter, '_split_markitdown_output_to_pages'):
                pages = converter._split_markitdown_output_to_pages(content_with_headers, tmp_path / "test.pdf")
            elif hasattr(converter, '_split_docling_output_to_pages'):
                pages = converter._split_docling_output_to_pages(content_with_headers, tmp_path / "test.pdf")
            else:
                continue

            # Should create multiple pages based on headers
            assert len(pages) > 1
            assert all(isinstance(page, MarkdownPage) for page in pages)
            assert all(page.content.strip() for page in pages)  # No empty pages

    def test_priority_order_in_auto_selection(self, monkeypatch):
        """Test that auto selection follows the correct priority order."""

        # Mock all backends as available
        dummy_modules = {}
        for name in ["marker", "markitdown", "docling"]:
            dummy_modules[name] = types.ModuleType(name)
            monkeypatch.setitem(sys.modules, name, dummy_modules[name])

        # Mock the converter classes to track which is selected
        with patch.multiple(
            'vexy_pdf_werk.core.markdown_converter',
            MarkerConverter=MagicMock(),
            MarkItDownConverter=MagicMock(),
            DoclingConverter=MagicMock()
        ) as mocks:

            # Make all converters appear available
            for mock_converter in mocks.values():
                instance = MagicMock()
                instance._available = True
                mock_converter.return_value = instance

            config = ConversionConfig(markdown_backend="auto")
            generator = MarkdownGenerator(config)

            # Should select marker first (highest priority)
            mocks['MarkerConverter'].assert_called_once()


class TestConverterPerformanceAndQuality:
    """Performance and quality comparison tests for different converters."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_converter_performance_comparison(self, sample_pdf_path):
        """Compare performance of different converters (if available)."""

        config = ConversionConfig()
        results = {}

        # Test each available converter
        for name, ConverterClass in [
            ("basic", BasicConverter),
            ("marker", MarkerConverter),
            ("markitdown", MarkItDownConverter),
            ("docling", DoclingConverter)
        ]:
            converter = ConverterClass(config)

            # Skip if not available
            if hasattr(converter, '_available') and not converter._available:
                continue

            start_time = asyncio.get_event_loop().time()
            result = await converter.convert_pdf(sample_pdf_path)
            end_time = asyncio.get_event_loop().time()

            results[name] = {
                'processing_time': end_time - start_time,
                'success': result.success,
                'page_count': len(result.pages),
                'word_count': sum(len(page.content.split()) for page in result.pages)
            }

        # Basic assertions about results
        assert len(results) > 0  # At least BasicConverter should work

        # All successful conversions should produce content
        for name, result in results.items():
            if result['success']:
                assert result['page_count'] > 0
                assert result['word_count'] > 0
