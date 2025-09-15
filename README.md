# Vexy PDF Werk

**Transform PDFs into high-quality, accessible formats**

Vexy PDF Werk (VPW) is a Python package that converts PDF documents into multiple high-quality formats using modern tools. Transform your PDFs into PDF/A archives, paginated Markdown, ePub books, and structured bibliographic metadata.

## Features

🔧 **Modern PDF Processing**
- PDF/A conversion for long-term archival
- OCR enhancement using OCRmyPDF
- Quality optimization with qpdf
- In-depth PDF analysis to detect text, images, and scanned documents.

📚 **Multiple Output Formats**
- Paginated Markdown documents with smart naming and YAML frontmatter.
- ePub generation from Markdown content.
- Structured bibliographic YAML metadata, including estimated word count and content preview.
- Preserves original PDF alongside enhanced versions.

🔄 **Advanced Conversion Options**
- **Marker**: High-quality PDF-to-Markdown using state-of-the-art ML models
- **MarkItDown**: Microsoft's robust document converter for complex layouts
- **Docling**: IBM's advanced document understanding with structure recognition
- **Basic**: Reliable PyPDF-based extraction for simple documents
- Automatic fallback system - if advanced converters aren't available, falls back to basic

⚙️ **Simple & Flexible**
- Clean, simple CLI interface with sensible defaults
- Platform-appropriate configuration storage
- Graceful error handling with helpful messages
- Easy integration into workflows

## Quick Start

### Installation

```bash
# Install from PyPI
pip install vexy-pdf-werk

# Or install in development mode
git clone https://github.com/vexyart/vexy-pdf-werk
cd vexy-pdf-werk
pip install -e .
```

### CLI Usage

The primary way to use Vexy PDF Werk is through its command-line interface, `vpw`.

#### Basic Usage

```bash
# Convert PDF to markdown (simplest usage)
vpw process document.pdf

# Convert to multiple formats
vpw process document.pdf --formats "pdfa,markdown,epub,yaml"

# Specify output directory
vpw process document.pdf --output_dir ./my-output

# Enable verbose logging for debugging
vpw process document.pdf --verbose
```

#### Advanced Converter Selection

By default, VPW automatically selects the best available converter. You can control this:

```bash
# Use automatic converter selection (default - tries Marker → Docling → MarkItDown → Basic)
vpw process document.pdf

# Force a specific converter in your config.toml:
# markdown_backend = "marker"    # High-quality ML-based conversion
# markdown_backend = "docling"   # IBM's document understanding
# markdown_backend = "markitdown" # Microsoft's robust converter
# markdown_backend = "basic"     # Simple PyPDF extraction
```

#### Configuration Management

```bash
# Display the current configuration
vpw config --show

# Create a default configuration file if one doesn't exist
vpw config --init
```

### Python API

You can also use VPW programmatically:

```python
import asyncio
from pathlib import Path
from vexy_pdf_werk.config import VPWConfig
from vexy_pdf_werk.core.markdown_converter import MarkdownGenerator

async def convert_pdf():
    # Simple conversion
    config = VPWConfig()
    converter = MarkdownGenerator(config.conversion)

    result = await converter.generate_markdown(
        Path("document.pdf"),
        Path("./output")
    )

    if result.success:
        print(f"✓ Converted {len(result.pages)} pages")
    else:
        print(f"✗ Error: {result.error}")

# Run conversion
asyncio.run(convert_pdf())
```

## Output Structure

VPW creates organized output with consistent naming:

```
output/
├── document_enhanced.pdf    # PDF/A version
├── 000--introduction.md     # Paginated Markdown files
├── 001--chapter-one.md
├── 002--conclusions.md
├── document.epub            # Generated ePub
└── metadata.yaml            # Bibliographic data
```

## System Requirements

### Required Dependencies
- Python 3.10+
- tesseract-ocr
- qpdf
- ghostscript

### Optional Dependencies for Advanced Converters

**Install all advanced converters:**
```bash
pip install vexy-pdf-werk[all]
```

**Or install specific converters:**
```bash
# High-quality ML-based conversion
pip install marker-pdf

# Microsoft's document converter
pip install markitdown

# IBM's document understanding
pip install docling

# ePub generation support
pip install ebooklib

# Pandoc for additional ePub features
# (install via system package manager as shown below)
```

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

## Configuration

VPW stores configuration in platform-appropriate directories:

- **Linux/macOS**: `~/.config/vexy-pdf-werk/config.toml`
- **Windows**: `%APPDATA%\vexy-pdf-werk\config.toml`

You can initialize a default configuration file by running `vpw config --init`.

### Example Configuration

```toml
[processing]
ocr_language = "eng"
pdf_quality = "high" # high, medium, low
force_ocr = false
deskew = true
rotate_pages = true

[conversion]
markdown_backend = "auto"  # auto, marker, markitdown, docling, basic
paginate_markdown = true
include_images = true
extract_tables = true

[ai]
enabled = false
provider = "claude"  # claude, gemini, custom
correction_enabled = false
enhancement_enabled = false
max_tokens = 4000

[output]
formats = ["pdfa", "markdown", "epub", "yaml"]
preserve_original = true
output_directory = "./output"
filename_template = "{stem}_{format}.{ext}"
```

## Architecture

VPW follows a modular pipeline architecture:

```
PDF Input → Analysis → OCR Enhancement → Content Extraction → Format Generation → Multi-Format Output
                                              ↓
                                   Multiple Converter Backends
                              (Marker/Docling/MarkItDown/Basic)
```

### Core Components

- **`PDFProcessor`**: Handles OCR, PDF/A conversion, and analysis of PDF files using `ocrmypdf` and `qpdf`.

- **`MarkdownGenerator`**: Intelligent PDF-to-Markdown conversion with multiple backends:
  - **`MarkerConverter`**: High-quality conversion using marker-pdf's ML models
  - **`DoclingConverter`**: Advanced document understanding using IBM's docling
  - **`MarkItDownConverter`**: Robust conversion using Microsoft's markitdown
  - **`BasicConverter`**: Reliable fallback using PyPDF extraction
  - Automatic backend selection and graceful fallbacks

- **`EpubCreator`**: Generates ePub files from Markdown content with proper chapter structure.

- **`MetadataExtractor`**: Extracts comprehensive metadata including file info, PDF properties, and content summaries.

- **`CLI`**: Clean command-line interface with simple defaults and helpful error messages.

- **`Config`**: Simple configuration management with sensible defaults.

## Development

This project uses modern Python tooling:

- **Package Management**: uv + hatch (use `uv run` to run but for other operations use `hatch` like `hatch test`)
- **Code Quality**: ruff + mypy
- **Testing**: pytest
- **Version Control**: git-tag-based semver with hatch-vcs

### Development Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/vexyart/vexy-pdf-werk
cd vexy-pdf-werk
uv venv --python 3.12
uv sync --all-extras

# Run tests
hatch run test

# Run linting
hatch run lint:fmt
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code quality standards
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Fontlab Ltd** - *Initial work* - [Vexy Art](https://vexy.art)

## Acknowledgments

- Built on proven tools: qpdf, OCRmyPDF, tesseract
- Integration with advanced document conversion libraries (Marker, Docling, MarkItDown)
- Inspired by the need for better PDF accessibility and archival

---

**Project Status**: Under active development
