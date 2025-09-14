#!/usr/bin/env python3
# this_file: examples/python_examples/basic_usage.py
"""
Basic usage example for Vexy PDF Werk Python API.

This script demonstrates the simplest way to process a PDF using the library.
"""

import sys
from pathlib import Path

# Add the parent directory to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from vexy_pdf_werk.core.pdf_processor import PDFProcessor
from vexy_pdf_werk.core.markdown_converter import MarkdownGenerator
from vexy_pdf_werk.core.epub_creator import EpubCreator
from vexy_pdf_werk.core.metadata_extractor import MetadataExtractor
from vexy_pdf_werk.config import Config


def main():
    """Demonstrate basic PDF processing workflow."""
    print("🔧 Vexy PDF Werk - Basic Usage Example")
    print("=" * 50)

    # Setup paths
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = Path(__file__).parent.parent / "output" / "basic_example"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Choose a sample PDF
    pdf_file = data_dir / "test1.pdf"

    if not pdf_file.exists():
        print(f"❌ Sample PDF not found: {pdf_file}")
        print("Please ensure test1.pdf exists in the data directory.")
        return

    print(f"📄 Processing: {pdf_file.name}")
    print(f"📁 Output directory: {output_dir}")

    try:
        # Step 1: Initialize PDF processor
        print("\n🔍 Step 1: Analyzing PDF...")
        processor = PDFProcessor()

        # Analyze the PDF
        pdf_info = processor.analyze_pdf(pdf_file)
        print(f"   ✓ Pages: {pdf_info.pages}")
        print(f"   ✓ Has text: {pdf_info.has_text}")
        print(f"   ✓ Is scanned: {pdf_info.is_scanned}")
        print(f"   ✓ Has images: {pdf_info.has_images}")
        if pdf_info.title:
            print(f"   ✓ Title: {pdf_info.title}")

        # Step 2: Convert to Markdown
        print("\n📝 Step 2: Converting to Markdown...")
        markdown_generator = MarkdownGenerator()
        markdown_result = markdown_generator.convert_pdf_to_markdown(pdf_file)

        if markdown_result.success:
            print(f"   ✓ Successfully converted {len(markdown_result.pages)} pages")

            # Save markdown files
            for i, page in enumerate(markdown_result.pages):
                page_file = output_dir / f"{i:03d}--{page.slug}.md"
                page_file.write_text(
                    f"---\ntitle: {page.title}\npage: {page.page_number + 1}\nslug: {page.slug}\n---\n\n{page.content}",
                    encoding='utf-8'
                )
                print(f"   ✓ Saved: {page_file.name}")
        else:
            print("   ❌ Markdown conversion failed")
            return

        # Step 3: Create ePub
        print("\n📚 Step 3: Creating ePub...")
        epub_creator = EpubCreator()
        epub_path = output_dir / f"{pdf_file.stem}.epub"

        epub_success = epub_creator.create_epub_from_markdown(
            markdown_result=markdown_result,
            output_path=epub_path,
            title=pdf_info.title or pdf_file.stem,
            author=pdf_info.author or "Unknown Author"
        )

        if epub_success:
            print(f"   ✓ Created: {epub_path.name}")
        else:
            print("   ❌ ePub creation failed")

        # Step 4: Extract metadata
        print("\n📊 Step 4: Extracting metadata...")
        metadata_extractor = MetadataExtractor()

        formats_generated = []
        if markdown_result.success:
            formats_generated.append("markdown")
        if epub_success:
            formats_generated.append("epub")

        metadata = metadata_extractor.extract_metadata(
            pdf_path=pdf_file,
            pdf_info=pdf_info,
            markdown_result=markdown_result,
            formats_generated=formats_generated,
            processing_time=0.0  # Would normally track actual time
        )

        # Save metadata to YAML
        metadata_path = output_dir / "metadata.yaml"
        metadata_extractor.save_metadata_yaml(metadata, metadata_path)
        print(f"   ✓ Saved: {metadata_path.name}")

        # Display summary
        print("\n🎉 Processing Complete!")
        print(f"📁 Output location: {output_dir}")
        print(f"📄 Generated {len(markdown_result.pages)} markdown files")
        if epub_success:
            print(f"📚 Created ePub: {epub_path.name}")
        print(f"📊 Metadata: {metadata_path.name}")
        print(f"📈 Estimated word count: {metadata.estimated_word_count}")

    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        print("Check that all system dependencies are installed:")
        print("  - tesseract-ocr")
        print("  - qpdf")
        print("  - ghostscript")
        print("  - pandoc")


if __name__ == "__main__":
    main()