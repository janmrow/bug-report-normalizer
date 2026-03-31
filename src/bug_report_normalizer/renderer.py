from __future__ import annotations

from bug_report_normalizer.models import BugReportDraft


def render_bug_report_as_json(draft: BugReportDraft) -> str:
    return draft.model_dump_json(indent=2)


def render_bug_report_as_text(draft: BugReportDraft) -> str:
    observed_behavior = draft.observed_behavior or "(not provided)"

    steps = _render_list(
        draft.steps_to_reproduce,
        empty_label="(not provided)",
    )
    missing_information = _render_list(
        draft.missing_information,
        empty_label="(none identified)",
    )

    environment_lines = [
        f"- Environment name: {draft.environment.environment_name or '(not provided)'}",
        f"- Browser: {draft.environment.browser or '(not provided)'}",
        f"- Operating system: {draft.environment.operating_system or '(not provided)'}",
        f"- Device: {draft.environment.device or '(not provided)'}",
    ]

    lines = [
        "Title:",
        draft.title,
        "",
        "Summary:",
        draft.summary,
        "",
        "Observed behavior:",
        observed_behavior,
        "",
        "Steps to reproduce:",
        steps,
        "",
        "Environment:",
        *environment_lines,
        "",
        "Missing information:",
        missing_information,
    ]

    return "\n".join(lines)


def _render_list(items: list[str], *, empty_label: str) -> str:
    if not items:
        return f"- {empty_label}"

    return "\n".join(f"- {item}" for item in items)
