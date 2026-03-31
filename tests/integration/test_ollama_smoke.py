from __future__ import annotations

import os

import pytest

from bug_report_normalizer.llm_client import OllamaClient
from bug_report_normalizer.service import draft_bug_report

pytestmark = pytest.mark.integration


def _require_integration_mode() -> None:
    if os.environ.get("RUN_OLLAMA_INTEGRATION") != "1":
        pytest.skip("Set RUN_OLLAMA_INTEGRATION=1 to run Ollama integration tests.")


def _require_model_name() -> str:
    model = os.environ.get("OLLAMA_MODEL")
    if not model:
        pytest.skip("Set OLLAMA_MODEL to run Ollama integration tests.")
    return model


def _build_client() -> OllamaClient:
    model = _require_model_name()
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    return OllamaClient(
        model=model,
        base_url=base_url,
        timeout_seconds=120.0,
    )


def test_ollama_smoke_returns_contract_valid_output() -> None:
    _require_integration_mode()
    client = _build_client()

    draft = draft_bug_report(
        raw_note="""
        Search page seems broken.
        When I enter the name of a product that definitely exists in our database,
        the search results page is completely empty.
        Seen on Chrome on Ubuntu.
        """,
        client=client,
    )

    assert draft.title
    assert draft.summary
    assert isinstance(draft.steps_to_reproduce, list)
    assert isinstance(draft.missing_information, list)


def test_ollama_smoke_preserves_key_input_signals_somewhere_in_output() -> None:
    _require_integration_mode()
    client = _build_client()

    draft = draft_bug_report(
        raw_note="""
        Search page seems broken.
        Searching for a known product returns empty results on Chrome on Ubuntu.
        """,
        client=client,
    )

    serialized_output = draft.model_dump_json().lower()

    assert "chrome" in serialized_output
    assert "ubuntu" in serialized_output
    assert "search" in serialized_output


def test_ollama_smoke_identifies_missing_information_without_hallucinating() -> None:
    _require_integration_mode()
    client = _build_client()

    draft = draft_bug_report(
        raw_note="""
        App crashed when I clicked the save button.
        I don't remember which screen it was.
        """,
        client=client,
    )

    assert draft.environment.browser is None
    assert draft.environment.operating_system is None
    assert draft.environment.device is None
    assert len(draft.missing_information) > 0
    serialized_missing = " ".join(draft.missing_information).lower()
    assert "screen" in serialized_missing or "environment" in serialized_missing
