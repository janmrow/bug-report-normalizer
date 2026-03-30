from __future__ import annotations


class LLMClientError(Exception):
    """Base exception for LLM client failures."""


class OllamaRequestError(LLMClientError):
    """Raised when the request to Ollama cannot be completed."""


class OllamaResponseError(LLMClientError):
    """Raised when Ollama returns an invalid or unusable response."""


class BugReportDraftingError(Exception):
    """Base exception for bug report drafting failures."""


class LLMOutputParseError(BugReportDraftingError):
    """Raised when LLM output cannot be parsed as the expected JSON object."""


class LLMOutputValidationError(BugReportDraftingError):
    """Raised when parsed LLM output does not match the bug report contract."""
