# Installation

## From PyPI

```bash
pip install vexy-pdf-werk
```

## In Development Mode

```bash
git clone https://github.com/vexyart/vexy-pdf-werk
cd vexy-pdf-werk
pip install -e .
```

## System Dependencies

Vexy PDF Werk relies on a few external tools for its core functionality.

### Required Dependencies

-   Python 3.10+
-   tesseract-ocr
-   qpdf
-   ghostscript

### Optional Dependencies

-   pandoc (for ePub generation)
-   marker-pdf (for advanced PDF conversion)
-   markitdown (for Microsoft's document converter)
-   docling (for IBM's document understanding)

### Installation Commands

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng qpdf ghostscript pandoc
```

**macOS:**

```bash
brew install tesseract tesseract-lang qpdf ghostscript pandoc
```

**Windows:**

```bash
choco install tesseract qpdf ghostscript pandoc
```
