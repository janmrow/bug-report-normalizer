from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from bug_report_normalizer.exceptions import (
    LLMOutputParseError,
    LLMOutputValidationError,
)
from bug_report_normalizer.llm_client import LLMClient
from bug_report_normalizer.models import BugReportDraft
from bug_report_normalizer.prompts import (
    BUG_REPORT_SYSTEM_PROMPT,
    build_bug_report_prompt,
)


def parse_llm_json_object(response_text: str) -> dict[str, Any]:
    if not response_text.strip():
        raise LLMOutputParseError("LLM returned an empty response.")

    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise LLMOutputParseError("LLM returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise LLMOutputParseError("LLM output must be a JSON object.")

    return payload


def validate_bug_report_payload(payload: dict[str, Any]) -> BugReportDraft:
    try:
        return BugReportDraft.model_validate(payload)
    except ValidationError as exc:
        raise LLMOutputValidationError("LLM JSON did not match the bug report contract.") from exc


def draft_bug_report(
    *,
    raw_note: str,
    client: LLMClient,
    system_prompt: str = BUG_REPORT_SYSTEM_PROMPT,
) -> BugReportDraft:
    schema = BugReportDraft.model_json_schema()
    prompt = build_bug_report_prompt(
        raw_note=raw_note,
        output_schema=schema,
    )

    response_text = client.generate_json(
        prompt=prompt,
        schema=schema,
        system_prompt=system_prompt,
    )

    payload = parse_llm_json_object(response_text)
    return validate_bug_report_payload(payload)
