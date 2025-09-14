# this_file: src/vexy_pdf_werk/integrations/ai_services.py

"""AI service integrations for text enhancement."""

import asyncio
import subprocess
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path

from loguru import logger

from ..config import AIConfig


class AIService(ABC):
    """Abstract base class for AI services."""

    @abstractmethod
    async def correct_text(self, text: str, context: str = "") -> str:
        """Correct OCR errors in text."""
        pass

    @abstractmethod
    async def enhance_content(self, text: str, document_type: str = "general") -> str:
        """Enhance content structure and formatting."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the AI service is available."""
        pass

    @abstractmethod
    async def enhance_pdf_structure(self, text_content: str) -> str:
        """Enhances PDF structure and returns a diff."""
        pass


class ClaudeCLIService(AIService):
    """Claude CLI service integration."""

    def __init__(self, config: AIConfig):
        """Initialize Claude service."""
        self.config = config
        self.max_tokens = config.max_tokens

    async def correct_text(self, text: str, context: str = "") -> str:
        """Correct OCR errors using Claude CLI."""
        prompt = self._create_correction_prompt(text, context)

        cmd = [
            "claude",
            "--model", "claude-sonnet-4-20250514",
            "--dangerously-skip-permissions",
            "-p", prompt
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown Claude error"
                logger.error(f"Claude CLI failed: {error_msg}")
                return text  # Return original text on failure

            corrected = stdout.decode().strip()
            logger.debug(f"Claude corrected {len(text)} -> {len(corrected)} chars")
            return corrected

        except Exception as e:
            logger.error(f"Claude CLI error: {e}")
            return text  # Return original text on failure

    async def enhance_content(self, text: str, document_type: str = "general") -> str:
        """Enhance content structure using Claude."""
        prompt = self._create_enhancement_prompt(text, document_type)

        # Similar implementation to correct_text but with different prompt
        return await self._call_claude(prompt, fallback=text)

    def _create_correction_prompt(self, text: str, context: str) -> str:
        """Create prompt for OCR correction."""
        return f"""Instructions:
You are an expert OCR error correction specialist. The text below contains OCR errors that need to be fixed.

Task requirements:
- Correct only obvious OCR mistakes: character substitutions, garbled words, missing spaces
- Maintain ALL original formatting, structure, and meaning
- Do NOT add, remove, or rephrase any content
- Do NOT change correct words or proper formatting

Context: {context}

Text to correct:
\"\"\"
{text}
\"\"\"

Return only the corrected text, nothing else.""".strip()

    def _create_enhancement_prompt(self, text: str, document_type: str) -> str:
        """Create prompt for content enhancement."""
        return f"""Instructions:
You are an expert document formatter. The text below is a {document_type} document that needs formatting improvements.

Task requirements:
- Enhance formatting and structure while preserving ALL content
- Fix formatting issues: proper heading hierarchy, paragraph breaks, lists
- Improve readability through better organization
- Maintain ALL original information and meaning
- Do NOT add, remove, or rephrase any content

Text to enhance:
\"\"\"
{text}
\"\"\"

Return the enhanced text in markdown format, nothing else.""".strip()

    async def _call_claude(self, prompt: str, fallback: str) -> str:
        """Generic Claude CLI call with fallback."""
        cmd = [
            "claude",
            "--model", "claude-sonnet-4-20250514",
            "--dangerously-skip-permissions",
            "-p", prompt
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                logger.error(f"Claude CLI failed: {stderr.decode()}")
                return fallback

            return stdout.decode().strip()

        except Exception as e:
            logger.error(f"Claude CLI error: {e}")
            return fallback

    def is_available(self) -> bool:
        """Check if Claude CLI is available."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    async def enhance_pdf_structure(self, text_content: str) -> str:
        """Enhances PDF structure using Claude and returns a diff."""
        prompt = self._create_structure_enhancement_prompt(text_content)
        # This will call the Claude CLI with the prompt
        # and return the diff.
        return await self._call_claude(prompt, fallback="")

    def _create_structure_enhancement_prompt(self, text_content: str) -> str:
        return f"""Instructions:
You are an expert document editor. The text below was extracted from a PDF via OCR and may contain both textual errors and structural problems.

Task requirements:
- Step 1: Correct all orthographical (spelling, grammar) and logical errors (misplaced, repeated, or missing words)
- Step 2: Improve document structure: restore headings, paragraph breaks, bullet/numbered lists, and tables based on content context
- Step 3: Do NOT insert new content or change meaning - only correct errors and improve formatting/structure
- Step 4: Return ALL changes as a single unified diff (unidiff) format where removed lines are prefixed with "-" and added lines with "+"

Example unified diff format:
```
--- original
+++ corrected
@@ -1,3 +1,3 @@
 This line stays the same
-This line has an eror
+This line has an error
 Another unchanged line
```

Text to correct and format:
\"\"\"
{text_content}
\"\"\"

Output only the unified diff, nothing else.""".strip()


class GeminiCLIService(AIService):
    """Gemini CLI service integration."""

    def __init__(self, config: AIConfig):
        """Initialize Gemini service."""
        self.config = config

    async def correct_text(self, text: str, context: str = "") -> str:
        """Correct OCR errors using Gemini CLI."""
        prompt = self._create_correction_prompt(text, context)

        cmd = [
            "gemini",
            "-c",  # Continue conversation
            "-y",  # Yes to prompts
            "-p", prompt
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                logger.error(f"Gemini CLI failed: {stderr.decode()}")
                return text

            return stdout.decode().strip()

        except Exception as e:
            logger.error(f"Gemini CLI error: {e}")
            return text

    async def enhance_content(self, text: str, document_type: str = "general") -> str:
        """Enhance content using Gemini."""
        # Similar to correct_text with different prompt
        return text  # Placeholder

    def _create_correction_prompt(self, text: str, context: str) -> str:
        """Create OCR correction prompt for Gemini."""
        return f"""Instructions:
You are an expert OCR error correction specialist. The text below contains OCR errors that need to be fixed.

Task requirements:
- Correct only obvious OCR mistakes: character substitutions, garbled words, missing spaces
- Maintain ALL original formatting, structure, and meaning
- Do NOT add, remove, or rephrase any content
- Do NOT change correct words or proper formatting

Context: {context}

Text to correct:
\"\"\"
{text}
\"\"\"

Return only the corrected text, nothing else.""".strip()

    def is_available(self) -> bool:
        """Check if Gemini CLI is available."""
        try:
            result = subprocess.run(
                ["gemini", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    async def enhance_pdf_structure(self, text_content: str) -> str:
        """Enhances PDF structure using Gemini and returns a diff."""
        prompt = self._create_structure_enhancement_prompt(text_content)
        # This will call the Claude CLI with the prompt
        # and return the diff.
        return ""

    def _create_structure_enhancement_prompt(self, text_content: str) -> str:
        return f"""Instructions:
You are an expert document editor. The text below was extracted from a PDF via OCR and may contain both textual errors and structural problems.

Task requirements:
- Step 1: Correct all orthographical (spelling, grammar) and logical errors (misplaced, repeated, or missing words)
- Step 2: Improve document structure: restore headings, paragraph breaks, bullet/numbered lists, and tables based on content context
- Step 3: Do NOT insert new content or change meaning - only correct errors and improve formatting/structure
- Step 4: Return ALL changes as a single unified diff (unidiff) format where removed lines are prefixed with "-" and added lines with "+"

Example unified diff format:
```
--- original
+++ corrected
@@ -1,3 +1,3 @@
 This line stays the same
-This line has an eror
+This line has an error
 Another unchanged line
```

Text to correct and format:
\"\"\"
{text_content}
\"\"\"

Output only the unified diff, nothing else.""".strip()


class AIServiceFactory:
    """Factory for creating AI services."""

    @staticmethod
    def create_service(config: AIConfig) -> Optional[AIService]:
        """Create AI service based on configuration."""
        if not config.enabled:
            return None

        services = {
            "claude": ClaudeCLIService,
            "gemini": GeminiCLIService,
        }

        service_class = services.get(config.provider)
        if not service_class:
            logger.warning(f"Unknown AI provider: {config.provider}")
            return None

        service = service_class(config)

        if not service.is_available():
            logger.warning(f"AI service {config.provider} not available")
            return None

        return service

    @staticmethod
    def list_available_services() -> Dict[str, bool]:
        """List all AI services and their availability."""
        from ..config import AIConfig

        services = {}
        dummy_config = AIConfig(enabled=True)

        for provider in ["claude", "gemini"]:
            dummy_config.provider = provider
            service = AIServiceFactory.create_service(dummy_config)
            services[provider] = service is not None and service.is_available()

        return services
