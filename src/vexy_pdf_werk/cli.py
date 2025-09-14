#!/usr/bin/env python3
# this_file: src/vexy_pdf_werk/cli.py
"""Fire-based CLI interface for Vexy PDF Werk."""

import sys
from pathlib import Path

import fire
from loguru import logger
from rich.console import Console

from vexy_pdf_werk import __version__
from vexy_pdf_werk.config import create_default_config, get_config_file, load_config

console = Console()


class VexyPDFWerk:
    """Vexy PDF Werk - Transform PDFs into better formats."""

    def __init__(self):
        """Initialize the VPW CLI."""
        self.version = __version__

    def process(
        self,
        pdf_path: str,
        output_dir: str | None = None,
        formats: str = "pdfa,markdown,epub,yaml",
        verbose: bool = False,
        config_file: str | None = None,
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

        # Load configuration
        config_path = Path(config_file) if config_file else None
        config = load_config(config_path)

        # Validate inputs
        input_path = Path(pdf_path)
        if not input_path.exists():
            console.print(f"[red]Error: PDF file not found: {pdf_path}[/red]")
            return 1

        if input_path.suffix.lower() != '.pdf':
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
        if isinstance(formats, (list, tuple)):
            # Fire sometimes parses comma-separated values as tuples
            requested_formats = [str(f).strip() for f in formats]
        else:
            requested_formats = [f.strip() for f in str(formats).split(',')]
        valid_formats = {'pdfa', 'markdown', 'epub', 'yaml'}
        invalid_formats = set(requested_formats) - valid_formats

        if invalid_formats:
            console.print(f"[red]Error: Invalid formats: {', '.join(invalid_formats)}[/red]")
            console.print(f"Valid formats: {', '.join(valid_formats)}")
            return 1

        console.print(f"Requested formats: [green]{', '.join(requested_formats)}[/green]")

        # Run the processing pipeline
        try:
            import asyncio
            result = asyncio.run(self._run_processing_pipeline(
                input_path, output_path, requested_formats, config, verbose
            ))
            return result
        except Exception as e:
            console.print(f"[red]Processing failed: {e}[/red]")
            if verbose:
                import traceback
                console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")
            return 1

    async def _run_processing_pipeline(
        self,
        input_path: Path,
        output_path: Path,
        requested_formats: list[str],
        config,
        verbose: bool
    ) -> int:
        """Run the complete PDF processing pipeline."""
        import time
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

        from .core.pdf_processor import PDFProcessor
        from .core.markdown_converter import MarkdownGenerator
        from .core.metadata_extractor import MetadataExtractor

        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:

            # Initialize processors
            try:
                pdf_processor = PDFProcessor(config)
                markdown_generator = MarkdownGenerator(config.conversion)
                metadata_extractor = MetadataExtractor()
            except Exception as e:
                console.print(f"[red]Failed to initialize processors: {e}[/red]")
                return 1

            formats_completed = []

            # Step 1: PDF Enhancement (if requested)
            if 'pdfa' in requested_formats:
                task = progress.add_task("Enhancing PDF with OCR and PDF/A conversion...", total=1)

                enhanced_pdf_path = output_path / f"{input_path.stem}_enhanced.pdf"
                result = await pdf_processor.create_better_pdf(
                    input_path, enhanced_pdf_path, progress, task
                )

                if result.success:
                    progress.update(task, completed=1, description="PDF enhancement completed")
                    formats_completed.append('pdfa')
                    console.print(f"[green]✓[/green] Enhanced PDF created: {enhanced_pdf_path}")
                else:
                    progress.update(task, completed=1, description="PDF enhancement failed")
                    console.print(f"[red]✗[/red] PDF enhancement failed: {result.error}")
                    console.print("[yellow]Continuing with original PDF for other formats...[/yellow]")

            # Get PDF info for metadata
            pdf_info = await pdf_processor.analyze_pdf(input_path)

            # Step 2: Markdown Generation (if requested)
            markdown_result = None
            if 'markdown' in requested_formats:
                task = progress.add_task("Converting to Markdown...", total=1)

                markdown_result = await markdown_generator.generate_markdown(
                    input_path, output_path
                )

                if markdown_result.success:
                    progress.update(task, completed=1, description="Markdown conversion completed")
                    formats_completed.append('markdown')
                    page_count = len(markdown_result.pages)
                    console.print(f"[green]✓[/green] Markdown created: {page_count} pages in {output_path}")
                else:
                    progress.update(task, completed=1, description="Markdown conversion failed")
                    console.print(f"[red]✗[/red] Markdown conversion failed: {markdown_result.error}")

            # Step 3: ePub Generation (if requested)
            if 'epub' in requested_formats:
                task = progress.add_task("Generating ePub...", total=1)
                progress.update(task, completed=1, description="ePub generation not yet implemented")
                console.print("[yellow]ePub generation not yet implemented[/yellow]")

            # Step 4: Metadata YAML (if requested)
            if 'yaml' in requested_formats:
                task = progress.add_task("Generating metadata...", total=1)

                try:
                    processing_time = time.time() - start_time
                    metadata = metadata_extractor.extract_metadata(
                        input_path,
                        pdf_info,
                        markdown_result,
                        formats_completed,
                        processing_time
                    )

                    yaml_path = output_path / "metadata.yaml"
                    metadata_extractor.save_metadata_yaml(metadata, yaml_path)

                    progress.update(task, completed=1, description="Metadata generation completed")
                    formats_completed.append('yaml')
                    console.print(f"[green]✓[/green] Metadata created: {yaml_path}")

                except Exception as e:
                    progress.update(task, completed=1, description="Metadata generation failed")
                    console.print(f"[red]✗[/red] Metadata generation failed: {e}")

        # Final summary
        total_time = time.time() - start_time
        console.print(f"\n[bold green]Processing completed in {total_time:.1f}s[/bold green]")
        console.print(f"Formats created: {', '.join(formats_completed) if formats_completed else 'none'}")
        console.print(f"Output directory: [cyan]{output_path}[/cyan]")

        return 0 if formats_completed else 1

    def config(self, show: bool = False, init: bool = False):
        """
        Manage VPW configuration.

        Args:
            show: Display current configuration
            init: Initialize default configuration file
        """
        if init:
            config = create_default_config()
            config_file = get_config_file()
            console.print(f"[green]Created default configuration at: {config_file}[/green]")
            return None

        if show:
            try:
                config = load_config()
                config_file = get_config_file()

                console.print(f"[blue]Configuration loaded from: {config_file}[/blue]")
                console.print("\n[bold]Current Configuration:[/bold]")

                # Display config sections
                console.print("[cyan]Processing:[/cyan]")
                console.print(f"  OCR Language: {config.processing.ocr_language}")
                console.print(f"  PDF Quality: {config.processing.pdf_quality}")
                console.print(f"  Force OCR: {config.processing.force_ocr}")

                console.print("[cyan]Conversion:[/cyan]")
                console.print(f"  Markdown Backend: {config.conversion.markdown_backend}")
                console.print(f"  Paginate Markdown: {config.conversion.paginate_markdown}")
                console.print(f"  Include Images: {config.conversion.include_images}")

                console.print("[cyan]AI:[/cyan]")
                console.print(f"  Enabled: {config.ai.enabled}")
                console.print(f"  Provider: {config.ai.provider}")
                console.print(f"  Correction Enabled: {config.ai.correction_enabled}")

                console.print("[cyan]Output:[/cyan]")
                console.print(f"  Formats: {', '.join(config.output.formats)}")
                console.print(f"  Output Directory: {config.output.output_directory}")
                console.print(f"  Preserve Original: {config.output.preserve_original}")

            except Exception as e:
                console.print(f"[red]Error loading configuration: {e}[/red]")
                return 1
        else:
            console.print("Use --show to display config or --init to create default config")
        return None

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

