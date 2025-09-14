#!/usr/bin/env python3
# this_file: src/vexy_pdf_werk/cli.py
"""Fire-based CLI interface for Vexy PDF Werk."""

import asyncio
import sys
import time
import traceback
from pathlib import Path

import fire  # type: ignore[import-untyped]
from loguru import logger
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from vexy_pdf_werk import __version__
from vexy_pdf_werk.config import VPWConfig, create_default_config, get_config_file, load_config
from vexy_pdf_werk.core.epub_creator import EpubCreator
from vexy_pdf_werk.core.markdown_converter import MarkdownGenerator
from vexy_pdf_werk.core.metadata_extractor import MetadataExtractor
from vexy_pdf_werk.core.pdf_processor import PDFProcessor
from vexy_pdf_werk.utils.validation import validate_formats, validate_output_directory, validate_pdf_file

console = Console()


class VexyPDFWerk:
    """Vexy PDF Werk - Transform PDFs into better formats."""

    def __init__(self) -> None:
        """Initialize the VPW CLI."""
        self._version = __version__

    def process(
        self,
        pdf_path: str,
        output_dir: str | None = None,
        formats: str | list[str] | tuple[str, ...] = "pdfa,markdown,epub,yaml",
        verbose: bool = False,  # noqa: FBT001, FBT002
        config_file: str | None = None,
    ) -> int:
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

        # Validate PDF input file
        input_path = Path(pdf_path)
        try:
            validate_pdf_file(input_path)
        except (FileNotFoundError, ValueError, PermissionError) as e:
            console.print("[red]PDF Validation Error:[/red]")
            # Split multi-line error messages for better formatting
            for line in str(e).split('\n'):
                if line.strip():
                    console.print(f"  {line.strip()}")
            console.print("\n[yellow]Tip:[/yellow] Use 'vpw --help' for usage examples")
            return 1

        # Set and validate output directory
        if output_dir is None:
            output_dir = f"./output/{input_path.stem}"
        output_path = Path(output_dir)

        try:
            validate_output_directory(output_path, create_if_missing=True, min_free_space_mb=50)
        except (ValueError, PermissionError, OSError) as e:
            console.print("[red]Output Directory Error:[/red]")
            # Split multi-line error messages for better formatting
            for line in str(e).split('\n'):
                if line.strip():
                    console.print(f"  {line.strip()}")
            console.print("\n[yellow]Tip:[/yellow] Try using a different output directory with --output-dir")
            return 1

        console.print(f"Processing: [cyan]{input_path}[/cyan]")
        console.print(f"Output directory: [cyan]{output_path}[/cyan]")

        # Parse and validate requested formats
        if isinstance(formats, list | tuple):
            # Fire sometimes parses comma-separated values as tuples
            requested_formats = [str(f).strip() for f in formats]
        else:
            requested_formats = [f.strip() for f in str(formats).split(',')]

        try:
            requested_formats = validate_formats(requested_formats)
        except ValueError as e:
            console.print("[red]Format Validation Error:[/red]")
            console.print(f"  {e!s}")
            console.print("\n[yellow]Tip:[/yellow] Use formats like: --formats=\"markdown,epub,yaml\"")
            console.print("[yellow]Available formats:[/yellow] pdfa, markdown, epub, yaml")
            return 1

        console.print(f"Requested formats: [green]{', '.join(requested_formats)}[/green]")

        # Check dependencies: ePub requires Markdown
        needs_markdown = 'markdown' in requested_formats or 'epub' in requested_formats
        if needs_markdown and 'markdown' not in requested_formats:
            console.print("[yellow]Note: ePub generation requires Markdown - will generate markdown content[/yellow]")

        # Run the processing pipeline
        try:
            return asyncio.run(self._run_processing_pipeline(
                input_path, output_path, requested_formats, config
            ))
        except KeyboardInterrupt:
            console.print("\n[yellow]Processing interrupted by user[/yellow]")
            console.print("[yellow]Tip:[/yellow] Partial results may be available in the output directory")
            return 1
        except MemoryError:
            console.print("[red]Processing Failed - Insufficient Memory:[/red]")
            console.print("  The PDF file is too large to process with available system memory.")
            console.print(f"  File size: {input_path.stat().st_size / (1024*1024):.1f} MB")
            console.print("\n[yellow]Suggestions:[/yellow]")
            console.print("  • Try processing on a system with more RAM")
            console.print("  • Split the PDF into smaller sections")
            console.print("  • Close other applications to free up memory")
            return 1
        except PermissionError as e:
            console.print("[red]Processing Failed - Permission Denied:[/red]")
            console.print(f"  {e!s}")
            console.print("\n[yellow]Suggestions:[/yellow]")
            console.print("  • Check file and directory permissions")
            console.print("  • Try running with appropriate user privileges")
            console.print("  • Ensure the PDF file is not open in another application")
            return 1
        except Exception as e:
            error_type = type(e).__name__
            console.print(f"[red]Processing Failed - {error_type}:[/red]")
            console.print(f"  {e!s}")
            console.print("\n[yellow]Troubleshooting:[/yellow]")
            console.print("  • Verify the PDF file is not corrupted")
            console.print("  • Try with a different PDF file")
            console.print("  • Check system dependencies (tesseract, qpdf, ghostscript)")
            console.print("  • Run with --verbose for detailed error information")
            if verbose:
                console.print("\n[red]Detailed Traceback:[/red]")
                console.print(f"{traceback.format_exc()}")
            return 1

    async def _run_processing_pipeline(
        self,
        input_path: Path,
        output_path: Path,
        requested_formats: list[str],
        config: VPWConfig,
    ) -> int:
        """Run the complete PDF processing pipeline."""

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
            except ImportError as e:
                console.print("[red]Initialization Failed - Missing Dependency:[/red]")
                console.print(f"  {e!s}")
                console.print("\n[yellow]Required Dependencies:[/yellow]")
                console.print("  • tesseract-ocr: for OCR processing")
                console.print("  • qpdf: for PDF optimization")
                console.print("  • ghostscript: for PDF/A conversion")
                console.print("  • python packages: see requirements.txt")
                console.print("\n[yellow]Installation Help:[/yellow]")
                console.print("  • Ubuntu/Debian: sudo apt-get install tesseract-ocr qpdf ghostscript")
                console.print("  • macOS: brew install tesseract qpdf ghostscript")
                console.print("  • Windows: choco install tesseract qpdf ghostscript")
                return 1
            except Exception as e:
                error_type = type(e).__name__
                console.print(f"[red]Initialization Failed - {error_type}:[/red]")
                console.print(f"  {e!s}")
                console.print("\n[yellow]Troubleshooting:[/yellow]")
                console.print("  • Check configuration file validity")
                console.print("  • Try 'vpw config --init' to reset configuration")
                console.print("  • Verify all system dependencies are installed")
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

            # Step 2: Markdown Generation (if requested or needed for ePub)
            markdown_result = None
            if 'markdown' in requested_formats or 'epub' in requested_formats:
                task = progress.add_task("Converting to Markdown...", total=1)

                markdown_result = await markdown_generator.generate_markdown(
                    input_path, output_path
                )

                if markdown_result.success:
                    progress.update(task, completed=1, description="Markdown conversion completed")
                    if 'markdown' in requested_formats:
                        formats_completed.append('markdown')
                    page_count = len(markdown_result.pages)
                    console.print(f"[green]✓[/green] Markdown created: {page_count} pages in {output_path}")
                else:
                    progress.update(task, completed=1, description="Markdown conversion failed")
                    console.print(f"[red]✗[/red] Markdown conversion failed: {markdown_result.error}")

            # Step 3: ePub Generation (if requested)
            if 'epub' in requested_formats:
                task = progress.add_task("Generating ePub...", total=1)

                if markdown_result and markdown_result.success:
                    try:
                        # Determine book metadata from PDF info
                        book_title = pdf_info.title
                        author = pdf_info.author

                        epub_creator = EpubCreator(book_title=book_title, author=author)
                        epub_path = output_path / f"{input_path.stem}.epub"

                        epub_result = await epub_creator.create_epub(
                            markdown_result, epub_path, input_path
                        )

                        if epub_result.success:
                            progress.update(task, completed=1, description="ePub generation completed")
                            formats_completed.append('epub')
                            console.print(f"[green]✓[/green] ePub created: {epub_path}")
                        else:
                            progress.update(task, completed=1, description="ePub generation failed")
                            console.print(f"[red]✗[/red] ePub generation failed: {epub_result.error}")

                    except ImportError as e:
                        progress.update(task, completed=1, description="ePub generation failed")
                        console.print(f"[red]✗[/red] ePub generation failed - Missing dependency: {e}")
                        console.print(
                            "[yellow]Tip:[/yellow] Install with 'pip install ebooklib' "
                            "or 'pip install vexy-pdf-werk[epub]'"
                        )
                    except Exception as e:
                        progress.update(task, completed=1, description="ePub generation failed")
                        error_type = type(e).__name__
                        console.print(f"[red]✗[/red] ePub generation failed - {error_type}: {e}")
                        console.print("[yellow]Tip:[/yellow] Ensure markdown content is valid and complete")
                else:
                    progress.update(task, completed=1, description="ePub generation skipped - no markdown content")
                    console.print("[yellow]ePub generation skipped - markdown conversion required[/yellow]")

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

                except PermissionError as e:
                    progress.update(task, completed=1, description="Metadata generation failed")
                    console.print(f"[red]✗[/red] Metadata generation failed - Permission denied: {e}")
                    console.print("[yellow]Tip:[/yellow] Check write permissions for the output directory")
                except Exception as e:
                    progress.update(task, completed=1, description="Metadata generation failed")
                    error_type = type(e).__name__
                    console.print(f"[red]✗[/red] Metadata generation failed - {error_type}: {e}")
                    console.print(
                        "[yellow]Tip:[/yellow] This usually indicates an issue with "
                        "PDF analysis or YAML formatting"
                    )

        # Final summary
        total_time = time.time() - start_time
        console.print(f"\n[bold green]Processing completed in {total_time:.1f}s[/bold green]")
        console.print(f"Formats created: {', '.join(formats_completed) if formats_completed else 'none'}")
        console.print(f"Output directory: [cyan]{output_path}[/cyan]")

        return 0 if formats_completed else 1

    def config(self, show: bool = False, init: bool = False) -> int | None:  # noqa: FBT001, FBT002
        """
        Manage VPW configuration.

        Args:
            show: Display current configuration
            init: Initialize default configuration file

        Returns:
            Exit code (1 for error, None for success)
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

            except FileNotFoundError:
                console.print("[red]Configuration Error - Config File Not Found:[/red]")
                console.print("  No configuration file found at expected location")
                console.print("\n[yellow]Solutions:[/yellow]")
                console.print("  • Run 'vpw config --init' to create default configuration")
                console.print("  • Use --config-file to specify a custom config file")
                return 1
            except PermissionError as e:
                console.print("[red]Configuration Error - Permission Denied:[/red]")
                console.print(f"  Cannot read configuration file: {e!s}")
                console.print("\n[yellow]Solutions:[/yellow]")
                console.print("  • Check file permissions on the configuration directory")
                console.print("  • Run with appropriate user privileges")
                return 1
            except Exception as e:
                error_type = type(e).__name__
                console.print(f"[red]Configuration Error - {error_type}:[/red]")
                console.print(f"  {e!s}")
                console.print("\n[yellow]Solutions:[/yellow]")
                console.print("  • Check configuration file syntax (valid TOML format)")
                console.print("  • Run 'vpw config --init' to reset to defaults")
                console.print("  • Use --verbose for detailed error information")
                return 1
        else:
            console.print("Use --show to display config or --init to create default config")
        return None

    def version(self) -> None:
        """Display version information."""
        console.print(f"Vexy PDF Werk version {self._version}")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        fire.Fire(VexyPDFWerk)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except ImportError as e:
        console.print("[red]Import Error - Missing Dependency:[/red]")
        console.print(f"  {e!s}")
        console.print("\n[yellow]Installation Required:[/yellow]")
        console.print("  • pip install vexy-pdf-werk[all]")
        console.print("  • Or install missing system dependencies")
        sys.exit(1)
    except Exception as e:
        error_type = type(e).__name__
        console.print(f"[red]Unexpected Error - {error_type}:[/red]")
        console.print(f"  {e!s}")
        console.print("\n[yellow]This may be a bug - please report it:[/yellow]")
        console.print("  • Include this error message")
        console.print("  • Include your command and PDF file details")
        console.print("  • Report at: https://github.com/vexyart/vexy-pdf-werk/issues")
        sys.exit(1)


if __name__ == "__main__":
    main()

