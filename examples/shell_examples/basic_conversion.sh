#!/bin/bash
# this_file: examples/shell_examples/basic_conversion.sh
# Basic CLI usage example for Vexy PDF Werk

echo "🔧 Vexy PDF Werk - Basic CLI Conversion Example"
echo "================================================"

# Set up paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
OUTPUT_DIR="$SCRIPT_DIR/../output/cli_basic"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📁 Data directory: $DATA_DIR"
echo "📁 Output directory: $OUTPUT_DIR"
echo ""

# Check if vpw command is available
if ! command -v vpw &> /dev/null; then
    echo "❌ vpw command not found!"
    echo "Please ensure Vexy PDF Werk is installed:"
    echo "  pip install vexy-pdf-werk"
    echo "  # OR for development:"
    echo "  pip install -e ."
    exit 1
fi

# Check for sample PDFs
if [ ! -d "$DATA_DIR" ] || [ -z "$(ls -A "$DATA_DIR"/*.pdf 2>/dev/null)" ]; then
    echo "❌ No PDF files found in $DATA_DIR"
    echo "Please add some PDF files to the data directory."
    exit 1
fi

echo "📄 Available PDF files:"
for pdf in "$DATA_DIR"/*.pdf; do
    if [ -f "$pdf" ]; then
        filename=$(basename "$pdf")
        size=$(du -h "$pdf" | cut -f1)
        echo "   • $filename ($size)"
    fi
done
echo ""

# Example 1: Basic conversion with default settings
echo "📝 Example 1: Basic Conversion"
echo "------------------------------"
echo "Converting first available PDF with default settings..."

FIRST_PDF=$(ls "$DATA_DIR"/*.pdf | head -n 1)
FILENAME=$(basename "$FIRST_PDF" .pdf)

echo "Command: vpw process \"$FIRST_PDF\" --output \"$OUTPUT_DIR/example1\""
echo ""

# Check if this is a real environment or demo
if [ "$1" = "--demo" ]; then
    echo "🎭 Demo mode - simulating command execution:"
    echo "✓ Analyzing PDF structure..."
    echo "✓ Extracting text content..."
    echo "✓ Converting to Markdown (3 pages)..."
    echo "✓ Generating ePub..."
    echo "✓ Creating metadata..."
    echo "📁 Output saved to: $OUTPUT_DIR/example1/"
else
    # Run actual command
    vpw process "$FIRST_PDF" --output "$OUTPUT_DIR/example1"

    if [ $? -eq 0 ]; then
        echo "✅ Basic conversion completed successfully!"
    else
        echo "❌ Conversion failed. Check error messages above."
    fi
fi

echo ""

# Example 2: Conversion with specific formats
echo "📚 Example 2: Specific Format Selection"
echo "----------------------------------------"
echo "Converting with only Markdown and YAML formats..."

if [ -n "$(ls "$DATA_DIR"/*.pdf 2>/dev/null | sed -n '2p')" ]; then
    SECOND_PDF=$(ls "$DATA_DIR"/*.pdf | sed -n '2p')
else
    SECOND_PDF="$FIRST_PDF"
fi

echo "Command: vpw process \"$SECOND_PDF\" --output \"$OUTPUT_DIR/example2\" --formats \"markdown,yaml\""
echo ""

if [ "$1" = "--demo" ]; then
    echo "🎭 Demo mode - simulating command execution:"
    echo "✓ Processing with selected formats only..."
    echo "✓ Generating Markdown files..."
    echo "✓ Creating metadata YAML..."
    echo "📁 Output saved to: $OUTPUT_DIR/example2/"
else
    vpw process "$SECOND_PDF" --output "$OUTPUT_DIR/example2" --formats "markdown,yaml"

    if [ $? -eq 0 ]; then
        echo "✅ Format-specific conversion completed!"
    else
        echo "❌ Conversion failed. Check error messages above."
    fi
fi

echo ""

# Example 3: Verbose output
echo "🔍 Example 3: Verbose Processing"
echo "---------------------------------"
echo "Converting with detailed logging..."

echo "Command: vpw process \"$FIRST_PDF\" --output \"$OUTPUT_DIR/example3\" --verbose"
echo ""

if [ "$1" = "--demo" ]; then
    echo "🎭 Demo mode - simulating verbose output:"
    echo "DEBUG: Initializing PDF processor..."
    echo "DEBUG: Analyzing PDF: $(basename "$FIRST_PDF")"
    echo "INFO:  Found 5 pages, text detected: Yes"
    echo "DEBUG: Starting OCR analysis..."
    echo "INFO:  OCR not required - text layer present"
    echo "DEBUG: Converting to Markdown..."
    echo "INFO:  Page 1/5: Extracted 245 words"
    echo "INFO:  Page 2/5: Extracted 312 words"
    echo "INFO:  Page 3/5: Extracted 198 words"
    echo "INFO:  Page 4/5: Extracted 267 words"
    echo "INFO:  Page 5/5: Extracted 156 words"
    echo "DEBUG: Generating ePub..."
    echo "INFO:  Created ePub with 5 chapters"
    echo "DEBUG: Extracting metadata..."
    echo "INFO:  Processing completed in 12.3 seconds"
    echo "✅ Verbose processing completed!"
else
    vpw process "$FIRST_PDF" --output "$OUTPUT_DIR/example3" --verbose

    if [ $? -eq 0 ]; then
        echo "✅ Verbose processing completed!"
    else
        echo "❌ Processing failed. Check verbose output above."
    fi
fi

echo ""

# Show CLI help
echo "📖 Example 4: CLI Help Information"
echo "-----------------------------------"
echo "Command: vpw --help"
echo ""

if [ "$1" = "--demo" ]; then
    echo "🎭 Demo mode - simulating help output:"
    cat << 'EOF'
usage: vpw [-h] {process,config,version} ...

Vexy PDF Werk - Transform PDFs into accessible formats

positional arguments:
  {process,config,version}
    process             Process PDF files
    config              Manage configuration
    version             Show version information

optional arguments:
  -h, --help            show this help message and exit

Examples:
  vpw process document.pdf
  vpw process file.pdf --formats "markdown,epub"
  vpw config --show
  vpw version
EOF
else
    vpw --help
fi

echo ""

# Summary
echo "📋 Summary of Examples"
echo "======================"
echo "1. ✅ Basic conversion with default settings"
echo "2. ✅ Format selection (markdown + yaml only)"
echo "3. ✅ Verbose processing with detailed logs"
echo "4. ✅ CLI help and usage information"
echo ""
echo "📁 Check output files in: $OUTPUT_DIR/"
echo ""
echo "💡 Next steps:"
echo "   • Try the batch processing script: ./batch_convert.sh"
echo "   • Explore format options: ./format_selection.sh"
echo "   • Check Python examples in ../python_examples/"
echo ""
echo "🎉 Basic CLI examples completed!"

# List generated files if they exist
if [ -d "$OUTPUT_DIR" ] && [ "$(ls -A "$OUTPUT_DIR" 2>/dev/null)" ]; then
    echo ""
    echo "📄 Generated files:"
    find "$OUTPUT_DIR" -type f -name "*.md" -o -name "*.epub" -o -name "*.yaml" | sort | while read -r file; do
        rel_path=$(echo "$file" | sed "s|$OUTPUT_DIR/||")
        size=$(du -h "$file" | cut -f1)
        echo "   • $rel_path ($size)"
    done
fi