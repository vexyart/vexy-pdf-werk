# Configuration

Vexy PDF Werk uses a `config.toml` file for configuration, which is located in the user's config directory (e.g., `~/.config/vexy-pdf-werk/config.toml`).

You can initialize a default configuration file by running `vpw config --init`.

The configuration is divided into the following sections:

## `[processing]`

-   `ocr_language`: The language to use for OCR (default: `eng`).
-   `pdf_quality`: The quality of the output PDF (default: `high`).
-   `force_ocr`: Whether to force OCR on all pages (default: `false`).
-   `deskew`: Whether to deskew pages (default: `true`).
-   `rotate_pages`: Whether to rotate pages (default: `true`).

## `[conversion]`

-   `markdown_backend`: The backend to use for Markdown conversion (default: `auto`).
-   `paginate_markdown`: Whether to create a separate Markdown file for each page (default: `true`).
-   `include_images`: Whether to include images in the Markdown output (default: `true`).
-   `extract_tables`: Whether to extract tables from the PDF (default: `true`).

## `[ai]`

-   `enabled`: Whether to enable AI features (default: `false`).
-   `provider`: The AI provider to use (default: `claude`).
-   `correction_enabled`: Whether to enable AI-powered text correction (default: `false`).
-   `enhancement_enabled`: Whether to enable AI-powered content enhancement (default: `false`).
-   `structure_enhancement_enabled`: Whether to enable AI-powered structure enhancement (default: `false`).
-   `max_tokens`: The maximum number of tokens to use for AI requests (default: `4000`).

## `[output]`

-   `formats`: A list of output formats to generate (default: `["pdfa", "markdown", "epub", "yaml"]`).
-   `preserve_original`: Whether to preserve the original PDF file (default: `true`).
-   `output_directory`: The directory to save the output files to (default: `./output`).
-   `filename_template`: A template for the output filenames (default: `{stem}_{format}.{ext}`).
