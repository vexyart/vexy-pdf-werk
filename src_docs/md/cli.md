# Command line

The `vpw` command has three subcommands: `process`, `config` and `version`. It is built with [Python Fire](https://github.com/google/python-fire), so each flag can be written with an underscore or a hyphen (`--output_dir` or `--output-dir`) and has a one-letter short form.

You can also start the CLI as a module:

```bash
python -m vexy_pdf_werk process document.pdf
```

To see help for a subcommand, run it with `--help`:

```bash
vpw process --help
```

## `vpw process`

Converts one PDF file into the requested formats.

```text
vpw process PDF_PATH [--output_dir DIR] [--formats LIST] [--verbose] [--config_file FILE]
```

| Argument | Short | Default | Meaning |
|---|---|---|---|
| `PDF_PATH` | | (required) | Path to the input PDF file. |
| `--output_dir` | `-o` | `./output/<stem>` | Folder for all outputs. Created if missing. |
| `--formats` | `-f` | `pdfa,markdown,epub,yaml` | Comma-separated list of formats to produce. |
| `--verbose` | `-v` | off | Print a Python traceback when the run fails. Debug logging is on in every run. |
| `--config_file` | `-c` | the user config file | Path to a `config.toml` to use instead of the default one. |

### Formats

`--formats` accepts these keys, in any order and any letter case:

- `pdfa`: write `<stem>_enhanced.pdf`.
- `markdown`: write one Markdown file per page.
- `epub`: write `<stem>.epub`. Markdown is converted even if you did not ask for it.
- `yaml`: write `metadata.yaml`.

Duplicate keys are ignored. An unknown key stops the run before any work starts:

```text
Error: Invalid output format: html. Available formats: pdfa, markdown, epub, yaml
```

The steps always run in the order `pdfa`, `markdown`, `epub`, `yaml`, whatever order you list them in.

### What `process` checks first

Before the pipeline starts, `vpw process` rejects the input with `Error: ...` and the result `1` when:

- the file does not exist;
- the path is a folder;
- the name does not end in `.pdf`;
- the file is empty;
- `pikepdf` cannot open it, it is password-protected, or it has no pages;
- `--output_dir` exists and is a file.

### Result and exit status

`vpw process` returns a result code, and Fire prints it as the last line of output:

| Printed result | Meaning |
|---|---|
| `0` | At least one requested format was produced. |
| `1` | Invalid input, invalid format list, missing `ocrmypdf` or `qpdf`, or no format was produced. |

!!! warning "The shell exit status does not follow the result"
    In the current version, the process exits with status `0` even when the printed result is `1`. The exit status is non-zero only when an unexpected error reaches the top level (status `1`, for example an invalid `config.toml`) or when Fire rejects the command line (status `2`). In scripts, check the last output line or the files in the output folder instead of `$?`.

A step that fails prints `✗` and a reason, and the remaining steps still run. For example, if the `pdfa` step fails, VPW prints `Continuing with original PDF for other formats...` and goes on to Markdown.

### Examples

Convert to Markdown only, into a chosen folder:

```bash
vpw process paper.pdf --formats markdown --output_dir ./paper-md
```

Use a project-specific configuration file:

```bash
vpw process scan.pdf -c ./scan-config.toml
```

Get a traceback while you track down a failure:

```bash
vpw process broken.pdf --verbose
```

Convert every PDF in a folder (shell loop):

```bash
for f in pdfs/*.pdf; do
  vpw process "$f" --formats markdown,yaml
done
```

Each file gets its own `./output/<stem>/` folder.

## `vpw config`

Creates or shows the user configuration file.

```text
vpw config [--init] [--show]
```

| Flag | Short | Meaning |
|---|---|---|
| `--init` | `-i` | Write a `config.toml` with all default values, unless the file already exists. |
| `--show` | `-s` | Print the path of the config file and the main settings VPW will use. |

With neither flag, `vpw config` prints `Use --show to display config or --init to create default config`.

`vpw config --show` always reads the default user file. It has no `--config_file` flag. If the file does not exist, it shows the built-in defaults.

```bash
vpw config --init
vpw config --show
```

```text
Configuration loaded from: /Users/you/Library/Application Support/vexy-pdf-werk/config.toml

Current Configuration:
Processing:
  OCR Language: eng
  PDF Quality: high
  Force OCR: False
Conversion:
  Markdown Backend: auto
  Paginate Markdown: True
  Include Images: True
AI:
  Enabled: False
  Provider: claude
  Correction Enabled: False
Output:
  Formats: pdfa, markdown, epub, yaml
  Output Directory: ./output
  Preserve Original: True
```

The file location depends on the operating system. See [Configuration](configuration.md#where-the-file-lives).

## `vpw version`

Prints the installed version:

```bash
vpw version
```

```text
Vexy PDF Werk version 1.2.1
```
