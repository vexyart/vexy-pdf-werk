# Python API Usage

While the primary way to use Vexy PDF Werk is through its command-line interface, it can also be used as a Python library.

**Note:** The Python API is currently considered a legacy interface. For full functionality, we recommend using the CLI.

## Basic Processing

The `process_data` function is the main entry point for the legacy API.

```python
import vexy_pdf_werk

# Create a configuration object
config = vexy_pdf_werk.Config(name="default", value="process")

# Process a list of data (e.g., file paths)
# Note: The legacy API does not have a direct PDF processing function.
# The CLI is the recommended way to process PDFs.
data = ["document.pdf"]
result = vexy_pdf_werk.process_data(data, config=config)

print(result)
```

## Future API

A more complete Python API is planned for future versions, which will provide direct access to the core components like the `PDFProcessor` and `MarkdownGenerator`.
