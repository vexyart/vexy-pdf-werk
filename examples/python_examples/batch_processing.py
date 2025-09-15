#!/usr/bin/env python3
# this_file: examples/python_examples/batch_processing.py
"""
Batch processing example for Vexy PDF Werk Python API.

This script demonstrates how to process multiple PDF files efficiently,
with progress tracking and error handling.
"""

import asyncio
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the parent directory to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from vexy_pdf_werk.core.pdf_processor import PDFProcessor
from vexy_pdf_werk.core.markdown_converter import MarkdownGenerator
from vexy_pdf_werk.core.epub_creator import EpubCreator
from vexy_pdf_werk.core.metadata_extractor import MetadataExtractor
from vexy_pdf_werk.config import VPWConfig, ConversionConfig




class BatchProcessor:
    """Handles batch processing of multiple PDF files."""

    def __init__(self, output_base_dir: Path):
        """Initialize batch processor with output directory."""
        self.output_base_dir = output_base_dir
        config = VPWConfig()
        self.pdf_processor = PDFProcessor(config)


        # Processing statistics
        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None
        }

    def process_single_pdf(self, pdf_path: Path) -> dict:
        """
        Process a single PDF file.

        Returns:
            Dictionary with processing results and metadata
        """
        start_time = time.time()
        result = {
            "pdf_path": pdf_path,
            "success": False,
            "error": None,
            "output_dir": None,
            "processing_time": 0,
            "formats_generated": []
        }

        try:
            print(f"🔄 Processing: {pdf_path.name}")

            # Create output directory for this PDF
            output_dir = self.output_base_dir / pdf_path.stem
            output_dir.mkdir(parents=True, exist_ok=True)
            result["output_dir"] = output_dir

            # Step 1: Analyze PDF
            pdf_info = asyncio.run(self.pdf_processor.analyze_pdf(pdf_path))

            # Step 2: Create enhanced PDF
            enhanced_pdf_path = output_dir / f"{pdf_path.stem}_enhanced.pdf"
            pdf_result = asyncio.run(self.pdf_processor.create_better_pdf(pdf_path, enhanced_pdf_path))

            if pdf_result.success:
                result["formats_generated"].append("pdfa")
                print(f"   ✓ Enhanced PDF: {enhanced_pdf_path.name}")
            else:
                print(f"   ⚠️  PDF enhancement failed: {pdf_result.error}")

            # Step 3: Convert to Markdown
            conversion_config = ConversionConfig()
            markdown_generator = MarkdownGenerator(conversion_config)
            markdown_result = asyncio.run(markdown_generator.generate_markdown(pdf_path, output_dir))

            if markdown_result.success:
                # Save markdown files
                for i, page in enumerate(markdown_result.pages):
                    page_file = output_dir / f"{i:03d}--{page.slug}.md"
                    frontmatter = f"---\ntitle: {page.title}\npage: {page.page_number + 1}\nslug: {page.slug}\n---\n\n"
                    page_file.write_text(frontmatter + page.content, encoding='utf-8')

                result["formats_generated"].append("markdown")
                print(f"   ✓ Markdown: {len(markdown_result.pages)} pages")

                # Step 4: Create ePub
                epub_path = output_dir / f"{pdf_path.stem}.epub"
                epub_creator = EpubCreator(book_title=pdf_info.title or pdf_path.stem, author=pdf_info.author or "Unknown Author")
                epub_result = asyncio.run(epub_creator.create_epub(
                    markdown_result=markdown_result,
                    output_path=epub_path,
                    source_pdf_path=pdf_path
                ))
                epub_success = epub_result.success

                if epub_success:
                    result["formats_generated"].append("epub")
                    print(f"   ✓ ePub: {epub_path.name}")

            # Step 5: Extract and save metadata
            processing_time = time.time() - start_time
            metadata_extractor = MetadataExtractor()
            metadata = metadata_extractor.extract_metadata(
                pdf_path=pdf_path,
                pdf_info=pdf_info,
                markdown_result=markdown_result,
                formats_generated=result["formats_generated"],
                processing_time=processing_time
            )

            metadata_path = output_dir / "metadata.yaml"
            metadata_extractor.save_metadata_yaml(metadata, metadata_path)
            result["formats_generated"].append("yaml")
            print(f"   ✓ Metadata: {metadata_path.name}")

            result["processing_time"] = processing_time
            result["success"] = True
            print(f"   ✅ Completed in {processing_time:.2f}s")

        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Failed: {e}")

        return result

    def process_batch(self, pdf_files: list[Path], max_workers: int = 2) -> list[dict]:
        """
        Process multiple PDF files in parallel.

        Args:
            pdf_files: List of PDF file paths
            max_workers: Maximum number of concurrent workers

        Returns:
            List of processing results
        """
        self.stats["total"] = len(pdf_files)
        self.stats["start_time"] = time.time()

        print(f"🚀 Starting batch processing of {len(pdf_files)} PDFs")
        print(f"👥 Using {max_workers} workers")
        print("=" * 60)

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(self.process_single_pdf, pdf_path): pdf_path
                for pdf_path in pdf_files
            }

            # Process completed tasks
            for future in as_completed(future_to_pdf):
                result = future.result()
                results.append(result)

                if result["success"]:
                    self.stats["successful"] += 1
                else:
                    self.stats["failed"] += 1

                # Progress update
                completed = self.stats["successful"] + self.stats["failed"]
                print(f"📊 Progress: {completed}/{self.stats['total']} "
                      f"(✅ {self.stats['successful']} ❌ {self.stats['failed']})")

        self.stats["end_time"] = time.time()
        return results

    def print_summary(self, results: list[dict]):
        """Print a summary of batch processing results."""
        total_time = self.stats["end_time"] - self.stats["start_time"]

        print("\n" + "=" * 60)
        print("📋 BATCH PROCESSING SUMMARY")
        print("=" * 60)
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"📄 Total PDFs: {self.stats['total']}")
        print(f"✅ Successful: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"📈 Success rate: {(self.stats['successful'] / self.stats['total']) * 100:.1f}%")

        if self.stats["successful"] > 0:
            avg_time = sum(r["processing_time"] for r in results if r["success"]) / self.stats["successful"]
            print(f"⚡ Average processing time: {avg_time:.2f}s per PDF")

        # Show failed files
        failed_files = [r for r in results if not r["success"]]
        if failed_files:
            print(f"\n❌ Failed files:")
            for result in failed_files:
                print(f"   • {result['pdf_path'].name}: {result['error']}")

        # Show output locations
        successful_files = [r for r in results if r["success"]]
        if successful_files:
            print(f"\n📁 Output directories:")
            for result in successful_files:
                formats = ", ".join(result["formats_generated"])
                print(f"   • {result['output_dir'].name}: {formats}")


def main():
    """Demonstrate batch processing of PDFs."""
    print("🔧 Vexy PDF Werk - Batch Processing Example")
    print("=" * 50)

    # Setup paths
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = Path(__file__).parent.parent / "output" / "batch_example"

    # Find all PDF files in data directory
    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in: {data_dir}")
        print("Please add some PDF files to the data directory.")
        return

    print(f"📁 Data directory: {data_dir}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        size_mb = pdf_file.stat().st_size / (1024 * 1024)
        print(f"   • {pdf_file.name} ({size_mb:.1f}MB)")

    # Initialize batch processor
    batch_processor = BatchProcessor(output_dir)

    # Process all PDFs
    # Note: Using max_workers=1 for demo to avoid overwhelming system
    # In production, you might use max_workers=cpu_count() or similar
    results = batch_processor.process_batch(pdf_files, max_workers=1)

    # Print summary
    batch_processor.print_summary(results)

    print(f"\n🎉 Batch processing complete!")
    print(f"📁 Check results in: {output_dir}")


if __name__ == "__main__":
    main()