from __future__ import annotations

import pytest

from bug_report_normalizer.prompts import BUG_REPORT_SYSTEM_PROMPT, build_bug_report_prompt


def test_system_prompt_contains_non_hallucination_rule() -> None:
    assert "Do not invent facts." in BUG_REPORT_SYSTEM_PROMPT


def test_build_bug_report_prompt_includes_raw_note_and_schema() -> None:
    raw_note = "Checkout fails after clicking Pay now."
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"},
        },
    }

    prompt = build_bug_report_prompt(raw_note=raw_note, output_schema=schema)

    assert "Checkout fails after clicking Pay now." in prompt
    assert '"title"' in prompt
    assert '"summary"' in prompt
    assert "Return valid JSON only." in prompt


def test_build_bug_report_prompt_rejects_blank_note() -> None:
    with pytest.raises(ValueError):
        build_bug_report_prompt(raw_note="   ", output_schema={"type": "object"})
