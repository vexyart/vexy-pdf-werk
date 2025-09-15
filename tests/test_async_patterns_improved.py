# this_file: tests/test_async_patterns_improved.py
"""Improved async test patterns for markdown conversion - demonstration of better practices."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, mock_open

import pytest

from vexy_pdf_werk.core.markdown_converter import BasicConverter, MarkdownResult, MarkdownPage


class TestImprovedAsyncPatterns:
    """Demonstration of improved async testing patterns."""

    @pytest.mark.asyncio
    async def test_convert_pdf_with_async_helper(self, config, sample_pdf_path, async_test_helper):
        """Test PDF conversion using improved async test helper."""
        converter = BasicConverter(config)

        # Mock PDF reader with proper async patterns
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        with patch('builtins.open', mock_open(read_data=b'fake_pdf_data')), \
             patch('pypdf.PdfReader', return_value=mock_reader), \
             patch('vexy_pdf_werk.core.markdown_converter.validate_pdf_file'):

            # Use helper for consistent async result testing
            result = await async_test_helper.assert_async_result(
                converter.convert_pdf(sample_pdf_path),
                expected_success=True,
                expected_pages_count=1
            )

            assert result.pages[0].content == "Test content"

    @pytest.mark.asyncio
    async def test_convert_pdf_with_timeout(self, config, sample_pdf_path, async_test_helper):
        """Test PDF conversion with timeout handling."""
        converter = BasicConverter(config)

        # Mock a slow operation
        async def slow_convert(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate work
            return MarkdownResult(
                success=True,
                pages=[MarkdownPage(0, "Slow content", "Title", "slug")],
                total_pages=1,
                processing_time=0.1
            )

        # Replace the actual method with our slow version
        original_method = converter.convert_pdf
        converter.convert_pdf = slow_convert

        # Test with timeout
        result = await async_test_helper.run_with_timeout(
            converter.convert_pdf(sample_pdf_path),
            timeout=1.0
        )

        assert result.success is True
        assert result.pages[0].content == "Slow content"

    @pytest.mark.asyncio
    async def test_convert_pdf_with_standardized_mocks(self, config, async_converter_mock, sample_pdf_path):
        """Test PDF conversion using standardized converter mocks."""
        # Setup mock with expected result
        mock_converter = async_converter_mock()
        mock_converter.set_result(success=True, pages=None)  # Will create default page

        # Test the mock
        result = await mock_converter.convert_pdf(sample_pdf_path)

        assert result.success is True
        assert len(result.pages) == 1
        assert result.pages[0].content == "Mock content"
        assert result.pages[0].title == "Mock title"

    @pytest.mark.asyncio
    async def test_convert_pdf_error_handling(self, config, async_converter_mock, sample_pdf_path):
        """Test error handling with standardized mock patterns."""
        mock_converter = async_converter_mock()
        mock_converter.set_result(success=False, error="Mock error occurred")

        result = await mock_converter.convert_pdf(sample_pdf_path)

        assert result.success is False
        assert result.error == "Mock error occurred"
        assert len(result.pages) == 0

    @pytest.mark.asyncio
    async def test_convert_pdf_availability_patterns(self, config, async_converter_mock):
        """Test availability detection with consistent patterns."""
        mock_converter = async_converter_mock()

        # Test available state
        assert mock_converter._available is True

        # Test unavailable state
        mock_converter.set_available(False)
        assert mock_converter._available is False

    @pytest.mark.asyncio
    async def test_multiple_async_operations(self, config, async_test_helper):
        """Test multiple async operations with proper coordination."""
        converter = BasicConverter(config)

        # Create multiple mock pages
        pages = async_test_helper.create_mock_pages(3, "Content for page {n}")

        # Mock all operations at once for multiple files
        mock_pages = []
        for i in range(3):
            mock_page = Mock()
            mock_page.extract_text.return_value = f"Content for page {i+1}"
            mock_pages.append(mock_page)

        mock_reader = Mock()
        mock_reader.pages = mock_pages

        with patch('builtins.open', mock_open(read_data=b'fake_pdf_data')), \
             patch('pypdf.PdfReader', return_value=mock_reader), \
             patch('vexy_pdf_werk.core.markdown_converter.validate_pdf_file'):

            # Create tasks for async execution
            tasks = [
                converter.convert_pdf(Path(f"/fake/file{i}.pdf"))
                for i in range(3)
            ]

            # Wait for all operations to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all succeeded
        for i, result in enumerate(results):
            assert isinstance(result, MarkdownResult)
            assert result.success is True
            assert len(result.pages) == 1
            assert f"Content for page {i+1}" in result.pages[0].content

    @pytest.mark.asyncio
    async def test_async_file_operations_mock(self, async_file_operations):
        """Test async file operations with standardized mocks."""
        file_mock = async_file_operations()

        # Test the mock file operations
        async with file_mock.aopen("/fake/path", "w") as f:
            await f.write("test content")

        # Verify calls
        file_mock.aopen.assert_called_once_with("/fake/path", "w")

    @pytest.mark.asyncio
    async def test_thread_pool_executor_patterns(self, thread_pool_executor_mock):
        """Test ThreadPoolExecutor mocking patterns."""
        executor_mock = thread_pool_executor_mock()
        executor_mock.setup_executor(return_value="mocked result")

        # Simulate using executor
        result = await executor_mock.run_in_executor(None, lambda: "test")

        assert result == "mocked result"
        executor_mock.run_in_executor.assert_called_once()

    @pytest.mark.asyncio
    async def test_exception_handling_patterns(self, config, sample_pdf_path):
        """Test exception handling in async operations."""
        converter = BasicConverter(config)

        # Test various exception scenarios
        exceptions_to_test = [
            (FileNotFoundError, "File not found"),
            (PermissionError, "Permission denied"),
            (ValueError, "Invalid value"),
            (Exception, "Generic error")
        ]

        for exception_type, error_message in exceptions_to_test:
            with patch('builtins.open', side_effect=exception_type(error_message)):
                result = await converter.convert_pdf(sample_pdf_path)

                assert result.success is False
                assert error_message in result.error

    @pytest.mark.asyncio
    async def test_concurrent_converter_operations(self, config):
        """Test concurrent operations with different converters."""
        converter = BasicConverter(config)

        # Create multiple concurrent operations
        async def mock_convert(file_path):
            # Simulate different processing times
            await asyncio.sleep(0.01)
            return MarkdownResult(
                success=True,
                pages=[MarkdownPage(0, f"Content from {file_path.name}", "Title", "slug")],
                total_pages=1,
                processing_time=0.01
            )

        # Run concurrent operations
        file_paths = [Path(f"/fake/file{i}.pdf") for i in range(5)]

        # Replace convert_pdf with our mock
        converter.convert_pdf = mock_convert

        # Execute concurrently
        results = await asyncio.gather(*[
            converter.convert_pdf(path) for path in file_paths
        ])

        # Verify all results
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result.success is True
            assert f"Content from file{i}.pdf" in result.pages[0].content