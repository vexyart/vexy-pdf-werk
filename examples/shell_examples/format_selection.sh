#!/bin/bash
# this_file: examples/shell_examples/format_selection.sh
# Format selection and customization example for Vexy PDF Werk CLI

echo "🔧 Vexy PDF Werk - Format Selection Examples"
echo "=============================================="

# Set up paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
OUTPUT_DIR="$SCRIPT_DIR/../output/cli_formats"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📁 Data directory: $DATA_DIR"
echo "📁 Output directory: $OUTPUT_DIR"
echo ""

# Function to run command or simulate
run_command() {
    local cmd="$1"
    local description="$2"

    echo "📝 $description"
    echo "Command: $cmd"
    echo ""

    if [ "$DEMO_MODE" = "true" ]; then
        echo "🎭 Demo mode - simulating execution..."
        case "$description" in
            *"Markdown only"*)
                echo "✓ Converting to Markdown format..."
                echo "✓ Generated 3 markdown files"
                echo "✓ Created page structure with proper slugs"
                ;;
            *"ePub only"*)
                echo "✓ Converting to ePub format..."
                echo "✓ Created ebook with table of contents"
                echo "✓ Embedded metadata and styling"
                ;;
            *"Metadata only"*)
                echo "✓ Extracting document metadata..."
                echo "✓ Analyzing PDF structure and content"
                echo "✓ Generated YAML metadata file"
                ;;
            *"All formats"*)
                echo "✓ Converting to all supported formats..."
                echo "✓ Markdown: 3 files generated"
                echo "✓ ePub: Created with TOC and styling"
                echo "✓ YAML: Metadata extracted"
                ;;
            *"Custom combination"*)
                echo "✓ Processing with selected formats..."
                echo "✓ Markdown and YAML files created"
                echo "✓ Skipped ePub generation as requested"
                ;;
        esac
        echo "📁 Output would be saved to: [output directory]"
    else
        eval "$cmd"
        if [ $? -eq 0 ]; then
            echo "✅ Command completed successfully!"
        else
            echo "❌ Command failed!"
        fi
    fi
    echo ""
    echo "----------------------------------------"
    echo ""
}

# Check for demo mode
DEMO_MODE="false"
if [ "$1" = "--demo" ]; then
    DEMO_MODE="true"
    echo "🎭 Running in demo mode (simulation only)"
    echo ""
fi

# Check for vpw command (unless demo mode)
if [ "$DEMO_MODE" = "false" ] && ! command -v vpw &> /dev/null; then
    echo "❌ vpw command not found!"
    echo "Please install Vexy PDF Werk or run in demo mode:"
    echo "  $0 --demo"
    exit 1
fi

# Find a sample PDF
SAMPLE_PDF=""
if [ -d "$DATA_DIR" ]; then
    SAMPLE_PDF=$(find "$DATA_DIR" -name "*.pdf" -type f | head -n 1)
fi

if [ -z "$SAMPLE_PDF" ] && [ "$DEMO_MODE" = "false" ]; then
    echo "❌ No PDF files found in $DATA_DIR"
    echo "Please add a PDF file to test with, or run in demo mode:"
    echo "  $0 --demo"
    exit 1
fi

if [ "$DEMO_MODE" = "false" ]; then
    echo "📄 Using sample PDF: $(basename "$SAMPLE_PDF")"
    echo ""
fi

# Example 1: Markdown only
run_command \
    "vpw process \"$SAMPLE_PDF\" --output \"$OUTPUT_DIR/markdown_only\" --formats \"markdown\"" \
    "Example 1: Markdown only"

# Example 2: ePub only
run_command \
    "vpw process \"$SAMPLE_PDF\" --output \"$OUTPUT_DIR/epub_only\" --formats \"epub\"" \
    "Example 2: ePub only"

# Example 3: Metadata only
run_command \
    "vpw process \"$SAMPLE_PDF\" --output \"$OUTPUT_DIR/metadata_only\" --formats \"yaml\"" \
    "Example 3: Metadata only"

# Example 4: All formats
run_command \
    "vpw process \"$SAMPLE_PDF\" --output \"$OUTPUT_DIR/all_formats\" --formats \"markdown,epub,yaml\"" \
    "Example 4: All formats"

# Example 5: Custom combination
run_command \
    "vpw process \"$SAMPLE_PDF\" --output \"$OUTPUT_DIR/custom\" --formats \"markdown,yaml\"" \
    "Example 5: Custom combination (Markdown + Metadata)"

# Show format information
echo "📖 Available Output Formats"
echo "============================"
echo ""

echo "📝 Markdown Format:"
echo "   • Description: Paginated markdown files with frontmatter"
echo "   • Files: 000--page-title.md, 001--chapter-1.md, etc."
echo "   • Features: Smart title detection, slug generation, metadata headers"
echo "   • Use cases: Documentation, web publishing, further processing"
echo ""

echo "📚 ePub Format:"
echo "   • Description: Standard ebook format with TOC and styling"
echo "   • Files: [document-name].epub"
echo "   • Features: Chapter structure, metadata, embedded fonts"
echo "   • Use cases: E-readers, digital libraries, mobile reading"
echo ""

echo "📊 YAML Metadata Format:"
echo "   • Description: Structured metadata about the document"
echo "   • Files: metadata.yaml"
echo "   • Features: PDF info, processing stats, content analysis"
echo "   • Use cases: Cataloging, automation, quality assessment"
echo ""

# Format comparison table
echo "📋 Format Comparison"
echo "===================="
printf "%-12s %-10s %-12s %-15s %-20s\n" "Format" "File Size" "Readability" "Compatibility" "Use Case"
echo "------------------------------------------------------------------------"
printf "%-12s %-10s %-12s %-15s %-20s\n" "Markdown" "Small" "High" "Universal" "Web/Documentation"
printf "%-12s %-10s %-12s %-15s %-20s\n" "ePub" "Medium" "High" "E-readers" "Digital Books"
printf "%-12s %-10s %-12s %-15s %-20s\n" "YAML" "Tiny" "Medium" "Automation" "Metadata/Analysis"
echo ""

# Advanced format options
echo "⚙️ Advanced Format Configuration"
echo "================================="
echo ""

echo "Quality Settings:"
echo "   --quality high      # Best quality, slower processing"
echo "   --quality medium    # Balanced quality and speed (default)"
echo "   --quality fast      # Faster processing, basic quality"
echo ""

echo "Markdown Options:"
echo "   --no-paginate       # Single markdown file instead of pages"
echo "   --include-images    # Extract and include images"
echo "   --preserve-tables   # Maintain table formatting"
echo ""

echo "ePub Options:"
echo "   --epub-style modern # Use modern styling"
echo "   --epub-cover auto   # Generate cover from first page"
echo "   --epub-metadata     # Enhanced metadata inclusion"
echo ""

echo "Output Organization:"
echo "   --flat-output       # All files in single directory"
echo "   --timestamp         # Add timestamp to output names"
echo "   --preserve-names    # Keep original PDF names"
echo ""

# Performance considerations
echo "⚡ Performance vs Quality Trade-offs"
echo "====================================="
echo ""

echo "🚀 Fast Processing (--quality fast):"
echo "   ✓ Faster conversion (2-3x speed)"
echo "   ✓ Lower resource usage"
echo "   ✓ Good for batch processing"
echo "   ⚠ Basic text extraction only"
echo "   ⚠ Limited formatting preservation"
echo ""

echo "⚖️ Balanced Processing (default):"
echo "   ✓ Good quality output"
echo "   ✓ Reasonable processing time"
echo "   ✓ Most features enabled"
echo "   ✓ Recommended for most use cases"
echo ""

echo "🎯 High Quality (--quality high):"
echo "   ✓ Best possible output quality"
echo "   ✓ Advanced text analysis"
echo "   ✓ Enhanced formatting preservation"
echo "   ⚠ Slower processing time"
echo "   ⚠ Higher resource usage"
echo ""

# Use case recommendations
echo "🎯 Format Selection Guide"
echo "=========================="
echo ""

echo "📖 For Documentation/Web Publishing:"
echo "   vpw process file.pdf --formats markdown --include-images"
echo ""

echo "📱 For E-reading/Mobile:"
echo "   vpw process file.pdf --formats epub --epub-style modern"
echo ""

echo "🤖 For Automation/Analysis:"
echo "   vpw process file.pdf --formats yaml --quality fast"
echo ""

echo "📦 For Complete Archive:"
echo "   vpw process file.pdf --formats markdown,epub,yaml --quality high"
echo ""

echo "⚡ For Quick Preview:"
echo "   vpw process file.pdf --formats markdown --quality fast --no-paginate"
echo ""

# Troubleshooting
echo "🔧 Troubleshooting Format Issues"
echo "================================="
echo ""

echo "❌ Markdown generation fails:"
echo "   • Check PDF has text layer (not pure image)"
echo "   • Try with --force-ocr flag"
echo "   • Verify write permissions in output directory"
echo ""

echo "❌ ePub creation fails:"
echo "   • Ensure pandoc is installed"
echo "   • Check markdown was generated successfully first"
echo "   • Try without custom styling options"
echo ""

echo "❌ Large file processing:"
echo "   • Use --quality fast for initial testing"
echo "   • Ensure sufficient disk space (3-5x PDF size)"
echo "   • Consider processing in smaller batches"
echo ""

# Show output structure example
if [ "$DEMO_MODE" = "true" ] || [ -d "$OUTPUT_DIR" ]; then
    echo "📁 Example Output Structure"
    echo "==========================="
    echo ""
    echo "output/"
    echo "├── markdown_only/"
    echo "│   ├── 000--introduction.md"
    echo "│   ├── 001--chapter-1.md"
    echo "│   └── 002--conclusion.md"
    echo "├── epub_only/"
    echo "│   └── document.epub"
    echo "├── metadata_only/"
    echo "│   └── metadata.yaml"
    echo "├── all_formats/"
    echo "│   ├── 000--introduction.md"
    echo "│   ├── 001--chapter-1.md"
    echo "│   ├── 002--conclusion.md"
    echo "│   ├── document.epub"
    echo "│   └── metadata.yaml"
    echo "└── custom/"
    echo "    ├── 000--introduction.md"
    echo "    ├── 001--chapter-1.md"
    echo "    ├── 002--conclusion.md"
    echo "    └── metadata.yaml"
    echo ""
fi

echo "💡 Pro Tips"
echo "==========="
echo "• Start with a single format to test your workflow"
echo "• Use metadata format to analyze document structure first"
echo "• Combine formats based on your specific needs"
echo "• Test quality settings with sample documents"
echo "• Check generated files before processing large batches"
echo ""

echo "🔗 Related Examples"
echo "==================="
echo "• Basic conversion: ./basic_conversion.sh"
echo "• Batch processing: ./batch_convert.sh"
echo "• Python API examples: ../python_examples/"
echo ""

echo "🎉 Format selection examples completed!"
echo ""

if [ "$DEMO_MODE" = "true" ]; then
    echo "💡 Run without --demo flag to process actual files:"
    echo "   $0"
fi