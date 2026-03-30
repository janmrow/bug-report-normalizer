from __future__ import annotations


class LLMClientError(Exception):
    """Base exception for LLM client failures."""


class OllamaRequestError(LLMClientError):
    """Raised when the request to Ollama cannot be completed."""


class OllamaResponseError(LLMClientError):
    """Raised when Ollama returns an invalid or unusable response."""
