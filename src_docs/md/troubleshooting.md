# Troubleshooting

VPW logs every step at the `DEBUG` level to standard error, so most runs already show where a problem started. Add `--verbose` to also print a Python traceback when the run fails:

```bash
vpw process document.pdf --verbose
```

## `Required tool 'ocrmypdf' not found in PATH`

```text
Initialization Failed - RuntimeError:
  Required tool 'ocrmypdf' not found in PATH. Please install it.
```

**Cause:** VPW checks for `ocrmypdf` and `qpdf` at the start of every run, even when you ask only for `markdown` or `yaml`.

**Fix:**

1. Install `ocrmypdf`, for example with `uv tool install ocrmypdf` or `brew install ocrmypdf`.
2. Check that the shell finds it: `ocrmypdf --version`.
3. Run `vpw process` again.

The same message with `'qpdf'` means `qpdf` is missing. Install it with your system package manager. See [Installation](installation.md#install-the-external-tools).

## `Error: File must have .pdf extension`

VPW checks the file name, not the content. Rename the file so it ends in `.pdf` (any letter case).

Other messages from the input check:

| Message | Meaning |
|---|---|
| `PDF file not found: ...` | The path does not exist. Check the spelling and the current folder. |
| `Path is not a file: ...` | The path is a folder. Pass one PDF file. For many files, use a shell loop. |
| `PDF file is empty: ...` | The file has 0 bytes. |
| `PDF file is password protected: ...` | Remove the password first, for example with `qpdf --decrypt --password=... in.pdf out.pdf`. |
| `PDF structure error: ...` | `pikepdf` could not parse the file. Try `qpdf --check` on it, or repair it with `qpdf in.pdf out.pdf`. |
| `PDF file has no pages: ...` | The PDF opens but contains no pages. |

## The enhanced PDF has no text layer

**Cause:** VPW ran OCR only if it classed the PDF as scanned, and that check rarely triggers. Without OCR, `<stem>_enhanced.pdf` is just a linearised copy.

**Fix:** set `force_ocr = true` in the `[processing]` section of your config file, or in a separate file you pass with `--config_file`:

```toml
[processing]
force_ocr = true
ocr_language = "eng"
```

Then run `vpw process scan.pdf --formats pdfa`.

## `PDF enhancement failed: OCR processing failed: ...`

The text after the colon is `ocrmypdf`'s own error output. Common causes:

- The language data for `ocr_language` is not installed. Install the Tesseract language pack, for example `tesseract-ocr-deu` on Debian or `tesseract-lang` on macOS.
- Ghostscript is missing, so PDF/A output cannot be written. Install `ghostscript`.

The other formats are still produced after this error.

## The Markdown pages are empty or say "appears to be empty"

```text
[Page 3 appears to be empty or contains only images]
```

**Cause:** the `basic` backend reads only the existing text layer. A scanned page has none.

**Fix:** either install an optional backend that does its own layout and OCR analysis, such as `marker-pdf` or `docling`, or create a text layer first:

1. Run `vpw process scan.pdf --formats pdfa` with `force_ocr = true`.
2. Run `vpw process output/scan/scan_enhanced.pdf --formats markdown`.

## My chosen backend was not used

If `markdown_backend` is `"marker"`, `"docling"` or `"markitdown"` and the package is not importable, or the conversion raises an error, VPW uses `basic` without a message. Check that the package is installed in the same environment as VPW:

```bash
python -c "import marker; import docling; import markitdown"
```

For a uv tool install, reinstall with the package: `uv tool install vexy-pdf-werk --with marker-pdf`.

## `Invalid output format`

```text
Error: Invalid output format: md. Available formats: pdfa, markdown, epub, yaml
```

Use the exact keys `pdfa`, `markdown`, `epub` and `yaml`, separated by commas without spaces, or quote the list: `--formats "markdown, yaml"`.

## `Configuration Error` or `Unexpected Error - ValidationError`

A value in `config.toml` has the wrong type, or the file is not valid TOML.

1. Run `vpw config --show` to see the path of the file.
2. Fix the value, or move the file away and run `vpw config --init` to write a fresh default file.

## The banner shows `<bound method ...>`

`vpw process` prints a line like `Vexy PDF Werk v<bound method VexyPDFWerk.version ...>` instead of the version number. This is a known cosmetic bug in the banner and does not affect processing. Use `vpw version` to see the version.

## Reporting a bug

Open an issue at [github.com/vexyart/vexy-pdf-werk/issues](https://github.com/vexyart/vexy-pdf-werk/issues). Include the command you ran, the output of `vpw version`, and the full output of the run with `--verbose`.
