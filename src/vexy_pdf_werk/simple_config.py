# this_file: src/vexy_pdf_werk/simple_config.py
"""Simplified configuration for easier user experience."""

from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class SimpleConfig:
    """Simple configuration with only essential options."""

    # Output settings
    output_dir: str = "./output"
    formats: list[str] = field(default_factory=lambda: ["markdown"])

    # Quality settings (simple)
    quality: str = "high"  # high, medium, low

    # Converter preference
    markdown_converter: str = "auto"  # auto, marker, basic

    # Simple flags
    paginate_markdown: bool = True
    include_images: bool = True
    ocr_language: str = "eng"

    @classmethod
    def load_from_file(cls, config_file: Path | None = None) -> "SimpleConfig":
        """Load simple config from file if it exists, otherwise use defaults."""
        if config_file and config_file.exists():
            # Simple TOML loading (basic implementation)
            try:
                import toml
                data = toml.load(config_file)

                # Extract only the fields we care about
                return cls(
                    output_dir=data.get("output_dir", "./output"),
                    formats=data.get("formats", ["markdown"]),
                    quality=data.get("quality", "high"),
                    markdown_converter=data.get("markdown_converter", "auto"),
                    paginate_markdown=data.get("paginate_markdown", True),
                    include_images=data.get("include_images", True),
                    ocr_language=data.get("ocr_language", "eng"),
                )
            except Exception:
                # If loading fails, just use defaults
                pass

        return cls()

    def save_to_file(self, config_file: Path) -> None:
        """Save simple config to file."""
        config_file.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "output_dir": self.output_dir,
            "formats": self.formats,
            "quality": self.quality,
            "markdown_converter": self.markdown_converter,
            "paginate_markdown": self.paginate_markdown,
            "include_images": self.include_images,
            "ocr_language": self.ocr_language,
        }

        try:
            import toml
            with open(config_file, "w") as f:
                toml.dump(config_data, f)
        except Exception:
            # If saving fails, just ignore
            pass

    def to_vpw_config(self):
        """Convert to full VPWConfig for internal use."""
        from vexy_pdf_werk.config import VPWConfig, ProcessingConfig, ConversionConfig, OutputConfig

        return VPWConfig(
            processing=ProcessingConfig(
                ocr_language=self.ocr_language,
                pdf_quality=self.quality,
            ),
            conversion=ConversionConfig(
                markdown_backend=self.markdown_converter,
                paginate_markdown=self.paginate_markdown,
                include_images=self.include_images,
            ),
            output=OutputConfig(
                formats=self.formats,
                output_directory=self.output_dir,
            ),
        )