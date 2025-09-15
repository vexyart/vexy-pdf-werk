#!/bin/bash
set -e
uv venv --clear
uv pip install -e .
uv run hatch clean
uv run mkdocs build -f mkdocs.yml -d docs
gitnextver .
uv run hatch build
