# Python API

The `vpw` command is a thin layer over a few classes that you can use directly. Most methods are `async`, so call them from an event loop, for example with `asyncio.run()`.

!!! note "Top-level names"
    `from vexy_pdf_werk import Config, process_data, main` gives you legacy placeholders kept for backward compatibility. `process_data()` only returns a dictionary that points you to `vpw process`. Import the classes below from their modules instead.

## Convert a PDF to Markdown

`MarkdownGenerator` picks a backend from a `ConversionConfig`, converts the PDF, and writes the Markdown files.

```python
import asyncio
from pathlib import Path

from vexy_pdf_werk.config import ConversionConfig
from vexy_pdf_werk.core.markdown_converter import MarkdownGenerator


async def main() -> None:
    generator = MarkdownGenerator(ConversionConfig(markdown_backend="basic"))
    result = await generator.generate_markdown(Path("report.pdf"), Path("out"))
    if not result.success:
        raise SystemExit(result.error)
    for page in result.pages:
        print(page.page_number, page.slug, page.title)


asyncio.run(main())
```

`generate_markdown(pdf_path, output_dir)` returns a `MarkdownResult`. When `success` is `True`, the files are already written to `output_dir`.

| `MarkdownResult` field | Type | Meaning |
|---|---|---|
| `success` | `bool` | `False` when the conversion raised an error. |
| `pages` | `list[MarkdownPage]` | Converted pages. Empty on failure. |
| `error` | `str` or `None` | Error message on failure. |
| `total_pages` | `int` | Number of pages converted. |
| `processing_time` | `float` | Seconds spent converting. |

| `MarkdownPage` field | Type | Meaning |
|---|---|---|
| `page_number` | `int` | 0-based index. |
| `content` | `str` | Markdown text, without front matter. |
| `title` | `str` or `None` | Title from the first line, if it qualifies. |
| `slug` | `str` or `None` | Slug used in the file name. |

To convert without writing files, call the converter directly:

```python
from vexy_pdf_werk.core.markdown_converter import BasicConverter

result = await BasicConverter(ConversionConfig()).convert_pdf(Path("report.pdf"))
```

The converter classes are `BasicConverter`, `MarkerConverter`, `DoclingConverter` and `MarkItDownConverter`. All take a `ConversionConfig` and implement `async convert_pdf(pdf_path) -> MarkdownResult`. The three optional ones fall back to `BasicConverter` when their package is missing.

## Analyse and enhance a PDF

`PDFProcessor` needs a full `VPWConfig`. Creating it raises `RuntimeError` if `ocrmypdf` or `qpdf` is not on `PATH`.

```python
from vexy_pdf_werk.config import load_config
from vexy_pdf_werk.core.pdf_processor import PDFProcessor


async def enhance() -> None:
    processor = PDFProcessor(load_config())

    info = await processor.analyze_pdf(Path("scan.pdf"))
    print(info.pages, info.has_text, info.is_scanned, info.title)

    result = await processor.create_better_pdf(Path("scan.pdf"), Path("out/scan_enhanced.pdf"))
    print(result.success, result.error)
```

- `analyze_pdf(pdf_path)` returns a `PDFInfo` with `path`, `pages`, `has_text`, `is_scanned`, `has_images`, `title`, `author` and `creation_date`. It raises `RuntimeError` if the file cannot be analysed.
- `create_better_pdf(pdf_path, output_path, progress=None, task_id=None)` returns a `ProcessingResult` with `success`, `output_path`, `pdf_info`, `error` and `processing_time`. It does not raise on tool failures; check `success`. The optional `progress` and `task_id` are a Rich `Progress` and task ID whose description it updates.

## Build an ePub

```python
from vexy_pdf_werk.core.epub_creator import EpubCreator

creator = EpubCreator(book_title="Annual report", author="Jane Doe")
epub_result = await creator.create_epub(result, Path("out/report.epub"), Path("report.pdf"))
```

`create_epub(markdown_result, output_path, source_pdf_path=None)` returns an `EpubCreationResult` with `success`, `output_path`, `error` and `processing_time`.

For non-async code, `create_epub_from_markdown(markdown_result, output_path, book_title=None, author=None, source_pdf_path=None)` in the same module wraps the call in `asyncio.run()`.

## Write metadata

`MetadataExtractor` is synchronous:

```python
from vexy_pdf_werk.core.metadata_extractor import MetadataExtractor

extractor = MetadataExtractor()
metadata = extractor.extract_metadata(
    Path("report.pdf"), info, markdown_result=result, formats_generated=["markdown"], processing_time=1.5
)
extractor.save_metadata_yaml(metadata, Path("out/metadata.yaml"))
```

`extract_metadata()` returns a `DocumentMetadata` dataclass. `save_metadata_yaml()` writes it in the grouped layout shown in [Output formats](output-formats.md#metadata-yaml).

## Load and save configuration

Functions in `vexy_pdf_werk.config`:

| Function | Purpose |
|---|---|
| `load_config(config_file=None)` | Read the TOML file (default: the user file) and environment variables into a `VPWConfig`. |
| `save_config(config, config_file=None)` | Write a `VPWConfig` as TOML, creating the folder. |
| `create_default_config()` | Write the defaults to the user file if it does not exist, and return them. |
| `get_config_dir()` / `get_config_file()` | Return the user config folder or file path. |

`VPWConfig` has the sections `processing` (`ProcessingConfig`), `conversion` (`ConversionConfig`), `ai` (`AIConfig`) and `output` (`OutputConfig`). They are Pydantic models, so you can build them in code:

```python
from vexy_pdf_werk.config import ProcessingConfig, VPWConfig

config = VPWConfig(processing=ProcessingConfig(force_ocr=True, ocr_language="deu"))
```

## Utility functions

| Function | Module | Purpose |
|---|---|---|
| `validate_pdf_file(path)` | `vexy_pdf_werk.utils.validation` | Raise `FileNotFoundError` or `ValueError` if the path is not a readable, non-empty PDF with pages. |
| `validate_formats(formats)` | `vexy_pdf_werk.utils.validation` | Lowercase, de-duplicate and check a list of format keys. |
| `generate_page_slug(content, max_length=50)` | `vexy_pdf_werk.utils.slug_utils` | Make a file-name slug from page text. |
| `find_tool_path(tool_name)` | `vexy_pdf_werk.utils.file_utils` | Return the full path of a command on `PATH`, or `None`. |
