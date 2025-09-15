#!/bin/bash

set -e

hatch clean

echo "Building Vexy PDF Werk..."

# Build the package
hatch build

echo "Building documentation..."

# Install documentation dependencies
uv pip install mkdocs mkdocs-material

# Build the documentation explicitly from src_docs to docs with Material
mkdocs build -f mkdocs.yml -d docs

# Ensure GitHub Pages doesn't run Jekyll
touch docs/.nojekyll

gitnextver .
