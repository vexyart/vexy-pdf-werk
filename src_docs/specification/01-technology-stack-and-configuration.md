### 1.2.3. Technology Stack Decisions

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
