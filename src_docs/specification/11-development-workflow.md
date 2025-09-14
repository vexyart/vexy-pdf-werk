#### 35.0.1. Development Workflow Setup

##### 1. Initialize Pre-commit Hooks

```bash
## 36. Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-toml, types-requests, types-PyYAML]
EOF

## 37. Install pre-commit hooks
uv run pre-commit install
```

##### 2. Create Development Scripts

```bash
## 38. Create development convenience scripts
mkdir -p scripts

cat > scripts/dev-setup.sh << 'EOF'
##!/bin/bash
## 39. Development environment setup script
set -e

echo "Setting up Vexy PDF Werk development environment..."

## 40. Ensure uv is available
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

## 41. Create virtual environment and install dependencies
echo "Installing dependencies..."
uv sync --all-extras

## 42. Install pre-commit hooks
echo "Setting up pre-commit hooks..."
uv run pre-commit install

## 43. Verify installation
echo "Verifying installation..."
uv run python -c "import vexy_pdf_werk; print('VPW imported successfully')"
uv run vpw version

echo "Development environment setup complete!"
EOF

chmod +x scripts/dev-setup.sh
```

##### 3. Verify Complete Setup

```bash
## 44. Run the development setup script
./scripts/dev-setup.sh

## 45. Run initial linting
uv run ruff check .
uv run ruff format .

## 46. Run initial tests (will be empty but should pass)
uv run pytest tests/ -v

## 47. Verify hatch can build the package
hatch build

## 48. Test CLI help output
uv run vpw --help
```
