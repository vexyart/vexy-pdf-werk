#!/bin/bash

set -e

hatch clean

echo "Building Vexy PDF Werk..."

# Build the package
hatch build

echo "Building documentation..."

# Install documentation dependencies
uv pip install mkdocs mkdocs-material

# Build the documentation
mkdocs build

gitnextver .

