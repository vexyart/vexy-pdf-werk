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
```
