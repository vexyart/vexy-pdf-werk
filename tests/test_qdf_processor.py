# this_file: tests/test_qdf_processor.py
"""Tests for QDF/JSON processor functionality."""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from vexy_pdf_werk.core.qdf_processor import QDFProcessor


@pytest.fixture
def qpdf_processor():
    """Fixture for a QDFProcessor instance with a mocked qpdf command."""
    return QDFProcessor(qpdf_cmd="/usr/bin/mock-qpdf")


@pytest.fixture
def sample_pdf_path():
    """Fixture for a sample PDF path."""
    return Path("/test/sample.pdf")


@pytest.fixture
def sample_qdf_json():
    """Fixture for a sample QDF/JSON structure."""
    return {
        "qpdf": ["--qdf", "--json"],
        "objects": {
            "1 0": {
                "stream": {
                    "dict": "2 0",
                    "data": "BT /F1 12 Tf 100 750 Td (Hello World) Tj ET"
                }
            },
            "2 0": {
                "value": {
                    "Length": "41"
                }
            }
        }
    }


@pytest.mark.asyncio
async def test_pdf_to_qdf_json_success(qpdf_processor, sample_pdf_path, sample_qdf_json):
    """Test successful conversion of a PDF page to QDF/JSON."""
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        # Configure the mock process
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (json.dumps(sample_qdf_json).encode(), b"")
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc

        # Call the method
        page_num = 0
        result_json = await qpdf_processor.pdf_to_qdf_json(sample_pdf_path, page_num)

        # Assertions
        mock_exec.assert_called_once_with(
            qpdf_processor.qpdf_cmd,
            "--qdf",
            "--json",
            str(sample_pdf_path),
            "--pages",
            ".",
            str(page_num + 1),
            "-",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert result_json == sample_qdf_json


@pytest.mark.asyncio
async def test_pdf_to_qdf_json_failure(qpdf_processor, sample_pdf_path):
    """Test that a RuntimeError is raised when qpdf fails."""
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        # Configure the mock process for failure
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"qpdf error: file not found")
        mock_proc.returncode = 1
        mock_exec.return_value = mock_proc

        # Expect a RuntimeError
        with pytest.raises(RuntimeError, match="qpdf to JSON conversion failed: qpdf error: file not found"):
            await qpdf_processor.pdf_to_qdf_json(sample_pdf_path, 0)


def test_extract_text_from_qdf(qpdf_processor, sample_qdf_json):
    """Test the extraction of text from a QDF/JSON object."""
    # The sample_qdf_json has one text stream
    expected_text = "BT /F1 12 Tf 100 750 Td (Hello World) Tj ET"
    
    extracted_text = qpdf_processor.extract_text_from_qdf(sample_qdf_json)
    
    assert extracted_text == expected_text


def test_apply_diff_to_qdf_empty_diff(qpdf_processor, sample_qdf_json):
    """Test applying an empty diff returns the original QDF."""
    result = qpdf_processor.apply_diff_to_qdf(sample_qdf_json, "")
    assert result == sample_qdf_json

    result = qpdf_processor.apply_diff_to_qdf(sample_qdf_json, "   ")
    assert result == sample_qdf_json


def test_apply_diff_to_qdf_simple_replacement(qpdf_processor, sample_qdf_json):
    """Test applying a simple unified diff that replaces text."""
    # Simple diff that changes "Hello World" to "Hi Universe"
    diff = """--- a/text
+++ b/text
-BT /F1 12 Tf 100 750 Td (Hello World) Tj ET
+BT /F1 12 Tf 100 750 Td (Hi Universe) Tj ET"""

    result = qpdf_processor.apply_diff_to_qdf(sample_qdf_json, diff)

    # Extract text from result to verify change
    extracted_text = qpdf_processor.extract_text_from_qdf(result)
    assert "Hi Universe" in extracted_text
    assert "Hello World" not in extracted_text


def test_apply_diff_to_qdf_addition(qpdf_processor, sample_qdf_json):
    """Test applying a diff that adds new lines."""
    diff = """--- a/text
+++ b/text
 BT /F1 12 Tf 100 750 Td (Hello World) Tj ET
+New line added
+Another line"""

    result = qpdf_processor.apply_diff_to_qdf(sample_qdf_json, diff)
    extracted_text = qpdf_processor.extract_text_from_qdf(result)

    assert "Hello World" in extracted_text
    assert "New line added" in extracted_text
    assert "Another line" in extracted_text


def test_apply_diff_to_qdf_deletion(qpdf_processor, sample_qdf_json):
    """Test applying a diff that deletes lines."""
    # Create a QDF with multiple text streams for this test
    multi_stream_qdf = {
        "qpdf": ["--qdf", "--json"],
        "objects": {
            "1 0": {
                "stream": {
                    "dict": "2 0",
                    "data": "First line\nSecond line\nThird line"
                }
            }
        }
    }

    diff = """--- a/text
+++ b/text
 First line
-Second line
 Third line"""

    result = qpdf_processor.apply_diff_to_qdf(multi_stream_qdf, diff)
    extracted_text = qpdf_processor.extract_text_from_qdf(result)

    assert "First line" in extracted_text
    assert "Second line" not in extracted_text
    assert "Third line" in extracted_text


def test_apply_diff_to_qdf_no_text_content(qpdf_processor):
    """Test applying diff to QDF with no text content."""
    empty_qdf = {
        "qpdf": ["--qdf", "--json"],
        "objects": {
            "1 0": {
                "value": {"Length": "0"}
            }
        }
    }

    diff = "+New content"
    result = qpdf_processor.apply_diff_to_qdf(empty_qdf, diff)
    assert result == empty_qdf


def test_apply_diff_to_qdf_invalid_diff(qpdf_processor, sample_qdf_json, caplog):
    """Test that invalid diffs are handled gracefully."""
    import logging
    from loguru import logger

    caplog.set_level(logging.ERROR)
    handler_id = logger.add(caplog.handler, format="{message}")

    # This should cause an exception in diff processing
    invalid_diff = "not a valid diff format"

    result = qpdf_processor.apply_diff_to_qdf(sample_qdf_json, invalid_diff)

    logger.remove(handler_id)

    # Should return original QDF on error
    assert result == sample_qdf_json


@pytest.mark.asyncio
async def test_qdf_json_to_pdf_success(qpdf_processor, sample_qdf_json):
    """Test successful conversion of QDF/JSON back to a PDF."""
    output_path = Path("/tmp/output.pdf")
    qdf_content = json.dumps(sample_qdf_json)

    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"")
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc

        await qpdf_processor.qdf_json_to_pdf(sample_qdf_json, output_path)

        mock_exec.assert_called_once_with(
            qpdf_processor.qpdf_cmd,
            "--qdf",
            "-",
            str(output_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        # Check that the correct data was sent to stdin
        mock_proc.communicate.assert_called_once_with(input=qdf_content.encode())


@pytest.mark.asyncio
async def test_qdf_json_to_pdf_failure(qpdf_processor, sample_qdf_json):
    """Test that a RuntimeError is raised when QDF to PDF conversion fails."""
    output_path = Path("/tmp/output.pdf")
    qdf_content = json.dumps(sample_qdf_json)

    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"qpdf error: invalid json")
        mock_proc.returncode = 2
        mock_exec.return_value = mock_proc

        with pytest.raises(RuntimeError, match="qpdf from JSON conversion failed: qpdf error: invalid json"):
            await qpdf_processor.qdf_json_to_pdf(sample_qdf_json, output_path)
