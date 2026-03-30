from __future__ import annotations

import pytest
from pydantic import ValidationError

from bug_report_normalizer.models import BugReportDraft, EnvironmentInfo


def test_environment_info_normalizes_blank_values_to_none() -> None:
    environment = EnvironmentInfo(
        environment_name="  ",
        browser="  Chrome  ",
        operating_system=" ",
        device="  iPhone  ",
    )

    assert environment.environment_name is None
    assert environment.browser == "Chrome"
    assert environment.operating_system is None
    assert environment.device == "iPhone"


def test_bug_report_draft_accepts_minimal_valid_payload() -> None:
    draft = BugReportDraft(
        title="Login button does nothing",
        summary="User clicks login button and nothing happens.",
    )

    assert draft.title == "Login button does nothing"
    assert draft.summary == "User clicks login button and nothing happens."
    assert draft.observed_behavior is None
    assert draft.steps_to_reproduce == []
    assert draft.missing_information == []
    assert draft.environment.environment_name is None


def test_bug_report_draft_normalizes_text_and_list_items() -> None:
    draft = BugReportDraft(
        title="  Checkout error  ",
        summary="  Payment fails after form submission.  ",
        observed_behavior="  Spinner stays visible forever.  ",
        steps_to_reproduce=[
            "  Open checkout page  ",
            "  Fill in card details  ",
        ],
        missing_information=[
            "  Browser version  ",
            "  Test account used  ",
        ],
    )

    assert draft.title == "Checkout error"
    assert draft.summary == "Payment fails after form submission."
    assert draft.observed_behavior == "Spinner stays visible forever."
    assert draft.steps_to_reproduce == [
        "Open checkout page",
        "Fill in card details",
    ]
    assert draft.missing_information == [
        "Browser version",
        "Test account used",
    ]


def test_bug_report_draft_rejects_blank_title() -> None:
    with pytest.raises(ValidationError):
        BugReportDraft(
            title="   ",
            summary="Valid summary",
        )


def test_bug_report_draft_rejects_blank_summary() -> None:
    with pytest.raises(ValidationError):
        BugReportDraft(
            title="Valid title",
            summary="   ",
        )


def test_bug_report_draft_rejects_blank_items_in_steps() -> None:
    with pytest.raises(ValidationError):
        BugReportDraft(
            title="Valid title",
            summary="Valid summary",
            steps_to_reproduce=["Open app", "   "],
        )


def test_bug_report_draft_rejects_blank_items_in_missing_information() -> None:
    with pytest.raises(ValidationError):
        BugReportDraft(
            title="Valid title",
            summary="Valid summary",
            missing_information=["Browser version", ""],
        )
