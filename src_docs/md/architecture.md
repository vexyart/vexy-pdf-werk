# Architecture

VPW is a single pipeline. The CLI checks the input, then calls one processor per output format, in a fixed order, inside one `asyncio` event loop. External tools run as subprocesses, and the synchronous PDF libraries run in a thread pool.

## Data flow

```text
                  ┌───────────────────────┐
 report.pdf ───▶  │ validate_pdf_file()   │  pikepdf: exists, .pdf, non-empty, pages > 0
                  └──────────┬────────────┘
                             │
          ┌──────────────────┼────────────────────────────────────┐
          ▼                  ▼                                    │
  PDFProcessor        PDFProcessor.analyze_pdf()                  │
  .create_better_pdf()  → PDFInfo (pages, title, author, ...)     │
   ocrmypdf (optional)       │                                    │
   qpdf --linearize          ▼                                    │
   → <stem>_enhanced.pdf  MarkdownGenerator.generate_markdown()   │
                            BasicConverter | MarkerConverter |    │
                            DoclingConverter | MarkItDownConverter│
                            → MarkdownResult + N--slug.md files   │
                             │                                    │
                             ▼                                    ▼
                       EpubCreator.create_epub()        MetadataExtractor
                         → <stem>.epub                    → metadata.yaml
```

Each step returns a result object with a `success` flag instead of raising, so the CLI can report a failed step and go on with the next one.

## Modules

| Module | Main names | Role |
|---|---|---|
| `vexy_pdf_werk.cli` | `VexyPDFWerk`, `main` | Fire CLI: `process`, `config`, `version`. Runs the pipeline and prints progress with Rich. |
| `vexy_pdf_werk.config` | `VPWConfig`, `ProcessingConfig`, `ConversionConfig`, `AIConfig`, `OutputConfig`, `load_config` | Pydantic settings models, TOML loading and saving, `platformdirs` paths. |
| `vexy_pdf_werk.core.pdf_processor` | `PDFProcessor`, `PDFInfo`, `ProcessingResult` | PDF analysis with `pikepdf`; OCR with `ocrmypdf`; final rewrite with `qpdf`. |
| `vexy_pdf_werk.core.markdown_converter` | `MarkdownGenerator`, `MarkdownConverter`, `BasicConverter`, `MarkerConverter`, `DoclingConverter`, `MarkItDownConverter`, `MarkdownResult`, `MarkdownPage` | Backend selection, text extraction, page splitting, Markdown file writing. |
| `vexy_pdf_werk.core.epub_creator` | `EpubCreator`, `EpubCreationResult` | ePub assembly with `ebooklib`. |
| `vexy_pdf_werk.core.metadata_extractor` | `MetadataExtractor`, `DocumentMetadata` | Builds and writes `metadata.yaml`. |
| `vexy_pdf_werk.core.qdf_processor` | `QDFProcessor` | Converts a page to qpdf's QDF/JSON form and applies text diffs. Used only by the experimental AI structure step. |
| `vexy_pdf_werk.integrations.ai_services` | `AIServiceFactory`, `ClaudeCLIService`, `GeminiCLIService` | Wrappers that call the `claude` and `gemini` command-line tools. Experimental. |
| `vexy_pdf_werk.utils.validation` | `validate_pdf_file`, `validate_output_directory`, `validate_formats` | Input checks shared by the CLI and processors. |
| `vexy_pdf_werk.utils.slug_utils` | `generate_page_slug`, `sanitize_file_slug` | File-name slugs from page text (`unicode-slugify`, `pathvalidate`). |
| `vexy_pdf_werk.utils.file_utils` | `find_tool_path`, `ensure_directory`, `safe_copy_file`, `generate_output_filename`, `cleanup_temp_files` | Small file-system helpers. |
| `vexy_pdf_werk.vexy_pdf_werk` | `Config`, `process_data`, `main` | Legacy placeholder API, re-exported from the package root. |
| `vexy_pdf_werk.simple_cli`, `vexy_pdf_werk.simple_config` | `SimplePDFConverter`, `SimpleConfig` | A reduced CLI and config. They have no installed command. |

## Backend selection

`MarkdownGenerator._create_converter()` maps `conversion.markdown_backend` to a converter class. For `"auto"`, it builds each optional converter in turn and keeps the first whose `__init__` managed to import its library. Each optional converter also catches errors during conversion and returns the `BasicConverter` result instead. This makes the Markdown step hard to break, but it also means a misconfigured backend fails silently. Run with `--verbose` and look at the number and shape of the pages to see which backend ran.

The optional backends return one document-wide Markdown string. VPW splits it at headings to keep the "one `MarkdownPage` per file" interface. Only `BasicConverter` maps files to PDF pages one to one.

## Concurrency

- `ocrmypdf` and `qpdf` run through `asyncio.create_subprocess_exec`, and their `stderr` becomes the error message on failure.
- PyPDF reading, Marker, Docling and MarkItDown run in a `ThreadPoolExecutor` through `loop.run_in_executor`.
- Markdown files are written with `aiofiles`.

The steps themselves run one after another, because each later step needs the result of an earlier one.

## External tools

| Tool | Found by | Used for |
|---|---|---|
| `ocrmypdf` | `PATH` lookup when `PDFProcessor` is created; missing tool raises `RuntimeError` | OCR and PDF/A-2 output |
| `qpdf` | `PATH` lookup when `PDFProcessor` is created; missing tool raises `RuntimeError` | Linearisation; QDF/JSON in the AI step |
| `tesseract`, Ghostscript | By `ocrmypdf` | OCR engine; PDF/A rendering |
| `claude`, `gemini` | Called by name in the AI step | Experimental AI services |

Because `PDFProcessor` is created at the start of every `vpw process` run, `ocrmypdf` and `qpdf` must be installed even when you request no `pdfa` output.

## Logging

VPW logs with `loguru` to `stderr`. Loguru's default sink logs at the `DEBUG` level, so every run prints debug messages. `--verbose` re-adds the sink at the same level and makes the CLI print a traceback when a run fails. The legacy module `vexy_pdf_werk.vexy_pdf_werk` also configures the standard `logging` module at `INFO` on import, so some libraries, such as `pikepdf`, print `INFO` lines.
