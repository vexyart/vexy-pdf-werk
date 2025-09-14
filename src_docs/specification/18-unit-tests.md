#### 56.0.1. Unit Tests Implementation

##### Configuration Tests (`tests/unit/test_config.py`)

```python
## 57. this_file: tests/unit/test_config.py

"""Unit tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest
import toml

from vexy_pdf_werk.config import (
    VPWConfig, ProcessingConfig, ConversionConfig, AIConfig, OutputConfig,
    load_config, save_config, get_config_dir, get_config_file
)


class TestVPWConfig:
    """Test VPW configuration model."""

    def test_default_config_creation(self):
        """Test creating default configuration."""
        config = VPWConfig()

        assert config.processing.ocr_language == "eng"
        assert config.conversion.markdown_backend == "auto"
        assert config.ai.enabled is False
        assert "pdfa" in config.output.formats

    def test_config_validation(self):
        """Test configuration validation."""
        # Valid configuration
        config = VPWConfig(
            processing=ProcessingConfig(ocr_language="eng+fra"),
            ai=AIConfig(enabled=True, provider="claude")
        )
        assert config.processing.ocr_language == "eng+fra"
        assert config.ai.enabled is True

    def test_nested_config_modification(self):
        """Test modifying nested configuration."""
        config = VPWConfig()
        config.ai.enabled = True
        config.ai.provider = "gemini"

        assert config.ai.enabled is True
        assert config.ai.provider == "gemini"


class TestConfigFileOperations:
    """Test configuration file operations."""

    def test_save_and_load_config(self, temp_dir):
        """Test saving and loading configuration."""
        config_file = temp_dir / "test_config.toml"

        # Create test configuration
        original_config = VPWConfig()
        original_config.processing.ocr_language = "deu"
        original_config.ai.enabled = True

        # Save configuration
        save_config(original_config, config_file)
        assert config_file.exists()

        # Load configuration
        loaded_config = load_config(config_file)
        assert loaded_config.processing.ocr_language == "deu"
        assert loaded_config.ai.enabled is True

    def test_config_file_format(self, temp_dir):
        """Test that configuration file is valid TOML."""
        config_file = temp_dir / "test_config.toml"
        config = VPWConfig()

        save_config(config, config_file)

        # Verify file is valid TOML
        with open(config_file) as f:
            loaded_toml = toml.load(f)

        assert "processing" in loaded_toml
        assert "conversion" in loaded_toml
        assert "ai" in loaded_toml
        assert "output" in loaded_toml

    def test_environment_variable_override(self):
        """Test environment variable configuration override."""
        # Set test environment variables
        test_env = {
            "DATALAB_API_KEY": "test-datalab-key",
            "ANTHROPIC_API_KEY": "test-claude-key",
            "TESSERACT_PATH": "/test/tesseract"
        }

        with patch.dict(os.environ, test_env):
            config = load_config()
            # Note: This test would need the actual environment override logic
            # to be implemented in the load_config function


class TestConfigDirectories:
    """Test configuration directory operations."""

    def test_get_config_dir(self):
        """Test getting configuration directory."""
        config_dir = get_config_dir()
        assert config_dir.name == "vexy-pdf-werk"
        assert config_dir.is_absolute()

    def test_get_config_file(self):
        """Test getting configuration file path."""
        config_file = get_config_file()
        assert config_file.name == "config.toml"
        assert config_file.parent.name == "vexy-pdf-werk"
```
