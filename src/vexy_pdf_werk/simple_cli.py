# this_file: src/vexy_pdf_werk/simple_cli.py
"""Simplified CLI interface for Vexy PDF Werk with streamlined user experience."""

import asyncio
import sys
from pathlib import Path

import fire
from rich.console import Console

from vexy_pdf_werk import __version__
from vexy_pdf_werk.config import VPWConfig, load_config
from vexy_pdf_werk.core.epub_creator import EpubCreator
from vexy_pdf_werk.core.markdown_converter import MarkdownGenerator
from vexy_pdf_werk.core.metadata_extractor import MetadataExtractor
from vexy_pdf_werk.core.pdf_processor import PDFProcessor
from vexy_pdf_werk.utils.validation import validate_formats, validate_output_directory, validate_pdf_file

console = Console()


class SimplePDFConverter:
    """Simple PDF converter with streamlined interface."""

    def __init__(self) -> None:
        """Initialize the converter."""
        self._version = __version__

    def convert(
        self,
        pdf_path: str,
        output_dir: str | None = None,
        formats: str = "markdown",
    ) -> int:
        """
        Convert a PDF to different formats.

        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory (default: ./output)
            formats: Output formats: markdown, epub, pdfa, yaml (default: markdown)
        """
        try:
            return asyncio.run(self._convert_async(pdf_path, output_dir, formats))
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            return 1
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return 1

    async def _convert_async(self, pdf_path: str, output_dir: str | None, formats: str) -> int:
        """Async implementation of convert."""
        # Simple validation
        input_path = Path(pdf_path)
        if not input_path.exists():
            console.print(f"[red]File not found: {pdf_path}[/red]")
            return 1

        if not input_path.suffix.lower() == '.pdf':
            console.print(f"[red]Not a PDF file: {pdf_path}[/red]")
            return 1

        # Setup output directory
        if output_dir is None:
            output_dir = f"./output/{input_path.stem}"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Parse formats
        requested_formats = [f.strip() for f in formats.split(',')]

        console.print(f"Converting [cyan]{input_path.name}[/cyan] to {', '.join(requested_formats)}")

        # Load simple config
        config = VPWConfig()

        try:
            # Initialize processors
            pdf_processor = PDFProcessor(config)
            markdown_generator = MarkdownGenerator(config.conversion)

            results = []

            # Process formats
            if 'pdfa' in requested_formats:
                enhanced_pdf_path = output_path / f"{input_path.stem}_enhanced.pdf"
                result = await pdf_processor.create_better_pdf(input_path, enhanced_pdf_path)
                if result.success:
                    console.print(f"✓ Created enhanced PDF")
                    results.append('pdfa')

            markdown_result = None
            if 'markdown' in requested_formats or 'epub' in requested_formats:
                markdown_result = await markdown_generator.generate_markdown(input_path, output_path)
                if markdown_result.success:
                    console.print(f"✓ Created {len(markdown_result.pages)} markdown files")
                    if 'markdown' in requested_formats:
                        results.append('markdown')

            if 'epub' in requested_formats and markdown_result and markdown_result.success:
                pdf_info = await pdf_processor.analyze_pdf(input_path)
                epub_creator = EpubCreator(
                    book_title=pdf_info.title or input_path.stem,
                    author=pdf_info.author or "Unknown"
                )
                epub_path = output_path / f"{input_path.stem}.epub"
                epub_result = await epub_creator.create_epub(markdown_result, epub_path, input_path)
                if epub_result.success:
                    console.print(f"✓ Created ePub")
                    results.append('epub')

            if 'yaml' in requested_formats:
                pdf_info = await pdf_processor.analyze_pdf(input_path)
                metadata_extractor = MetadataExtractor()
                metadata = metadata_extractor.extract_metadata(
                    input_path, pdf_info, markdown_result, results, 0.0
                )
                yaml_path = output_path / "metadata.yaml"
                metadata_extractor.save_metadata_yaml(metadata, yaml_path)
                console.print(f"✓ Created metadata")
                results.append('yaml')

            console.print(f"\n[green]Done![/green] Output: {output_path}")
            return 0

        except ImportError as e:
            console.print(f"[red]Missing dependency: {e}[/red]")
            console.print("Install with: pip install vexy-pdf-werk[all]")
            return 1

    def version(self) -> None:
        """Show version."""
        console.print(f"Vexy PDF Werk {self._version}")


def main() -> None:
    """Main entry point."""
    try:
        fire.Fire(SimplePDFConverter)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    main()