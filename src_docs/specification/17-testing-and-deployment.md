# 4. Vexy PDF Werk (VPW) - Part 4: Testing and Deployment

This final section covers comprehensive testing strategies, quality assurance processes, packaging, and deployment procedures.

### 53.1. Testing Strategy Implementation

#### 53.1.1. Test Structure and Organization

##### Test Directory Structure
```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and fixtures
├── unit/
│   ├── __init__.py
│   ├── test_config.py          # Configuration testing
│   ├── test_pdf_processor.py   # PDF processing unit tests
│   ├── test_markdown_generator.py # Markdown generation tests
│   ├── test_ai_services.py     # AI service mocking tests
│   └── test_utils.py           # Utility function tests
├── integration/
│   ├── __init__.py
│   ├── test_full_pipeline.py   # End-to-end pipeline tests
│   ├── test_cli.py            # CLI interface tests
│   └── test_external_tools.py # External tool integration tests
└── fixtures/
    ├── sample_pdfs/           # Test PDF files
    ├── expected_outputs/      # Expected test results
    └── configs/               # Test configuration files
```

#### 53.1.2. Test Configuration and Fixtures

##### Pytest Configuration (`tests/conftest.py`)

```python
## 54. this_file: tests/conftest.py

"""Pytest configuration and shared fixtures for VPW tests."""

import tempfile
import shutil
from pathlib import Path
from typing import Generator

import pytest
from unittest.mock import Mock, patch

from vexy_pdf_werk.config import VPWConfig, ProcessingConfig, ConversionConfig, AIConfig, OutputConfig


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def sample_pdf() -> Path:
    """Path to a sample PDF file for testing."""
    # Create a simple PDF for testing if it doesn't exist
    fixtures_dir = Path(__file__).parent / "fixtures" / "sample_pdfs"
    sample_path = fixtures_dir / "simple_text.pdf"

    if not sample_path.exists():
        # Create a minimal PDF using reportlab for testing
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            fixtures_dir.mkdir(parents=True, exist_ok=True)
            c = canvas.Canvas(str(sample_path), pagesize=letter)
            c.drawString(100, 750, "Test PDF Document")
            c.drawString(100, 700, "This is a sample PDF for testing VPW.")
            c.showPage()
            c.save()
        except ImportError:
            pytest.skip("reportlab not available for PDF generation")

    return sample_path


@pytest.fixture
def default_config() -> VPWConfig:
    """Default VPW configuration for testing."""
    return VPWConfig(
        processing=ProcessingConfig(
            ocr_language="eng",
            pdf_quality="high",
            force_ocr=False
        ),
        conversion=ConversionConfig(
            markdown_backend="basic",  # Use basic converter for tests
            paginate_markdown=True,
            include_images=True
        ),
        ai=AIConfig(
            enabled=False,  # Disable AI by default in tests
            provider="claude",
            correction_enabled=False
        ),
        output=OutputConfig(
            formats=["pdfa", "markdown", "epub", "yaml"],
            preserve_original=True,
            output_directory="./test_output"
        )
    )


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    mock_service = Mock()
    mock_service.correct_text.return_value = "Corrected text"
    mock_service.enhance_content.return_value = "Enhanced content"
    mock_service.is_available.return_value = True
    return mock_service


@pytest.fixture
def mock_ocrmypdf():
    """Mock OCRmyPDF for testing without requiring external tools."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"OCR completed successfully"
        mock_run.return_value.stderr = b""
        yield mock_run


@pytest.fixture
def mock_qpdf():
    """Mock qpdf for testing."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"PDF processing completed"
        mock_run.return_value.stderr = b""
        yield mock_run


## 55. Pytest markers configuration
pytest_plugins = []

## 56. Skip slow tests by default
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return

    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--runai", action="store_true", default=False,
        help="run tests that require AI services"
    )
```
