# this_file: examples/README.md
---

# Vexy PDF Werk Examples

This directory contains comprehensive examples demonstrating how to use Vexy PDF Werk both as a Python library and through the command-line interface.

## Directory Structure

```
examples/
├── README.md              # This file
├── data/                  # Sample PDF files for testing
│   ├── base64image.pdf    # PDF with embedded base64 images
│   ├── multicolumn.pdf    # Multi-column layout PDF
│   ├── pdflatex-image.pdf # LaTeX-generated PDF with images
│   └── test1.pdf          # General test document
├── output/                # Generated output files
├── python_examples/       # Python API usage examples
│   ├── basic_usage.py     # Simple PDF processing
│   ├── batch_processing.py # Process multiple PDFs
│   ├── custom_config.py   # Custom configuration example
│   └── ai_enhancement.py  # AI-powered enhancement example
└── shell_examples/        # Shell script examples
    ├── basic_conversion.sh # Basic CLI usage
    ├── batch_convert.sh   # Batch processing script
    └── format_selection.sh # Selective format generation
```

## Sample Data

The `data/` directory contains several test PDF files:

- **base64image.pdf** (2.3MB) - Contains embedded base64-encoded images, good for testing image extraction
- **multicolumn.pdf** (77KB) - Multi-column academic layout, tests text flow analysis
- **pdflatex-image.pdf** (74KB) - LaTeX-generated with mathematical content and images
- **test1.pdf** (1.4MB) - General test document with mixed content

## Quick Start

### Python API

```python
from vexy_pdf_werk import PDFProcessor, Config

# Basic usage
processor = PDFProcessor()
result = processor.process_pdf("data/test1.pdf", output_dir="output/")

# Custom configuration
config = Config(
    ocr_language="eng",
    formats=["markdown", "epub", "yaml"],
    ai_enhancement_enabled=True
)
result = processor.process_pdf("data/multicolumn.pdf", config=config)
```

### Command Line

```bash
# Basic conversion
vpw process data/test1.pdf --output output/

# Multi-format with AI enhancement
vpw process data/multicolumn.pdf --formats "markdown,epub,yaml" --ai-enabled

# Batch processing
vpw batch-process data/ --output output/ --formats "markdown,epub"
```

## Running Examples

### Python Examples

```bash
# Navigate to examples directory
cd examples/

# Run basic usage example
python python_examples/basic_usage.py

# Run batch processing example
python python_examples/batch_processing.py

# Run AI enhancement example (requires Claude/Gemini API key)
export ANTHROPIC_API_KEY="your-key-here"
python python_examples/ai_enhancement.py
```

### Shell Examples

```bash
# Make scripts executable
chmod +x shell_examples/*.sh

# Run basic conversion
./shell_examples/basic_conversion.sh

# Run batch processing
./shell_examples/batch_convert.sh

# Run format selection example
./shell_examples/format_selection.sh
```

## Expected Output

Each example will generate output in the `output/` directory:

```
output/
├── test1/
│   ├── 000--introduction.md
│   ├── 001--chapter-1.md
│   ├── test1.epub
│   └── metadata.yaml
├── multicolumn/
│   ├── 000--abstract.md
│   ├── 001--methodology.md
│   ├── multicolumn.epub
│   └── metadata.yaml
└── processing_logs/
    └── 2025-01-15_processing.log
```

## Configuration Examples

See `python_examples/custom_config.py` for detailed configuration options:

- OCR settings and language selection
- Output format customization
- AI enhancement configuration
- Quality and performance tuning
- Error handling strategies

## Prerequisites

Ensure you have the required system dependencies:

```bash
# macOS
brew install tesseract tesseract-lang qpdf ghostscript pandoc

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng qpdf ghostscript pandoc

# Windows (using Chocolatey)
choco install tesseract qpdf ghostscript pandoc
```

## Troubleshooting

- **Permission errors**: Ensure write permissions for the output directory
- **Missing dependencies**: Install system dependencies listed above
- **AI API errors**: Verify API keys are properly set in environment variables
- **Large file processing**: Increase timeout settings in configuration for large PDFs

## Contributing

To add new examples:

1. Place sample PDFs in `data/` directory
2. Create Python examples in `python_examples/`
3. Create shell scripts in `shell_examples/`
4. Update this README with new example descriptions
5. Test examples with the provided sample data

## Support

For issues with examples or the Vexy PDF Werk package:

- Check the main project README for system requirements
- Review configuration options in the documentation
- File issues at: https://github.com/vexyart/vexy-pdf-werk/issues