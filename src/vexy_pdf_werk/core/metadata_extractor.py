# this_file: src/vexy_pdf_werk/core/metadata_extractor.py
"""Metadata extraction and YAML generation for PDF documents."""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml
from loguru import logger

from .pdf_processor import PDFInfo
from .markdown_converter import MarkdownResult


@dataclass
class DocumentMetadata:
    """Complete metadata for a processed document."""
    # Source information
    source_file: str
    source_size_bytes: int
    processed_at: str

    # PDF metadata
    pdf_pages: int
    pdf_title: Optional[str] = None
    pdf_author: Optional[str] = None
    pdf_creation_date: Optional[str] = None
    pdf_has_text: bool = False
    pdf_is_scanned: bool = False
    pdf_has_images: bool = False

    # Processing information
    formats_generated: List[str] = None
    markdown_pages: int = 0
    processing_time_seconds: float = 0.0

    # Content summary
    estimated_word_count: int = 0
    first_page_preview: Optional[str] = None

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.formats_generated is None:
            self.formats_generated = []


class MetadataExtractor:
    """Extracts and generates metadata for processed documents."""

    def __init__(self):
        """Initialize the metadata extractor."""
        pass

    def extract_metadata(
        self,
        pdf_path: Path,
        pdf_info: PDFInfo,
        markdown_result: Optional[MarkdownResult] = None,
        formats_generated: Optional[List[str]] = None,
        processing_time: float = 0.0
    ) -> DocumentMetadata:
        """
        Extract comprehensive metadata from processed document.

        Args:
            pdf_path: Path to original PDF
            pdf_info: PDF analysis information
            markdown_result: Markdown conversion result
            formats_generated: List of generated output formats
            processing_time: Total processing time in seconds

        Returns:
            Complete document metadata
        """
        logger.debug(f"Extracting metadata for {pdf_path}")

        # Get file size
        file_size = pdf_path.stat().st_size if pdf_path.exists() else 0

        # Calculate word count and get preview
        word_count = 0
        first_page_preview = None

        if markdown_result and markdown_result.success and markdown_result.pages:
            word_count = self._calculate_word_count(markdown_result)
            first_page_preview = self._get_first_page_preview(markdown_result)

        metadata = DocumentMetadata(
            # Source information
            source_file=pdf_path.name,
            source_size_bytes=file_size,
            processed_at=datetime.now().isoformat(),

            # PDF metadata
            pdf_pages=pdf_info.pages,
            pdf_title=pdf_info.title,
            pdf_author=pdf_info.author,
            pdf_creation_date=pdf_info.creation_date,
            pdf_has_text=pdf_info.has_text,
            pdf_is_scanned=pdf_info.is_scanned,
            pdf_has_images=pdf_info.has_images,

            # Processing information
            formats_generated=formats_generated or [],
            markdown_pages=len(markdown_result.pages) if markdown_result else 0,
            processing_time_seconds=round(processing_time, 2),

            # Content summary
            estimated_word_count=word_count,
            first_page_preview=first_page_preview
        )

        logger.debug(f"Extracted metadata with {word_count} estimated words")
        return metadata

    def save_metadata_yaml(self, metadata: DocumentMetadata, output_path: Path) -> None:
        """
        Save metadata to YAML file.

        Args:
            metadata: Document metadata to save
            output_path: Path to output YAML file
        """
        try:
            # Convert to dictionary and clean up None values
            metadata_dict = asdict(metadata)
            metadata_dict = self._clean_metadata_dict(metadata_dict)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write YAML file
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    metadata_dict,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False
                )

            logger.debug(f"Saved metadata to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save metadata YAML: {e}")
            raise

    def _calculate_word_count(self, markdown_result: MarkdownResult) -> int:
        """
        Calculate estimated word count from markdown content.

        Args:
            markdown_result: Markdown conversion result

        Returns:
            Estimated word count
        """
        total_words = 0

        for page in markdown_result.pages:
            if page.content:
                # Simple word counting - split by whitespace and count non-empty strings
                words = [word.strip() for word in page.content.split() if word.strip()]
                # Filter out markdown formatting and very short "words"
                meaningful_words = [
                    word for word in words
                    if len(word) > 1 and not word.startswith('#') and word != '---'
                ]
                total_words += len(meaningful_words)

        return total_words

    def _get_first_page_preview(self, markdown_result: MarkdownResult) -> Optional[str]:
        """
        Extract a preview from the first page content.

        Args:
            markdown_result: Markdown conversion result

        Returns:
            Preview text or None
        """
        if not markdown_result.pages:
            return None

        first_page = markdown_result.pages[0]
        if not first_page.content:
            return None

        # Get first few lines of content
        lines = [line.strip() for line in first_page.content.split('\n') if line.strip()]

        if not lines:
            return None

        # Take first 2-3 meaningful lines, up to ~200 characters
        preview_lines = []
        char_count = 0

        for line in lines[:5]:  # Check up to 5 lines
            if char_count + len(line) > 200:
                break

            # Skip markdown headers and formatting
            if line.startswith('#') or line == '---':
                continue

            preview_lines.append(line)
            char_count += len(line) + 1  # +1 for space

            if len(preview_lines) >= 2 and char_count > 100:
                break

        if not preview_lines:
            return None

        preview = ' '.join(preview_lines)

        # Truncate if still too long
        if len(preview) > 200:
            preview = preview[:197] + "..."

        return preview

    def _clean_metadata_dict(self, metadata_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up metadata dictionary by removing None values and organizing structure.

        Args:
            metadata_dict: Raw metadata dictionary

        Returns:
            Cleaned metadata dictionary
        """
        cleaned = {}

        # Organize into logical sections
        cleaned['document'] = {
            'source_file': metadata_dict['source_file'],
            'source_size_bytes': metadata_dict['source_size_bytes'],
            'processed_at': metadata_dict['processed_at'],
            'processing_time_seconds': metadata_dict['processing_time_seconds'],
        }

        cleaned['pdf_info'] = {
            'pages': metadata_dict['pdf_pages'],
            'has_text': metadata_dict['pdf_has_text'],
            'is_scanned': metadata_dict['pdf_is_scanned'],
            'has_images': metadata_dict['pdf_has_images'],
        }

        # Add optional PDF metadata if present
        if metadata_dict.get('pdf_title'):
            cleaned['pdf_info']['title'] = metadata_dict['pdf_title']
        if metadata_dict.get('pdf_author'):
            cleaned['pdf_info']['author'] = metadata_dict['pdf_author']
        if metadata_dict.get('pdf_creation_date'):
            cleaned['pdf_info']['creation_date'] = metadata_dict['pdf_creation_date']

        cleaned['processing'] = {
            'formats_generated': metadata_dict['formats_generated'],
            'markdown_pages': metadata_dict['markdown_pages'],
        }

        cleaned['content'] = {
            'estimated_word_count': metadata_dict['estimated_word_count'],
        }

        if metadata_dict.get('first_page_preview'):
            cleaned['content']['first_page_preview'] = metadata_dict['first_page_preview']

        return cleaned