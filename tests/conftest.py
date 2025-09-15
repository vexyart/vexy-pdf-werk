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


@pytest.fixture
def sample_pdf_path() -> Generator[Path, None, None]:
    """Create a temporary PDF file path for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\n0000000000 65535 f\ntrailer\n<< /Size 1 /Root 1 0 R >>\nstartxref\n9\n%%EOF')
        tmp.flush()
        yield Path(tmp.name)

    # Cleanup
    Path(tmp.name).unlink(missing_ok=True)


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
            self.aopen = AsyncMock()
            self.mkdir = Mock()

        def setup_successful_write(self):
            mock_file = AsyncMock()
            mock_file.__aenter__.return_value = mock_file
            mock_file.__aexit__.return_value = None
            mock_file.write = AsyncMock()
            self.aopen.return_value = mock_file
            return mock_file

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