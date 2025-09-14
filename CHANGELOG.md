# this_file: CHANGELOG.md

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Phase 1 Foundation Complete
- **Configuration System**: Dynamic config loading with TOML files, environment variables, and CLI args
  - Platform-aware config directory (`~/.config/vexy-pdf-werk/config.toml`)
  - Hierarchical configuration: CLI > env vars > config file > defaults
  - Pydantic-based validation and type safety
- **CLI Interface**: Fire-based command-line interface with rich console output
  - Commands: `process`, `config --show/--init`, `version`
  - Input validation and comprehensive error handling
  - Progress tracking with Rich progress bars
- **PDF Processing Foundation**: Async PDF analysis and processing workflow
  - PDF content analysis using pikepdf (pages, text, images, metadata)
  - External tool integration (ocrmypdf, qpdf, tesseract)
  - OCR and PDF/A conversion pipeline framework
- **Core Infrastructure**: Utility modules for file operations and validation
  - PDF validation with detailed error reporting
  - File operation utilities with proper error handling
  - Slug generation for organized output files
- **Development Toolchain**: Complete modern Python development setup
  - hatch + hatch-vcs for version management (working correctly)
  - uv for package management and virtual environments
  - ruff for linting and formatting, mypy for type checking
  - pytest for testing with proper source path configuration

### Technical Implementation
- Modular architecture with clear separation: `core/`, `integrations/`, `utils/`
- Async workflow support for external process management
- Comprehensive error handling with graceful fallbacks
- Type-safe configuration management with Pydantic models
- Rich console interface for better user experience

### Testing & Validation
- All development tools (ruff, mypy, pytest) running successfully
- CLI functionality validated with integration tests
- Configuration system tested with real config files
- Import structure and packaging verified

### Previous Work
- Created comprehensive 4-part development specification (SPEC.md)
- Established detailed project roadmap in PLAN.md
- Technical architecture and toolchain decisions documented

## [0.1.0] - Initial Commit

### Added
- Initial project structure with modern Python packaging (pyproject.toml)
- Basic hatch configuration with hatch-vcs versioning
- Development tool configuration (ruff, mypy, pytest)
- Placeholder source structure in src/vexy_pdf_werk/
- External integrations directory structure
- Git repository initialization
### Changed
- Configured pytest to include `src` on PYTHONPATH via pyproject, enabling `python -m pytest` to import package without env tweaks
- Updated PLAN.md, TODO.md, and WORK.md to reflect actual repo state and next steps

### Fixed
- Resolved local test import error (`ModuleNotFoundError: vexy_pdf_werk`) by adjusting pytest configuration

### Added
- Minimal CLI (MVP): `vexy_pdf_werk/cli.py` with `version` and `process` commands
- Console script entry `vpw` in `pyproject.toml`
