# Vexy PDF Werk

**Transform PDFs into high-quality, accessible formats with AI-enhanced processing**

Vexy PDF Werk (VPW) is a Python package that converts PDF documents into multiple high-quality formats using modern tools and optional AI enhancement. Transform your PDFs into PDF/A archives, paginated Markdown, ePub books, and structured bibliographic metadata.

- `SPEC.md` is the full specification

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

🤖 **Optional AI Enhancement (Future)**
- Text correction using Claude or Gemini CLI.
- Content structure optimization.
- Fallback to proven traditional methods.

⚙️ **Flexible Architecture**
- Multiple conversion backends (Marker, MarkItDown, Docling, basic).
- Platform-appropriate configuration storage (`~/.config/vexy-pdf-werk/config.toml`).
- Robust error handling with graceful fallbacks.
- Command-line interface for easy integration into workflows.

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

#### Process a PDF

```bash
# Process a PDF into all default formats (pdfa, markdown, epub, yaml)
vpw process document.pdf

# Specify output directory and formats
vpw process document.pdf --output_dir ./my-output --formats "markdown,epub"

# Enable verbose logging for debugging
vpw process document.pdf --verbose
```

#### Manage Configuration

```bash
# Display the current configuration
vpw config --show

# Create a default configuration file if one doesn't exist
vpw config --init
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

### Optional Dependencies
- pandoc (for ePub generation)
- marker-pdf (advanced PDF conversion)
- markitdown (Microsoft's document converter)
- docling (IBM's document understanding)

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
                   Optional AI Enhancement
```

### Core Components

- **`PDFProcessor`**: Handles OCR, PDF/A conversion, and analysis of the PDF file. It uses `ocrmypdf` and `qpdf` for robust processing.
- **`MarkdownGenerator`**: Converts the processed PDF into Markdown. It supports different backends (currently `basic` is implemented) and can create paginated or single-file output.
- **`EpubCreator`**: Generates an ePub file from the Markdown content, creating chapters for each page.
- **`MetadataExtractor`**: Extracts comprehensive metadata from the PDF and the processing results, saving it to a `metadata.yaml` file. This includes file info, PDF properties, and content summaries like word count.
- **`cli.py`**: Provides the command-line interface using `fire`, allowing for easy configuration and execution of the processing pipeline.
- **`config.py`**: Manages the application's configuration using `pydantic` and `toml`, with support for environment variable overrides.

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
- Integration with cutting-edge AI services
- Inspired by the need for better PDF accessibility and archival

---

**Project Status**: Under active development

For detailed implementation specifications, see the [spec/](spec/) directory.
