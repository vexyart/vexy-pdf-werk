##### Markdown Generator with Multiple Backends (`src/vexy_pdf_werk/core/markdown_generator.py`)

```python
## 51. this_file: src/vexy_pdf_werk/core/markdown_generator.py

"""Markdown generation with multiple conversion backends."""

import asyncio
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from loguru import logger
from rich.progress import Progress, TaskID

from ..config import VPWConfig, ConversionConfig
from ..utils.slug_utils import generate_page_slug
from ..utils.file_utils import ensure_directory
from .pdf_processor import PDFInfo


@dataclass
class PageContent:
    """Content of a single page."""
    page_number: int
    markdown_content: str
    images: List[Path]
    slug: str


@dataclass
class MarkdownResult:
    """Result of markdown conversion."""
    success: bool
    pages: List[PageContent]
    images_dir: Optional[Path] = None
    error: Optional[str] = None


class MarkdownConverter(ABC):
    """Abstract base class for markdown converters."""

    @abstractmethod
    async def convert(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> MarkdownResult:
        """Convert PDF to markdown."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the converter is available."""
        pass


class MarkerConverter(MarkdownConverter):
    """Marker PDF converter."""

    async def convert(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> MarkdownResult:
        """Convert PDF using Marker."""
        logger.info("Converting PDF with Marker")

        try:
            # Import marker (lazy loading)
            from marker.convert import convert_single_pdf
            from marker.models import load_all_models

            # Load Marker models (cached)
            model_list = load_all_models()

            # Convert PDF
            full_text, images, out_meta = convert_single_pdf(
                str(pdf_path),
                model_list,
                max_pages=None,
                langs=None,
                batch_multiplier=1
            )

            # Split into pages if paginated output requested
            if config.paginate_markdown:
                pages = self._split_paginated_content(full_text, images, output_dir)
            else:
                # Single file output
                slug = generate_page_slug(full_text[:200])
                pages = [PageContent(
                    page_number=0,
                    markdown_content=full_text,
                    images=list(images.values()) if images else [],
                    slug=slug
                )]

            return MarkdownResult(success=True, pages=pages)

        except ImportError:
            logger.error("Marker not installed. Install with: pip install marker-pdf")
            return MarkdownResult(
                success=False,
                pages=[],
                error="Marker not available - install with 'pip install marker-pdf'"
            )
        except Exception as e:
            logger.error(f"Marker conversion failed: {e}")
            return MarkdownResult(success=False, pages=[], error=str(e))

    def is_available(self) -> bool:
        """Check if Marker is available."""
        try:
            import marker
            return True
        except ImportError:
            return False

    def _split_paginated_content(
        self,
        content: str,
        images: Dict[str, Path],
        output_dir: Path
    ) -> List[PageContent]:
        """Split Marker output into pages."""
        # Marker uses page separators like "{PAGE_NUMBER}\n" + dashes
        import re

        pages = []
        page_splits = re.split(r'\n(\d+)\n-{40,}\n', content)

        if len(page_splits) == 1:
            # No page markers found, treat as single page
            slug = generate_page_slug(content[:200])
            return [PageContent(0, content, list(images.values()), slug)]

        # Process split content
        for i in range(1, len(page_splits), 2):
            if i + 1 < len(page_splits):
                page_num = int(page_splits[i])
                page_content = page_splits[i + 1].strip()
                slug = generate_page_slug(page_content[:200])

                # Find images for this page (basic heuristic)
                page_images = [img for img in images.values()
                             if f"page_{page_num}" in img.name.lower()]

                pages.append(PageContent(page_num, page_content, page_images, slug))

        return pages


class MarkItDownConverter(MarkdownConverter):
    """Microsoft MarkItDown converter."""

    async def convert(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> MarkdownResult:
        """Convert PDF using MarkItDown."""
        logger.info("Converting PDF with MarkItDown")

        try:
            from markitdown import MarkItDown

            md_converter = MarkItDown()
            result = md_converter.convert(str(pdf_path))

            if config.paginate_markdown:
                # MarkItDown doesn't have built-in pagination
                # We'll need to split manually or process page-by-page
                pages = await self._convert_page_by_page(pdf_path, output_dir, config)
            else:
                slug = generate_page_slug(result.text_content[:200])
                pages = [PageContent(0, result.text_content, [], slug)]

            return MarkdownResult(success=True, pages=pages)

        except ImportError:
            logger.error("MarkItDown not installed. Install with: pip install markitdown")
            return MarkdownResult(
                success=False,
                pages=[],
                error="MarkItDown not available - install with 'pip install markitdown'"
            )
        except Exception as e:
            logger.error(f"MarkItDown conversion failed: {e}")
            return MarkdownResult(success=False, pages=[], error=str(e))

    async def _convert_page_by_page(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> List[PageContent]:
        """Convert PDF page by page for pagination."""
        import pikepdf
        from markitdown import MarkItDown

        pages = []
        md_converter = MarkItDown()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Split PDF into individual pages
            with pikepdf.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_pdf = pikepdf.new()
                    page_pdf.pages.append(page)
                    page_file = temp_path / f"page_{i:03d}.pdf"
                    page_pdf.save(page_file)

                    # Convert individual page
                    try:
                        result = md_converter.convert(str(page_file))
                        content = result.text_content.strip()

                        if content:  # Skip empty pages
                            slug = generate_page_slug(content[:200])
                            pages.append(PageContent(i, content, [], slug))

                    except Exception as e:
                        logger.warning(f"Failed to convert page {i}: {e}")
                        continue

        return pages

    def is_available(self) -> bool:
        """Check if MarkItDown is available."""
        try:
            import markitdown
            return True
        except ImportError:
            return False


class BasicConverter(MarkdownConverter):
    """Basic fallback converter using PyMuPDF."""

    async def convert(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> MarkdownResult:
        """Convert PDF using basic text extraction."""
        logger.info("Converting PDF with basic text extraction")

        try:
            import fitz  # PyMuPDF

            pages = []
            doc = fitz.open(str(pdf_path))

            for page_num in range(doc.page_count):
                page = doc[page_num]

                # Extract text with basic markdown formatting
                if config.include_images:
                    # Try markdown extraction (preserves some formatting)
                    text = page.get_text("markdown")
                else:
                    # Plain text extraction
                    text = page.get_text()

                if text.strip():  # Skip empty pages
                    slug = generate_page_slug(text[:200])

                    # Extract images if requested
                    images = []
                    if config.include_images:
                        images = await self._extract_page_images(
                            page, page_num, output_dir
                        )

                    pages.append(PageContent(page_num, text, images, slug))

            doc.close()
            return MarkdownResult(success=True, pages=pages)

        except ImportError:
            logger.error("PyMuPDF not installed. Install with: pip install PyMuPDF")
            return MarkdownResult(
                success=False,
                pages=[],
                error="PyMuPDF not available - install with 'pip install PyMuPDF'"
            )
        except Exception as e:
            logger.error(f"Basic conversion failed: {e}")
            return MarkdownResult(success=False, pages=[], error=str(e))

    async def _extract_page_images(
        self, page, page_num: int, output_dir: Path
    ) -> List[Path]:
        """Extract images from a page."""
        images = []
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Save image
                image_filename = f"page_{page_num:03d}_img_{img_index:02d}.{image_ext}"
                image_path = output_dir / "images" / image_filename
                image_path.parent.mkdir(exist_ok=True)

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                images.append(image_path)

            except Exception as e:
                logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
                continue

        return images

    def is_available(self) -> bool:
        """Check if PyMuPDF is available."""
        try:
            import fitz
            return True
        except ImportError:
            return False


class MarkdownGenerator:
    """Main markdown generation coordinator."""

    def __init__(self, config: VPWConfig):
        """Initialize the markdown generator."""
        self.config = config
        self.conversion_config = config.conversion

        # Initialize converters
        self.converters = {
            "marker": MarkerConverter(),
            "markitdown": MarkItDownConverter(),
            "basic": BasicConverter(),
        }

    async def generate_markdown(
        self,
        pdf_path: Path,
        output_dir: Path,
        pdf_info: PDFInfo,
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None
    ) -> MarkdownResult:
        """
        Generate markdown from PDF using the best available converter.

        Args:
            pdf_path: Input PDF file
            output_dir: Output directory for markdown files
            pdf_info: PDF analysis information
            progress: Optional progress tracker
            task_id: Optional progress task ID

        Returns:
            Markdown conversion result
        """
        logger.info(f"Generating markdown from {pdf_path}")

        # Select converter
        converter = self._select_converter()
        if progress and task_id is not None:
            progress.update(task_id, description=f"Converting with {converter.__class__.__name__}...")

        # Ensure output directory exists
        ensure_directory(output_dir)

        # Convert to markdown
        result = await converter.convert(pdf_path, output_dir, self.conversion_config)

        if not result.success:
            logger.error(f"Markdown conversion failed: {result.error}")
            return result

        # Write markdown files
        if progress and task_id is not None:
            progress.update(task_id, description="Writing markdown files...")

        markdown_files = await self._write_markdown_files(result.pages, output_dir)

        logger.success(f"Generated {len(markdown_files)} markdown files")
        return result

    def _select_converter(self) -> MarkdownConverter:
        """Select the best available converter."""
        backend = self.conversion_config.markdown_backend

        if backend != "auto":
            # User specified a backend
            converter = self.converters.get(backend)
            if converter and converter.is_available():
                logger.info(f"Using requested converter: {backend}")
                return converter
            else:
                logger.warning(f"Requested converter '{backend}' not available, falling back to auto")

        # Auto-selection: try converters in order of preference
        preference_order = ["marker", "markitdown", "basic"]

        for backend_name in preference_order:
            converter = self.converters[backend_name]
            if converter.is_available():
                logger.info(f"Auto-selected converter: {backend_name}")
                return converter

        # This should never happen since BasicConverter should always be available
        raise RuntimeError("No markdown converters available")

    async def _write_markdown_files(
        self,
        pages: List[PageContent],
        output_dir: Path
    ) -> List[Path]:
        """Write markdown content to individual page files."""
        markdown_files = []

        for page in pages:
            # Generate filename: 000--slug.md
            filename = f"{page.page_number:03d}--{page.slug}.md"
            file_path = output_dir / filename

            # Create content with frontmatter if it's the first page
            content = page.markdown_content
            if page.page_number == 0:
                # Add YAML frontmatter to first page
                frontmatter = self._generate_frontmatter()
                content = f"---\n{frontmatter}\n---\n\n{content}"

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            markdown_files.append(file_path)
            logger.debug(f"Wrote markdown file: {file_path}")

        return markdown_files

    def _generate_frontmatter(self) -> str:
        """Generate YAML frontmatter for the first markdown file."""
        import yaml
        from datetime import datetime

        frontmatter = {
            "generated_by": "Vexy PDF Werk",
            "generated_at": datetime.now().isoformat(),
            "conversion_backend": self.conversion_config.markdown_backend,
            "paginated": self.conversion_config.paginate_markdown,
        }

        return yaml.dump(frontmatter, default_flow_style=False).strip()
```