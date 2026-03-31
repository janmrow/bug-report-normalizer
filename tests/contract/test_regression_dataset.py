from __future__ import annotations

import json
from pathlib import Path

import pytest

from bug_report_normalizer.service import draft_bug_report
from tests.fakes import FakeLLMClient

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "regression_cases.json"


with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
    REGRESSION_CASES = json.load(fixture_file)


@pytest.mark.parametrize(
    "case",
    REGRESSION_CASES,
    ids=[case["name"] for case in REGRESSION_CASES],
)
def test_regression_cases_produce_validated_bug_report_drafts(case: dict[str, object]) -> None:
    llm_response = json.dumps(case["llm_response"])
    client = FakeLLMClient(llm_response)

    draft = draft_bug_report(
        raw_note=str(case["raw_note"]),
        client=client,
    )

    expected = case["expected"]

    assert draft.title == expected["title"]

    if "browser" in expected:
        assert draft.environment.browser == expected["browser"]

    if "device" in expected:
        assert draft.environment.device == expected["device"]

    if "operating_system" in expected:
        assert draft.environment.operating_system == expected["operating_system"]

    assert expected["missing_information_contains"] in draft.missing_information
    assert len(client.calls) == 1
