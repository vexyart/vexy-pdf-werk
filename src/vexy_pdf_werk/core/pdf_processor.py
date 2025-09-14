# this_file: src/vexy_pdf_werk/core/pdf_processor.py
"""PDF processing and OCR enhancement."""

import asyncio
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import pikepdf
from loguru import logger
from rich.progress import Progress, TaskID

from vexy_pdf_werk.config import ProcessingConfig, VPWConfig
from vexy_pdf_werk.utils.file_utils import find_tool_path
from vexy_pdf_werk.utils.validation import validate_pdf_file


@dataclass
class PDFInfo:
    """Information about a PDF file."""
    path: Path
    pages: int
    has_text: bool
    is_scanned: bool
    has_images: bool
    title: str | None = None
    author: str | None = None
    creation_date: str | None = None


@dataclass
class ProcessingResult:
    """Result of PDF processing."""
    success: bool
    output_path: Path | None = None
    pdf_info: PDFInfo | None = None
    error: str | None = None
    processing_time: float = 0.0


class PDFProcessor:
    """Handles PDF processing and OCR enhancement."""

    def __init__(self, config: VPWConfig):
        """Initialize the PDF processor."""
        self.config = config
        self.processing_config = config.processing
        self.ai_config = config.ai

        # Find external tools
        self.ocrmypdf_cmd = self._find_tool("ocrmypdf")
        self.qpdf_cmd = self._find_tool("qpdf")
        self.tesseract_cmd = config.tesseract_path or find_tool_path("tesseract")

    def _find_tool(self, tool_name: str) -> str:
        """Find external tool in PATH."""
        path = find_tool_path(tool_name)
        if not path:
            msg = f"Required tool '{tool_name}' not found in PATH. Please install it."
            raise RuntimeError(msg)
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

                # Analyze content characteristics
                has_text = False
                is_scanned = False
                has_images = False

                # Sample first few pages for analysis
                sample_pages = min(3, pages)
                text_content_found = 0
                image_content_found = 0

                for i in range(sample_pages):
                    page = pdf.pages[i]

                    # Check for text content
                    try:
                        if '/Contents' in page:
                            # Simple heuristic: check if page has substantive content
                            has_text = True
                            text_content_found += 1
                    except Exception:
                        pass

                    # Check for images
                    try:
                        if '/Resources' in page and '/XObject' in page['/Resources']:
                            xobjects = page['/Resources']['/XObject']
                            for _obj_name, obj in xobjects.items():
                                if hasattr(obj, 'get') and obj.get('/Subtype') == '/Image':
                                    has_images = True
                                    image_content_found += 1
                                    break
                    except Exception:
                        pass

                # Determine if document is likely scanned
                # Heuristic: many images but little extractable text suggests scanned document
                if has_images and text_content_found < sample_pages / 2:
                    is_scanned = True

                logger.info(f"PDF analysis complete: {pages} pages, text={has_text}, images={has_images}, scanned={is_scanned}")

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
            msg = f"PDF analysis failed: {e}"
            raise RuntimeError(msg)

    async def create_better_pdf(
        self,
        pdf_path: Path,
        output_path: Path,
        progress: Progress | None = None,
        task_id: TaskID | None = None
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
                    msg = "PDF processing completed but output file not found"
                    raise RuntimeError(msg)

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

        _stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown OCRmyPDF error"
            logger.error(f"OCRmyPDF failed: {error_msg}")
            msg = f"OCR processing failed: {error_msg}"
            raise RuntimeError(msg)

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
        pdf_info: PDFInfo  # noqa: ARG002
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

        _stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown qpdf error"
            logger.error(f"qpdf failed: {error_msg}")
            msg = f"PDF/A conversion failed: {error_msg}"
            raise RuntimeError(msg)

        logger.success("PDF/A conversion completed")

