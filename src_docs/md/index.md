# Vexy PDF Werk

Vexy PDF Werk (VPW) is a Python package and a command-line tool, `vpw`, that takes one PDF file and produces up to four outputs from it:

| Format key | Output | Made by |
|---|---|---|
| `pdfa` | `<stem>_enhanced.pdf`, an optimised copy of the PDF, OCR'd to PDF/A-2 when OCR runs | `ocrmypdf` and `qpdf` |
| `markdown` | One Markdown file per page (or one combined file), each with YAML front matter | PyPDF, or Marker, Docling or MarkItDown when installed |
| `epub` | `<stem>.epub`, one chapter per Markdown page | `ebooklib` |
| `yaml` | `metadata.yaml` with file, PDF and content facts | PyYAML |

## How a run works

You give `vpw process` a PDF. VPW checks that the file exists, ends in `.pdf`, is not empty, opens with `pikepdf`, and has at least one page. It then runs the steps for the formats you asked for, in this order:

1. `pdfa`: OCR the file with `ocrmypdf` if needed, then rewrite it with `qpdf --linearize`.
2. Read the PDF's page count, title, author and creation date.
3. `markdown`: extract text page by page and write Markdown files.
4. `epub`: build an ePub from the Markdown pages.
5. `yaml`: write `metadata.yaml`.

A failed step does not stop later steps. As its last line of output, the command prints `0` if at least one format was produced and `1` otherwise. See [Command line](cli.md#result-and-exit-status) for how this relates to the shell exit status.

## A short example

```bash
vpw process report.pdf --formats markdown,yaml
```

For a three-page `report.pdf`, this writes to `./output/report/`:

```text
output/report/
├── 0--first-meaningful-line-of-page-one.md
├── 1--first-meaningful-line-of-page-two.md
├── 2--first-meaningful-line-of-page-three.md
└── metadata.yaml
```

## Where to go next

- [Installation](installation.md): Python package, external tools, optional converters.
- [Quick start](quickstart.md): your first conversion, step by step.
- [Command line](cli.md): every `vpw` command and flag.
- [Configuration](configuration.md): the `config.toml` file and environment variables.
- [Output formats](output-formats.md): file names, front matter, ePub and YAML layout.
- [Python API](python-api.md): calling the converters from your own code.
- [Architecture](architecture.md): modules, classes and data flow.
- [Troubleshooting](troubleshooting.md): error messages and their fixes.
- [Contributing](contributing.md): development setup, tests, docs and releases.

## Project status

VPW is in beta (`Development Status :: 4 - Beta`). The AI options in the configuration are placeholders and do not change the output yet. See [Configuration](configuration.md#ai-section).

VPW is released under the MIT license. Source code: [github.com/vexyart/vexy-pdf-werk](https://github.com/vexyart/vexy-pdf-werk).
