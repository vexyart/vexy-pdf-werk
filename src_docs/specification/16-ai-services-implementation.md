#### 51.0.1. AI Services Integration

##### AI Services Factory and Implementations (`src/vexy_pdf_werk/integrations/ai_services.py`)

```python
## 52. this_file: src/vexy_pdf_werk/integrations/ai_services.py

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
        return f"""
Please review and correct any OCR errors in the following text.
Maintain the original formatting, structure, and meaning.
Only fix obvious OCR mistakes like character substitutions or garbled words.
Do not add, remove, or rephrase content.

Context: {context}

Text to correct:
{text}

Return only the corrected text, nothing else.
        """.strip()

    def _create_enhancement_prompt(self, text: str, document_type: str) -> str:
        """Create prompt for content enhancement."""
        return f"""
Please enhance the formatting and structure of this {document_type} text while preserving all content.
Fix any formatting issues, ensure proper heading hierarchy, and improve readability.
Maintain all original information and meaning.

Text to enhance:
{text}

Return the enhanced text in markdown format.
        """.strip()

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
        return f"Correct OCR errors in this text, maintaining original meaning:\n\n{text}"

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
```