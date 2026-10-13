# Installation

VPW needs three things: the Python package, two external command-line tools that every run uses, and, optionally, one or more advanced Markdown converters.

## Requirements

- Python 3.10 or newer.
- `ocrmypdf` on your `PATH`. **Every `vpw process` run needs it**, even when you ask only for `markdown` or `yaml`, because VPW locates the tool when it starts the pipeline.
- `qpdf` on your `PATH`. Every run needs it for the same reason.
- `tesseract`, with the language data for the documents you OCR. `ocrmypdf` calls it.
- Ghostscript (`gs`). `ocrmypdf` uses it to write PDF/A output.

The Python dependencies (`pikepdf`, `pypdf`, `ebooklib`, `pydantic`, `fire`, `rich`, `loguru` and others) install automatically with the package.

## Install the Python package

1. Install VPW from PyPI:

    ```bash
    uv tool install vexy-pdf-werk
    ```

    Or, with pip:

    ```bash
    python -m pip install vexy-pdf-werk
    ```

2. Check that the `vpw` command works:

    ```bash
    vpw version
    ```

    The command prints `Vexy PDF Werk version` followed by the installed version.

## Install the external tools

`ocrmypdf` is a Python application. You can install it with your system package manager or as a uv tool:

```bash
uv tool install ocrmypdf
```

Install the other tools with your system package manager.

=== "macOS"

    ```bash
    brew install ocrmypdf qpdf tesseract tesseract-lang ghostscript
    ```

=== "Ubuntu and Debian"

    ```bash
    sudo apt-get update
    sudo apt-get install ocrmypdf qpdf tesseract-ocr tesseract-ocr-eng ghostscript
    ```

=== "Windows"

    ```bash
    choco install qpdf tesseract ghostscript
    python -m pip install ocrmypdf
    ```

Check that VPW will find them:

```bash
ocrmypdf --version
qpdf --version
tesseract --version
```

!!! note "Tool paths"
    VPW looks up `ocrmypdf` and `qpdf` on `PATH` only. The `tesseract_path` setting and the `TESSERACT_PATH` environment variable are stored, but `ocrmypdf` still finds Tesseract on its own. See [Configuration](configuration.md).

## Optional Markdown converters

Without extra packages, VPW extracts text with PyPDF (the `basic` backend). Three other backends become available when you install their packages into the same environment as VPW:

| Backend | Package to install | Import VPW checks |
|---|---|---|
| `marker` | `marker-pdf` | `marker.converters.pdf.PdfConverter` |
| `docling` | `docling` | `docling.document_converter.DocumentConverter` |
| `markitdown` | `markitdown` | `markitdown.MarkItDown` |

To add a backend to a uv tool install:

```bash
uv tool install vexy-pdf-werk --with marker-pdf
```

To add it to a pip environment:

```bash
python -m pip install marker-pdf
```

!!! warning "No extras for converters"
    The package defines no `[all]` or `[epub]` extra that installs these converters. Install each one by name. `ebooklib`, which the ePub step needs, is already a core dependency.

With `markdown_backend = "auto"` (the default), VPW uses the first backend it can import, in this order: `marker`, `docling`, `markitdown`, `basic`. See [Configuration](configuration.md#conversion-section).

## Install from source

1. Clone the repository:

    ```bash
    git clone https://github.com/vexyart/vexy-pdf-werk
    cd vexy-pdf-werk
    ```

2. Create the environment and install the package with its test tools:

    ```bash
    uv sync --extra test
    ```

3. Run the command from the environment:

    ```bash
    uv run vpw version
    ```

The version number comes from the latest Git tag. `hatch-vcs` writes it to `src/vexy_pdf_werk/_version.py` when the package is built or installed. If that file is missing, `vexy_pdf_werk.__version__` falls back to `0.0.0+dev`.
