# this_file: CHANGELOG.md

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Created comprehensive 4-part development specification (spec/101.md - spec/104.md)
  - Part 1: Planning and Architecture - Complete technical architecture and design decisions
  - Part 2: Project Structure and Setup - Development environment and scaffolding setup
  - Part 3: Implementation Details - Full code implementation for core components
  - Part 4: Testing and Deployment - Testing strategy, quality assurance, and CI/CD
- Established detailed project roadmap in PLAN.md for quality and reliability improvements
- Created TODO.md with prioritized task list for infrastructure improvements
- Added CHANGELOG.md for version tracking and change documentation

### Technical Specifications
- Defined modern Python toolchain: hatch + hatch-vcs, uv, ruff, Fire
- Architected modular pipeline: PDF processor → Markdown generator → ePub creator → Metadata extractor
- Designed multi-backend conversion system (Marker, MarkItDown, Docling, basic fallback)
- Planned optional AI integration with Claude/Gemini CLI services
- Established comprehensive testing strategy with unit/integration/CI workflows
- Created packaging and deployment automation with PyPI publishing

### Documentation
- Comprehensive specification covering all aspects from planning to deployment
- Step-by-step instructions suitable for junior developers
- Complete code examples with type hints and error handling
- Quality assurance procedures and automated release workflows

## [0.1.0] - Initial Commit

### Added
- Initial project structure with modern Python packaging (pyproject.toml)
- Basic hatch configuration with hatch-vcs versioning
- Development tool configuration (ruff, mypy, pytest)
- Placeholder source structure in src/vexy_pdf_werk/
- External integrations directory structure
- Git repository initialization