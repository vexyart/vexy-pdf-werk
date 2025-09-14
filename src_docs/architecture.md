# Architecture

Vexy PDF Werk follows a modular pipeline architecture, allowing for flexibility and extensibility.

## Data Flow Pipeline

The processing pipeline consists of the following stages:

```
Input PDF → PDF Analysis → OCR Enhancement → PDF/A Creation → Content Extraction → Format Generation → Output Files
                           ↓
                    Optional AI Enhancement
```

## Core Components

-   **`PDFProcessor`**: The heart of the application, responsible for analyzing, OCRing, and converting PDFs to the PDF/A format.
-   **`MarkdownGenerator`**: Converts the processed PDF into Markdown. It supports multiple backends, including a basic text extractor and more advanced options like `marker-pdf`.
-   **`EpubCreator`**: Generates an ePub file from the Markdown content.
-   **`MetadataExtractor`**: Extracts comprehensive metadata from the PDF and the processing results.
-   **`QDFProcessor`**: A new component for advanced AI-powered structure enhancement, which converts PDF pages to the QDF/JSON format for manipulation.
-   **`AIService`**: An abstraction for integrating with various AI services (like Claude and Gemini) for text correction and structure enhancement.
-   **`cli.py`**: The command-line interface, built with `fire`.
-   **`config.py`**: The configuration management system, using `pydantic` and `toml`.

## Technology Stack

-   **Build and Development**: `hatch`, `hatch-vcs`, `uv`, `ruff`
-   **Core PDF Processing**: `ocrmypdf`, `qpdf`, `pikepdf`
-   **Content Conversion**: `pypdf`, `marker-pdf` (optional), `markitdown` (optional)
-   **AI Integration**: `claude` and `gemini` CLI tools
