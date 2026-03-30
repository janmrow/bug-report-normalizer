from __future__ import annotations

import pytest

from bug_report_normalizer.exceptions import OllamaResponseError
from bug_report_normalizer.llm_client import OllamaClient


def test_ollama_client_builds_expected_request_payload(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_post_json(
        url: str, payload: dict[str, object], timeout_seconds: float
    ) -> dict[str, object]:
        captured["url"] = url
        captured["payload"] = payload
        captured["timeout_seconds"] = timeout_seconds
        return {"response": '{"title":"Example","summary":"Example summary"}'}

    monkeypatch.setattr("bug_report_normalizer.llm_client._post_json", fake_post_json)

    client = OllamaClient(
        model="llama3.2",
        base_url="http://localhost:11434",
        timeout_seconds=12.0,
    )

    schema = {"type": "object"}
    result = client.generate_json(
        prompt="Normalize this bug note",
        schema=schema,
        system_prompt="System instructions",
    )

    assert result == '{"title":"Example","summary":"Example summary"}'
    assert captured["url"] == "http://localhost:11434/api/generate"
    assert captured["timeout_seconds"] == 12.0
    assert captured["payload"] == {
        "model": "llama3.2",
        "prompt": "Normalize this bug note",
        "format": schema,
        "stream": False,
        "system": "System instructions",
    }


def test_ollama_client_raises_when_response_contains_error(monkeypatch) -> None:
    def fake_post_json(
        url: str, payload: dict[str, object], timeout_seconds: float
    ) -> dict[str, object]:
        return {"error": "model not found"}

    monkeypatch.setattr("bug_report_normalizer.llm_client._post_json", fake_post_json)

    client = OllamaClient(model="llama3.2")

    with pytest.raises(OllamaResponseError, match="model not found"):
        client.generate_json(
            prompt="Normalize this bug note",
            schema={"type": "object"},
        )


def test_ollama_client_raises_when_response_field_is_missing(monkeypatch) -> None:
    def fake_post_json(
        url: str, payload: dict[str, object], timeout_seconds: float
    ) -> dict[str, object]:
        return {"done": True}

    monkeypatch.setattr("bug_report_normalizer.llm_client._post_json", fake_post_json)

    client = OllamaClient(model="llama3.2")

    with pytest.raises(OllamaResponseError, match="valid text response"):
        client.generate_json(
            prompt="Normalize this bug note",
            schema={"type": "object"},
        )


def test_ollama_client_rejects_blank_prompt() -> None:
    client = OllamaClient(model="llama3.2")

    with pytest.raises(ValueError, match="prompt must not be empty"):
        client.generate_json(
            prompt="   ",
            schema={"type": "object"},
        )


def test_ollama_client_rejects_invalid_constructor_inputs() -> None:
    with pytest.raises(ValueError, match="model must not be empty"):
        OllamaClient(model="   ")

    with pytest.raises(ValueError, match="base_url must not be empty"):
        OllamaClient(model="llama3.2", base_url="   ")

    with pytest.raises(ValueError, match="greater than zero"):
        OllamaClient(model="llama3.2", timeout_seconds=0)
