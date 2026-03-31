from __future__ import annotations

import json
from typing import Any

BUG_REPORT_SYSTEM_PROMPT = """You are a careful QA assistant.

Your task is to transform a raw bug note into a structured draft bug report.

Rules:
- Use only information that is present in the source note.
- Do not invent facts.
- Do not guess environment details, versions, or reproduction steps.
- When important information is missing, leave the relevant field empty or null
  and include the gap in missing_information.
- Fields marked as required (like 'title' and 'summary') MUST NOT be empty strings.
- Return only valid JSON that matches the requested schema.
"""


def build_bug_report_prompt(raw_note: str, output_schema: dict[str, Any]) -> str:
    note = raw_note.strip()
    if not note:
        raise ValueError("raw_note must not be empty.")

    schema_json = json.dumps(output_schema, indent=2, sort_keys=True)

    return f"""Transform the raw bug note into a structured draft bug report.

Return valid JSON only.

JSON schema:
{schema_json}

Raw bug note:
{note}
"""
