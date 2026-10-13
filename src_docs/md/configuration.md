# Configuration

VPW reads its settings from a TOML file and a few environment variables. Settings it does not find keep their built-in defaults, so you need a file only to change something.

## Where the file lives

VPW uses the user configuration folder that the `platformdirs` package returns for the application name `vexy-pdf-werk`:

| System | Default path |
|---|---|
| macOS | `~/Library/Application Support/vexy-pdf-werk/config.toml` |
| Linux | `~/.config/vexy-pdf-werk/config.toml` (or `$XDG_CONFIG_HOME/vexy-pdf-werk/config.toml`) |
| Windows | `config.toml` in the `platformdirs` user config folder under `%LOCALAPPDATA%` |

To print the exact path on your machine, run `vpw config --show`. The first line shows it.

To use a different file for one run, pass it to `vpw process`:

```bash
vpw process document.pdf --config_file ./my-config.toml
```

If the file you name does not exist, VPW uses the defaults without a warning.

## Create the file

1. Write a file with every default value:

    ```bash
    vpw config --init
    ```

    VPW prints `Created default configuration at:` and the path. If a file is already there, VPW leaves it unchanged.

2. Open the file in a text editor and change the values you need.

3. Check the result:

    ```bash
    vpw config --show
    ```

## Default file

`vpw config --init` writes this:

```toml
[processing]
ocr_language = "eng"
pdf_quality = "high"
force_ocr = false
deskew = true
rotate_pages = true

[conversion]
markdown_backend = "auto"
paginate_markdown = true
include_images = true
extract_tables = true

[ai]
enabled = false
provider = "claude"
correction_enabled = false
enhancement_enabled = false
structure_enhancement_enabled = false
max_tokens = 4000

[output]
formats = [ "pdfa", "markdown", "epub", "yaml",]
preserve_original = true
output_directory = "./output"
filename_template = "{stem}_{format}.{ext}"
```

The file is validated with Pydantic models. A value of the wrong type, such as `force_ocr = "maybe"`, stops the run with an error. Unknown keys are ignored.

## `[processing]` section

These settings control the `pdfa` step. They are passed to `ocrmypdf` when OCR runs.

| Key | Default | Effect |
|---|---|---|
| `ocr_language` | `"eng"` | Passed as `ocrmypdf --language`. Use Tesseract language codes, for example `"deu"` or `"eng+fra"`. The language data must be installed. |
| `pdf_quality` | `"high"` | `"high"` passes `--optimize 1` to `ocrmypdf`. Any other value passes `--optimize 0`. |
| `force_ocr` | `false` | `true` runs OCR on every page, replacing any existing text layer (`ocrmypdf --force-ocr`). |
| `deskew` | `true` | Adds `ocrmypdf --deskew`. |
| `rotate_pages` | `true` | Adds `ocrmypdf --rotate-pages`. |

OCR runs only when VPW classes the PDF as scanned or when `force_ocr = true`. See [Output formats](output-formats.md#enhanced-pdf-pdfa).

## `[conversion]` section

| Key | Default | Effect |
|---|---|---|
| `markdown_backend` | `"auto"` | Which converter makes the Markdown. One of `"auto"`, `"marker"`, `"docling"`, `"markitdown"`, `"basic"`. |
| `paginate_markdown` | `true` | `true` writes one file per page. `false` writes one file, `<stem>.md`. |
| `include_images` | `true` | Shown by `vpw config --show`. No converter reads it yet. |
| `extract_tables` | `true` | Not read by any converter yet. |

How `markdown_backend` is resolved:

- `"auto"` tries `marker`, then `docling`, then `markitdown`, and uses the first one whose package imports. If none imports, it uses `basic`.
- `"marker"`, `"docling"` or `"markitdown"` use that backend. If its package is missing, or the conversion raises an error, VPW falls back to `basic` without a message.
- `"basic"` always uses PyPDF.
- Any other value uses `basic`.

## `[ai]` section

The AI settings are experimental. In the current version they do not change any output:

- `correction_enabled = true` (with `enabled = true`) copies the PDF unchanged and logs `AI enhancement not yet implemented, skipping`.
- `structure_enhancement_enabled = true` (with `enabled = true`) sends each page's text to the `claude` or `gemini` command-line tool, if one is installed, but writes the original pages back.
- `enhancement_enabled` and `max_tokens` are not used by the pipeline.

`provider` accepts `"claude"` or `"gemini"`. Leave `enabled = false` unless you are working on this feature.

## `[output]` section

`vpw process` does not read this section. Its formats and output folder come from the `--formats` and `--output_dir` flags and their defaults. `vpw config --show` prints `formats`, `output_directory` and `preserve_original` from here. `filename_template` is not used.

## Top-level keys

| Key | Default | Effect |
|---|---|---|
| `tesseract_path` | not set | Stored on the processor, but not passed to `ocrmypdf`, which finds Tesseract on `PATH`. |
| `qpdf_path` | not set | Not used. VPW finds `qpdf` on `PATH`. |
| `pandoc_path` | not set | Not used. |

## Environment variables

| Variable | Effect |
|---|---|
| `TESSERACT_PATH` | Sets `tesseract_path`. Same limits as the key above. |
| `QPDF_PATH` | Sets `qpdf_path`, which is not used. |
| `ANTHROPIC_API_KEY`, `GOOGLE_AI_API_KEY`, `DATALAB_API_KEY` | Read into the `[ai]` section, but the AI settings model has no field for them, so they are discarded. |

!!! warning "API key variables replace the `[ai]` section"
    When any of `ANTHROPIC_API_KEY`, `GOOGLE_AI_API_KEY` or `DATALAB_API_KEY` is set, VPW builds a new `[ai]` section from the variables and drops the one in your file. Your `[ai]` values then fall back to defaults. This matters only if you use the experimental AI settings.
