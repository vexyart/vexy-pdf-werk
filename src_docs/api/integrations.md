# Integrations

This section describes the integration with external services, particularly AI services.

## `AIService`

The `AIService` class is an abstract base class that defines the interface for AI services. It has the following methods:

-   `correct_text(text: str, context: str = "") -> str`: Corrects OCR errors in text.
-   `enhance_content(text: str, document_type: str = "general") -> str`: Enhances content structure and formatting.
-   `enhance_pdf_structure(text_content: str) -> str`: Enhances PDF structure and returns a diff.
-   `is_available() -> bool`: Checks if the AI service is available.

## `ClaudeCLIService`

A concrete implementation of `AIService` that uses the `claude` CLI tool to interact with Anthropic's models.

## `GeminiCLIService`

A concrete implementation of `AIService` that uses the `gemini` CLI tool to interact with Google's models.

## `AIServiceFactory`

A factory class for creating AI services based on the configuration. It also provides a method to list all available AI services.
