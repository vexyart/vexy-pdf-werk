#!/bin/bash
# this_file: examples/shell_examples/batch_convert.sh
# Batch processing example for Vexy PDF Werk CLI

echo "🔧 Vexy PDF Werk - Batch Processing Example"
echo "============================================="

# Set up paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
OUTPUT_DIR="$SCRIPT_DIR/../output/cli_batch"
LOG_DIR="$OUTPUT_DIR/logs"

# Create directories
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

echo "📁 Data directory: $DATA_DIR"
echo "📁 Output directory: $OUTPUT_DIR"
echo "📁 Log directory: $LOG_DIR"
echo ""

# Function to log with timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/batch_processing.log"
}

# Function to process a single PDF
process_pdf() {
    local pdf_file="$1"
    local pdf_name=$(basename "$pdf_file" .pdf)
    local start_time=$(date +%s)

    log_message "Starting processing: $pdf_name"

    # Create individual output directory
    local pdf_output="$OUTPUT_DIR/$pdf_name"
    mkdir -p "$pdf_output"

    if [ "$DEMO_MODE" = "true" ]; then
        # Demo mode - simulate processing
        log_message "🎭 DEMO: Simulating processing of $pdf_name"
        sleep 1

        # Simulate file creation
        echo "# Demo Markdown for $pdf_name" > "$pdf_output/demo_page.md"
        echo "source_file: $pdf_name.pdf" > "$pdf_output/metadata.yaml"

        log_message "✅ DEMO: Completed $pdf_name (simulated)"
        return 0
    else
        # Real processing
        local cmd="vpw process \"$pdf_file\" --output \"$pdf_output\" --formats \"markdown,epub,yaml\""
        log_message "Executing: $cmd"

        if eval "$cmd" >> "$LOG_DIR/${pdf_name}_processing.log" 2>&1; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            log_message "✅ Completed $pdf_name in ${duration}s"
            return 0
        else
            log_message "❌ Failed to process $pdf_name"
            return 1
        fi
    fi
}

# Function to show progress bar
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))

    printf "\r["
    for ((i=0; i<filled; i++)); do printf "█"; done
    for ((i=filled; i<width; i++)); do printf "░"; done
    printf "] %d%% (%d/%d)" "$percentage" "$current" "$total"
}

# Check for demo mode
DEMO_MODE="false"
if [ "$1" = "--demo" ]; then
    DEMO_MODE="true"
    echo "🎭 Running in demo mode (simulation only)"
    echo ""
fi

# Check if vpw command is available (unless in demo mode)
if [ "$DEMO_MODE" = "false" ] && ! command -v vpw &> /dev/null; then
    echo "❌ vpw command not found!"
    echo "Please ensure Vexy PDF Werk is installed:"
    echo "  pip install vexy-pdf-werk"
    echo "  # OR for development:"
    echo "  pip install -e ."
    echo ""
    echo "💡 Run with --demo flag to see example output:"
    echo "  $0 --demo"
    exit 1
fi

# Find all PDF files
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ Data directory not found: $DATA_DIR"
    exit 1
fi

PDF_FILES=($(find "$DATA_DIR" -name "*.pdf" -type f))

if [ ${#PDF_FILES[@]} -eq 0 ]; then
    echo "❌ No PDF files found in $DATA_DIR"
    echo "Please add some PDF files to process."
    exit 1
fi

echo "📄 Found ${#PDF_FILES[@]} PDF files to process:"
total_size=0
for pdf in "${PDF_FILES[@]}"; do
    filename=$(basename "$pdf")
    size=$(stat -f%z "$pdf" 2>/dev/null || stat -c%s "$pdf" 2>/dev/null)
    size_mb=$((size / 1024 / 1024))
    total_size=$((total_size + size))
    echo "   • $filename (${size_mb}MB)"
done

total_size_mb=$((total_size / 1024 / 1024))
echo ""
echo "📊 Batch Statistics:"
echo "   • Total files: ${#PDF_FILES[@]}"
echo "   • Total size: ${total_size_mb}MB"
echo "   • Estimated time: ~$((${#PDF_FILES[@]} * 30))s (varies by file size)"
echo ""

# Initialize statistics
successful=0
failed=0
start_time=$(date +%s)

log_message "Starting batch processing of ${#PDF_FILES[@]} files"

# Process files sequentially
echo "🚀 Starting batch processing..."
echo ""

for i in "${!PDF_FILES[@]}"; do
    pdf_file="${PDF_FILES[$i]}"
    current=$((i + 1))

    # Show progress
    show_progress "$current" "${#PDF_FILES[@]}"
    echo ""

    # Process the PDF
    if process_pdf "$pdf_file"; then
        successful=$((successful + 1))
    else
        failed=$((failed + 1))
    fi

    echo ""
done

# Calculate final statistics
end_time=$(date +%s)
total_duration=$((end_time - start_time))

echo ""
echo "📋 Batch Processing Summary"
echo "==========================="
log_message "Batch processing completed"

echo "⏱️  Total time: ${total_duration} seconds"
echo "📄 Total files: ${#PDF_FILES[@]}"
echo "✅ Successful: $successful"
echo "❌ Failed: $failed"

if [ "${#PDF_FILES[@]}" -gt 0 ]; then
    success_rate=$((successful * 100 / ${#PDF_FILES[@]}))
    echo "📈 Success rate: ${success_rate}%"
fi

if [ "$successful" -gt 0 ]; then
    avg_time=$((total_duration / successful))
    echo "⚡ Average time per file: ${avg_time}s"
fi

echo ""

# Show output structure
if [ "$successful" -gt 0 ]; then
    echo "📁 Output Structure:"
    echo "==================="

    # Show first few output directories
    count=0
    for dir in "$OUTPUT_DIR"/*/; do
        if [ -d "$dir" ] && [ "$count" -lt 3 ]; then
            dir_name=$(basename "$dir")
            echo "📂 $dir_name/"

            # Show files in this directory
            for file in "$dir"*; do
                if [ -f "$file" ]; then
                    filename=$(basename "$file")
                    size=$(du -h "$file" | cut -f1)
                    echo "   ├── $filename ($size)"
                fi
            done
            echo ""
            count=$((count + 1))
        fi
    done

    if [ "${#PDF_FILES[@]}" -gt 3 ]; then
        remaining=$((${#PDF_FILES[@]} - 3))
        echo "   ... and $remaining more directories"
        echo ""
    fi
fi

# Show log files
if [ -d "$LOG_DIR" ] && [ "$(ls -A "$LOG_DIR")" ]; then
    echo "📄 Log Files:"
    echo "============="
    for log_file in "$LOG_DIR"/*.log; do
        if [ -f "$log_file" ]; then
            filename=$(basename "$log_file")
            size=$(du -h "$log_file" | cut -f1)
            echo "   • $filename ($size)"
        fi
    done
    echo ""
fi

# Show errors if any
if [ "$failed" -gt 0 ]; then
    echo "❌ Failed Files:"
    echo "================"
    echo "Check individual log files in $LOG_DIR/ for error details"
    echo ""

    # Show last few lines of main log for errors
    if [ -f "$LOG_DIR/batch_processing.log" ]; then
        echo "Recent errors from main log:"
        grep "❌" "$LOG_DIR/batch_processing.log" | tail -3
        echo ""
    fi
fi

# Performance recommendations
echo "💡 Performance Tips:"
echo "===================="
echo "• For large batches, consider parallel processing"
echo "• Monitor disk space (each PDF can generate 2-5x size in outputs)"
echo "• Use SSD storage for better I/O performance"
echo "• Adjust formats based on your needs (fewer formats = faster)"

if [ "$DEMO_MODE" = "false" ]; then
    echo "• Enable AI enhancement only when needed (slower but better quality)"
    echo "• Use --fast flag for quick processing of simple documents"
fi

echo ""

# Cleanup suggestions
echo "🧹 Cleanup Commands:"
echo "===================="
echo "# Remove all generated files:"
echo "rm -rf \"$OUTPUT_DIR\""
echo ""
echo "# Remove only log files:"
echo "rm -rf \"$LOG_DIR\""
echo ""
echo "# Keep outputs but clean logs:"
echo "find \"$LOG_DIR\" -name '*.log' -delete"
echo ""

# Show next steps
echo "🎯 Next Steps:"
echo "=============="
echo "• Review generated files in output directories"
echo "• Check processing logs for any warnings"
echo "• Try format-specific processing: ./format_selection.sh"
echo "• Explore Python API examples: ../python_examples/"
echo ""

if [ "$DEMO_MODE" = "true" ]; then
    echo "• Run without --demo flag for real processing"
    echo ""
fi

echo "🎉 Batch processing example completed!"

log_message "Batch processing example finished - Success: $successful, Failed: $failed"