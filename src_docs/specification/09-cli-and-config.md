##### 2. Create Basic CLI Framework
```python
#!/usr/bin/env python3
## 19. this_file: src/vexy_pdf_werk/cli.py

"""Fire-based CLI interface for Vexy PDF Werk."""

import sys
from pathlib import Path
from typing import Optional

import fire
from loguru import logger
from rich.console import Console

from . import __version__

console = Console()


class VexyPDFWerk:
    """Vexy PDF Werk - Transform PDFs into better formats."""

    def __init__(self):
        """Initialize the VPW CLI."""
        self.version = __version__

    def process(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        formats: str = "pdfa,markdown,epub,yaml",
        verbose: bool = False,
        config_file: Optional[str] = None,
    ):
        """
        Process a PDF file through the complete VPW pipeline.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Output directory (default: ./output)
            formats: Comma-separated list of output formats
            verbose: Enable verbose logging
            config_file: Path to custom config file
        """
        if verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")

        console.print(f"[bold blue]Vexy PDF Werk v{self.version}[/bold blue]")

        # Validate inputs
        input_path = Path(pdf_path)
        if not input_path.exists():
            console.print(f"[red]Error: PDF file not found: {pdf_path}[/red]")
            return 1

        if not input_path.suffix.lower() == '.pdf':
            console.print(f"[red]Error: File must be a PDF: {pdf_path}[/red]")
            return 1

        # Set output directory
        if output_dir is None:
            output_dir = f"./output/{input_path.stem}"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        console.print(f"Processing: [cyan]{input_path}[/cyan]")
        console.print(f"Output directory: [cyan]{output_path}[/cyan]")

        # Parse requested formats
        requested_formats = [f.strip() for f in formats.split(',')]
        valid_formats = {'pdfa', 'markdown', 'epub', 'yaml'}
        invalid_formats = set(requested_formats) - valid_formats

        if invalid_formats:
            console.print(f"[red]Error: Invalid formats: {', '.join(invalid_formats)}[/red]")
            console.print(f"Valid formats: {', '.join(valid_formats)}")
            return 1

        console.print(f"Requested formats: [green]{', '.join(requested_formats)}[/green]")

        # TODO: Implement actual processing pipeline
        console.print("[yellow]Processing pipeline not yet implemented[/yellow]")
        return 0

    def config(self, show: bool = False, init: bool = False):
        """
        Manage VPW configuration.

        Args:
            show: Display current configuration
            init: Initialize default configuration file
        """
        if show:
            console.print("[blue]Configuration management not yet implemented[/blue]")
        elif init:
            console.print("[blue]Configuration initialization not yet implemented[/blue]")
        else:
            console.print("Use --show to display config or --init to create default config")

    def version(self):
        """Display version information."""
        console.print(f"Vexy PDF Werk version {self.version}")


def main():
    """Main entry point for the CLI."""
    try:
        fire.Fire(VexyPDFWerk)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

##### 3. Create Basic Configuration Module

```python
## 20. this_file: src/vexy_pdf_werk/config.py

"""Configuration management for Vexy PDF Werk."""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List

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
    max_tokens: int = 4000


class OutputConfig(BaseModel):
    """Output configuration."""
    formats: List[str] = Field(default=["pdfa", "markdown", "epub", "yaml"])
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
    tesseract_path: Optional[str] = None
    qpdf_path: Optional[str] = None
    pandoc_path: Optional[str] = None


def get_config_dir() -> Path:
    """Get the user configuration directory."""
    return Path(user_config_dir("vexy-pdf-werk"))


def get_config_file() -> Path:
    """Get the path to the main configuration file."""
    return get_config_dir() / "config.toml"


def load_config(config_file: Optional[Path] = None) -> VPWConfig:
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
    env_overrides = {}

    # AI configuration from environment
    if api_key := os.getenv("DATALAB_API_KEY"):
        env_overrides.setdefault("ai", {})["datalab_api_key"] = api_key

    if claude_key := os.getenv("ANTHROPIC_API_KEY"):
        env_overrides.setdefault("ai", {})["claude_api_key"] = claude_key

    if gemini_key := os.getenv("GOOGLE_AI_API_KEY"):
        env_overrides.setdefault("ai", {})["gemini_api_key"] = gemini_key

    # Tool paths from environment
    if tesseract := os.getenv("TESSERACT_PATH"):
        env_overrides["tesseract_path"] = tesseract

    if qpdf := os.getenv("QPDF_PATH"):
        env_overrides["qpdf_path"] = qpdf

    # Merge configurations (env overrides config file)
    final_config = {**config_data, **env_overrides}

    return VPWConfig(**final_config)


def save_config(config: VPWConfig, config_file: Optional[Path] = None) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration to save
        config_file: Optional path to config file
    """
    if config_file is None:
        config_file = get_config_file()

    # Ensure config directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dictionary and save
    config_dict = config.model_dump()
    with open(config_file, 'w') as f:
        toml.dump(config_dict, f)


def create_default_config() -> VPWConfig:
    """Create and save a default configuration file."""
    config = VPWConfig()
    config_file = get_config_file()

    if not config_file.exists():
        save_config(config, config_file)

    return config
```