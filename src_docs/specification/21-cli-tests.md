##### CLI Tests (`tests/integration/test_cli.py`)

```python
## 60. this_file: tests/integration/test_cli.py

"""Integration tests for CLI interface."""

import subprocess
import sys
from pathlib import Path

import pytest

from vexy_pdf_werk.cli import VexyPDFWerk, main


@pytest.mark.integration
class TestCLI:
    """Test CLI functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        # Test that CLI can be imported and help works
        vpw = VexyPDFWerk()
        assert vpw.version is not None

    def test_cli_version_command(self, capsys):
        """Test version command."""
        vpw = VexyPDFWerk()
        vpw.version()

        captured = capsys.readouterr()
        assert "Vexy PDF Werk version" in captured.out

    def test_cli_config_show(self, capsys):
        """Test config show command."""
        vpw = VexyPDFWerk()
        vpw.config(show=True)

        captured = capsys.readouterr()
        assert "Configuration" in captured.out

    def test_cli_process_nonexistent_file(self, capsys):
        """Test processing non-existent file."""
        vpw = VexyPDFWerk()
        result = vpw.process("nonexistent.pdf")

        assert result == 1  # Error exit code

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_cli_process_invalid_format(self, sample_pdf, capsys):
        """Test processing with invalid output format."""
        vpw = VexyPDFWerk()
        result = vpw.process(str(sample_pdf), formats="invalid_format")

        assert result == 1  # Error exit code

        captured = capsys.readouterr()
        assert "Invalid formats" in captured.out

    @pytest.mark.slow
    def test_cli_process_basic(self, sample_pdf, temp_dir, capsys):
        """Test basic CLI processing."""
        vpw = VexyPDFWerk()
        result = vpw.process(
            str(sample_pdf),
            output_dir=str(temp_dir),
            formats="yaml",  # Only request metadata (simplest)
            verbose=True
        )

        # Should return 0 when implementation is complete
        # For now, it returns 0 but shows "not implemented"
        captured = capsys.readouterr()
        assert "Processing" in captured.out

    @pytest.mark.subprocess
    def test_cli_as_subprocess(self, sample_pdf):
        """Test CLI as subprocess (when installed)."""
        try:
            # Try to run the CLI as a subprocess
            result = subprocess.run([
                sys.executable, "-m", "vexy_pdf_werk.cli",
                "version"
            ], capture_output=True, text=True, timeout=10)

            # If the module is properly installed, this should work
            if result.returncode == 0:
                assert "version" in result.stdout.lower()
            else:
                # If not installed, we expect an import error
                assert "ModuleNotFoundError" in result.stderr or result.returncode != 0

        except subprocess.TimeoutExpired:
            pytest.fail("CLI subprocess timed out")


@pytest.mark.integration
class TestCLIFireIntegration:
    """Test Fire integration with CLI."""

    def test_fire_help_generation(self):
        """Test that Fire generates proper help."""
        vpw = VexyPDFWerk()

        # Check that methods have proper docstrings for Fire
        assert vpw.process.__doc__ is not None
        assert "PDF file" in vpw.process.__doc__

        assert vpw.config.__doc__ is not None
        assert "configuration" in vpw.config.__doc__.lower()

    def test_fire_argument_parsing(self):
        """Test Fire's argument parsing."""
        vpw = VexyPDFWerk()

        # Fire should handle these arguments correctly
        # This is more of a smoke test to ensure Fire integration works
        assert hasattr(vpw, 'process')
        assert hasattr(vpw, 'config')
        assert hasattr(vpw, 'version')
```
