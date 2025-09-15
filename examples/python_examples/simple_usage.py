#!/usr/bin/env python3
# this_file: examples/python_examples/simple_usage.py
"""
Simple usage example for Vexy PDF Werk.

This demonstrates the easiest way to convert PDFs.
"""

import asyncio
from pathlib import Path

# For this example, assume vexy-pdf-werk is installed
from vexy_pdf_werk.config import VPWConfig
from vexy_pdf_werk.core.markdown_converter import MarkdownGenerator


async def convert_pdf_simple():
    """Convert a PDF to markdown - simple example."""
    # Input PDF
    pdf_file = Path("sample.pdf")

    # Output directory
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    # Convert to markdown
    config = VPWConfig()
    converter = MarkdownGenerator(config.conversion)

    result = await converter.generate_markdown(pdf_file, output_dir)

    if result.success:
        print(f"✓ Converted {len(result.pages)} pages to markdown")
        print(f"Output: {output_dir}")
    else:
        print(f"✗ Conversion failed: {result.error}")


async def convert_pdf_all_formats():
    """Convert a PDF to all formats - complete example."""
    from vexy_pdf_werk.core.pdf_processor import PDFProcessor
    from vexy_pdf_werk.core.epub_creator import EpubCreator
    from vexy_pdf_werk.core.metadata_extractor import MetadataExtractor

    pdf_file = Path("sample.pdf")
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)

    config = VPWConfig()

    # 1. Enhanced PDF
    pdf_processor = PDFProcessor(config)
    enhanced_pdf = output_dir / "enhanced.pdf"
    await pdf_processor.create_better_pdf(pdf_file, enhanced_pdf)
    print("✓ Created enhanced PDF")

    # 2. Markdown
    markdown_generator = MarkdownGenerator(config.conversion)
    markdown_result = await markdown_generator.generate_markdown(pdf_file, output_dir)
    print(f"✓ Created {len(markdown_result.pages)} markdown files")

    # 3. ePub
    pdf_info = await pdf_processor.analyze_pdf(pdf_file)
    epub_creator = EpubCreator(book_title=pdf_info.title or "Book")
    epub_file = output_dir / "book.epub"
    await epub_creator.create_epub(markdown_result, epub_file, pdf_file)
    print("✓ Created ePub")

    # 4. Metadata
    metadata_extractor = MetadataExtractor()
    metadata = metadata_extractor.extract_metadata(
        pdf_file, pdf_info, markdown_result, ["pdfa", "markdown", "epub"], 0.0
    )
    yaml_file = output_dir / "metadata.yaml"
    metadata_extractor.save_metadata_yaml(metadata, yaml_file)
    print("✓ Created metadata")


if __name__ == "__main__":
    # Simple conversion
    asyncio.run(convert_pdf_simple())

    # Full conversion (uncomment to try)
    # asyncio.run(convert_pdf_all_formats())