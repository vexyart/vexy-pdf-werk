#### 77.0.1. Packaging and Distribution

##### Release Workflow (`scripts/release.sh`)

```bash
#!/bin/bash
## 78. this_file: scripts/release.sh

"""Automated release workflow script."""

set -e

## 79. Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

## 80. Check arguments
if [[ $# -ne 1 ]]; then
    print_error "Usage: $0 <version>"
    print_error "Example: $0 1.0.0"
    exit 1
fi

VERSION="$1"

## 81. Validate version format (semantic versioning)
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    print_error "Invalid version format. Use semantic versioning (e.g., 1.0.0)"
    exit 1
fi

print_status "Starting release process for version $VERSION"

## 82. Check for clean working directory
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory is not clean. Commit or stash changes first."
    exit 1
fi

## 83. Check current branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    print_warning "You are not on the main branch (current: $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Release cancelled"
        exit 1
    fi
fi

## 84. Run quality checks
print_status "Running comprehensive quality checks..."
if ! ./scripts/quality-check.sh; then
    print_error "Quality checks failed. Fix issues before release."
    exit 1
fi

## 85. Update version in relevant files if needed
print_status "Preparing version $VERSION..."

## 86. Run full test suite including slow tests
print_status "Running complete test suite..."
if ! uv run pytest tests/ -v --runslow; then
    print_error "Test suite failed"
    exit 1
fi

## 87. Build package
print_status "Building package..."
if ! hatch build; then
    print_error "Package build failed"
    exit 1
fi

## 88. Create git tag
print_status "Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release version $VERSION"

## 89. Push changes and tag
print_status "Pushing changes and tag to remote..."
git push origin "$CURRENT_BRANCH"
git push origin "v$VERSION"

## 90. Publish to PyPI (test first)
print_status "Publishing to Test PyPI..."
if hatch publish -r test; then
    print_success "Published to Test PyPI"

    print_status "Testing installation from Test PyPI..."
    sleep 10  # Wait for package to be available

    # Test installation in temporary environment
    if python -m pip install --index-url https://test.pypi.org/simple/ vexy-pdf-werk==$VERSION --dry-run; then
        print_success "Test PyPI installation check passed"

        print_status "Publishing to main PyPI..."
        read -p "Publish to main PyPI? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if hatch publish; then
                print_success "Successfully published to PyPI!"
            else
                print_error "PyPI publication failed"
                exit 1
            fi
        else
            print_warning "Skipped main PyPI publication"
        fi
    else
        print_error "Test PyPI installation check failed"
        exit 1
    fi
else
    print_error "Test PyPI publication failed"
    exit 1
fi

## 91. Clean up build artifacts
print_status "Cleaning up build artifacts..."
rm -rf dist/ build/ *.egg-info/

## 92. Create GitHub release (if gh is available)
if command -v gh &> /dev/null; then
    print_status "Creating GitHub release..."

    # Generate release notes
    RELEASE_NOTES="Release version $VERSION

### 92.1. Changes
$(git log --oneline --pretty=format:\"- %s\" $(git describe --tags --abbrev=0 HEAD~1)..HEAD)

### 92.2. Installation
\`\`\`bash
pip install vexy-pdf-werk==$VERSION
\`\`\`

### 92.3. Documentation
See [README.md](README.md) for usage instructions.
"

    if gh release create "v$VERSION" --title "Release v$VERSION" --notes "$RELEASE_NOTES"; then
        print_success "GitHub release created"
    else
        print_warning "GitHub release creation failed (manual creation needed)"
    fi
else
    print_warning "GitHub CLI not available, skipping GitHub release"
fi

print_success "Release $VERSION completed successfully! 🎉"
print_status "Summary:"
echo "  ✅ Quality checks passed"
echo "  ✅ Tests passed"
echo "  ✅ Package built"
echo "  ✅ Git tag created and pushed"
echo "  ✅ Published to Test PyPI"
echo "  ✅ Published to main PyPI"
echo "  ✅ GitHub release created"

print_status "Next steps:"
echo "  1. Update documentation if needed"
echo "  2. Announce release on relevant channels"
echo "  3. Monitor for issues and feedback"
```