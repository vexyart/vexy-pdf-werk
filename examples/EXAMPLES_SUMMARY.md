# this_file: examples/EXAMPLES_SUMMARY.md
---

# Vexy PDF Werk Examples - Summary

This document provides a comprehensive overview of all examples created for the Vexy PDF Werk package.

## 🎯 What's Included

### 📁 Directory Structure
```
examples/
├── README.md                    # Main documentation
├── EXAMPLES_SUMMARY.md         # This summary file
├── run_examples.py             # Interactive example runner
├── data/                       # Sample PDF files (4 files, ~4MB total)
├── output/                     # Generated output files
├── python_examples/            # Python API demonstrations
│   ├── basic_usage.py          # Simple PDF processing workflow
│   ├── batch_processing.py     # Multi-file processing with progress tracking
│   ├── custom_config.py        # Configuration options and customization
│   └── ai_enhancement.py       # AI-powered text correction and structure enhancement
└── shell_examples/             # CLI script demonstrations
    ├── basic_conversion.sh     # Basic command-line usage
    ├── batch_convert.sh        # Batch processing with logging
    └── format_selection.sh     # Output format options and customization
```

### 📊 Example Categories

#### 🐍 Python API Examples (4 scripts)
1. **basic_usage.py** - Demonstrates the fundamental workflow
   - PDF analysis and validation
   - Markdown conversion with page segmentation
   - ePub generation with metadata
   - YAML metadata extraction
   - Error handling and progress reporting

2. **batch_processing.py** - Shows efficient multi-file processing
   - Parallel processing with ThreadPoolExecutor
   - Progress tracking and statistics
   - Error recovery and logging
   - Performance optimization strategies

3. **custom_config.py** - Explores configuration options
   - Quality vs performance trade-offs
   - Format-specific settings
   - Error handling configurations
   - Use case recommendations

4. **ai_enhancement.py** - Demonstrates AI-powered features
   - Text correction for OCR errors
   - Document structure enhancement
   - AI service integration (Claude/Gemini)
   - Prerequisites and configuration

#### 🐚 Shell Script Examples (3 scripts)
1. **basic_conversion.sh** - CLI fundamentals
   - Simple PDF processing commands
   - Format selection options
   - Verbose output demonstration
   - Help and usage information

2. **batch_convert.sh** - Automated batch processing
   - Sequential file processing
   - Progress bars and logging
   - Error handling and recovery
   - Performance statistics

3. **format_selection.sh** - Output format customization
   - Individual format generation
   - Format combination strategies
   - Quality settings comparison
   - Use case recommendations

### 📄 Sample Data (4 PDF files)
- **base64image.pdf** (2.2MB) - Tests image extraction and base64 handling
- **multicolumn.pdf** (77KB) - Academic layout with complex text flow
- **pdflatex-image.pdf** (74KB) - LaTeX-generated with mathematical content
- **test1.pdf** (1.3MB) - General-purpose test document

## 🚀 Quick Start

### Option 1: Interactive Runner
```bash
# List all available examples
python examples/run_examples.py list

# Check prerequisites
python examples/run_examples.py check

# Run all Python examples
python examples/run_examples.py python

# Run shell examples in demo mode
python examples/run_examples.py shell

# Run everything
python examples/run_examples.py all
```

### Option 2: Direct Execution

**Python Examples:**
```bash
cd examples/
python python_examples/basic_usage.py
python python_examples/batch_processing.py
python python_examples/custom_config.py
python python_examples/ai_enhancement.py
```

**Shell Examples:**
```bash
cd examples/
./shell_examples/basic_conversion.sh --demo
./shell_examples/batch_convert.sh --demo
./shell_examples/format_selection.sh --demo
```

### Option 3: Real Processing
```bash
# Remove --demo flag for actual PDF processing
./shell_examples/basic_conversion.sh
./shell_examples/batch_convert.sh
./shell_examples/format_selection.sh
```

## 📈 Example Features

### 🔧 Technical Demonstrations
- **PDF Analysis**: Document structure, text detection, metadata extraction
- **Format Generation**: Markdown (paginated), ePub, YAML metadata
- **Error Handling**: Graceful failures, retry logic, fallback strategies
- **Performance**: Parallel processing, progress tracking, optimization
- **Configuration**: Quality settings, format options, AI integration

### 💡 Educational Content
- **Best Practices**: Code organization, error handling, resource management
- **Use Cases**: Documentation, e-books, automation, analysis
- **Trade-offs**: Quality vs speed, features vs simplicity
- **Troubleshooting**: Common issues and solutions
- **Integration**: API usage patterns, CLI workflows

### 🎯 Real-World Scenarios
- **Single Document**: Quick conversion for immediate use
- **Batch Processing**: Large-scale document conversion
- **Automation**: Scripted processing pipelines
- **Quality Control**: Metadata analysis and validation
- **AI Enhancement**: OCR correction and structure improvement

## 📊 Output Examples

### Markdown Output
```markdown
---
title: Introduction
page: 1
slug: introduction
---

# Introduction

This is the introduction to our document...
```

### ePub Features
- Table of contents generation
- Chapter structure preservation
- Metadata embedding
- Cross-platform compatibility

### YAML Metadata
```yaml
document:
  source_file: test1.pdf
  source_size_bytes: 1377202
  processed_at: "2025-01-15T10:30:00+00:00"
pdf_info:
  pages: 5
  has_text: true
  title: "Sample Document"
content:
  estimated_word_count: 1250
  first_page_preview: "This document covers..."
```

## 🔧 Prerequisites

### Required System Dependencies
```bash
# macOS
brew install tesseract tesseract-lang qpdf ghostscript pandoc

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng qpdf ghostscript pandoc

# Windows
choco install tesseract qpdf ghostscript pandoc
```

### Python Requirements
- Python 3.10+
- Vexy PDF Werk package
- Dependencies handled by package installation

### Optional AI Features
- Claude API key (ANTHROPIC_API_KEY)
- Gemini API key (GOOGLE_API_KEY)
- claude-cli or gemini-cli tools

## 🎓 Learning Path

### Beginner (Start Here)
1. Run `python examples/run_examples.py check`
2. Try `./shell_examples/basic_conversion.sh --demo`
3. Run `python python_examples/basic_usage.py`
4. Read the generated output files

### Intermediate
1. Experiment with `custom_config.py`
2. Try real processing with sample PDFs
3. Explore batch processing scripts
4. Customize format selection options

### Advanced
1. Set up AI enhancement features
2. Modify examples for your use case
3. Integrate into existing workflows
4. Develop custom processing pipelines

## 🚨 Troubleshooting

### Common Issues
- **Import errors**: Ensure Vexy PDF Werk is installed
- **Permission errors**: Check write access to output directories
- **Missing tools**: Install system dependencies listed above
- **Large files**: Increase timeouts or use quality=fast

### Demo Mode
All shell scripts support `--demo` flag for safe testing without actual file processing.

### Error Logs
Check `examples/output/*/logs/` for detailed error information during real processing.

## 🎯 Next Steps

### For Developers
- Modify examples for your specific needs
- Integrate examples into CI/CD pipelines
- Extend examples with custom converters
- Add new sample data for testing

### For Users
- Process your own PDF files
- Customize output formats
- Set up batch processing workflows
- Explore AI enhancement features

### For Contributors
- Add new example scenarios
- Improve error handling
- Enhance documentation
- Create tutorial videos

## 📞 Support

- **Documentation**: See `examples/README.md` for detailed information
- **Issues**: Report problems at project GitHub repository
- **Examples**: All examples include inline documentation
- **Community**: Share your use cases and improvements

---

**Created**: 2025-01-15
**Examples Version**: 1.0
**Compatible With**: Vexy PDF Werk v1.1.3+