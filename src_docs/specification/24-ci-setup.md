#### 92.3.1. Continuous Integration Setup

##### GitHub Actions Workflow (`.github/workflows/ci.yml`)

```yaml
## 93. this_file: .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: "3.12"

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for hatch-vcs

    - name: Install uv
      uses: astral-sh/setup-uv@v2
      with:
        version: "latest"

    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}

    - name: Install system dependencies (Ubuntu)
      if: matrix.os == 'ubuntu-latest'
      run: |
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng qpdf ghostscript

    - name: Install system dependencies (macOS)
      if: matrix.os == 'macos-latest'
      run: |
        brew install tesseract tesseract-lang qpdf ghostscript

    - name: Install system dependencies (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        choco install tesseract qpdf ghostscript

    - name: Install dependencies
      run: |
        uv sync --all-extras

    - name: Lint with ruff
      run: |
        uv run ruff check .
        uv run ruff format --check .

    - name: Type check with mypy
      run: |
        uv run mypy src/vexy_pdf_werk/

    - name: Test with pytest
      run: |
        uv run pytest tests/unit/ -v --cov=src/vexy_pdf_werk --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  integration-test:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Install uv
      uses: astral-sh/setup-uv@v2

    - name: Set up Python
      run: uv python install 3.12

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng qpdf ghostscript imagemagick pandoc

    - name: Install dependencies
      run: |
        uv sync --all-extras

    - name: Run integration tests
      run: |
        uv run pytest tests/integration/ -v -m "not slow"

  build:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Install uv
      uses: astral-sh/setup-uv@v2

    - name: Set up Python
      run: uv python install 3.12

    - name: Install hatch
      run: uv tool install hatch

    - name: Build package
      run: hatch build

    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  security:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v2

    - name: Set up Python
      run: uv python install 3.12

    - name: Install dependencies
      run: uv sync

    - name: Run security scan
      run: |
        uv add --dev bandit[toml]
        uv run bandit -r src/ -f json -o bandit-report.json

    - name: Upload security report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-report
        path: bandit-report.json
```
