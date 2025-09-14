# this_file: src/vexy_pdf_werk/config.py
"""Configuration management for Vexy PDF Werk."""

import os
from pathlib import Path
from typing import Any

import toml
from platformdirs import user_config_dir
from pydantic import BaseModel, Field


class ProcessingConfig(BaseModel):
    """PDF processing configuration."""
    ocr_language: str = "eng"
    pdf_quality: str = "high"  # high, medium, low
    force_ocr: bool = False
    deskew: bool = True
    rotate_pages: bool = True


class ConversionConfig(BaseModel):
    """Content conversion configuration."""
    markdown_backend: str = "auto"  # auto, marker, markitdown, docling, basic
    paginate_markdown: bool = True
    include_images: bool = True
    extract_tables: bool = True


class AIConfig(BaseModel):
    """AI integration configuration."""
    enabled: bool = False
    provider: str = "claude"  # claude, gemini, custom
    correction_enabled: bool = False
    enhancement_enabled: bool = False
    structure_enhancement_enabled: bool = False
    max_tokens: int = 4000


class OutputConfig(BaseModel):
    """Output configuration."""
    formats: list[str] = Field(default=["pdfa", "markdown", "epub", "yaml"])
    preserve_original: bool = True
    output_directory: str = "./output"
    filename_template: str = "{stem}_{format}.{ext}"


class VPWConfig(BaseModel):
    """Main configuration model."""
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    conversion: ConversionConfig = Field(default_factory=ConversionConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    # External tool paths (auto-detected if None)
    tesseract_path: str | None = None
    qpdf_path: str | None = None
    pandoc_path: str | None = None


def get_config_dir() -> Path:
    """Get the user configuration directory."""
    return Path(user_config_dir("vexy-pdf-werk"))


def get_config_file() -> Path:
    """Get the path to the main configuration file."""
    return get_config_dir() / "config.toml"


def load_config(config_file: Path | None = None) -> VPWConfig:
    """
    Load configuration from file and environment variables.

    Args:
        config_file: Optional path to config file

    Returns:
        Loaded configuration
    """
    if config_file is None:
        config_file = get_config_file()

    # Load from file if it exists
    config_data = {}
    if config_file.exists():
        config_data = toml.load(config_file)

    # Apply environment variable overrides
    env_overrides: dict[str, Any] = {}

    # AI configuration from environment
    if api_key := os.getenv("DATALAB_API_KEY"):
        ai_config = env_overrides.setdefault("ai", {})
        ai_config["datalab_api_key"] = api_key

    if claude_key := os.getenv("ANTHROPIC_API_KEY"):
        ai_config = env_overrides.setdefault("ai", {})
        ai_config["claude_api_key"] = claude_key

    if gemini_key := os.getenv("GOOGLE_AI_API_KEY"):
        ai_config = env_overrides.setdefault("ai", {})
        ai_config["gemini_api_key"] = gemini_key

    # Tool paths from environment
    if tesseract := os.getenv("TESSERACT_PATH"):
        env_overrides["tesseract_path"] = tesseract

    if qpdf := os.getenv("QPDF_PATH"):
        env_overrides["qpdf_path"] = qpdf

    # Merge configurations (env overrides config file)
    final_config = {**config_data, **env_overrides}

    return VPWConfig(**final_config)


def save_config(config: VPWConfig, config_file: Path | None = None) -> None:
    """
    Save configuration to file with enhanced error handling.

    Args:
        config: Configuration to save
        config_file: Optional path to config file

    Raises:
        PermissionError: If unable to write to config file or directory
        OSError: If unable to create config directory
        ValueError: If config serialization fails
    """
    if config_file is None:
        config_file = get_config_file()

    try:
        # Ensure config directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        msg = f"Permission denied creating config directory: {config_file.parent}"
        raise PermissionError(msg) from e
    except OSError as e:
        msg = f"Failed to create config directory: {config_file.parent}"
        raise OSError(msg) from e

    try:
        # Convert to dictionary and save
        config_dict = config.model_dump()
        with open(config_file, 'w', encoding='utf-8') as f:
            toml.dump(config_dict, f)
    except PermissionError as e:
        msg = f"Permission denied writing config file: {config_file}"
        raise PermissionError(msg) from e
    except OSError as e:
        msg = f"Failed to write config file: {config_file}"
        raise OSError(msg) from e
    except Exception as e:
        msg = f"Failed to serialize config data: {e}"
        raise ValueError(msg) from e


def create_default_config() -> VPWConfig:
    """
    Create and save a default configuration file.

    Returns:
        Default VPW configuration

    Raises:
        PermissionError: If unable to write config file
        OSError: If unable to create config directory
        ValueError: If config serialization fails
    """
    config = VPWConfig()
    config_file = get_config_file()

    if not config_file.exists():
        try:
            save_config(config, config_file)
        except (PermissionError, OSError, ValueError) as e:
            # Re-raise with additional context
            msg = f"Failed to create default config file at {config_file}: {e}"
            raise type(e)(msg) from e

    return config

