# Output formats

All outputs go into one folder: `--output_dir`, or `./output/<stem>/` by default. `<stem>` is the input file name without `.pdf`. Existing files with the same names are overwritten.

| Format key | File(s) |
|---|---|
| `pdfa` | `<stem>_enhanced.pdf` |
| `markdown` | `<N>--<slug>.md` per page, or `<stem>.md` |
| `epub` | `<stem>.epub` |
| `yaml` | `metadata.yaml` |

## Enhanced PDF (`pdfa`)

The `pdfa` step writes `<stem>_enhanced.pdf`. What that file is depends on whether OCR runs.

### When OCR runs

VPW first inspects up to the first three pages with `pikepdf`. It counts a page as having text when the page has a `/Contents` entry, and as having images when its resources contain an image XObject. It classes the document as scanned when it found images and fewer than half of the sampled pages had text.

OCR runs when the document is classed as scanned, or when `force_ocr = true` in the [configuration](configuration.md#processing-section). Because almost every PDF page has a `/Contents` entry, the scanned check rarely triggers. **For scanned documents, set `force_ocr = true`.**

### The two paths

1. **With OCR:** VPW runs `ocrmypdf` with `--output-type pdfa-2`, the OCR language, the optimisation level, `--deskew` and `--rotate-pages` (if enabled), and `--force-ocr` or `--skip-text`. It also passes the PDF's title and author if they are set. The result is PDF/A-2b with a searchable text layer. VPW then runs `qpdf --linearize --object-streams=generate` on it.
2. **Without OCR:** VPW runs only `qpdf --linearize --object-streams=generate` on the original. The output is a linearised ("fast web view") copy with compressed object streams. It is **not** converted to PDF/A.

If either tool fails, VPW prints `PDF enhancement failed:` with the tool's error message and continues with the other formats. The original PDF is never modified.

## Markdown (`markdown`)

### One file per page

With `paginate_markdown = true` (the default), VPW writes one file per page named `<N>--<slug>.md`:

- `<N>` is the page index, starting at `0`. It is zero-padded to the width of the last index: `0`–`9` for up to 10 pages, `00`–`99` for up to 100 pages, and so on.
- `<slug>` comes from the page text. VPW takes the first line longer than 10 characters, removes the characters `#`, `*`, `_`, `[`, `]`, `(`, `)` and the backtick, cuts it to at most 50 characters at a word boundary, and turns it into a lowercase hyphenated slug. A blank page gets `empty-page`. A slug shorter than 3 characters becomes `page-content`.

Each file starts with YAML front matter:

```markdown
---
page: 1
total_pages: 3
title: "Two-Column Document with Lorem Ipsum"
slug: "two-column-document-with-lorem-ipsum"
---

Two-Column Document with Lorem Ipsum
...
```

- `page` is the 1-based page number.
- `total_pages` is the number of Markdown pages written.
- `title` is the first non-empty line, if it is 6 to 99 characters long and contains a letter. Otherwise the key is left out.
- `slug` is the slug used in the file name.

### One combined file

With `paginate_markdown = false`, VPW writes `<stem>.md`. It starts with `# <stem>`, and each page follows under a `## Page <n>` heading, with `---` between pages. No front matter is written.

### What the `basic` backend produces

The `basic` backend extracts text with PyPDF, page by page, so file `0--…` always holds PDF page 1. It then:

- trims each line and keeps at most two blank lines in a row;
- collapses runs of three or more spaces to two;
- turns a line into a `## ` heading when more than 70 % of its words are upper case or non-alphabetic and the line is under 80 characters, or when it starts with a number followed by a capital letter (`1. Introduction`, `2 Methods`);
- writes `[Page N appears to be empty or contains only images]` for a page with no extractable text.

### What the other backends produce

`marker`, `docling` and `markitdown` convert the whole document to one Markdown text. VPW then splits that text at headings (`#` and `##` for Marker, `#` to `###` for Docling and MarkItDown). Each "page" is therefore a section, not a PDF page, and the number of Markdown files can differ from the PDF page count.

## ePub (`epub`)

The `epub` step builds `<stem>.epub` with `ebooklib` from the Markdown pages:

- one chapter per Markdown page, named `page_000.xhtml` or `page_000_<slug>.xhtml`;
- a table of contents with one entry per chapter, plus NCX and navigation files;
- the language set to `en` and a random UUID as the identifier.

The book title is the first page's `title` if there is one, otherwise the PDF's `/Title`, otherwise the file stem with `_` and `-` replaced by spaces and each word capitalised. The author is the PDF's `/Author`, or `VPW User` if it is not set.

The Markdown-to-HTML conversion is simple: lines starting with `#`, `##` or `###` become headings, other lines become `<p>` paragraphs, and blank lines become `<br/>`. Lists, emphasis, links and tables are not converted.

If the Markdown step failed, VPW prints `ePub generation skipped - markdown conversion required`.

## Metadata (`yaml`)

The `yaml` step writes `metadata.yaml` with four groups:

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

| Key | Source |
|---|---|
| `document.processed_at` | UTC time when the metadata was written, ISO 8601. |
| `document.processing_time_seconds` | Time from the start of the pipeline to the metadata step. |
| `pdf_info.*` | The `pikepdf` analysis described above. `title`, `author` and `creation_date` appear only when the PDF sets them. `creation_date` is the raw PDF date string. |
| `processing.formats_generated` | Formats finished before this step. `yaml` is never listed. |
| `processing.markdown_pages` | Number of Markdown pages, or `0` if Markdown was not made. |
| `content.estimated_word_count` | Whitespace-separated words longer than one character, skipping words that start with `#` and `---`. `0` without Markdown. |
| `content.first_page_preview` | Up to 200 characters from the first lines of the first page, skipping headings. Left out when there is no Markdown. |
