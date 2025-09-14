#!/usr/bin/env python3
# this_file: examples/run_examples.py
"""
Example runner script for Vexy PDF Werk examples.

This script helps users run the examples and verify everything works.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🔧 {title}")
    print("=" * 60)


def print_section(title):
    """Print a formatted section header."""
    print(f"\n📋 {title}")
    print("-" * 40)


def run_command(cmd, description, cwd=None):
    """Run a command and display results."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    print()

    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout.strip():
                print("Output:")
                print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("❌ Failed!")
            if result.stderr.strip():
                print("Error:")
                print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)

    except Exception as e:
        print(f"❌ Exception: {e}")

    print()


def check_prerequisites():
    """Check if required tools are installed."""
    print_section("Checking Prerequisites")

    tools = [
        ("python3", "Python 3"),
        ("pip", "Python package installer"),
    ]

    all_good = True
    for tool, description in tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"✅ {description}: {version}")
            else:
                print(f"❌ {description}: Not found")
                all_good = False
        except FileNotFoundError:
            print(f"❌ {description}: Not installed")
            all_good = False

    # Check for vexy-pdf-werk package
    try:
        import vexy_pdf_werk
        print(f"✅ Vexy PDF Werk: Installed")
    except ImportError:
        print(f"⚠️  Vexy PDF Werk: Not installed (will use development version)")

    return all_good


def list_available_examples():
    """List all available examples."""
    print_section("Available Examples")

    examples_dir = Path(__file__).parent

    # Python examples
    python_dir = examples_dir / "python_examples"
    if python_dir.exists():
        print("🐍 Python Examples:")
        for py_file in sorted(python_dir.glob("*.py")):
            print(f"   • {py_file.name}")

    # Shell examples
    shell_dir = examples_dir / "shell_examples"
    if shell_dir.exists():
        print("\n🐚 Shell Examples:")
        for sh_file in sorted(shell_dir.glob("*.sh")):
            print(f"   • {sh_file.name}")

    # Data files
    data_dir = examples_dir / "data"
    if data_dir.exists():
        print("\n📄 Sample Data:")
        for pdf_file in sorted(data_dir.glob("*.pdf")):
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            print(f"   • {pdf_file.name} ({size_mb:.1f}MB)")


def run_python_examples():
    """Run Python examples."""
    print_section("Running Python Examples")

    examples_dir = Path(__file__).parent
    python_dir = examples_dir / "python_examples"

    if not python_dir.exists():
        print("❌ Python examples directory not found")
        return

    python_examples = [
        ("basic_usage.py", "Basic usage demonstration"),
        ("custom_config.py", "Custom configuration examples"),
        ("batch_processing.py", "Batch processing demonstration"),
        ("ai_enhancement.py", "AI enhancement capabilities"),
    ]

    for example_file, description in python_examples:
        example_path = python_dir / example_file
        if example_path.exists():
            run_command([sys.executable, str(example_path)], description, cwd=examples_dir)
        else:
            print(f"⚠️  {example_file} not found")


def run_shell_examples():
    """Run shell examples in demo mode."""
    print_section("Running Shell Examples (Demo Mode)")

    examples_dir = Path(__file__).parent
    shell_dir = examples_dir / "shell_examples"

    if not shell_dir.exists():
        print("❌ Shell examples directory not found")
        return

    shell_examples = [
        ("basic_conversion.sh", "Basic CLI conversion"),
        ("format_selection.sh", "Format selection options"),
        ("batch_convert.sh", "Batch processing"),
    ]

    for example_file, description in shell_examples:
        example_path = shell_dir / example_file
        if example_path.exists():
            run_command([str(example_path), "--demo"], description, cwd=examples_dir)
        else:
            print(f"⚠️  {example_file} not found")


def show_usage():
    """Show usage information."""
    print_header("Vexy PDF Werk Examples Runner")

    print("""
This script helps you run and test the Vexy PDF Werk examples.

Usage:
    python run_examples.py [command]

Commands:
    check       - Check prerequisites
    list        - List available examples
    python      - Run Python examples
    shell       - Run shell examples (demo mode)
    all         - Run all examples
    help        - Show this help

Examples:
    python run_examples.py check
    python run_examples.py python
    python run_examples.py all
""")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        command = "help"
    else:
        command = sys.argv[1].lower()

    if command == "check":
        print_header("Prerequisites Check")
        check_prerequisites()

    elif command == "list":
        print_header("Example Listing")
        list_available_examples()

    elif command == "python":
        print_header("Python Examples")
        check_prerequisites()
        run_python_examples()

    elif command == "shell":
        print_header("Shell Examples")
        run_shell_examples()

    elif command == "all":
        print_header("All Examples")
        check_prerequisites()
        list_available_examples()
        run_python_examples()
        run_shell_examples()

    elif command == "help":
        show_usage()

    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python run_examples.py help' for usage information")
        sys.exit(1)

    print_section("Example Runner Complete")
    print("💡 Check the output/ directory for generated files")
    print("📖 Read examples/README.md for detailed information")


if __name__ == "__main__":
    main()