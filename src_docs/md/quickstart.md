# Quick start

This page converts one PDF into all four formats and shows what each output file contains. The example uses `multicolumn.pdf`, a three-page two-column document from the repository's `examples/data/` folder. Any text-based PDF works the same way.

## Before you start

- VPW is installed and `vpw version` works. See [Installation](installation.md).
- `ocrmypdf` and `qpdf` are on your `PATH`.

## Convert a PDF

1. Run `vpw process` on the file:

    ```bash
    vpw process multicolumn.pdf
    ```

    VPW prints the input path, the output directory and the requested formats, then shows one progress line per step. The run ends with a summary:

    ```text
    Processing completed in 0.3s
    Formats created: pdfa, markdown, epub, yaml
    Output directory: output/multicolumn
    0
    ```

    The final `0` is the command's result: at least one format was produced. See [Command line](cli.md#result-and-exit-status).

2. List the output directory:

    ```bash
    ls output/multicolumn
    ```

    ```text
    0--two-column-document-with-lorem-ipsum.md
    1--lacus-vel-est-curabitur-consectetuer.md
    2--table-1-eu-countries-information.md
    metadata.yaml
    multicolumn.epub
    multicolumn_enhanced.pdf
    ```

When you give no `--output_dir`, VPW writes to `./output/<stem>/`, where `<stem>` is the PDF file name without `.pdf`. It creates the directory if needed.

## Read the results

Each Markdown file holds one page. The number before `--` is the page index, starting at `0`. The text after `--` is a slug made from the first line on the page that is longer than 10 characters. The file starts with YAML front matter:

```markdown
---
page: 1
total_pages: 3
title: "Two-Column Document with Lorem Ipsum"
slug: "two-column-document-with-lorem-ipsum"
---

Two-Column Document with Lorem Ipsum
Your Name
January 3, 2024
Abstract
...
```

`metadata.yaml` describes the source file and the run:

```yaml
document:
  source_file: multicolumn.pdf
  source_size_bytes: 78657
  processed_at: '2026-10-12T20:39:26.512117+00:00'
  processing_time_seconds: 0.22
pdf_info:
  pages: 3
  has_text: true
  is_scanned: false
  has_images: false
  creation_date: D:20240103093826+01'00'
processing:
  formats_generated:
  - pdfa
  - markdown
  - epub
  markdown_pages: 3
content:
  estimated_word_count: 1061
  first_page_preview: Two-Column Document with Lorem Ipsum Your Name January 3, 2024
    Abstract This is a sample document with two columns ﬁlled
```

`formats_generated` lists the formats finished before the metadata step, so it never includes `yaml` itself.

`multicolumn.epub` has one chapter per Markdown file. `multicolumn_enhanced.pdf` is the processed PDF. For this file no OCR ran, so it is a linearised copy of the original. See [Output formats](output-formats.md#enhanced-pdf-pdfa) for when VPW applies OCR and PDF/A.

## Choose formats and a folder

Ask for a subset of formats with `--formats` and a different folder with `--output_dir`:

```bash
vpw process multicolumn.pdf --formats markdown,yaml --output_dir ./notes
```

This writes only the three Markdown files and `metadata.yaml` into `./notes`.

If you ask for `epub` without `markdown`, VPW still converts to Markdown, because the ePub is built from it. The Markdown files are written to the output folder in that case too.

## Next steps

- See every flag in [Command line](cli.md).
- Switch the Markdown backend or OCR language in [Configuration](configuration.md).
- Call the converters from Python in [Python API](python-api.md).
