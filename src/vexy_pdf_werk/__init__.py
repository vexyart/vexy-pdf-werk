# this_file: src/vexy_pdf_werk/__init__.py

"""Vexy PDF Werk - Transform PDFs into high-quality, accessible formats.

A Python package for processing PDF documents using modern tools like qpdf,
OCRmyPDF, and optional AI-enhanced conversion to multiple formats including
PDF/A, Markdown, ePub, and structured metadata.
"""

# Import version from hatch-vcs generated file
try:
    from vexy_pdf_werk._version import __version__, __version_tuple__
except ImportError:
    # Fallback for development environment without git tags
    __version__ = "0.0.0+dev"
    __version_tuple__ = (0, 0, 0, "dev")

# Import main components from the main module
from vexy_pdf_werk.vexy_pdf_werk import Config, main, process_data

# Package metadata
__author__ = "Fontlab Ltd"
__email__ = "opensource@vexy.art"
__license__ = "MIT"

# Define what gets imported with "from vexy_pdf_werk import *"
__all__ = [
    "Config",
    "__author__",
    "__email__",
    "__license__",
    "__version__",
    "__version_tuple__",
    "main",
    "process_data",
]
