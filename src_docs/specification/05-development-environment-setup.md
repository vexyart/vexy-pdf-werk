# 2. Vexy PDF Werk (VPW) - Part 2: Project Structure and Setup

This section provides detailed step-by-step instructions for setting up the development environment and creating the initial project structure.

### 2.1. Development Environment Setup

#### 2.1.1. Prerequisites Installation

##### 1. Install uv (Fast Python Package Manager)
```bash
## 3. Install uv globally
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal

## 4. Verify installation
uv --version
```

##### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng qpdf ghostscript imagemagick pandoc
```

**macOS (using Homebrew):**
```bash
brew install tesseract tesseract-lang qpdf ghostscript imagemagick pandoc
```

**Windows (using Chocolatey):**
```powershell
choco install tesseract qpdf ghostscript imagemagick pandoc
```

##### 3. Install hatch with uv
```bash
## 5. Install hatch globally using uv
uv tool install hatch

## 6. Verify installation
hatch --version
```
