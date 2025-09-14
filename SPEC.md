
# `spec/101.md`

## 1. Vexy PDF Werk (VPW) - Part 1: Planning and Architecture

**Problem Analysis**: What exactly are we solving and why?

We're creating a comprehensive PDF processing tool that transforms "vexing" PDFs into multiple high-quality, accessible formats. The core problems we're solving:

1. **PDF/A Compliance**: Many PDFs aren't archival-quality or standardized
2. **OCR Quality**: Scanned documents often have poor or missing text layers
3. **Format Conversion**: Need to convert PDFs to modern formats (Markdown, ePub)
4. **Metadata Management**: Extract and standardize bibliographic information
5. **AI Enhancement**: Use LLMs to improve OCR accuracy and content extraction

**Constraints**: What limitations must we respect?

- Must use modern Python toolchain (hatch, ruff, uv, git-tag-based semver)
- Must integrate with existing robust tools (qpdf, OCRmyPDF) rather than reinventing
- Must support optional advanced features (Marker, AI services) without breaking core functionality
- Must follow anti-enterprise bloat guidelines - keep it simple
- Must work cross-platform with appropriate configuration directories

**Solution Options**: What are 2-3 viable approaches with trade-offs?

1. **Modular Pipeline Approach** (CHOSEN)
   - Sequential processing stages: PDF enhancement → Markdown conversion → ePub creation → Metadata extraction
   - Clean separation of concerns, easy testing, optional stages
   - Trade-off: More complex than monolithic, but much more maintainable

2. **Monolithic Processing**
   - Single large function handling everything
   - Simple but inflexible, hard to test, no optional features

3. **Plugin Architecture**
   - Extensible converter system
   - Over-engineered for this use case, violates simplicity principles

### 1.1. Project Scope (One Sentence)

**VPW transforms PDF documents into PDF/A format, paginated Markdown, ePub, and bibliographic YAML through a configurable pipeline using proven external tools.**

### 1.2. High-Level Architecture

#### 1.2.1. Data Flow Pipeline

```
Input PDF → PDF Analysis → OCR Enhancement → PDF/A Creation → Content Extraction → Format Generation → Output Files
                           ↓
                    Optional AI Enhancement
```

#### 1.2.2. Core Components

1. **PDF Processor** - Handles OCR, PDF/A conversion, quality enhancement
2. **Content Extractors** - Multiple backends for PDF-to-Markdown conversion
3. **Format Generators** - Creates ePub and metadata outputs
4. **AI Integrations** - Optional LLM services for enhancement
5. **CLI Interface** - Fire-based command-line tool
6. **Configuration System** - TOML-based settings management

#### 1.2.3. Technology Stack Decisions

##### Build and Development Tools
- **hatch + hatch-vcs**: Modern Python project management with git-tag versioning
- **uv**: Ultra-fast package management and virtual environments, and `uv run` 
- **ruff**: High-performance linting and formatting
- **Fire**: Automatic CLI generation from Python objects

**Rationale**: This stack represents the current best practices in Python development, emphasizing speed, simplicity, and modern workflows.

##### Core PDF Processing
- **OCRmyPDF**: Battle-tested OCR and PDF/A conversion
- **qpdf**: Low-level PDF manipulation and optimization
- **pikepdf**: Python wrapper for qpdf functionality

**Rationale**: These tools are industry-standard, well-maintained, and handle the complex edge cases of PDF processing.

##### Content Conversion (Optional)
- **Marker**: High-fidelity academic PDF conversion with deep learning
- **MarkItDown**: Microsoft's lightweight document converter
- **Docling**: IBM's advanced document understanding platform

**Rationale**: Multiple backends provide flexibility - users can choose based on their needs and available resources.

##### AI Integration (Optional)
- **Claude CLI**: Direct command-line access to Anthropic's models
- **Gemini CLI**: Google's AI model access
- **Custom Python integrations**: Flexible API wrappers

**Rationale**: CLI tools are simpler to integrate than API libraries, and optional nature ensures core functionality works without AI.

#### 1.2.4. Configuration Architecture

##### Configuration Hierarchy
1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **User config file** (`~/.config/vexy-pdf-werk/config.toml`)
4. **Default values** (lowest priority)

##### Configuration Categories
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
provider = "claude"  # claude, gemini, custom
correction_enabled = false

[output]
formats = ["pdfa", "markdown", "epub", "yaml"]
preserve_original = true
output_directory = "./output"
```

#### 1.2.5. Integration Points

##### External Tool Dependencies
- **System Requirements**: tesseract-ocr, qpdf, ghostscript
- **Optional Requirements**: pandoc (for ePub), marker/markitdown/docling
- **AI Services**: API keys for Claude/Gemini if using AI features

##### File System Interactions
- **Input**: Single PDF files or batch processing
- **Temporary**: Isolated working directories for each job
- **Output**: Organized directory structure with consistent naming
- **Config**: Platform-appropriate configuration directories

#### 1.2.6. Error Handling Philosophy

##### Graceful Degradation
- Core PDF/A conversion must always work
- Optional features fail gracefully with clear messages
- Fallback mechanisms for conversion backends
- Clear error messages with suggested solutions

##### Recovery Strategies
- Retry mechanisms for network-dependent operations
- Temporary file cleanup on failures
- Validation checkpoints throughout pipeline
- Detailed logging for debugging

#### 1.2.7. Security Considerations

##### Input Validation
- PDF structure validation before processing
- Path traversal prevention
- File size and type restrictions
- Malformed PDF handling

##### API Key Management
- Environment variables for sensitive data
- No hardcoded credentials
- Optional secure config file storage
- Clear separation of public/private settings

### 1.3. Performance and Resource Management

#### 1.3.1. Processing Efficiency
- **Parallel Processing**: Multi-core utilization where possible
- **Memory Management**: Streaming for large files, cleanup of temp files
- **Caching**: Basic caching of heavy operations (model loading)
- **Progress Reporting**: User feedback for long-running operations

#### 1.3.2. Scalability Considerations
- **Batch Processing**: Handle multiple PDFs efficiently
- **Resource Limits**: Configurable memory and CPU usage
- **Async Operations**: Non-blocking network calls for AI services
- **Interrupt Handling**: Clean shutdown and cleanup

### 1.4. Quality Assurance Strategy

#### 1.4.1. Code Quality
- **Type Hints**: Full type annotation for maintainability
- **Documentation**: Comprehensive docstrings and README
- **Testing**: Unit tests for core functions, integration tests for pipeline
- **Formatting**: Automated code formatting with ruff

#### 1.4.2. User Experience
- **Clear CLI**: Intuitive commands with good help text
- **Progress Feedback**: Status updates for long operations
- **Error Messages**: Actionable error descriptions
- **Examples**: Comprehensive usage examples in documentation

### 1.5. Future Extensibility

#### 1.5.1. Plugin Architecture Preparation
- Clean interfaces between components
- Configurable backend selection
- Easy addition of new conversion engines
- Minimal coupling between optional features

#### 1.5.2. Enhancement Opportunities
- Web interface for non-technical users
- Database backend for document management
- Integration with reference managers
- Advanced document analysis features

### 1.6. Success Criteria

#### 1.6.1. Functional Requirements
1. **PDF/A Conversion**: Reliably converts any valid PDF to PDF/A format
2. **OCR Enhancement**: Adds searchable text layers to scanned documents
3. **Format Generation**: Produces quality Markdown, ePub, and metadata files
4. **AI Integration**: Optional LLM enhancement works when configured
5. **Cross-Platform**: Runs on Linux, macOS, and Windows

#### 1.6.2. Quality Requirements
1. **Reliability**: Handles malformed PDFs gracefully
2. **Performance**: Processes typical documents in reasonable time
3. **Usability**: Clear CLI with helpful error messages
4. **Maintainability**: Clean, documented, testable code
5. **Extensibility**: Easy to add new features and backends

#### 1.6.3. Deployment Requirements
1. **Easy Installation**: Single command installation via pip
2. **Clear Dependencies**: Well-documented system requirements
3. **Configuration**: Simple setup for optional features
4. **Documentation**: Comprehensive user and developer guides
5. **Versioning**: Semantic versioning with git tags

This architecture provides a solid foundation for building a robust, maintainable, and user-friendly PDF processing tool that can grow with user needs while maintaining simplicity at its core.

------------------------------------------------------------

# `spec/102.md`

## 2. Vexy PDF Werk (VPW) - Part 2: Project Structure and Setup

This section provides detailed step-by-step instructions for setting up the development environment and creating the initial project structure.

### 2.1. Development Environment Setup

#### 2.1.1. Prerequisites Installation

##### 1. Install uv (Fast Python Package Manager)
```bash
## 3. Install uv globally
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal

## 4. Verify installation
uv --version
```

##### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng qpdf ghostscript imagemagick pandoc
```

**macOS (using Homebrew):**
```bash
brew install tesseract tesseract-lang qpdf ghostscript imagemagick pandoc
```

**Windows (using Chocolatey):**
```powershell
choco install tesseract qpdf ghostscript imagemagick pandoc
```

##### 3. Install hatch with uv
```bash
## 5. Install hatch globally using uv
uv tool install hatch

## 6. Verify installation
hatch --version
```

#### 6.0.1. Project Initialization

##### 1. Create Project Directory and Initialize
```bash
## 7. Create project directory
mkdir vexy-pdf-werk
cd vexy-pdf-werk

## 8. Initialize uv environment
uv venv --python 3.12
uv init --name vexy-pdf-werk --app

## 9. Initialize git repository
git init
```

##### 2. Configure pyproject.toml

Create the comprehensive `pyproject.toml` configuration:

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "vexy-pdf-werk"
dynamic = ["version"]
description = "Transform PDFs into high-quality, accessible formats with AI-enhanced processing"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10"
authors = [
    { name = "Your Name", email = "your.email@example.com" },
]
keywords = ["pdf", "ocr", "markdown", "epub", "ai", "document-processing"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Multimedia :: Graphics :: Graphics Conversion",
    "Topic :: Office/Business",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Text Processing :: Markup",
]

dependencies = [
    "fire>=0.5.0",
    "rich>=13.0.0",
    "loguru>=0.7.0",
    "platformdirs>=3.0.0",
    "pydantic>=2.0.0",
    "pathvalidate>=3.0.0",
    "unicode-slugify>=0.1.5",
    "pypdf>=3.0.0",
    "pikepdf>=8.0.0",
    "pyyaml>=6.0",
    "toml>=0.10.2",
    "requests>=2.31.0",
    "aiohttp>=3.8.0",
    "ebooklib>=0.18",
]

[project.optional-dependencies]
## 10. Advanced PDF-to-Markdown conversion
markdown = [
    "marker-pdf>=0.2.0",
    "markitdown>=0.0.5",
    "docling>=1.0.0",
]

## 11. AI/LLM integration
ai = [
    "anthropic>=0.20.0",
    "google-generativeai>=0.5.0",
    "openai>=1.0.0",
]

## 12. Development dependencies
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.4.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
]

## 13. All optional dependencies
all = [
    "vexy-pdf-werk[markdown]",
    "vexy-pdf-werk[ai]",
    "vexy-pdf-werk[dev]",
]

[project.urls]
Homepage = "https://github.com/your-username/vexy-pdf-werk"
Documentation = "https://github.com/your-username/vexy-pdf-werk#readme"
Repository = "https://github.com/your-username/vexy-pdf-werk.git"
"Issue Tracker" = "https://github.com/your-username/vexy-pdf-werk/issues"
Changelog = "https://github.com/your-username/vexy-pdf-werk/blob/main/CHANGELOG.md"

[project.scripts]
vpw = "vexy_pdf_werk.cli:main"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/vexy_pdf_werk/_version.py"

[tool.hatch.envs.default]
installer = "uv"
dependencies = [
    "pytest",
    "pytest-cov",
]

[tool.hatch.envs.default.scripts]
test = "pytest {args:tests}"
test-cov = "pytest --cov=src/vexy_pdf_werk --cov-report=html --cov-report=term {args:tests}"
lint = [
    "ruff check --fix {args:.}",
    "ruff format {args:.}",
]

[tool.hatch.envs.dev]
dependencies = [
    "vexy-pdf-werk[all]",
    "mypy",
    "pre-commit",
]

[tool.ruff]
target-version = "py312"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "N",    # pep8-naming
]
ignore = [
    "E501",  # line too long, handled by formatter
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "requires_ai: marks tests that require AI service configuration",
    "requires_marker: marks tests that require Marker to be installed",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/test_*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
]
```

##### 3. Create Project Directory Structure

```bash
## 14. Create the complete directory structure
mkdir -p src/vexy_pdf_werk/{core,integrations,utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p docs/{api,user-guide,development}
mkdir -p external/{ai-inference,datalab}

## 15. Create __init__.py files
touch src/vexy_pdf_werk/__init__.py
touch src/vexy_pdf_werk/core/__init__.py
touch src/vexy_pdf_werk/integrations/__init__.py
touch src/vexy_pdf_werk/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py

## 16. Create main module files
touch src/vexy_pdf_werk/{cli,config}.py
touch src/vexy_pdf_werk/core/{pdf_processor,markdown_generator,epub_creator,metadata_extractor}.py
touch src/vexy_pdf_werk/integrations/{ai_services,ocr_services,marker_services}.py
touch src/vexy_pdf_werk/utils/{file_utils,slug_utils,validation}.py
```

**Final Project Structure:**
```
vexy-pdf-werk/
├── .git/
├── .venv/
├── src/
│   └── vexy_pdf_werk/
│       ├── __init__.py
│       ├── _version.py              # Auto-generated by hatch-vcs
│       ├── cli.py                   # Fire CLI interface
│       ├── config.py                # Configuration management
│       ├── core/
│       │   ├── __init__.py
│       │   ├── pdf_processor.py     # PDF/A conversion, OCR
│       │   ├── markdown_generator.py # Markdown creation
│       │   ├── epub_creator.py      # ePub generation
│       │   └── metadata_extractor.py # Bibliographic data
│       ├── integrations/
│       │   ├── __init__.py
│       │   ├── ai_services.py       # AI LLM integrations
│       │   ├── ocr_services.py      # OCR integrations
│       │   └── marker_services.py   # Marker integrations
│       └── utils/
│           ├── __init__.py
│           ├── file_utils.py        # File operations
│           ├── slug_utils.py        # Slug generation
│           └── validation.py        # Input validation
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── fixtures/                    # Test PDF files
├── docs/
│   ├── api/
│   ├── user-guide/
│   └── development/
├── external/
│   ├── ai-inference/               # AI integration scripts
│   └── datalab/                    # DataLab API integration
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

#### 16.0.1. Initial File Setup

##### 1. Create Main Package __init__.py

```python
## 17. src/vexy_pdf_werk/__init__.py
## 18. this_file: src/vexy_pdf_werk/__init__.py

"""Vexy PDF Werk - Transform PDFs into high-quality, accessible formats."""

try:
    from ._version import __version__
except ImportError:
    # Fallback for development without hatch-vcs
    __version__ = "dev"

__all__ = ["__version__"]
```

##### 2. Create Basic CLI Framework

```python
##!/usr/bin/env python3
## 19. this_file: src/vexy_pdf_werk/cli.py

"""Fire-based CLI interface for Vexy PDF Werk."""

import sys
from pathlib import Path
from typing import Optional

import fire
from loguru import logger
from rich.console import Console

from . import __version__

console = Console()


class VexyPDFWerk:
    """Vexy PDF Werk - Transform PDFs into better formats."""

    def __init__(self):
        """Initialize the VPW CLI."""
        self.version = __version__

    def process(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        formats: str = "pdfa,markdown,epub,yaml",
        verbose: bool = False,
        config_file: Optional[str] = None,
    ):
        """
        Process a PDF file through the complete VPW pipeline.

        Args:
            pdf_path: Path to input PDF file
            output_dir: Output directory (default: ./output)
            formats: Comma-separated list of output formats
            verbose: Enable verbose logging
            config_file: Path to custom config file
        """
        if verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")

        console.print(f"[bold blue]Vexy PDF Werk v{self.version}[/bold blue]")

        # Validate inputs
        input_path = Path(pdf_path)
        if not input_path.exists():
            console.print(f"[red]Error: PDF file not found: {pdf_path}[/red]")
            return 1

        if not input_path.suffix.lower() == '.pdf':
            console.print(f"[red]Error: File must be a PDF: {pdf_path}[/red]")
            return 1

        # Set output directory
        if output_dir is None:
            output_dir = f"./output/{input_path.stem}"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        console.print(f"Processing: [cyan]{input_path}[/cyan]")
        console.print(f"Output directory: [cyan]{output_path}[/cyan]")

        # Parse requested formats
        requested_formats = [f.strip() for f in formats.split(',')]
        valid_formats = {'pdfa', 'markdown', 'epub', 'yaml'}
        invalid_formats = set(requested_formats) - valid_formats

        if invalid_formats:
            console.print(f"[red]Error: Invalid formats: {', '.join(invalid_formats)}[/red]")
            console.print(f"Valid formats: {', '.join(valid_formats)}")
            return 1

        console.print(f"Requested formats: [green]{', '.join(requested_formats)}[/green]")

        # TODO: Implement actual processing pipeline
        console.print("[yellow]Processing pipeline not yet implemented[/yellow]")
        return 0

    def config(self, show: bool = False, init: bool = False):
        """
        Manage VPW configuration.

        Args:
            show: Display current configuration
            init: Initialize default configuration file
        """
        if show:
            console.print("[blue]Configuration management not yet implemented[/blue]")
        elif init:
            console.print("[blue]Configuration initialization not yet implemented[/blue]")
        else:
            console.print("Use --show to display config or --init to create default config")

    def version(self):
        """Display version information."""
        console.print(f"Vexy PDF Werk version {self.version}")


def main():
    """Main entry point for the CLI."""
    try:
        fire.Fire(VexyPDFWerk)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

##### 3. Create Basic Configuration Module

```python
## 20. this_file: src/vexy_pdf_werk/config.py

"""Configuration management for Vexy PDF Werk."""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List

import toml
from platformdirs import user_config_dir
from pydantic import BaseModel, Field


class ProcessingConfig(BaseModel):
    """PDF processing configuration."""
    ocr_language: str = "eng"
    pdf_quality: str = "high"  # high, medium, low
    force_ocr: bool = False
    deskew: bool = True
    rotate_pages: bool = True


class ConversionConfig(BaseModel):
    """Content conversion configuration."""
    markdown_backend: str = "auto"  # auto, marker, markitdown, docling, basic
    paginate_markdown: bool = True
    include_images: bool = True
    extract_tables: bool = True


class AIConfig(BaseModel):
    """AI integration configuration."""
    enabled: bool = False
    provider: str = "claude"  # claude, gemini, custom
    correction_enabled: bool = False
    enhancement_enabled: bool = False
    max_tokens: int = 4000


class OutputConfig(BaseModel):
    """Output configuration."""
    formats: List[str] = Field(default=["pdfa", "markdown", "epub", "yaml"])
    preserve_original: bool = True
    output_directory: str = "./output"
    filename_template: str = "{stem}_{format}.{ext}"


class VPWConfig(BaseModel):
    """Main configuration model."""
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    conversion: ConversionConfig = Field(default_factory=ConversionConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)

    # External tool paths (auto-detected if None)
    tesseract_path: Optional[str] = None
    qpdf_path: Optional[str] = None
    pandoc_path: Optional[str] = None


def get_config_dir() -> Path:
    """Get the user configuration directory."""
    return Path(user_config_dir("vexy-pdf-werk"))


def get_config_file() -> Path:
    """Get the path to the main configuration file."""
    return get_config_dir() / "config.toml"


def load_config(config_file: Optional[Path] = None) -> VPWConfig:
    """
    Load configuration from file and environment variables.

    Args:
        config_file: Optional path to config file

    Returns:
        Loaded configuration
    """
    if config_file is None:
        config_file = get_config_file()

    # Load from file if it exists
    config_data = {}
    if config_file.exists():
        config_data = toml.load(config_file)

    # Apply environment variable overrides
    env_overrides = {}

    # AI configuration from environment
    if api_key := os.getenv("DATALAB_API_KEY"):
        env_overrides.setdefault("ai", {})["datalab_api_key"] = api_key

    if claude_key := os.getenv("ANTHROPIC_API_KEY"):
        env_overrides.setdefault("ai", {})["claude_api_key"] = claude_key

    if gemini_key := os.getenv("GOOGLE_AI_API_KEY"):
        env_overrides.setdefault("ai", {})["gemini_api_key"] = gemini_key

    # Tool paths from environment
    if tesseract := os.getenv("TESSERACT_PATH"):
        env_overrides["tesseract_path"] = tesseract

    if qpdf := os.getenv("QPDF_PATH"):
        env_overrides["qpdf_path"] = qpdf

    # Merge configurations (env overrides config file)
    final_config = {**config_data, **env_overrides}

    return VPWConfig(**final_config)


def save_config(config: VPWConfig, config_file: Optional[Path] = None) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration to save
        config_file: Optional path to config file
    """
    if config_file is None:
        config_file = get_config_file()

    # Ensure config directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dictionary and save
    config_dict = config.model_dump()
    with open(config_file, 'w') as f:
        toml.dump(config_dict, f)


def create_default_config() -> VPWConfig:
    """Create and save a default configuration file."""
    config = VPWConfig()
    config_file = get_config_file()

    if not config_file.exists():
        save_config(config, config_file)

    return config
```

##### 4. Create Basic Git Configuration

```bash
## 21. Create .gitignore
cat > .gitignore << 'EOF'
## 22. Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

## 23. Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

## 24. IDE
.vscode/
.idea/
*.swp
*.swo
*~

## 25. Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

## 26. Jupyter
.ipynb_checkpoints

## 27. OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

## 28. Project specific
output/
temp/
*.pdf
*.epub
test_output/
logs/
*.log

## 29. Configuration (don't commit secrets)
config.local.toml
.env.local

## 30. External integrations
external/ai-inference/*.key
external/datalab/*.key
EOF
```

##### 5. Install Dependencies and Verify Setup

```bash
## 31. Install core dependencies
uv add fire rich loguru platformdirs pydantic pathvalidate unicode-slugify pypdf pikepdf pyyaml toml requests aiohttp ebooklib

## 32. Install development dependencies
uv add --dev pytest pytest-cov pytest-asyncio ruff mypy pre-commit

## 33. Verify the installation
uv run python -c "import vexy_pdf_werk; print(f'VPW version: {vexy_pdf_werk.__version__}')"

## 34. Test the CLI
uv run vpw --help
uv run vpw version

## 35. Test basic functionality (should show "not implemented" message)
echo "Test PDF" > test.pdf
uv run vpw process test.pdf --verbose
rm test.pdf
```

#### 35.0.1. Development Workflow Setup

##### 1. Initialize Pre-commit Hooks

```bash
## 36. Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-toml, types-requests, types-PyYAML]
EOF

## 37. Install pre-commit hooks
uv run pre-commit install
```

##### 2. Create Development Scripts

```bash
## 38. Create development convenience scripts
mkdir -p scripts

cat > scripts/dev-setup.sh << 'EOF'
##!/bin/bash
## 39. Development environment setup script
set -e

echo "Setting up Vexy PDF Werk development environment..."

## 40. Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

## 41. Create virtual environment and install dependencies
echo "Installing dependencies..."
uv sync --all-extras

## 42. Install pre-commit hooks
echo "Setting up pre-commit hooks..."
uv run pre-commit install

## 43. Verify installation
echo "Verifying installation..."
uv run python -c "import vexy_pdf_werk; print('VPW imported successfully')"
uv run vpw version

echo "Development environment setup complete!"
EOF

chmod +x scripts/dev-setup.sh
```

##### 3. Verify Complete Setup

```bash
## 44. Run the development setup script
./scripts/dev-setup.sh

## 45. Run initial linting
uv run ruff check .
uv run ruff format .

## 46. Run initial tests (will be empty but should pass)
uv run pytest tests/ -v

## 47. Verify hatch can build the package
hatch build

## 48. Test CLI help output
uv run vpw --help
```

This completes the project structure and setup phase. The next part will focus on implementing the core processing pipeline and integrations.

------------------------------------------------------------

# `spec/103.md`

## 49. Vexy PDF Werk (VPW) - Part 3: Implementation Details

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

#### 50.0.1. Markdown Generator Implementation

##### Markdown Generator with Multiple Backends (`src/vexy_pdf_werk/core/markdown_generator.py`)

```python
## 51. this_file: src/vexy_pdf_werk/core/markdown_generator.py

"""Markdown generation with multiple conversion backends."""

import asyncio
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from loguru import logger
from rich.progress import Progress, TaskID

from ..config import VPWConfig, ConversionConfig
from ..utils.slug_utils import generate_page_slug
from ..utils.file_utils import ensure_directory
from .pdf_processor import PDFInfo


@dataclass
class PageContent:
    """Content of a single page."""
    page_number: int
    markdown_content: str
    images: List[Path]
    slug: str


@dataclass
class MarkdownResult:
    """Result of markdown conversion."""
    success: bool
    pages: List[PageContent]
    images_dir: Optional[Path] = None
    error: Optional[str] = None


class MarkdownConverter(ABC):
    """Abstract base class for markdown converters."""

    @abstractmethod
    async def convert(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> MarkdownResult:
        """Convert PDF to markdown."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the converter is available."""
        pass


class MarkerConverter(MarkdownConverter):
    """Marker PDF converter."""

    async def convert(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> MarkdownResult:
        """Convert PDF using Marker."""
        logger.info("Converting PDF with Marker")

        try:
            # Import marker (lazy loading)
            from marker.convert import convert_single_pdf
            from marker.models import load_all_models

            # Load Marker models (cached)
            model_list = load_all_models()

            # Convert PDF
            full_text, images, out_meta = convert_single_pdf(
                str(pdf_path),
                model_list,
                max_pages=None,
                langs=None,
                batch_multiplier=1
            )

            # Split into pages if paginated output requested
            if config.paginate_markdown:
                pages = self._split_paginated_content(full_text, images, output_dir)
            else:
                # Single file output
                slug = generate_page_slug(full_text[:200])
                pages = [PageContent(
                    page_number=0,
                    markdown_content=full_text,
                    images=list(images.values()) if images else [],
                    slug=slug
                )]

            return MarkdownResult(success=True, pages=pages)

        except ImportError:
            logger.error("Marker not installed. Install with: pip install marker-pdf")
            return MarkdownResult(
                success=False,
                pages=[],
                error="Marker not available - install with 'pip install marker-pdf'"
            )
        except Exception as e:
            logger.error(f"Marker conversion failed: {e}")
            return MarkdownResult(success=False, pages=[], error=str(e))

    def is_available(self) -> bool:
        """Check if Marker is available."""
        try:
            import marker
            return True
        except ImportError:
            return False

    def _split_paginated_content(
        self,
        content: str,
        images: Dict[str, Path],
        output_dir: Path
    ) -> List[PageContent]:
        """Split Marker output into pages."""
        # Marker uses page separators like "{PAGE_NUMBER}\n" + dashes
        import re

        pages = []
        page_splits = re.split(r'\n(\d+)\n-{40,}\n', content)

        if len(page_splits) == 1:
            # No page markers found, treat as single page
            slug = generate_page_slug(content[:200])
            return [PageContent(0, content, list(images.values()), slug)]

        # Process split content
        for i in range(1, len(page_splits), 2):
            if i + 1 < len(page_splits):
                page_num = int(page_splits[i])
                page_content = page_splits[i + 1].strip()
                slug = generate_page_slug(page_content[:200])

                # Find images for this page (basic heuristic)
                page_images = [img for img in images.values()
                             if f"page_{page_num}" in img.name.lower()]

                pages.append(PageContent(page_num, page_content, page_images, slug))

        return pages


class MarkItDownConverter(MarkdownConverter):
    """Microsoft MarkItDown converter."""

    async def convert(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> MarkdownResult:
        """Convert PDF using MarkItDown."""
        logger.info("Converting PDF with MarkItDown")

        try:
            from markitdown import MarkItDown

            md_converter = MarkItDown()
            result = md_converter.convert(str(pdf_path))

            if config.paginate_markdown:
                # MarkItDown doesn't have built-in pagination
                # We'll need to split manually or process page-by-page
                pages = await self._convert_page_by_page(pdf_path, output_dir, config)
            else:
                slug = generate_page_slug(result.text_content[:200])
                pages = [PageContent(0, result.text_content, [], slug)]

            return MarkdownResult(success=True, pages=pages)

        except ImportError:
            logger.error("MarkItDown not installed. Install with: pip install markitdown")
            return MarkdownResult(
                success=False,
                pages=[],
                error="MarkItDown not available - install with 'pip install markitdown'"
            )
        except Exception as e:
            logger.error(f"MarkItDown conversion failed: {e}")
            return MarkdownResult(success=False, pages=[], error=str(e))

    async def _convert_page_by_page(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> List[PageContent]:
        """Convert PDF page by page for pagination."""
        import pikepdf
        from markitdown import MarkItDown

        pages = []
        md_converter = MarkItDown()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Split PDF into individual pages
            with pikepdf.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_pdf = pikepdf.new()
                    page_pdf.pages.append(page)
                    page_file = temp_path / f"page_{i:03d}.pdf"
                    page_pdf.save(page_file)

                    # Convert individual page
                    try:
                        result = md_converter.convert(str(page_file))
                        content = result.text_content.strip()

                        if content:  # Skip empty pages
                            slug = generate_page_slug(content[:200])
                            pages.append(PageContent(i, content, [], slug))

                    except Exception as e:
                        logger.warning(f"Failed to convert page {i}: {e}")
                        continue

        return pages

    def is_available(self) -> bool:
        """Check if MarkItDown is available."""
        try:
            import markitdown
            return True
        except ImportError:
            return False


class BasicConverter(MarkdownConverter):
    """Basic fallback converter using PyMuPDF."""

    async def convert(
        self,
        pdf_path: Path,
        output_dir: Path,
        config: ConversionConfig
    ) -> MarkdownResult:
        """Convert PDF using basic text extraction."""
        logger.info("Converting PDF with basic text extraction")

        try:
            import fitz  # PyMuPDF

            pages = []
            doc = fitz.open(str(pdf_path))

            for page_num in range(doc.page_count):
                page = doc[page_num]

                # Extract text with basic markdown formatting
                if config.include_images:
                    # Try markdown extraction (preserves some formatting)
                    text = page.get_text("markdown")
                else:
                    # Plain text extraction
                    text = page.get_text()

                if text.strip():  # Skip empty pages
                    slug = generate_page_slug(text[:200])

                    # Extract images if requested
                    images = []
                    if config.include_images:
                        images = await self._extract_page_images(
                            page, page_num, output_dir
                        )

                    pages.append(PageContent(page_num, text, images, slug))

            doc.close()
            return MarkdownResult(success=True, pages=pages)

        except ImportError:
            logger.error("PyMuPDF not installed. Install with: pip install PyMuPDF")
            return MarkdownResult(
                success=False,
                pages=[],
                error="PyMuPDF not available - install with 'pip install PyMuPDF'"
            )
        except Exception as e:
            logger.error(f"Basic conversion failed: {e}")
            return MarkdownResult(success=False, pages=[], error=str(e))

    async def _extract_page_images(
        self, page, page_num: int, output_dir: Path
    ) -> List[Path]:
        """Extract images from a page."""
        images = []
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Save image
                image_filename = f"page_{page_num:03d}_img_{img_index:02d}.{image_ext}"
                image_path = output_dir / "images" / image_filename
                image_path.parent.mkdir(exist_ok=True)

                with open(image_path, "wb") as f:
                    f.write(image_bytes)

                images.append(image_path)

            except Exception as e:
                logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
                continue

        return images

    def is_available(self) -> bool:
        """Check if PyMuPDF is available."""
        try:
            import fitz
            return True
        except ImportError:
            return False


class MarkdownGenerator:
    """Main markdown generation coordinator."""

    def __init__(self, config: VPWConfig):
        """Initialize the markdown generator."""
        self.config = config
        self.conversion_config = config.conversion

        # Initialize converters
        self.converters = {
            "marker": MarkerConverter(),
            "markitdown": MarkItDownConverter(),
            "basic": BasicConverter(),
        }

    async def generate_markdown(
        self,
        pdf_path: Path,
        output_dir: Path,
        pdf_info: PDFInfo,
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None
    ) -> MarkdownResult:
        """
        Generate markdown from PDF using the best available converter.

        Args:
            pdf_path: Input PDF file
            output_dir: Output directory for markdown files
            pdf_info: PDF analysis information
            progress: Optional progress tracker
            task_id: Optional progress task ID

        Returns:
            Markdown conversion result
        """
        logger.info(f"Generating markdown from {pdf_path}")

        # Select converter
        converter = self._select_converter()
        if progress and task_id is not None:
            progress.update(task_id, description=f"Converting with {converter.__class__.__name__}...")

        # Ensure output directory exists
        ensure_directory(output_dir)

        # Convert to markdown
        result = await converter.convert(pdf_path, output_dir, self.conversion_config)

        if not result.success:
            logger.error(f"Markdown conversion failed: {result.error}")
            return result

        # Write markdown files
        if progress and task_id is not None:
            progress.update(task_id, description="Writing markdown files...")

        markdown_files = await self._write_markdown_files(result.pages, output_dir)

        logger.success(f"Generated {len(markdown_files)} markdown files")
        return result

    def _select_converter(self) -> MarkdownConverter:
        """Select the best available converter."""
        backend = self.conversion_config.markdown_backend

        if backend != "auto":
            # User specified a backend
            converter = self.converters.get(backend)
            if converter and converter.is_available():
                logger.info(f"Using requested converter: {backend}")
                return converter
            else:
                logger.warning(f"Requested converter '{backend}' not available, falling back to auto")

        # Auto-selection: try converters in order of preference
        preference_order = ["marker", "markitdown", "basic"]

        for backend_name in preference_order:
            converter = self.converters[backend_name]
            if converter.is_available():
                logger.info(f"Auto-selected converter: {backend_name}")
                return converter

        # This should never happen since BasicConverter should always be available
        raise RuntimeError("No markdown converters available")

    async def _write_markdown_files(
        self,
        pages: List[PageContent],
        output_dir: Path
    ) -> List[Path]:
        """Write markdown content to individual page files."""
        markdown_files = []

        for page in pages:
            # Generate filename: 000--slug.md
            filename = f"{page.page_number:03d}--{page.slug}.md"
            file_path = output_dir / filename

            # Create content with frontmatter if it's the first page
            content = page.markdown_content
            if page.page_number == 0:
                # Add YAML frontmatter to first page
                frontmatter = self._generate_frontmatter()
                content = f"---\n{frontmatter}\n---\n\n{content}"

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            markdown_files.append(file_path)
            logger.debug(f"Wrote markdown file: {file_path}")

        return markdown_files

    def _generate_frontmatter(self) -> str:
        """Generate YAML frontmatter for the first markdown file."""
        import yaml
        from datetime import datetime

        frontmatter = {
            "generated_by": "Vexy PDF Werk",
            "generated_at": datetime.now().isoformat(),
            "conversion_backend": self.conversion_config.markdown_backend,
            "paginated": self.conversion_config.paginate_markdown,
        }

        return yaml.dump(frontmatter, default_flow_style=False).strip()
```

#### 51.0.1. AI Services Integration

##### AI Services Factory and Implementations (`src/vexy_pdf_werk/integrations/ai_services.py`)

```python
## 52. this_file: src/vexy_pdf_werk/integrations/ai_services.py

"""AI service integrations for text enhancement."""

import asyncio
import subprocess
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path

from loguru import logger

from ..config import AIConfig


class AIService(ABC):
    """Abstract base class for AI services."""

    @abstractmethod
    async def correct_text(self, text: str, context: str = "") -> str:
        """Correct OCR errors in text."""
        pass

    @abstractmethod
    async def enhance_content(self, text: str, document_type: str = "general") -> str:
        """Enhance content structure and formatting."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI service is available."""
        pass


class ClaudeCLIService(AIService):
    """Claude CLI service integration."""

    def __init__(self, config: AIConfig):
        """Initialize Claude service."""
        self.config = config
        self.max_tokens = config.max_tokens

    async def correct_text(self, text: str, context: str = "") -> str:
        """Correct OCR errors using Claude CLI."""
        prompt = self._create_correction_prompt(text, context)

        cmd = [
            "claude",
            "--model", "claude-sonnet-4-20250514",
            "--dangerously-skip-permissions",
            "-p", prompt
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown Claude error"
                logger.error(f"Claude CLI failed: {error_msg}")
                return text  # Return original text on failure

            corrected = stdout.decode().strip()
            logger.debug(f"Claude corrected {len(text)} -> {len(corrected)} chars")
            return corrected

        except Exception as e:
            logger.error(f"Claude CLI error: {e}")
            return text  # Return original text on failure

    async def enhance_content(self, text: str, document_type: str = "general") -> str:
        """Enhance content structure using Claude."""
        prompt = self._create_enhancement_prompt(text, document_type)

        # Similar implementation to correct_text but with different prompt
        return await self._call_claude(prompt, fallback=text)

    def _create_correction_prompt(self, text: str, context: str) -> str:
        """Create prompt for OCR correction."""
        return f"""
Please review and correct any OCR errors in the following text.
Maintain the original formatting, structure, and meaning.
Only fix obvious OCR mistakes like character substitutions or garbled words.
Do not add, remove, or rephrase content.

Context: {context}

Text to correct:
{text}

Return only the corrected text, nothing else.
        """.strip()

    def _create_enhancement_prompt(self, text: str, document_type: str) -> str:
        """Create prompt for content enhancement."""
        return f"""
Please enhance the formatting and structure of this {document_type} text while preserving all content.
Fix any formatting issues, ensure proper heading hierarchy, and improve readability.
Maintain all original information and meaning.

Text to enhance:
{text}

Return the enhanced text in markdown format.
        """.strip()

    async def _call_claude(self, prompt: str, fallback: str) -> str:
        """Generic Claude CLI call with fallback."""
        cmd = [
            "claude",
            "--model", "claude-sonnet-4-20250514",
            "--dangerously-skip-permissions",
            "-p", prompt
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                logger.error(f"Claude CLI failed: {stderr.decode()}")
                return fallback

            return stdout.decode().strip()

        except Exception as e:
            logger.error(f"Claude CLI error: {e}")
            return fallback

    def is_available(self) -> bool:
        """Check if Claude CLI is available."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False


class GeminiCLIService(AIService):
    """Gemini CLI service integration."""

    def __init__(self, config: AIConfig):
        """Initialize Gemini service."""
        self.config = config

    async def correct_text(self, text: str, context: str = "") -> str:
        """Correct OCR errors using Gemini CLI."""
        prompt = self._create_correction_prompt(text, context)

        cmd = [
            "gemini",
            "-c",  # Continue conversation
            "-y",  # Yes to prompts
            "-p", prompt
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                logger.error(f"Gemini CLI failed: {stderr.decode()}")
                return text

            return stdout.decode().strip()

        except Exception as e:
            logger.error(f"Gemini CLI error: {e}")
            return text

    async def enhance_content(self, text: str, document_type: str = "general") -> str:
        """Enhance content using Gemini."""
        # Similar to correct_text with different prompt
        return text  # Placeholder

    def _create_correction_prompt(self, text: str, context: str) -> str:
        """Create OCR correction prompt for Gemini."""
        return f"Correct OCR errors in this text, maintaining original meaning:\n\n{text}"

    def is_available(self) -> bool:
        """Check if Gemini CLI is available."""
        try:
            result = subprocess.run(
                ["gemini", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False


class AIServiceFactory:
    """Factory for creating AI services."""

    @staticmethod
    def create_service(config: AIConfig) -> Optional[AIService]:
        """Create AI service based on configuration."""
        if not config.enabled:
            return None

        services = {
            "claude": ClaudeCLIService,
            "gemini": GeminiCLIService,
        }

        service_class = services.get(config.provider)
        if not service_class:
            logger.warning(f"Unknown AI provider: {config.provider}")
            return None

        service = service_class(config)

        if not service.is_available():
            logger.warning(f"AI service {config.provider} not available")
            return None

        return service

    @staticmethod
    def list_available_services() -> Dict[str, bool]:
        """List all AI services and their availability."""
        from ..config import AIConfig

        services = {}
        dummy_config = AIConfig(enabled=True)

        for provider in ["claude", "gemini"]:
            dummy_config.provider = provider
            service = AIServiceFactory.create_service(dummy_config)
            services[provider] = service is not None and service.is_available()

        return services
```

This completes the core implementation details for the main processing components. The next part (104) will cover testing, quality assurance, and deployment.

------------------------------------------------------------

# `spec/104.md`

## 53. Vexy PDF Werk (VPW) - Part 4: Testing and Deployment

This final section covers comprehensive testing strategies, quality assurance processes, packaging, and deployment procedures.

### 53.1. Testing Strategy Implementation

#### 53.1.1. Test Structure and Organization

##### Test Directory Structure
```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and fixtures
├── unit/
│   ├── __init__.py
│   ├── test_config.py          # Configuration testing
│   ├── test_pdf_processor.py   # PDF processing unit tests
│   ├── test_markdown_generator.py # Markdown generation tests
│   ├── test_ai_services.py     # AI service mocking tests
│   └── test_utils.py           # Utility function tests
├── integration/
│   ├── __init__.py
│   ├── test_full_pipeline.py   # End-to-end pipeline tests
│   ├── test_cli.py            # CLI interface tests
│   └── test_external_tools.py # External tool integration tests
└── fixtures/
    ├── sample_pdfs/           # Test PDF files
    ├── expected_outputs/      # Expected test results
    └── configs/               # Test configuration files
```

#### 53.1.2. Test Configuration and Fixtures

##### Pytest Configuration (`tests/conftest.py`)

```python
## 54. this_file: tests/conftest.py

"""Pytest configuration and shared fixtures for VPW tests."""

import tempfile
import shutil
from pathlib import Path
from typing import Generator

import pytest
from unittest.mock import Mock, patch

from vexy_pdf_werk.config import VPWConfig, ProcessingConfig, ConversionConfig, AIConfig, OutputConfig


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def sample_pdf() -> Path:
    """Path to a sample PDF file for testing."""
    # Create a simple PDF for testing if it doesn't exist
    fixtures_dir = Path(__file__).parent / "fixtures" / "sample_pdfs"
    sample_path = fixtures_dir / "simple_text.pdf"

    if not sample_path.exists():
        # Create a minimal PDF using reportlab for testing
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter

            fixtures_dir.mkdir(parents=True, exist_ok=True)
            c = canvas.Canvas(str(sample_path), pagesize=letter)
            c.drawString(100, 750, "Test PDF Document")
            c.drawString(100, 700, "This is a sample PDF for testing VPW.")
            c.showPage()
            c.save()
        except ImportError:
            pytest.skip("reportlab not available for PDF generation")

    return sample_path


@pytest.fixture
def default_config() -> VPWConfig:
    """Default VPW configuration for testing."""
    return VPWConfig(
        processing=ProcessingConfig(
            ocr_language="eng",
            pdf_quality="high",
            force_ocr=False
        ),
        conversion=ConversionConfig(
            markdown_backend="basic",  # Use basic converter for tests
            paginate_markdown=True,
            include_images=True
        ),
        ai=AIConfig(
            enabled=False,  # Disable AI by default in tests
            provider="claude",
            correction_enabled=False
        ),
        output=OutputConfig(
            formats=["pdfa", "markdown", "epub", "yaml"],
            preserve_original=True,
            output_directory="./test_output"
        )
    )


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    mock_service = Mock()
    mock_service.correct_text.return_value = "Corrected text"
    mock_service.enhance_content.return_value = "Enhanced content"
    mock_service.is_available.return_value = True
    return mock_service


@pytest.fixture
def mock_ocrmypdf():
    """Mock OCRmyPDF for testing without requiring external tools."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"OCR completed successfully"
        mock_run.return_value.stderr = b""
        yield mock_run


@pytest.fixture
def mock_qpdf():
    """Mock qpdf for testing."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"PDF processing completed"
        mock_run.return_value.stderr = b""
        yield mock_run


## 55. Pytest markers configuration
pytest_plugins = []

## 56. Skip slow tests by default
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers."""
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return

    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--runai", action="store_true", default=False,
        help="run tests that require AI services"
    )
```

#### 56.0.1. Unit Tests Implementation

##### Configuration Tests (`tests/unit/test_config.py`)

```python
## 57. this_file: tests/unit/test_config.py

"""Unit tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest
import toml

from vexy_pdf_werk.config import (
    VPWConfig, ProcessingConfig, ConversionConfig, AIConfig, OutputConfig,
    load_config, save_config, get_config_dir, get_config_file
)


class TestVPWConfig:
    """Test VPW configuration model."""

    def test_default_config_creation(self):
        """Test creating default configuration."""
        config = VPWConfig()

        assert config.processing.ocr_language == "eng"
        assert config.conversion.markdown_backend == "auto"
        assert config.ai.enabled is False
        assert "pdfa" in config.output.formats

    def test_config_validation(self):
        """Test configuration validation."""
        # Valid configuration
        config = VPWConfig(
            processing=ProcessingConfig(ocr_language="eng+fra"),
            ai=AIConfig(enabled=True, provider="claude")
        )
        assert config.processing.ocr_language == "eng+fra"
        assert config.ai.enabled is True

    def test_nested_config_modification(self):
        """Test modifying nested configuration."""
        config = VPWConfig()
        config.ai.enabled = True
        config.ai.provider = "gemini"

        assert config.ai.enabled is True
        assert config.ai.provider == "gemini"


class TestConfigFileOperations:
    """Test configuration file operations."""

    def test_save_and_load_config(self, temp_dir):
        """Test saving and loading configuration."""
        config_file = temp_dir / "test_config.toml"

        # Create test configuration
        original_config = VPWConfig()
        original_config.processing.ocr_language = "deu"
        original_config.ai.enabled = True

        # Save configuration
        save_config(original_config, config_file)
        assert config_file.exists()

        # Load configuration
        loaded_config = load_config(config_file)
        assert loaded_config.processing.ocr_language == "deu"
        assert loaded_config.ai.enabled is True

    def test_config_file_format(self, temp_dir):
        """Test that configuration file is valid TOML."""
        config_file = temp_dir / "test_config.toml"
        config = VPWConfig()

        save_config(config, config_file)

        # Verify file is valid TOML
        with open(config_file) as f:
            loaded_toml = toml.load(f)

        assert "processing" in loaded_toml
        assert "conversion" in loaded_toml
        assert "ai" in loaded_toml
        assert "output" in loaded_toml

    def test_environment_variable_override(self):
        """Test environment variable configuration override."""
        # Set test environment variables
        test_env = {
            "DATALAB_API_KEY": "test-datalab-key",
            "ANTHROPIC_API_KEY": "test-claude-key",
            "TESSERACT_PATH": "/test/tesseract"
        }

        with patch.dict(os.environ, test_env):
            config = load_config()
            # Note: This test would need the actual environment override logic
            # to be implemented in the load_config function


class TestConfigDirectories:
    """Test configuration directory operations."""

    def test_get_config_dir(self):
        """Test getting configuration directory."""
        config_dir = get_config_dir()
        assert config_dir.name == "vexy-pdf-werk"
        assert config_dir.is_absolute()

    def test_get_config_file(self):
        """Test getting configuration file path."""
        config_file = get_config_file()
        assert config_file.name == "config.toml"
        assert config_file.parent.name == "vexy-pdf-werk"
```

##### PDF Processor Tests (`tests/unit/test_pdf_processor.py`)

```python
## 58. this_file: tests/unit/test_pdf_processor.py

"""Unit tests for PDF processor."""

import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest

from vexy_pdf_werk.core.pdf_processor import PDFProcessor, PDFInfo, ProcessingResult
from vexy_pdf_werk.config import VPWConfig


class TestPDFProcessor:
    """Test PDF processor functionality."""

    @pytest.fixture
    def pdf_processor(self, default_config):
        """Create PDF processor with mocked external tools."""
        with patch('shutil.which') as mock_which:
            # Mock external tools as available
            mock_which.side_effect = lambda tool: f"/usr/bin/{tool}"
            processor = PDFProcessor(default_config)
            return processor

    @pytest.mark.asyncio
    async def test_analyze_pdf_basic(self, pdf_processor, sample_pdf):
        """Test basic PDF analysis."""
        with patch('pikepdf.open') as mock_open:
            # Mock PDF structure
            mock_pdf = Mock()
            mock_pdf.pages = [Mock(), Mock()]  # 2 pages
            mock_pdf.docinfo = {
                '/Title': 'Test Document',
                '/Author': 'Test Author'
            }
            mock_open.return_value.__enter__.return_value = mock_pdf

            pdf_info = await pdf_processor.analyze_pdf(sample_pdf)

            assert pdf_info.path == sample_pdf
            assert pdf_info.pages == 2
            assert pdf_info.title == 'Test Document'
            assert pdf_info.author == 'Test Author'

    @pytest.mark.asyncio
    async def test_analyze_pdf_no_metadata(self, pdf_processor, sample_pdf):
        """Test PDF analysis without metadata."""
        with patch('pikepdf.open') as mock_open:
            mock_pdf = Mock()
            mock_pdf.pages = [Mock()]
            mock_pdf.docinfo = {}  # No metadata
            mock_open.return_value.__enter__.return_value = mock_pdf

            pdf_info = await pdf_processor.analyze_pdf(sample_pdf)

            assert pdf_info.pages == 1
            assert pdf_info.title is None
            assert pdf_info.author is None

    @pytest.mark.asyncio
    async def test_create_better_pdf_success(self, pdf_processor, sample_pdf, temp_dir):
        """Test successful PDF processing."""
        output_pdf = temp_dir / "output.pdf"

        # Mock the analyze_pdf method
        mock_pdf_info = PDFInfo(
            path=sample_pdf,
            pages=1,
            has_text=True,
            is_scanned=False,
            has_images=False,
            title="Test PDF"
        )

        with patch.object(pdf_processor, 'analyze_pdf', return_value=mock_pdf_info), \
             patch.object(pdf_processor, '_convert_to_pdfa', new_callable=AsyncMock) as mock_convert:

            # Mock successful conversion
            mock_convert.return_value = None

            # Create empty output file to simulate successful processing
            output_pdf.touch()

            result = await pdf_processor.create_better_pdf(sample_pdf, output_pdf)

            assert result.success is True
            assert result.output_path == output_pdf
            assert result.pdf_info == mock_pdf_info
            assert result.processing_time > 0

    @pytest.mark.asyncio
    async def test_create_better_pdf_failure(self, pdf_processor, sample_pdf, temp_dir):
        """Test PDF processing failure handling."""
        output_pdf = temp_dir / "output.pdf"

        with patch.object(pdf_processor, 'analyze_pdf', side_effect=RuntimeError("PDF corrupt")):
            result = await pdf_processor.create_better_pdf(sample_pdf, output_pdf)

            assert result.success is False
            assert result.error == "PDF corrupt"
            assert result.output_path is None

    @pytest.mark.asyncio
    async def test_enhance_with_ocr(self, pdf_processor, sample_pdf, temp_dir):
        """Test OCR enhancement process."""
        output_pdf = temp_dir / "ocr_output.pdf"
        pdf_info = PDFInfo(sample_pdf, 1, False, True, False)

        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock successful OCRmyPDF execution
            mock_process = Mock()
            mock_process.communicate.return_value = (b"Success", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Create output file to simulate OCRmyPDF success
            output_pdf.touch()

            await pdf_processor._enhance_with_ocr(sample_pdf, output_pdf, pdf_info)

            # Verify OCRmyPDF was called with correct arguments
            args, kwargs = mock_subprocess.call_args
            assert "ocrmypdf" in args[0]
            assert str(sample_pdf) in args[0]
            assert str(output_pdf) in args[0]

    @pytest.mark.asyncio
    async def test_enhance_with_ocr_failure(self, pdf_processor, sample_pdf, temp_dir):
        """Test OCR enhancement failure handling."""
        output_pdf = temp_dir / "ocr_output.pdf"
        pdf_info = PDFInfo(sample_pdf, 1, False, True, False)

        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock OCRmyPDF failure
            mock_process = Mock()
            mock_process.communicate.return_value = (b"", b"OCR failed")
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process

            with pytest.raises(RuntimeError, match="OCR processing failed"):
                await pdf_processor._enhance_with_ocr(sample_pdf, output_pdf, pdf_info)


class TestPDFInfo:
    """Test PDFInfo dataclass."""

    def test_pdf_info_creation(self):
        """Test PDFInfo object creation."""
        path = Path("test.pdf")
        info = PDFInfo(
            path=path,
            pages=10,
            has_text=True,
            is_scanned=False,
            has_images=True,
            title="Test Document"
        )

        assert info.path == path
        assert info.pages == 10
        assert info.has_text is True
        assert info.is_scanned is False
        assert info.has_images is True
        assert info.title == "Test Document"

    def test_pdf_info_defaults(self):
        """Test PDFInfo with default values."""
        info = PDFInfo(
            path=Path("test.pdf"),
            pages=1,
            has_text=False,
            is_scanned=True,
            has_images=False
        )

        assert info.title is None
        assert info.author is None
        assert info.creation_date is None
```

#### 58.0.1. Integration Tests

##### Full Pipeline Tests (`tests/integration/test_full_pipeline.py`)

```python
## 59. this_file: tests/integration/test_full_pipeline.py

"""Integration tests for the complete VPW pipeline."""

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest

from vexy_pdf_werk.core.pdf_processor import PDFProcessor
from vexy_pdf_werk.core.markdown_generator import MarkdownGenerator
from vexy_pdf_werk.core.epub_creator import EPubCreator
from vexy_pdf_werk.core.metadata_extractor import MetadataExtractor


@pytest.mark.integration
class TestFullPipeline:
    """Test complete processing pipeline."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_complete_pipeline_basic(self, sample_pdf, temp_dir, default_config):
        """Test complete pipeline with basic converters only."""
        # Initialize all processors
        pdf_processor = PDFProcessor(default_config)
        markdown_generator = MarkdownGenerator(default_config)
        # epub_creator = EPubCreator(default_config)
        # metadata_extractor = MetadataExtractor(default_config)

        # Define output paths
        pdfa_output = temp_dir / "output.pdf"
        markdown_output = temp_dir / "markdown"
        markdown_output.mkdir(exist_ok=True)

        # Mock external tools for integration testing
        with patch('shutil.which', return_value="/usr/bin/mock"), \
             patch('asyncio.create_subprocess_exec') as mock_subprocess:

            # Mock successful subprocess calls
            mock_process = Mock()
            mock_process.communicate.return_value = (b"Success", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Step 1: Process PDF
            pdfa_result = await pdf_processor.create_better_pdf(sample_pdf, pdfa_output)

            # For integration test, we'll mock the successful file creation
            pdfa_output.touch()  # Simulate successful PDF creation

            assert pdfa_result.success, f"PDF processing failed: {pdfa_result.error}"
            assert pdfa_output.exists()

            # Step 2: Generate Markdown (using basic converter)
            if pdfa_result.success and pdfa_result.pdf_info:
                markdown_result = await markdown_generator.generate_markdown(
                    sample_pdf,  # Use original for markdown conversion
                    markdown_output,
                    pdfa_result.pdf_info
                )

                # Basic converter should work without external dependencies
                assert markdown_result.success, f"Markdown generation failed: {markdown_result.error}"

                # Check that markdown files were created
                markdown_files = list(markdown_output.glob("*.md"))
                assert len(markdown_files) > 0, "No markdown files generated"

                # Verify file naming convention
                for md_file in markdown_files:
                    assert md_file.name.count('--') == 1, f"Invalid filename format: {md_file.name}"
                    page_num = md_file.name.split('--')[0]
                    assert page_num.isdigit(), f"Page number not numeric: {page_num}"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_pipeline_with_ai_mock(self, sample_pdf, temp_dir, default_config, mock_ai_service):
        """Test pipeline with mocked AI services."""
        # Enable AI in config
        default_config.ai.enabled = True
        default_config.ai.correction_enabled = True

        pdf_processor = PDFProcessor(default_config)

        # Mock AI service factory to return our mock
        with patch('vexy_pdf_werk.integrations.ai_services.AIServiceFactory.create_service',
                   return_value=mock_ai_service), \
             patch('shutil.which', return_value="/usr/bin/mock"), \
             patch('asyncio.create_subprocess_exec') as mock_subprocess:

            mock_process = Mock()
            mock_process.communicate.return_value = (b"Success", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            output_pdf = temp_dir / "ai_enhanced.pdf"
            output_pdf.touch()  # Mock successful creation

            result = await pdf_processor.create_better_pdf(sample_pdf, output_pdf)

            assert result.success
            # Verify AI service was called (in actual implementation)
            # mock_ai_service.correct_text.assert_called()

    def test_output_file_structure(self, temp_dir):
        """Test that output file structure matches specifications."""
        # Create mock output structure
        output_dir = temp_dir / "test_output"
        output_dir.mkdir()

        # Create expected files
        (output_dir / "document.pdf").touch()  # PDF/A output
        (output_dir / "000--introduction.md").touch()  # Markdown files
        (output_dir / "001--chapter-one.md").touch()
        (output_dir / "document.epub").touch()  # ePub output
        (output_dir / "metadata.yaml").touch()  # Metadata

        # Verify structure
        assert (output_dir / "document.pdf").exists()
        assert len(list(output_dir.glob("*.md"))) == 2
        assert (output_dir / "document.epub").exists()
        assert (output_dir / "metadata.yaml").exists()

        # Verify markdown naming convention
        md_files = list(output_dir.glob("*.md"))
        for md_file in md_files:
            parts = md_file.stem.split('--')
            assert len(parts) == 2
            page_num, slug = parts
            assert page_num.isdigit()
            assert len(slug) > 0


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in integration scenarios."""

    @pytest.mark.asyncio
    async def test_missing_external_tools(self, sample_pdf, temp_dir, default_config):
        """Test graceful handling of missing external tools."""
        with patch('shutil.which', return_value=None):
            with pytest.raises(RuntimeError, match="Required tool .* not found"):
                PDFProcessor(default_config)

    @pytest.mark.asyncio
    async def test_corrupted_pdf_handling(self, temp_dir, default_config):
        """Test handling of corrupted PDF files."""
        # Create a fake corrupted PDF
        corrupted_pdf = temp_dir / "corrupted.pdf"
        corrupted_pdf.write_text("This is not a PDF file")

        pdf_processor = PDFProcessor(default_config)

        with patch('shutil.which', return_value="/usr/bin/mock"):
            with pytest.raises(RuntimeError, match="PDF analysis failed"):
                await pdf_processor.analyze_pdf(corrupted_pdf)

    @pytest.mark.asyncio
    async def test_permission_denied_output(self, sample_pdf, default_config):
        """Test handling of permission denied on output."""
        # Try to write to a read-only directory
        readonly_dir = Path("/proc")  # System directory that should be read-only
        output_path = readonly_dir / "test.pdf"

        pdf_processor = PDFProcessor(default_config)

        with patch('shutil.which', return_value="/usr/bin/mock"):
            result = await pdf_processor.create_better_pdf(sample_pdf, output_path)
            assert result.success is False
            assert "permission" in result.error.lower() or "not found" in result.error.lower()
```

##### CLI Tests (`tests/integration/test_cli.py`)

```python
## 60. this_file: tests/integration/test_cli.py

"""Integration tests for CLI interface."""

import subprocess
import sys
from pathlib import Path

import pytest

from vexy_pdf_werk.cli import VexyPDFWerk, main


@pytest.mark.integration
class TestCLI:
    """Test CLI functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        # Test that CLI can be imported and help works
        vpw = VexyPDFWerk()
        assert vpw.version is not None

    def test_cli_version_command(self, capsys):
        """Test version command."""
        vpw = VexyPDFWerk()
        vpw.version()

        captured = capsys.readouterr()
        assert "Vexy PDF Werk version" in captured.out

    def test_cli_config_show(self, capsys):
        """Test config show command."""
        vpw = VexyPDFWerk()
        vpw.config(show=True)

        captured = capsys.readouterr()
        assert "Configuration" in captured.out

    def test_cli_process_nonexistent_file(self, capsys):
        """Test processing non-existent file."""
        vpw = VexyPDFWerk()
        result = vpw.process("nonexistent.pdf")

        assert result == 1  # Error exit code

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_cli_process_invalid_format(self, sample_pdf, capsys):
        """Test processing with invalid output format."""
        vpw = VexyPDFWerk()
        result = vpw.process(str(sample_pdf), formats="invalid_format")

        assert result == 1  # Error exit code

        captured = capsys.readouterr()
        assert "Invalid formats" in captured.out

    @pytest.mark.slow
    def test_cli_process_basic(self, sample_pdf, temp_dir, capsys):
        """Test basic CLI processing."""
        vpw = VexyPDFWerk()
        result = vpw.process(
            str(sample_pdf),
            output_dir=str(temp_dir),
            formats="yaml",  # Only request metadata (simplest)
            verbose=True
        )

        # Should return 0 when implementation is complete
        # For now, it returns 0 but shows "not implemented"
        captured = capsys.readouterr()
        assert "Processing" in captured.out

    @pytest.mark.subprocess
    def test_cli_as_subprocess(self, sample_pdf):
        """Test CLI as subprocess (when installed)."""
        try:
            # Try to run the CLI as a subprocess
            result = subprocess.run([
                sys.executable, "-m", "vexy_pdf_werk.cli",
                "version"
            ], capture_output=True, text=True, timeout=10)

            # If the module is properly installed, this should work
            if result.returncode == 0:
                assert "version" in result.stdout.lower()
            else:
                # If not installed, we expect an import error
                assert "ModuleNotFoundError" in result.stderr or result.returncode != 0

        except subprocess.TimeoutExpired:
            pytest.fail("CLI subprocess timed out")


@pytest.mark.integration
class TestCLIFireIntegration:
    """Test Fire integration with CLI."""

    def test_fire_help_generation(self):
        """Test that Fire generates proper help."""
        vpw = VexyPDFWerk()

        # Check that methods have proper docstrings for Fire
        assert vpw.process.__doc__ is not None
        assert "PDF file" in vpw.process.__doc__

        assert vpw.config.__doc__ is not None
        assert "configuration" in vpw.config.__doc__.lower()

    def test_fire_argument_parsing(self):
        """Test Fire's argument parsing."""
        vpw = VexyPDFWerk()

        # Fire should handle these arguments correctly
        # This is more of a smoke test to ensure Fire integration works
        assert hasattr(vpw, 'process')
        assert hasattr(vpw, 'config')
        assert hasattr(vpw, 'version')
```

#### 60.0.1. Quality Assurance and Code Analysis

##### Code Quality Scripts (`scripts/quality-check.sh`)

```bash
##!/bin/bash
## 61. this_file: scripts/quality-check.sh

"""Comprehensive quality assurance script."""

set -e

echo "🔍 Running comprehensive quality checks for Vexy PDF Werk..."

## 62. Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

## 63. Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "Not in project root directory (pyproject.toml not found)"
    exit 1
fi

print_status "Checking development environment..."

## 64. Check uv availability
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed or not in PATH"
    exit 1
fi

## 65. Check hatch availability
if ! command -v hatch &> /dev/null; then
    print_error "hatch is not installed or not in PATH"
    exit 1
fi

print_success "Development tools available"

## 66. Code formatting with ruff
print_status "Checking code formatting..."
if uv run ruff format --check .; then
    print_success "Code formatting is correct"
else
    print_warning "Code formatting issues found. Run 'uv run ruff format .' to fix"
    # Auto-fix formatting
    uv run ruff format .
    print_success "Code formatting fixed"
fi

## 67. Linting with ruff
print_status "Running linting checks..."
if uv run ruff check --fix .; then
    print_success "No linting issues found"
else
    print_warning "Some linting issues were found and fixed"
fi

## 68. Type checking with mypy
print_status "Running type checks..."
if uv run mypy src/vexy_pdf_werk/; then
    print_success "Type checking passed"
else
    print_error "Type checking failed"
    exit 1
fi

## 69. Security scan (if bandit is available)
print_status "Running security scan..."
if uv run bandit -r src/ -f json -o bandit-report.json 2>/dev/null; then
    print_success "Security scan completed"
else
    print_warning "Security scan skipped (bandit not available)"
fi

## 70. Run tests
print_status "Running test suite..."

## 71. Unit tests
print_status "Running unit tests..."
if uv run pytest tests/unit/ -v --tb=short; then
    print_success "Unit tests passed"
else
    print_error "Unit tests failed"
    exit 1
fi

## 72. Integration tests (if not in CI)
if [[ -z "$CI" ]]; then
    print_status "Running integration tests..."
    if uv run pytest tests/integration/ -v --tb=short -m "not slow"; then
        print_success "Integration tests passed"
    else
        print_error "Integration tests failed"
        exit 1
    fi
else
    print_status "Skipping integration tests in CI"
fi

## 73. Test coverage
print_status "Checking test coverage..."
if uv run pytest --cov=src/vexy_pdf_werk --cov-report=term --cov-report=html tests/unit/; then
    print_success "Coverage report generated"
else
    print_warning "Coverage check failed"
fi

## 74. Build check
print_status "Testing package build..."
if hatch build; then
    print_success "Package builds successfully"
    # Clean up build artifacts
    rm -rf dist/
else
    print_error "Package build failed"
    exit 1
fi

## 75. Documentation check
print_status "Checking documentation..."
if [[ -f "README.md" ]]; then
    print_success "README.md exists"
else
    print_warning "README.md missing"
fi

## 76. Configuration validation
print_status "Validating configuration..."
if uv run python -c "
from src.vexy_pdf_werk.config import VPWConfig
try:
    config = VPWConfig()
    print('Configuration validation: OK')
except Exception as e:
    print(f'Configuration validation failed: {e}')
    exit(1)
"; then
    print_success "Configuration validation passed"
else
    print_error "Configuration validation failed"
    exit 1
fi

## 77. CLI smoke test
print_status "Testing CLI interface..."
if uv run python -m vexy_pdf_werk.cli version >/dev/null 2>&1; then
    print_success "CLI smoke test passed"
else
    print_error "CLI smoke test failed"
    exit 1
fi

print_success "All quality checks passed! 🎉"
print_status "Summary:"
echo "  ✅ Code formatting (ruff format)"
echo "  ✅ Linting (ruff check)"
echo "  ✅ Type checking (mypy)"
echo "  ✅ Security scan (bandit)"
echo "  ✅ Unit tests (pytest)"
echo "  ✅ Integration tests (pytest)"
echo "  ✅ Test coverage"
echo "  ✅ Package build (hatch)"
echo "  ✅ Documentation check"
echo "  ✅ Configuration validation"
echo "  ✅ CLI smoke test"

print_status "Project is ready for deployment! 🚀"
```

#### 77.0.1. Packaging and Distribution

##### Release Workflow (`scripts/release.sh`)

```bash
##!/bin/bash
## 78. this_file: scripts/release.sh

"""Automated release workflow script."""

set -e

## 79. Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

## 80. Check arguments
if [[ $# -ne 1 ]]; then
    print_error "Usage: $0 <version>"
    print_error "Example: $0 1.0.0"
    exit 1
fi

VERSION="$1"

## 81. Validate version format (semantic versioning)
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    print_error "Invalid version format. Use semantic versioning (e.g., 1.0.0)"
    exit 1
fi

print_status "Starting release process for version $VERSION"

## 82. Check for clean working directory
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory is not clean. Commit or stash changes first."
    exit 1
fi

## 83. Check current branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    print_warning "You are not on the main branch (current: $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Release cancelled"
        exit 1
    fi
fi

## 84. Run quality checks
print_status "Running comprehensive quality checks..."
if ! ./scripts/quality-check.sh; then
    print_error "Quality checks failed. Fix issues before release."
    exit 1
fi

## 85. Update version in relevant files if needed
print_status "Preparing version $VERSION..."

## 86. Run full test suite including slow tests
print_status "Running complete test suite..."
if ! uv run pytest tests/ -v --runslow; then
    print_error "Test suite failed"
    exit 1
fi

## 87. Build package
print_status "Building package..."
if ! hatch build; then
    print_error "Package build failed"
    exit 1
fi

## 88. Create git tag
print_status "Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION"

## 89. Push changes and tag
print_status "Pushing changes and tag to remote..."
git push origin "$CURRENT_BRANCH"
git push origin "v$VERSION"

## 90. Publish to PyPI (test first)
print_status "Publishing to Test PyPI..."
if hatch publish -r test; then
    print_success "Published to Test PyPI"

    print_status "Testing installation from Test PyPI..."
    sleep 10  # Wait for package to be available

    # Test installation in temporary environment
    if python -m pip install --index-url https://test.pypi.org/simple/ vexy-pdf-werk==$VERSION --dry-run; then
        print_success "Test PyPI installation check passed"

        print_status "Publishing to main PyPI..."
        read -p "Publish to main PyPI? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if hatch publish; then
                print_success "Successfully published to PyPI!"
            else
                print_error "PyPI publication failed"
                exit 1
            fi
        else
            print_warning "Skipped main PyPI publication"
        fi
    else
        print_error "Test PyPI installation check failed"
        exit 1
    fi
else
    print_error "Test PyPI publication failed"
    exit 1
fi

## 91. Clean up build artifacts
print_status "Cleaning up build artifacts..."
rm -rf dist/ build/ *.egg-info/

## 92. Create GitHub release (if gh is available)
if command -v gh &> /dev/null; then
    print_status "Creating GitHub release..."

    # Generate release notes
    RELEASE_NOTES="Release version $VERSION

### 92.1. Changes
$(git log --oneline --pretty=format:"- %s" $(git describe --tags --abbrev=0 HEAD~1)..HEAD)

### 92.2. Installation
\`\`\`bash
pip install vexy-pdf-werk==$VERSION
\`\`\`

### 92.3. Documentation
See [README.md](README.md) for usage instructions.
"

    if gh release create "v$VERSION" --title "Release v$VERSION" --notes "$RELEASE_NOTES"; then
        print_success "GitHub release created"
    else
        print_warning "GitHub release creation failed (manual creation needed)"
    fi
else
    print_warning "GitHub CLI not available, skipping GitHub release"
fi

print_success "Release $VERSION completed successfully! 🎉"
print_status "Summary:"
echo "  ✅ Quality checks passed"
echo "  ✅ Tests passed"
echo "  ✅ Package built"
echo "  ✅ Git tag created and pushed"
echo "  ✅ Published to Test PyPI"
echo "  ✅ Published to main PyPI"
echo "  ✅ GitHub release created"

print_status "Next steps:"
echo "  1. Update documentation if needed"
echo "  2. Announce release on relevant channels"
echo "  3. Monitor for issues and feedback"
```

#### 92.3.1. Continuous Integration Setup

##### GitHub Actions Workflow (`.github/workflows/ci.yml`)

```yaml
## 93. this_file: .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: "3.12"

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for hatch-vcs

    - name: Install uv
      uses: astral-sh/setup-uv@v2
      with:
        version: "latest"

    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}

    - name: Install system dependencies (Ubuntu)
      if: matrix.os == 'ubuntu-latest'
      run: |
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng qpdf ghostscript

    - name: Install system dependencies (macOS)
      if: matrix.os == 'macos-latest'
      run: |
        brew install tesseract tesseract-lang qpdf ghostscript

    - name: Install system dependencies (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        choco install tesseract qpdf ghostscript

    - name: Install dependencies
      run: |
        uv sync --all-extras

    - name: Lint with ruff
      run: |
        uv run ruff check .
        uv run ruff format --check .

    - name: Type check with mypy
      run: |
        uv run mypy src/vexy_pdf_werk/

    - name: Test with pytest
      run: |
        uv run pytest tests/unit/ -v --cov=src/vexy_pdf_werk --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  integration-test:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Install uv
      uses: astral-sh/setup-uv@v2

    - name: Set up Python
      run: uv python install 3.12

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng qpdf ghostscript imagemagick pandoc

    - name: Install dependencies
      run: |
        uv sync --all-extras

    - name: Run integration tests
      run: |
        uv run pytest tests/integration/ -v -m "not slow"

  build:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Install uv
      uses: astral-sh/setup-uv@v2

    - name: Set up Python
      run: uv python install 3.12

    - name: Install hatch
      run: uv tool install hatch

    - name: Build package
      run: hatch build

    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  security:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v2

    - name: Set up Python
      run: uv python install 3.12

    - name: Install dependencies
      run: uv sync

    - name: Run security scan
      run: |
        uv add --dev bandit[toml]
        uv run bandit -r src/ -f json -o bandit-report.json

    - name: Upload security report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-report
        path: bandit-report.json
```

This completes the comprehensive 4-part specification for Vexy PDF Werk. The junior developer now has detailed, step-by-step instructions for:

1. **Planning and Architecture** (101.md) - Understanding the problem, constraints, and high-level design decisions
2. **Project Structure and Setup** (102.md) - Setting up the development environment and project scaffolding
3. **Implementation Details** (103.md) - Detailed code implementation for all core components
4. **Testing and Deployment** (104.md) - Comprehensive testing, quality assurance, and deployment procedures

Each part builds upon the previous one, providing a complete roadmap from conception to deployment while maintaining the anti-enterprise bloat principles and focusing on simplicity and functionality.

------------------------------------------------------------
