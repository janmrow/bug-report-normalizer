from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Protocol

from bug_report_normalizer.exceptions import OllamaRequestError, OllamaResponseError


class LLMClient(Protocol):
    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
    ) -> str:
        """Generate structured JSON text from a prompt."""


def _build_ollama_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/api/generate"


def _post_json(url: str, payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise OllamaRequestError(
            f"Ollama request failed with status {exc.code}: {error_body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise OllamaRequestError(f"Could not reach Ollama at {url}: {exc.reason}") from exc

    try:
        decoded = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise OllamaResponseError("Ollama returned a non-JSON HTTP response.") from exc

    if not isinstance(decoded, dict):
        raise OllamaResponseError("Ollama returned an unexpected response shape.")

    return decoded


class OllamaClient:
    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout_seconds: float = 120.0,
    ) -> None:
        if not model.strip():
            raise ValueError("model must not be empty.")
        if not base_url.strip():
            raise ValueError("base_url must not be empty.")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")

        self.model = model.strip()
        self.base_url = base_url.strip()
        self.timeout_seconds = timeout_seconds

    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
    ) -> str:
        if not prompt.strip():
            raise ValueError("prompt must not be empty.")

        request_payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "format": schema,
            "stream": False,
        }

        if system_prompt is not None:
            request_payload["system"] = system_prompt

        response_payload = _post_json(
            url=_build_ollama_url(self.base_url),
            payload=request_payload,
            timeout_seconds=self.timeout_seconds,
        )

        if "error" in response_payload:
            raise OllamaResponseError(f"Ollama returned an error: {response_payload['error']}")

        response_text = response_payload.get("response")
        if not isinstance(response_text, str):
            raise OllamaResponseError("Ollama response did not include a valid text response.")

        return response_text
