# this_file: src/vexy_pdf_werk/core/qdf_processor.py

"""QDF/JSON processing for advanced AI-powered PDF enhancement."""

import asyncio
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

class QDFProcessor:
    """Handles the conversion of PDF pages to and from QDF/JSON format."""

    def __init__(self, qpdf_cmd: str):
        self.qpdf_cmd = qpdf_cmd

    async def pdf_to_qdf_json(self, pdf_path: Path, page_num: int) -> Dict[str, Any]:
        """Converts a single PDF page to its QDF/JSON representation."""
        cmd = [
            self.qpdf_cmd,
            "--qdf",
            "--json",
            str(pdf_path),
            f"--pages",
            ".",
            f"{page_num+1}",
            "-"
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"qpdf to JSON conversion failed: {stderr.decode()}")
        return json.loads(stdout)

    def extract_text_from_qdf(self, qdf_json: Dict[str, Any]) -> str:
        """Extracts only the text streams from a QDF/JSON object."""
        # This is a simplified example. The actual implementation will need to
        # traverse the JSON structure and extract all text-related streams.
        text_parts = []
        for obj_id, obj_data in qdf_json.get("objects", {}).items():
            if "stream" in obj_data and "data" in obj_data["stream"]:
                # A more robust check for text streams is needed here
                text_parts.append(obj_data["stream"]["data"])
        return "\n".join(text_parts)

    def apply_diff_to_qdf(self, qdf_json: Dict[str, Any], diff: str) -> Dict[str, Any]:
        """Applies a unified diff to the QDF/JSON object to update text streams."""
        if not diff or not diff.strip():
            logger.debug("Empty diff provided, returning original QDF")
            return qdf_json

        try:
            # Extract current text content
            original_text = self.extract_text_from_qdf(qdf_json)
            if not original_text.strip():
                logger.debug("No text content found in QDF, returning original")
                return qdf_json

            # Apply the diff to get the modified text
            modified_text = self._apply_unified_diff(original_text, diff)

            # Update the QDF JSON with the modified text
            updated_qdf = self._update_text_streams_in_qdf(qdf_json, modified_text)

            logger.debug(f"Applied diff: {len(original_text)} -> {len(modified_text)} chars")
            return updated_qdf

        except Exception as e:
            logger.error(f"Failed to apply diff to QDF: {e}")
            return qdf_json

    async def qdf_json_to_pdf(self, qdf_json: Dict[str, Any], output_path: Path):
        """Converts a QDF/JSON object back to a PDF file."""
        qdf_content = json.dumps(qdf_json)
        cmd = [
            self.qpdf_cmd,
            "--qdf",
            "-",
            str(output_path)
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate(input=qdf_content.encode())
        if proc.returncode != 0:
            raise RuntimeError(f"qpdf from JSON conversion failed: {stderr.decode()}")

    def _apply_unified_diff(self, original_text: str, diff: str) -> str:
        """Applies a unified diff to text and returns the modified version."""
        # Parse the unified diff format
        lines = diff.strip().split('\n')

        # Skip header lines (@@, ---, +++ etc.)
        diff_lines = []
        for line in lines:
            if line.startswith('@@') or line.startswith('---') or line.startswith('+++'):
                continue
            diff_lines.append(line)

        if not diff_lines:
            logger.debug("No actual diff content found")
            return original_text

        # Simple approach: collect all additions and deletions
        # This is a simplified diff application - for production use,
        # a proper diff library like 'difflib' or 'patch' would be better

        original_lines = original_text.split('\n')
        result_lines = []

        i = 0
        for diff_line in diff_lines:
            if diff_line.startswith(' '):
                # Context line - keep as is
                if i < len(original_lines):
                    result_lines.append(original_lines[i])
                    i += 1
            elif diff_line.startswith('-'):
                # Deletion - skip the original line
                if i < len(original_lines):
                    i += 1
            elif diff_line.startswith('+'):
                # Addition - add the new line
                result_lines.append(diff_line[1:])  # Remove the + prefix

        # Add any remaining original lines
        while i < len(original_lines):
            result_lines.append(original_lines[i])
            i += 1

        return '\n'.join(result_lines)

    def _update_text_streams_in_qdf(self, qdf_json: Dict[str, Any], new_text: str) -> Dict[str, Any]:
        """Updates text streams in QDF JSON with new content."""
        # Create a deep copy to avoid modifying the original
        import copy
        updated_qdf = copy.deepcopy(qdf_json)

        # For simplicity, replace all text stream data with the new text
        # In a more sophisticated implementation, we would map specific
        # parts of the text to specific stream objects

        text_stream_count = 0
        for obj_id, obj_data in updated_qdf.get("objects", {}).items():
            if "stream" in obj_data and "data" in obj_data["stream"]:
                # Replace with the new text (distribute across streams if needed)
                if text_stream_count == 0:
                    # Put all new text in the first text stream
                    obj_data["stream"]["data"] = new_text
                else:
                    # Clear subsequent streams to avoid duplication
                    obj_data["stream"]["data"] = ""
                text_stream_count += 1

        return updated_qdf
