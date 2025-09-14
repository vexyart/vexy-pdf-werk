# Quick Start

The fastest way to get started with Vexy PDF Werk is to use the `vpw` command-line tool.

## Process a PDF

To process a PDF file with the default settings, simply run:

```bash
vpw process my_document.pdf
```

This will create a directory named `output/my_document` containing the following files:

-   `my_document_enhanced.pdf`: A PDF/A version of your document with an OCR text layer.
-   A series of Markdown files, one for each page of your document.
-   `my_document.epub`: An ePub version of your document.
-   `metadata.yaml`: A file containing bibliographic and processing metadata.

## Customize the Output

You can easily customize the output by providing additional options:

```bash
# Specify a different output directory and only generate Markdown and ePub files
vpw process my_document.pdf --output_dir ./my_docs --formats "markdown,epub"
```
