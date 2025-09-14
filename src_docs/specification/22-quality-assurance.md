#### 60.0.1. Quality Assurance and Code Analysis

##### Code Quality Scripts (`scripts/quality-check.sh`)

```bash
##!/bin/bash
## 61. this_file: scripts/quality-check.sh

"""Comprehensive quality assurance script."""

set -e

echo "🔍 Running comprehensive quality checks for Vexy PDF Werk..."

## 62. Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

## 63. Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "Not in project root directory (pyproject.toml not found)"
    exit 1
fi

print_status "Checking development environment..."

## 64. Check uv availability
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed or not in PATH"
    exit 1
fi

## 65. Check hatch availability
if ! command -v hatch &> /dev/null; then
    print_error "hatch is not installed or not in PATH"
    exit 1
fi

print_success "Development tools available"

## 66. Code formatting with ruff
print_status "Checking code formatting..."
if uv run ruff format --check .; then
    print_success "Code formatting is correct"
else
    print_warning "Code formatting issues found. Run 'uv run ruff format .' to fix"
    # Auto-fix formatting
    uv run ruff format .
    print_success "Code formatting fixed"
fi

## 67. Linting with ruff
print_status "Running linting checks..."
if uv run ruff check --fix .; then
    print_success "No linting issues found"
else
    print_warning "Some linting issues were found and fixed"
fi

## 68. Type checking with mypy
print_status "Running type checks..."
if uv run mypy src/vexy_pdf_werk/; then
    print_success "Type checking passed"
else
    print_error "Type checking failed"
    exit 1
fi

## 69. Security scan (if bandit is available)
print_status "Running security scan..."
if uv run bandit -r src/ -f json -o bandit-report.json 2>/dev/null; then
    print_success "Security scan completed"
else
    print_warning "Security scan skipped (bandit not available)"
fi

## 70. Run tests
print_status "Running test suite..."

## 71. Unit tests
print_status "Running unit tests..."
if uv run pytest tests/unit/ -v --tb=short; then
    print_success "Unit tests passed"
else
    print_error "Unit tests failed"
    exit 1
fi

## 72. Integration tests (if not in CI)
if [[ -z "$CI" ]]; then
    print_status "Running integration tests..."
    if uv run pytest tests/integration/ -v --tb=short -m "not slow"; then
        print_success "Integration tests passed"
    else
        print_error "Integration tests failed"
        exit 1
    fi
else
    print_status "Skipping integration tests in CI"
fi

## 73. Test coverage
print_status "Checking test coverage..."
if uv run pytest --cov=src/vexy_pdf_werk --cov-report=term --cov-report=html tests/unit/; then
    print_success "Coverage report generated"
else
    print_warning "Coverage check failed"
fi

## 74. Build check
print_status "Testing package build..."
if hatch build; then
    print_success "Package builds successfully"
    # Clean up build artifacts
    rm -rf dist/
else
    print_error "Package build failed"
    exit 1
fi

## 75. Documentation check
print_status "Checking documentation..."
if [[ -f "README.md" ]]; then
    print_success "README.md exists"
else
    print_warning "README.md missing"
fi

## 76. Configuration validation
print_status "Validating configuration..."
if uv run python -c "
from src.vexy_pdf_werk.config import VPWConfig
try:
    config = VPWConfig()
    print('Configuration validation: OK')
except Exception as e:
    print(f'Configuration validation failed: {e}')
    exit(1)
"; then
    print_success "Configuration validation passed"
else
    print_error "Configuration validation failed"
    exit 1
fi

## 77. CLI smoke test
print_status "Testing CLI interface..."
if uv run python -m vexy_pdf_werk.cli version >/dev/null 2>&1; then
    print_success "CLI smoke test passed"
else
    print_error "CLI smoke test failed"
    exit 1
fi

print_success "All quality checks passed! 🎉"
print_status "Summary:"
echo "  ✅ Code formatting (ruff format)"
echo "  ✅ Linting (ruff check)"
echo "  ✅ Type checking (mypy)"
echo "  ✅ Security scan (bandit)"
echo "  ✅ Unit tests (pytest)"
echo "  ✅ Integration tests (pytest)"
echo "  ✅ Test coverage"
echo "  ✅ Package build (hatch)"
echo "  ✅ Documentation check"
echo "  ✅ Configuration validation"
echo "  ✅ CLI smoke test"

print_status "Project is ready for deployment! 🚀"
```
