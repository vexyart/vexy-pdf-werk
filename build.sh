#!/bin/bash

set -e

uv venv --clear

uv pip install -e .

uv run hatch clean

uv run hatch build

uv run mkdocs build -f mkdocs.yml -d docs

gitnextver .

