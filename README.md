# this_file: README.md

# Vexy PDF Werk

**Transform PDFs into high-quality, accessible formats with AI-enhanced processing**

Vexy PDF Werk (VPW) is a Python package that converts PDF documents into multiple high-quality formats using modern tools and optional AI enhancement. Transform your PDFs into PDF/A archives, paginated Markdown, ePub books, and structured bibliographic metadata.

## Features

🔧 **Modern PDF Processing**
- PDF/A conversion for long-term archival
- OCR enhancement using OCRmyPDF
- Quality optimization with qpdf

📚 **Multiple Output Formats**
- Paginated Markdown documents with smart naming
- ePub generation from Markdown
- Structured bibliographic YAML metadata
- Preserves original PDF alongside enhanced versions

🤖 **Optional AI Enhancement**
- Text correction using Claude or Gemini CLI
- Content structure optimization
- Fallback to proven traditional methods

⚙️ **Flexible Architecture**
- Multiple conversion backends (Marker, MarkItDown, Docling, basic)
- Platform-appropriate configuration storage
- Robust error handling with graceful fallbacks

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

### Basic Usage

```python
import vexy_pdf_werk

# Process a PDF with default settings
config = vexy_pdf_werk.Config(name="default", value="process")
result = vexy_pdf_werk.process_data(["document.pdf"], config=config)
```

### CLI Usage (Coming Soon)

```bash
# Process a PDF into all formats
vpw process document.pdf

# Process with specific formats only
vpw process document.pdf --formats pdfa,markdown

# Enable AI enhancement
vpw process document.pdf --ai-enabled --ai-provider claude
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
- **Windows**: `%APPDATA%\\vexy-pdf-werk\\config.toml`

### Example Configuration

```toml
[processing]
ocr_language = "eng"
pdf_quality = "high"
force_ocr = false

[conversion]
markdown_backend = "auto"  # auto, marker, markitdown, docling, basic
paginate_markdown = true
include_images = true

[ai]
enabled = false
provider = "claude"  # claude, gemini
correction_enabled = false

[output]
formats = ["pdfa", "markdown", "epub", "yaml"]
preserve_original = true
output_directory = "./output"
```

## Development

This project uses modern Python tooling:

- **Package Management**: uv + hatch
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
PYTHONPATH=src python -m pytest tests/

# Run linting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src/vexy_pdf_werk/
```

## Architecture

VPW follows a modular pipeline architecture:

```
PDF Input → Analysis → OCR Enhancement → Content Extraction → Format Generation → Multi-Format Output
                          ↓
                   Optional AI Enhancement
```

### Core Components

- **PDF Processor**: Handles OCR and PDF/A conversion
- **Content Extractors**: Multiple backends for PDF-to-Markdown
- **Format Generators**: Creates ePub and metadata outputs
- **AI Integrations**: Optional LLM enhancement services
- **Configuration System**: Platform-aware settings management

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