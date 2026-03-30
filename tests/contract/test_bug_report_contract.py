from __future__ import annotations

from bug_report_normalizer.models import BugReportDraft


def test_bug_report_contract_serializes_to_expected_shape() -> None:
    draft = BugReportDraft(
        title="Search results are empty",
        summary="Search returns no results for a valid query.",
        observed_behavior="Page shows an empty state.",
        steps_to_reproduce=[
            "Open the search page",
            "Enter a valid product name",
            "Press Enter",
        ],
        missing_information=[
            "Affected environment",
            "Whether issue is reproducible every time",
        ],
    )

    payload = draft.model_dump()

    assert set(payload.keys()) == {
        "title",
        "summary",
        "observed_behavior",
        "steps_to_reproduce",
        "environment",
        "missing_information",
    }

    assert set(payload["environment"].keys()) == {
        "environment_name",
        "browser",
        "operating_system",
        "device",
    }


def test_bug_report_contract_uses_lists_not_nulls_for_collection_fields() -> None:
    draft = BugReportDraft(
        title="Profile page crashes",
        summary="The page crashes after opening the profile tab.",
    )

    payload = draft.model_dump()

    assert payload["steps_to_reproduce"] == []
    assert payload["missing_information"] == []
    assert payload["environment"] == {
        "environment_name": None,
        "browser": None,
        "operating_system": None,
        "device": None,
    }
