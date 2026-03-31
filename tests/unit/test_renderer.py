from __future__ import annotations

from bug_report_normalizer.models import BugReportDraft, EnvironmentInfo
from bug_report_normalizer.renderer import (
    render_bug_report_as_json,
    render_bug_report_as_text,
)


def test_render_bug_report_as_json_returns_pretty_json() -> None:
    draft = BugReportDraft(
        title="Login button does nothing",
        summary="Clicking login has no visible effect.",
    )

    rendered = render_bug_report_as_json(draft)

    assert '"title": "Login button does nothing"' in rendered
    assert '"summary": "Clicking login has no visible effect."' in rendered
    assert "\n" in rendered


def test_render_bug_report_as_text_renders_all_sections() -> None:
    draft = BugReportDraft(
        title="Checkout spinner never ends",
        summary="Payment submission never completes.",
        observed_behavior="Spinner stays visible forever.",
        steps_to_reproduce=[
            "Open checkout page",
            "Click Pay now",
        ],
        environment=EnvironmentInfo(
            environment_name="staging",
            browser="Firefox",
            operating_system="Ubuntu 24.04",
            device="desktop",
        ),
        missing_information=[
            "Affected account type",
        ],
    )

    rendered = render_bug_report_as_text(draft)

    assert "Title:" in rendered
    assert "Summary:" in rendered
    assert "Observed behavior:" in rendered
    assert "Steps to reproduce:" in rendered
    assert "Environment:" in rendered
    assert "Missing information:" in rendered
    assert "- Open checkout page" in rendered
    assert "- Browser: Firefox" in rendered
    assert "- Affected account type" in rendered


def test_render_bug_report_as_text_shows_placeholders_for_missing_values() -> None:
    draft = BugReportDraft(
        title="Profile page is blank",
        summary="Opening profile page shows no content.",
    )

    rendered = render_bug_report_as_text(draft)

    assert "(not provided)" in rendered
    assert "(none identified)" in rendered
