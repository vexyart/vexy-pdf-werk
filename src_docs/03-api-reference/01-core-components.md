# Core Components

This section describes the core components of the Vexy PDF Werk package.

## `PDFProcessor`

The `PDFProcessor` class is the main engine for PDF processing. It handles:

-   Analyzing PDF structure and content.
-   Applying OCR to scanned documents using `ocrmypdf`.
-   Converting PDFs to the PDF/A format using `qpdf`.
-   Coordinating with the `QDFProcessor` and `AIService` for advanced AI-powered structure enhancement.

## `MarkdownGenerator`

The `MarkdownGenerator` class is responsible for converting PDFs to Markdown. It supports multiple backends:

-   **`BasicConverter`**: A fallback converter that uses `pypdf` for basic text extraction.
-   **`MarkerConverter`**: An optional backend that uses the `marker-pdf` library for high-fidelity conversion.
-   **`MarkItDownConverter`**: An optional backend that uses the `markitdown` library.

## `EpubCreator`

The `EpubCreator` class generates an ePub file from the Markdown content produced by the `MarkdownGenerator`.

## `MetadataExtractor`

The `MetadataExtractor` class extracts comprehensive metadata from the PDF and the processing results, and saves it to a `metadata.yaml` file.

## `QDFProcessor`

The `QDFProcessor` class is a new component that handles the conversion of PDF pages to and from the QDF/JSON format. This is used for the advanced AI-powered structure enhancement feature.
