# 3. Vexy PDF Werk (VPW) - Part 3: Implementation Details

This section provides detailed implementation guidance for all core components of the VPW processing pipeline.

### 49.1. Core Processing Pipeline Implementation

#### 49.1.1. PDF Processor Implementation

The PDF processor is the heart of VPW, handling OCR enhancement and PDF/A conversion.

##### Core PDF Processor (`src/vexy_pdf_werk/core/pdf_processor.py`)

```python
## 50. this_file: src/vexy_pdf_werk/core/pdf_processor.py

"""PDF processing and OCR enhancement."""

import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import pikepdf
from loguru import logger
from rich.progress import Progress, TaskID

from ..config import VPWConfig, ProcessingConfig
from ..utils.validation import validate_pdf_file
from ..integrations.ai_services import AIServiceFactory


@dataclass
class PDFInfo:
    """Information about a PDF file."""
    path: Path
    pages: int
    has_text: bool
    is_scanned: bool
    has_images: bool
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None


@dataclass
class ProcessingResult:
    """Result of PDF processing."""
    success: bool
    output_path: Optional[Path] = None
    pdf_info: Optional[PDFInfo] = None
    error: Optional[str] = None
    processing_time: float = 0.0


class PDFProcessor:
    """Handles PDF processing and OCR enhancement."""

    def __init__(self, config: VPWConfig):
        """Initialize the PDF processor."""
        self.config = config
        self.processing_config = config.processing
        self.ai_config = config.ai

        # Tool paths
        self.ocrmypdf_cmd = self._find_tool("ocrmypdf")
        self.qpdf_cmd = self._find_tool("qpdf")
        self.tesseract_cmd = config.tesseract_path or self._find_tool("tesseract")

    def _find_tool(self, tool_name: str) -> str:
        """Find external tool in PATH."""
        import shutil
        path = shutil.which(tool_name)
        if not path:
            raise RuntimeError(f"Required tool '{tool_name}' not found in PATH")
        return path

    async def analyze_pdf(self, pdf_path: Path) -> PDFInfo:
        """
        Analyze PDF structure and content.

        Args:
            pdf_path: Path to PDF file

        Returns:
            PDF information and characteristics
        """
        logger.debug(f"Analyzing PDF: {pdf_path}")

        # Validate file first
        validate_pdf_file(pdf_path)

        try:
            # Open PDF with pikepdf for analysis
            with pikepdf.open(pdf_path) as pdf:
                pages = len(pdf.pages)

                # Extract metadata
                metadata = pdf.docinfo
                title = str(metadata.get('/Title', '')) if metadata.get('/Title') else None
                author = str(metadata.get('/Author', '')) if metadata.get('/Author') else None
                creation_date = str(metadata.get('/CreationDate', '')) if metadata.get('/CreationDate') else None

                # Analyze text content and images
                has_text = False
                is_scanned = False
                has_images = False

                for i, page in enumerate(pdf.pages):
                    if i >= 3:  # Sample first 3 pages
                        break

                    # Check for text content
                    if '/Contents' in page:
                        # Simple heuristic: if page has text content
                        has_text = True

                    # Check for images
                    if '/XObject' in page.get('/Resources', {}):
                        xobjects = page['/Resources']['/XObject']
                        for obj in xobjects.values():
                            if obj.get('/Subtype') == '/Image':
                                has_images = True
                                # If large images but little text, likely scanned
                                if not has_text:
                                    is_scanned = True

                return PDFInfo(
                    path=pdf_path,
                    pages=pages,
                    has_text=has_text,
                    is_scanned=is_scanned,
                    has_images=has_images,
                    title=title,
                    author=author,
                    creation_date=creation_date
                )

        except Exception as e:
            logger.error(f"Failed to analyze PDF {pdf_path}: {e}")
            raise RuntimeError(f"PDF analysis failed: {e}")

    async def create_better_pdf(
        self,
        pdf_path: Path,
        output_path: Path,
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None
    ) -> ProcessingResult:
        """
        Create an enhanced PDF/A version with OCR.

        Args:
            pdf_path: Input PDF path
            output_path: Output PDF path
            progress: Optional progress tracker
            task_id: Optional progress task ID

        Returns:
            Processing result with success status and details
        """
        import time
        start_time = time.time()

        logger.info(f"Processing PDF: {pdf_path} -> {output_path}")

        try:
            # Analyze input PDF
            pdf_info = await self.analyze_pdf(pdf_path)

            if progress and task_id is not None:
                progress.update(task_id, description="Analyzing PDF...")

            # Create temporary directory for intermediate files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Step 1: OCR Enhancement if needed
                if pdf_info.is_scanned or self.processing_config.force_ocr:
                    if progress and task_id is not None:
                        progress.update(task_id, description="Performing OCR...")

                    ocr_output = temp_path / "ocr_enhanced.pdf"
                    await self._enhance_with_ocr(pdf_path, ocr_output, pdf_info)
                    intermediate_pdf = ocr_output
                else:
                    logger.info("PDF already has text, skipping OCR")
                    intermediate_pdf = pdf_path

                # Step 2: AI Enhancement (optional)
                if self.ai_config.enabled and self.ai_config.correction_enabled:
                    if progress and task_id is not None:
                        progress.update(task_id, description="AI text correction...")

                    ai_output = temp_path / "ai_enhanced.pdf"
                    await self._enhance_with_ai(intermediate_pdf, ai_output)
                    intermediate_pdf = ai_output

                # Step 3: PDF/A Conversion
                if progress and task_id is not None:
                    progress.update(task_id, description="Converting to PDF/A...")

                await self._convert_to_pdfa(intermediate_pdf, output_path, pdf_info)

                # Step 4: Validate output
                if progress and task_id is not None:
                    progress.update(task_id, description="Validating output...")

                if not output_path.exists():
                    raise RuntimeError("PDF processing completed but output file not found")

                processing_time = time.time() - start_time
                logger.success(f"PDF processing completed in {processing_time:.2f}s")

                return ProcessingResult(
                    success=True,
                    output_path=output_path,
                    pdf_info=pdf_info,
                    processing_time=processing_time
                )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"PDF processing failed after {processing_time:.2f}s: {e}")
            return ProcessingResult(
                success=False,
                error=str(e),
                processing_time=processing_time
            )

    async def _enhance_with_ocr(
        self,
        input_pdf: Path,
        output_pdf: Path,
        pdf_info: PDFInfo
    ) -> None:
        """Enhance PDF with OCR using OCRmyPDF."""
        logger.info("Enhancing PDF with OCR")

        cmd = [
            self.ocrmypdf_cmd,
            "--language", self.processing_config.ocr_language,
            "--output-type", "pdfa-2",  # Create PDF/A-2b
            "--optimize", "1" if self.processing_config.pdf_quality == "high" else "0",
        ]

        # Add processing options
        if self.processing_config.deskew:
            cmd.append("--deskew")

        if self.processing_config.rotate_pages:
            cmd.append("--rotate-pages")

        if not pdf_info.has_text or self.processing_config.force_ocr:
            # Force OCR on all pages
            cmd.append("--force-ocr")
        else:
            # Only OCR pages without text
            cmd.append("--skip-text")

        # Add metadata if available
        if pdf_info.title:
            cmd.extend(["--title", pdf_info.title])
        if pdf_info.author:
            cmd.extend(["--author", pdf_info.author])

        # Input and output files
        cmd.extend([str(input_pdf), str(output_pdf)])

        logger.debug(f"Running OCRmyPDF: {' '.join(cmd)}")

        # Run OCRmyPDF
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown OCRmyPDF error"
            logger.error(f"OCRmyPDF failed: {error_msg}")
            raise RuntimeError(f"OCR processing failed: {error_msg}")

        logger.success("OCR enhancement completed")

    async def _enhance_with_ai(self, input_pdf: Path, output_pdf: Path) -> None:
        """Enhance PDF text using AI correction."""
        logger.info("Enhancing PDF with AI text correction")

        # For now, just copy the file - AI enhancement will be implemented
        # in the AI services integration
        import shutil
        shutil.copy2(input_pdf, output_pdf)

        # TODO: Implement actual AI text correction
        # This would involve:
        # 1. Extracting text from PDF
        # 2. Sending to AI service for correction
        # 3. Overlaying corrected text back onto PDF
        logger.warning("AI enhancement not yet implemented, skipping")

    async def _convert_to_pdfa(
        self,
        input_pdf: Path,
        output_pdf: Path,
        pdf_info: PDFInfo
    ) -> None:
        """Convert PDF to PDF/A format using qpdf for final optimization."""
        logger.info("Converting to PDF/A format")

        cmd = [
            self.qpdf_cmd,
            "--linearize",  # Optimize for web viewing
            "--object-streams=generate",  # Compress object streams
            str(input_pdf),
            str(output_pdf)
        ]

        logger.debug(f"Running qpdf: {' '.join(cmd)}")

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown qpdf error"
            logger.error(f"qpdf failed: {error_msg}")
            raise RuntimeError(f"PDF/A conversion failed: {error_msg}")

        logger.success("PDF/A conversion completed")
```
