# Command-Line Interface (CLI)

The primary way to use Vexy PDF Werk is through its command-line interface, `vpw`.

## `vpw process`

Processes a PDF file through the complete VPW pipeline.

**Usage:**

```bash
vpw process [OPTIONS] <pdf_path>
```

**Arguments:**

-   `<pdf_path>`: Path to the input PDF file.

**Options:**

-   `--output_dir`: Output directory (default: `./output/<pdf_name>`).
-   `--formats`: Comma-separated list of output formats (default: `pdfa,markdown,epub,yaml`).
-   `--verbose`: Enable verbose logging.
-   `--config_file`: Path to a custom config file.

## `vpw config`

Manages the VPW configuration.

**Usage:**

```bash
vpw config [OPTIONS]
```

**Options:**

-   `--show`: Display the current configuration.
-   `--init`: Initialize a default configuration file.

## `vpw version`

Displays the version of Vexy PDF Werk.
