from __future__ import annotations

import pytest

from bug_report_normalizer.exceptions import (
    LLMOutputParseError,
    LLMOutputValidationError,
)
from bug_report_normalizer.service import (
    draft_bug_report,
    parse_llm_json_object,
    validate_bug_report_payload,
)
from tests.fakes import FakeLLMClient


def test_parse_llm_json_object_returns_dict_for_valid_json() -> None:
    payload = parse_llm_json_object(
        """
        {
          "title": "Login button does nothing",
          "summary": "Clicking login has no visible effect."
        }
        """
    )

    assert payload["title"] == "Login button does nothing"
    assert payload["summary"] == "Clicking login has no visible effect."


def test_parse_llm_json_object_rejects_invalid_json() -> None:
    with pytest.raises(LLMOutputParseError, match="invalid JSON"):
        parse_llm_json_object("not a json payload")


def test_parse_llm_json_object_rejects_non_object_json() -> None:
    with pytest.raises(LLMOutputParseError, match="JSON object"):
        parse_llm_json_object('["wrong", "shape"]')


def test_validate_bug_report_payload_returns_domain_model() -> None:
    draft = validate_bug_report_payload(
        {
            "title": "Checkout spinner never ends",
            "summary": "The spinner remains visible after clicking Pay now.",
            "observed_behavior": "The page does not move to confirmation.",
            "steps_to_reproduce": [
                "Open checkout page",
                "Enter valid payment data",
                "Click Pay now",
            ],
            "environment": {
                "environment_name": "production",
                "browser": "Safari",
                "operating_system": "iOS 17",
                "device": "iPhone 13",
            },
            "missing_information": [
                "Whether the issue happens for all cards",
            ],
        }
    )

    assert draft.title == "Checkout spinner never ends"
    assert draft.environment.browser == "Safari"
    assert draft.steps_to_reproduce[0] == "Open checkout page"


def test_validate_bug_report_payload_rejects_contract_mismatch() -> None:
    with pytest.raises(LLMOutputValidationError, match="contract"):
        validate_bug_report_payload(
            {
                "title": "Missing summary example",
                "steps_to_reproduce": [],
                "environment": {},
                "missing_information": [],
            }
        )


def test_draft_bug_report_returns_validated_model_and_calls_client() -> None:
    client = FakeLLMClient(
        """
        {
          "title": "Search returns no results",
          "summary": "A valid product query shows an empty state.",
          "observed_behavior": "The results list stays empty.",
          "steps_to_reproduce": [
            "Open search page",
            "Enter a known product name",
            "Press Enter"
          ],
          "environment": {
            "environment_name": "staging",
            "browser": "Chrome",
            "operating_system": "Ubuntu 24.04",
            "device": "desktop"
          },
          "missing_information": [
            "Whether this happens for all product categories"
          ]
        }
        """
    )

    draft = draft_bug_report(
        raw_note="""
        Search seems broken.
        When I search for a product that should exist, I get empty results.
        Seen on Chrome on Ubuntu.
        """,
        client=client,
    )

    assert draft.title == "Search returns no results"
    assert draft.environment.browser == "Chrome"
    assert len(client.calls) == 1

    recorded_call = client.calls[0]
    assert "Search seems broken." in recorded_call["prompt"]
    assert recorded_call["system_prompt"] is not None
    assert recorded_call["schema"]["type"] == "object"


def test_draft_bug_report_raises_parse_error_for_invalid_json_response() -> None:
    client = FakeLLMClient("this is not valid json")

    with pytest.raises(LLMOutputParseError, match="invalid JSON"):
        draft_bug_report(
            raw_note="Login does not work on Firefox.",
            client=client,
        )


def test_draft_bug_report_raises_validation_error_for_invalid_contract() -> None:
    client = FakeLLMClient(
        """
        {
          "title": "Blank summary example",
          "summary": "   ",
          "observed_behavior": null,
          "steps_to_reproduce": [],
          "environment": {},
          "missing_information": []
        }
        """
    )

    with pytest.raises(LLMOutputValidationError, match="contract"):
        draft_bug_report(
            raw_note="Checkout issue observed after clicking submit.",
            client=client,
        )
