# this_file: tests/conftest.py
"""Shared test configuration and fixtures."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock
from typing import AsyncGenerator, Generator

import pytest

from vexy_pdf_werk.config import ConversionConfig


@pytest.fixture
def config() -> ConversionConfig:
    """Provide a basic ConversionConfig for testing."""
    return ConversionConfig()


def create_valid_test_pdf(file_path: Path, content: str = "Test PDF Content") -> None:
    """Create a valid PDF file for testing using reportlab."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    # Create a proper PDF with reportlab - this should always work since reportlab is a dependency
    c = canvas.Canvas(str(file_path), pagesize=letter)
    c.drawString(100, 750, content)
    c.drawString(100, 730, "This is a test PDF file.")
    c.drawString(100, 710, "Created for testing purposes.")
    c.save()

    # Verify the PDF was created correctly
    if not file_path.exists() or file_path.stat().st_size == 0:
        raise RuntimeError(f"Failed to create valid test PDF at {file_path}")

    # Quick validation with pikepdf
    try:
        import pikepdf
        with pikepdf.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise RuntimeError(f"Created PDF has no pages: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Created PDF failed validation: {e}") from e


@pytest.fixture
def sample_pdf_path() -> Generator[Path, None, None]:
    """Create a temporary PDF file path for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        pdf_path = Path(tmp.name)

    create_valid_test_pdf(pdf_path)
    yield pdf_path

    # Cleanup
    pdf_path.unlink(missing_ok=True)


@pytest.fixture
def async_mock_pdf_reader():
    """Create a mock PDF reader for async testing."""
    def create_mock_reader(pages_content: list[str]):
        mock_pages = []
        for content in pages_content:
            mock_page = Mock()
            mock_page.extract_text.return_value = content
            mock_pages.append(mock_page)

        mock_reader = Mock()
        mock_reader.pages = mock_pages
        return mock_reader

    return create_mock_reader


@pytest.fixture
def async_converter_mock():
    """Create standardized async converter mocks."""
    class AsyncConverterMock:
        def __init__(self):
            self.convert_pdf = AsyncMock()
            self._available = True

        def set_available(self, available: bool):
            self._available = available

        def set_result(self, success: bool, pages: list = None, error: str = None):
            from vexy_pdf_werk.core.markdown_converter import MarkdownResult, MarkdownPage

            if pages is None and success:
                pages = [MarkdownPage(0, "Mock content", "Mock title", "mock-slug")]
            elif pages is None:
                pages = []

            result = MarkdownResult(
                success=success,
                pages=pages,
                error=error,
                total_pages=len(pages),
                processing_time=0.1
            )
            self.convert_pdf.return_value = result

    return AsyncConverterMock


@pytest.fixture
def async_file_operations():
    """Mock async file operations consistently."""
    class AsyncFileMock:
        def __init__(self):
            self.aopen = self._create_async_context_manager()
            self.mkdir = Mock()

        def _create_async_context_manager(self):
            """Create a proper async context manager mock."""
            class AsyncContextManager:
                def __init__(self):
                    self.file_mock = AsyncMock()
                    self.file_mock.write = AsyncMock()
                    self.file_mock.read = AsyncMock(return_value="mock content")

                async def __aenter__(self):
                    return self.file_mock

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    return None

            def create_context_manager(*args, **kwargs):
                return AsyncContextManager()

            aopen_mock = Mock(side_effect=create_context_manager)
            return aopen_mock

        def setup_successful_write(self):
            """Setup for successful file write operations."""
            return self.aopen

    return AsyncFileMock


@pytest.fixture
def thread_pool_executor_mock():
    """Mock ThreadPoolExecutor for consistent async testing."""
    class ThreadPoolMock:
        def __init__(self):
            self.executor_mock = Mock()
            self.run_in_executor = AsyncMock()

        def setup_executor(self, return_value=None, side_effect=None):
            if side_effect:
                self.run_in_executor.side_effect = side_effect
            else:
                self.run_in_executor.return_value = return_value

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    return ThreadPoolMock


class AsyncTestHelper:
    """Helper class for standardized async testing patterns."""

    @staticmethod
    async def assert_async_result(coro, expected_success: bool, expected_pages_count: int = None):
        """Standard assertion pattern for async results."""
        result = await coro
        assert result.success == expected_success

        if expected_pages_count is not None:
            assert len(result.pages) == expected_pages_count

        if expected_success:
            assert result.error is None
        else:
            assert result.error is not None

        return result

    @staticmethod
    def create_mock_pages(count: int, content_template: str = "Page {n} content"):
        """Create mock pages for testing."""
        from vexy_pdf_werk.core.markdown_converter import MarkdownPage

        pages = []
        for i in range(count):
            content = content_template.format(n=i+1)
            page = MarkdownPage(
                page_number=i,
                content=content,
                title=f"Page {i+1}",
                slug=f"page-{i+1}"
            )
            pages.append(page)
        return pages

    @staticmethod
    async def run_with_timeout(coro, timeout: float = 5.0):
        """Run async operations with timeout for testing."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            pytest.fail(f"Async operation timed out after {timeout} seconds")


@pytest.fixture
def async_test_helper():
    """Provide AsyncTestHelper for tests."""
    return AsyncTestHelper