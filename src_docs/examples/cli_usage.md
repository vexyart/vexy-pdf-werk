# CLI Usage Examples

## Basic Processing

Process a PDF file and generate all default output formats (`pdfa`, `markdown`, `epub`, `yaml`):

```bash
vpw process my_document.pdf
```

## Specify Output Directory and Formats

Process a PDF file, save the output to a specific directory, and only generate Markdown and ePub files:

```bash
vpw process my_document.pdf --output_dir ./docs --formats "markdown,epub"
```

## Enable Verbose Logging

Process a PDF file with verbose logging enabled for debugging:

```bash
vpw process my_document.pdf --verbose
```

## Manage Configuration

Display the current configuration:

```bash
vpw config --show
```

Initialize a default configuration file:

```bash
vpw config --init
```
